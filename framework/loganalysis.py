import re
import subprocess
import queue

from framework.utils import logreader, iohelpers, uuidlookup
from framework.model.AnalysisResults import AnalysisResults
from framework.model.SIG import *


# Regular expressions to find our own logs
pattern_prefix = r'W/TaintLog\( *\d+\): '
prefix_pattern = re.compile(pattern_prefix)
exception_pattern = re.compile(pattern_prefix + '.*This is a fake exception.*')
exception_multiline_pattern = re.compile(pattern_prefix + r'\s*at .*')
data_dump_pattern = re.compile(pattern_prefix + r"Data dumped at /data/asdasd/.*\.dump")

# Results accumulator
analysis_result: AnalysisResults


def __print_warning():
    print("Please verify that a device is connected and adb can see it")
    input("Press [Enter] to continue...")


def __is_uuid_leak(line):
    return "UUID-LEAK" in line


def __parse_leaked_uuid(line):
    return line.split('UUID-LEAK: ')[1]


def __parse_prefix_leaked_uuid(line):
    if 'SERVICE' in line:
        return 'SERVICE-'
    elif 'CHARACTERISTIC' in line:
        return 'CHARACTERISTIC-'
    elif 'DESCRIPTOR' in line:
        return 'DESCRIPTOR-'
    else:
        return ''


def __is_data_dumped(line):
    return re.search(data_dump_pattern, line) is not None


def __parse_dump_path(line):
    return line.split('Data dumped at ')[1]


def __is_custom_exception(line):
    return re.search(exception_pattern, line) is not None


def __is_custom_exception_multiline(line):
    return re.search(exception_multiline_pattern, line) is not None


def __create_or_increase_count(dictionary, uuid, predef_id):
    meta_data_name = '-' if predef_id is None else predef_id.name
    if uuid not in dictionary.keys():
        dictionary[uuid] = {'counter': 1, 'name': meta_data_name}
    else:
        dictionary[uuid]['counter'] = dictionary[uuid]['counter'] + 1


def __put_uuid_in_category(prefix, uuid, predef_id):
    if 'SERVICE' in prefix:
        __create_or_increase_count(analysis_result.leaked_service_uuids, uuid, predef_id)
    elif 'CHARACTERISTIC' in prefix:
        __create_or_increase_count(analysis_result.leaked_characteristic_uuids, uuid, predef_id)
    elif 'DESCRIPTOR' in prefix:
        __create_or_increase_count(analysis_result.leaked_descriptor_uuids, uuid, predef_id)
    else:
        misc_key = type(predef_id).__name__.split('.')[-1]
        misc_key_dict = analysis_result.leaked_categorized_misc_uuids.get(misc_key, {})
        newly_created = len(misc_key_dict.keys()) == 0
        __create_or_increase_count(misc_key_dict, uuid, predef_id)
        if newly_created:
            analysis_result.leaked_categorized_misc_uuids[misc_key] = misc_key_dict


def __clear_ring_buffer():
    user_choice = iohelpers.yes_no_choice("Clear ring buffers on device? [y/N] ", {"default": 'n', "non-default": 'y'})
    if user_choice['yes']:
        with subprocess.Popen(["adb", "logcat", "-c"]) as logcat:
            print("Waiting for adb to finish")
            logcat.wait()
        print("Clear done")


def analyse_logcat():
    """
    Performs the analysis of the live Logs provided by the Android logcat
    facility.
    :return: an object containing call traces as strings and leaked UUIDs
    """
    global analysis_result
    __print_warning()
    __clear_ring_buffer()
    print("Starting log analysis")

    analysis_result = AnalysisResults()

    # Fork off adb logcat
    logcat = subprocess.Popen(["adb", "logcat", "-b", "main"],
                              stdout=subprocess.PIPE)

    # Launch the asynchronous readers of the process' stdout.
    stdout_queue = queue.Queue()
    stdout_reader = logreader.AsynchronousFileReader(logcat,
                                                     stdout_queue)
    # Begin to parse output of logcat an put into the queue
    stdout_reader.start()

    parsing_multiline = False
    print("Press [CTRL+C] to stop log processing")
    # Check the queues if we received some output (until there is nothing
    # more to get).
    current_multiline = []
    try:
        while True:
            if stdout_reader.eof():
                break

            # Ignore Empty exception as maybe nothing is currently written
            # to logcat, so we can't cancel the analysis. However as soon as
            # the phone is disconnected and so logcat is killed we stop the
            # analysis because we know that nothing else will come
            line = ''
            try:
                line = stdout_queue.get(block=False).decode(encoding="utf-8", errors='ignore').rstrip()
            except queue.Empty:
                pass

            # Check if we are handling an exception
            if parsing_multiline or __is_custom_exception(line):
                begin = False
                if not parsing_multiline:
                    print("Begin of multiline exception")
                    current_multiline = []
                    begin = True
                parsing_multiline = True
                if not (begin or __is_custom_exception_multiline(line)):
                    parsing_multiline = False
                    analysis_result.call_paths.append(current_multiline)
                    print('\n'.join(current_multiline))
                    print("End of multiline exception")
                else:
                    current_multiline.append(re.sub(prefix_pattern, '', line))
            # Check if the line contains a UUID
            elif __is_uuid_leak(line):
                uuid = __parse_leaked_uuid(line).lower()
                prefix = __parse_prefix_leaked_uuid(line)
                print("Found {}UUID: {}".format(prefix, uuid))
                predef_id = uuidlookup.check_if_uuid_predefined(uuid)
                __create_or_increase_count(analysis_result.leaked_uuids, uuid, predef_id)
                if predef_id is not None:
                    print("Found entry to {}: {}".format(uuid, predef_id.name))
                    if isinstance(predef_id, (Member, Service)):
                        prefix = 'SERVICE'
                    elif isinstance(predef_id, Characteristic):
                        prefix = 'CHARACTERISTIC'
                    elif isinstance(predef_id, Descriptor):
                        prefix = 'DESCRIPTOR'
                    else:
                        prefix = 'MISC'
                if len(prefix) > 0:
                    __put_uuid_in_category(prefix, uuid, predef_id)
            # Check if we are currently dumped data
            elif __is_data_dumped(line):
                path = __parse_dump_path(line)
                print("Dumped data at {}".format(path))
                analysis_result.dump_paths.append(path)
            # TODO: analyse the line
    except KeyboardInterrupt:
        pass
    finally:
        logcat.stdout.flush()
        logcat.kill()
        stdout_reader.cont = False

    return analysis_result
