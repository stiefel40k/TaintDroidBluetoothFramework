#!/usr/bin/env python3

from framework import loganalysis, visualizeanalysis, correlate
from framework.external import deguard
from framework.model.AnalysisResults import AnalysisResults
import sys

analysis_result = None
analysis_results = []

header = r''' (
 )\ )                                                )
(()/(  (       )     )      (   (  (         (    ( /(
 /(_)) )(   ( /(    (      ))\  )\))(    (   )(   )\())
(_))_|(()\  )(_))   )\  ' /((_)((_)()\   )\ (()\ ((_)\
| |_   ((_)((_)_  _((_)) (_))  _(()((_) ((_) ((_)| |(_)
| __| | '_|/ _` || '  \()/ -_) \ V  V // _ \| '_|| / /
|_|   |_|  \__,_||_|_|_| \___|  \_/\_/ \___/|_|  |_\_\
'''


def check_return_value(return_value):
    global analysis_result
    global analysis_results
    if return_value is None:
        return
    if type(return_value) == AnalysisResults:
        analysis_result = return_value
        analysis_results.append(analysis_result)


def get_choice(menu_items):
    """
    Print the possible choices and read user input
    :param menu_items: possible choices
    :return: a list containing the users' menu choice and additional arguments
    """
    for item in menu_items:
        print("[{}] {}".format(str(menu_items.index(item)),
                               list(item.keys())[0]))
    return input(">> ").rstrip().split(' ')


def submenu_external():
    menu_items = [
        {"Deobfuscate APK path [output=<output dir>] [timeout=<timeout>]":
            getattr(deguard, 'upload_to_deguard')},
        {"Back": "back"}
    ]
    while True:
        user_input = get_choice(menu_items)
        try:
            choice = int(user_input[0])
            to_execute = list(menu_items[choice].values())[0]
            if "back" == to_execute:
                return
            else:
                list(menu_items[choice].values())[0](*user_input[1:])
        except(ValueError, IndexError):
            pass


def submenu_correlation():
    global analysis_results
    menu_items = [
        {"Show common UUIDs [limit]":
         getattr(correlate, 'show_common_uuids')},
        {"Back": "back"}
    ]
    while True:
        user_input = get_choice(menu_items)
        if len(analysis_results) == 0:
            print("WARNING: You should first execute at least one analysis!")
            print("Exiting submenu")
            user_input = [len(menu_items) - 1]
        try:
            choice = int(user_input[0])
            to_execute = list(menu_items[choice].values())[0]
            if "back" == to_execute:
                return
            else:
                return_value = list(menu_items[choice].values())[0](
                    analysis_results, *user_input[1:])
                check_return_value(return_value)
        except(ValueError, IndexError):
            pass


def submenu_show_results():
    global analysis_result
    menu_items = [
        {"Show all UUIDs [limit]":
            getattr(visualizeanalysis, 'show_all_leak_uuid')},
        {"Show service UUIDs [limit]":
            getattr(visualizeanalysis, 'show_service_leak_uuid')},
        {"Show characteristic UUIDs [limit]":
            getattr(visualizeanalysis, 'show_characteristic_leak_uuid')},
        {"Show descriptor UUIDs [limit]":
            getattr(visualizeanalysis, 'show_descriptor_leak_uuid')},
        {"Show other categorized UUIDs [limit]":
             getattr(visualizeanalysis, 'show_categorized_leak_uuid')},
        {"Show call traces [mapping path]":
            getattr(visualizeanalysis, 'show_call_traces')},
        {"Show path of dumped BLE traffic":
            getattr(visualizeanalysis, 'show_dump_paths')},
        {"Download dumps [output path]":
            getattr(visualizeanalysis, 'download_dumps')},
        {"Back": "back"}
    ]
    while True:
        user_input = get_choice(menu_items)
        if analysis_result is None:
            print("WARNING: You should first execute an analysis!")
            print("Exiting submenu")
            user_input = [len(menu_items) - 1]
        try:
            choice = int(user_input[0])
            to_execute = list(menu_items[choice].values())[0]
            if "back" == to_execute:
                return
            else:
                return_value = list(menu_items[choice].values())[0](
                    analysis_result, *user_input[1:])
                check_return_value(return_value)
        except(ValueError, IndexError):
            pass


def main():
    menu_items = [
        {"Start log analysis": getattr(loganalysis, 'analyse_logcat')},
        {"Show analysis results": submenu_show_results},
        {"Correlate analysis results": submenu_correlation},
        {"External analysis": submenu_external},
        {"Exit": sys.exit},
    ]
    print(header)
    while True:
        user_input = get_choice(menu_items)
        try:
            choice = int(user_input[0])
            return_value = list(menu_items[choice].values())[0]()
            check_return_value(return_value)
        except(ValueError, IndexError):
            pass


if "__main__" == __name__:
    main()
