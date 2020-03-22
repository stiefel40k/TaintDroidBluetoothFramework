from tabulate import tabulate


#####################################################
#                Printing UUIDs                     #
#####################################################
def check_limit(args):
    limit = -1
    if len(args) > 0:
        try:
            limit = int(args[0])
        except ValueError:
            print("Limit is not a number - ignoring")

    return limit


def sort_and_limit(dictionary, limit):
    sorted_uuid = [(k, dictionary[k]['counter'], dictionary[k]['name'])
                   for k in sorted(dictionary,
                                   key=lambda x: dictionary[x]['counter'])]
    if limit > 0:
        return sorted_uuid[0:limit]
    else:
        return sorted_uuid


def print_result(sorted_uuid):
    print(tabulate(sorted_uuid, ['UUID', '# of occurrence', 'Official name'], tablefmt='grid'))


def process_show_uuid(dictionary, args, uuid_type=''):
    limit = check_limit(args)
    sorted_uuid = sort_and_limit(dictionary, limit)
    print("Showing every {}UUID".format(uuid_type))
    print_result(sorted_uuid)


def process_show_misc_uuid(dictionary, args):
    limit = check_limit(args)
    for key in dictionary.keys():
        sorted_uuid = sort_and_limit(dictionary[key], limit)
        print("Showing every {}-UUID".format(key))
        print_result(sorted_uuid)


#####################################################
#                  User input                       #
#####################################################
def yes_no_choice(text, possible_choices):
    """
    Reads in the users choice regarding a yes/no question

    :param text: the question and possible answers with default as capital
    :type text: str
    :param possible_choices: a dictionary, with "default" and "non-default"
        keys with either 'y' or 'n' as value
    :type possible_choices: dict[str, str]
    :return: a dictionary with 'yes' and 'no' keys and boolean values
    """
    choice = input(text).rstrip().lower()
    if not choice or choice == possible_choices['default']:
        if possible_choices['default'] == 'y':
            return {'yes': True, 'no': False}
        else:
            return {'yes': False, 'no': True}
    elif choice == possible_choices['non-default']:
        if possible_choices['non-default'] == 'y':
            return {'yes': True, 'no': False}
        else:
            return {'yes': False, 'no': True}
    else:
        while True:
            print("Please answer with 'y' or 'n'")
            choice = input(text).rstrip().lower()
            if not choice or choice == possible_choices['default']:
                if possible_choices['default'] == 'y':
                    return {'yes': True, 'no': False}
                else:
                    return {'yes': False, 'no': True}
            elif choice == possible_choices['non-default']:
                if possible_choices['non-default'] == 'y':
                    return {'yes': True, 'no': False}
                else:
                    return {'yes': False, 'no': True}
