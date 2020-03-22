import os
import subprocess

from framework.model.AnalysisResults import AnalysisResults
from framework.model.Mapping import Mapping
from framework.utils import iohelpers


#####################################################
#           UUID Related methods begin              #
#####################################################
def show_all_leak_uuid(analysis_result, *args):
    """
    Show every leaked UUID sorted by occurrence

    :param analysis_result: an AnalysisResult
    :type analysis_result: AnalysisResults
    :param args: at the first place the can optionally be passed a limit to
        only show the first <limit> UUIDs
    :type args: list
    """
    iohelpers.process_show_uuid(analysis_result.leaked_uuids, args)


def show_service_leak_uuid(analysis_result, *args):
    """
    Show every leaked Service-UUID sorted by occurrence

    :param analysis_result: an AnalysisResult
    :type analysis_result: AnalysisResults
    :param args: at the first place the can optionally be passed a limit to
        only show the first <limit> UUIDs
    :type args: list
    """
    iohelpers.process_show_uuid(analysis_result.leaked_service_uuids,
                                args, 'Service-')


def show_characteristic_leak_uuid(analysis_result, *args):
    """
    Show every leaked Characteristic-UUID sorted by occurrence

    :param analysis_result: an AnalysisResult
    :type analysis_result: AnalysisResults
    :param args: at the first place the can optionally be passed a limit to
        only show the first <limit> UUIDs
    :type args: list
    """
    iohelpers.process_show_uuid(analysis_result.leaked_characteristic_uuids,
                                args, 'Characteristic-')


def show_descriptor_leak_uuid(analysis_result, *args):
    """
    Show every leaked Descriptor-UUID sorted by occurrence

    :param analysis_result: an AnalysisResult
    :type analysis_result: AnalysisResults
    :param args: at the first place the can optionally be passed a limit to
        only show the first <limit> UUIDs
    :type args: list
    """
    iohelpers.process_show_uuid(analysis_result.leaked_descriptor_uuids, args,
                                'Descriptor-')


def show_categorized_leak_uuid(analysis_result, *args):
    """
    Show every leaked Descriptor-UUID sorted by occurrence

    :param analysis_result: an AnalysisResult
    :type analysis_result: AnalysisResults
    :param args: at the first place the can optionally be passed a limit to
        only show the first <limit> UUIDs
    :type args: list
    """
    iohelpers.process_show_misc_uuid(
        analysis_result.leaked_categorized_misc_uuids, args)


#####################################################
#        Call trace related methods begin           #
#####################################################
def __check_mapping_path(args):
    path = None
    if len(args) > 0:
        path = args[0]

    return path


def __filter_out_unique_call_trace(call_traces):
    return list(set(tuple(row) for row in call_traces))


def __print_calls(call_traces):
    for call_trace in call_traces:
        print('\n'.join(call_trace))
        user_choice = iohelpers.yes_no_choice("Continue? [Y/n] ",
                                              {"default": 'y',
                                               "non-default": 'n'})
        if user_choice['yes']:
            continue
        else:
            break


def __rebuild_line(line, mapping):
    # remove leading at
    important_part = line.split('at ')[1]
    # remove line information
    important_part = important_part[:important_part.index('(')]

    # split on every dot
    splitted_important_part = important_part.split('.')
    # take possible class parts and method part apart
    class_parts = splitted_important_part[:len(splitted_important_part) - 1]
    method_name = splitted_important_part[len(splitted_important_part) - 1]

    # check if we can find a mapping
    for i in range(len(class_parts), 0, -1):
        current_try = '.'.join(class_parts[:i])
        if current_try in mapping.classes:
            mapped_class = mapping.classes[current_try]
            break
    else:
        # We didn't find a mapping
        mapped_class = None

    if mapped_class is None:
        # If the class is not mapped, than we can ignore the whole thing
        return line

    new_line = line.replace(mapped_class.original_name, mapped_class.new_name)

    mapped_method = mapped_class.methods.get(method_name, None)

    if mapped_method is None:
        # If only the class name has been mapped, than we ignore the rest
        return new_line

    # Replace the method name as well
    return new_line.replace(
        '{}.{}'.format(mapped_class.new_name, mapped_method.original_name),
        '{}.{}'.format(mapped_class.new_name, mapped_method.new_name))


def __print_calls_with_mapping(call_traces, mapping_path):
    with open(mapping_path, 'r') as f:
        mapping = f.readlines()

    mapping = Mapping(mapping)
    for call_trace in call_traces:
        new_trace = [call_trace[0]]
        for line in call_trace[1:]:
            new_trace.append(__rebuild_line(line, mapping))

        print('\n'.join(new_trace))
        user_choice = iohelpers.yes_no_choice("Continue? [Y/n] ",
                                              {"default": 'y',
                                               "non-default": 'n'})
        if user_choice['yes']:
            continue
        else:
            break


def show_call_traces(analysis_result, *args):
    """
    Prints the collected call traces one after another
    :param analysis_result: an AnalysisResult object
    :type analysis_result: AnalysisResults
    :param args: it is currently not used
    :type args: list
    """
    unique_calls = __filter_out_unique_call_trace(analysis_result.call_paths)
    mapping_path = __check_mapping_path(args)
    if mapping_path is None:
        __print_calls(unique_calls)
    else:
        __print_calls_with_mapping(unique_calls, mapping_path)


#####################################################
#         Dump path related methods begin           #
#####################################################
def __check_path(args):
    path = "/tmp/ble-dump"
    if len(args) > 0:
        path = args[0]

    return path


def __download_file_from_phone(remote_path, output_path):
    # TODO: rewrite to this as soon as
    #  core/java/android/bluetooth/BluetoothGatt.java has been updated to
    #  set permissions to 777 `with subprocess.Popen(["adb", "pull",
    #  remote_path, output_path])`
    with open("{}/{}".format(output_path, remote_path.split('/')[-1]),
              'wb') as f:
        with subprocess.Popen(
                ["adb", "-d", "shell", "su -c cat {}".format(remote_path)],
                stdout=f) as adb:
            print("Waiting for adb to pull file")
            adb.wait()
            if adb.poll() != 0:
                print("File {} couldn't be pulled".format(remote_path))


def show_dump_paths(analysis_result, *args):
    """
    Prints the paths of dumped BLE traffic

    :param analysis_result: an AnalysisResult object
    :type analysis_result: AnalysisResults
    :param args: it is currently not used
    :type args: list
    """
    print("Paths of BLE traffic dumps")
    print('\n'.join(analysis_result.dump_paths))


def download_dumps(analysis_result, *args):
    """
    Downloads the dumps from the phone to the host

    :param analysis_result: an AnalysisResult object
    :type analysis_result: AnalysisResults
    :param args: the first argument should be the output folder default is
        /tmp/ble-dump
    :type args: list
    """
    output_path = __check_path(args)
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for path in analysis_result.dump_paths:
        __download_file_from_phone(path, output_path)
    pass
