import os
import time

import requests

from framework.model.Arguments import Arguments

__base_url = 'http://apk-deguard.com'
__upload_url = '{}/upload'.format(__base_url)
__status_url = '{}/status?fp={{}}'.format(__base_url)
__fetch_url = '{}/fetch?fp={{}}&q={{}}'.format(__base_url)


def __write_out_content(response, output):
    with open(output, 'wb') as f:
        f.write(response.content)


def __is_input_alright(path):
    if not path.endswith('.apk'):
        print("Only APK files are accepted")
        return False

    if not os.path.exists(path):
        print("File not found")
        return False

    if not os.path.isfile(path):
        print("Given path is not a file")
        return False

    return True


def __parse_args(args):
    if len(args) < 1:
        return None

    args_dict = {}
    for arg in args[1:]:
        key, value = arg.split('=')
        args_dict[key] = value

    return Arguments(path=args[0], **args_dict)


def upload_to_deguard(*args):
    """
    Uploads an APK to deguard and grabs the output

    :param args: at the first place the path should be and 'output' and
        'timeout' can optionally be specified
    :return:
    """
    arguments = __parse_args(args)

    if arguments is None:
        print("Path to apk is missing")
        return

    if not __is_input_alright(arguments.path):
        return

    if not os.path.exists(arguments.output):
        os.makedirs(arguments.output)

    session = requests.Session()
    session.get(__base_url)

    apk = {'file': open(arguments.path, 'rb')}
    print("Beginning to upload")
    resp = session.post(__upload_url, files=apk, data={'deguard': True})
    print("Upload done")
    try:
        json_resp = resp.json()
    except ValueError:
        print('Something went wrong with the upload: "{}" is the response'.format(resp.text))
        return

    if "fp" not in json_resp.keys():
        print("There is no session key - something went wrong")
        return

    fp = json_resp['fp']

    print("Waiting for deobfuscation. Please be patient, this can take up to "
          "10 minutes")
    status = session.get(__status_url.format(fp)).json()['progress']
    print("Status: {}".format(status))
    time_spent = 0
    while status != 'READY':
        if time_spent > arguments.timeout:
            print("Timeout reached")
            print("You can check manually using the session key '{}'".format(fp))
            return
        time.sleep(10)
        time_spent = time_spent + 10
        new_status = session.get(__status_url.format(fp)).json()['progress']
        if new_status != status:
            status = new_status
            print("Status: {}".format(status))

    mapping = session.get(__fetch_url.format(fp, 'mapping'))
    src = session.get(__fetch_url.format(fp, 'src'))
    output_apk = session.get(__fetch_url.format(fp, 'apk'))

    __write_out_content(mapping, os.path.join(arguments.output, 'mapping.txt'))
    __write_out_content(src, os.path.join(arguments.output, 'src.zip'))
    __write_out_content(output_apk, os.path.join(arguments.output, 'output.apk'))
