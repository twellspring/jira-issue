#!/usr/bin/env python3
"""Quickly put in jira issues
"""
# prerequisites: pip3 install jira python-editor

import argparse
import configparser
import json
import os
import sys
import warnings

import editor
from jira.client import JIRA, JIRAError

warnings.filterwarnings(
    "ignore",
    message=
    "Old private GreenHopper API is used, all parameters will be ignored.")


def get_custom_fields():
    """ Get custom fields from config file ( only in DEFAULT section)
    """
    default = parse_file_args('DEFAULT')
    custom_fields = {}
    for name, value in default.items():
        if name.startswith('customfield'):
            field_info = json.loads(value)
            if not field_info.get('type', False):
                field_info['type'] = 'string'
            custom_fields[name] = field_info
    return custom_fields


def parse_file_args(section):
    """Parse config file ~/.jira_config
    """
    env_file = os.path.expanduser("~/.jira_config")
    config = configparser.ConfigParser()
    config.read(env_file)
    if config.has_section(section) or section == 'DEFAULT':
        config = config.items(section)
    else:
        print('Config file does not have section: ' + section)
        sys.exit(1)

    config_dict = dict(config)

    return config_dict


def parse_command_args(custom_fields):
    """Parse command line arguments
    """
    parser = argparse.ArgumentParser(
        prog=sys.argv[0],
        formatter_class=
        lambda prog: argparse.HelpFormatter(prog, max_help_position=35))
    parser.add_argument(
        '-a', '--assignee', help='Assignee user id', metavar="USER_ID")
    parser.add_argument(
        '-b',
        '--board',
        help=
        'Scrum board.  Setting this will add new issues to the current sprint')
    parser.add_argument(
        '-c', '--close', action='store_const', const=True, help='Close issue')
    # parser.add_argument(
    #     '-d', '--description', help='Description', metavar='TEXT')
    parser.add_argument(
        '-d',
        '--description',
        action='store_const',
        const=True,
        dest='get_description',
        help='Input Description in editor')
    parser.add_argument(
        '-i',
        '--issue',
        dest='issue_key',
        help='Issue key (leave blank to create new issue)')
    parser.add_argument('-k', '--key', help='Project Key')
    parser.add_argument(
        '-l', '--labels', help='labels ( comma or space delineated )')
    #parser.add_argument('-s', '--squad', help='Squad')
    parser.add_argument('-t', '--type', help='Issue type')
    parser.add_argument(
        '-u',
        '--use',
        dest='config_section',
        metavar='SECTION',
        help="Config to use from ~/.git_config",
        default='DEFAULT')
    parser.add_argument(
        '-w', '--work', help='jira worklog time string (ex: 15m, 3h)')
    parser.add_argument(
        'title', nargs='+', help='Issue Title (quotes not needed)')

    for field, values in custom_fields.items():
        alias = values['alias']
        help_message = 'Custom field ({})'.format(values['type'])
        parser.add_argument('--' + alias, metavar=alias, help=help_message)

    args = vars(parser.parse_args())
    args['title'] = ' '.join(args['title'])
    return args


def get_args():
    """Merge command line and config file args
    """
    custom_fields = get_custom_fields()

    command_args = parse_command_args(custom_fields)
    command_args_clean = {
        k: v
        for k, v in command_args.items() if v is not None
    }
    file_args = parse_file_args(command_args.get('config_section'))
    args = {**file_args, **command_args_clean}

    if args.get('labels', False):
        args['labels'] = make_list(args['labels'])

    if args.get('get_description', False):
        args['description'] = editor.edit(
            contents=b"Replace this text with the description").decode()

    custom_fields_valued = {}
    for field, field_info in custom_fields.items():
        custom_value = args.get(field_info['alias'], False)
        if custom_value:
            custom_fields_valued[field] = field_info
            custom_fields_valued[field]['value'] = custom_value
    args['custom_fields'] = custom_fields_valued

    return args


def get_session(args):
    """Get Jira session
    """
    auth = args.get("password", args.get('token'))
    options = {'server': args.get('server')}
    try:
        jira = JIRA(
            options,
            basic_auth=(args.get('username'), auth),
            timeout=3.001,
            max_retries=0)
        return jira
    except AttributeError as err:
        sys.exit(err)
    except JIRAError as err:
        if err.status_code == 401:
            print("Login to JIRA failed. Check your username and password")
        else:
            print(err)
        sys.exit(1)


def create_issue(args, jira):
    """Create Jira Issue
    """
    issue_dict = {
        'project': {
            'key': args.get('key')
        },
        'summary': args.get('title'),
        'description': args.get('description', ''),
        'issuetype': {
            'name': args.get('type'),
        },
        'assignee': {
            'name': args.get('assignee')
        },
        'labels': args.get('labels', [])
    }

    for field, field_data in args.get('custom_fields', {}).items():
        value = args.get(field_data['alias'])
        if field_data['type'] == 'list':
            issue_dict[field] = make_list(value)
        else:
            issue_dict[field] = value

    try:
        issue = jira.create_issue(fields=issue_dict)

        print(issue.raw['key'] + ': Created')
        return issue
    except KeyError as err:
        sys.exit(err)
    except JIRAError as err:
        sys.exit(err)


def add_to_sprint(issue_key, args, jira):
    """  Add issue to active sprint
    """
    board_id = args.get('board_id', None)
    if not board_id:
        boards = jira.boards()
        for board in boards:
            if board.name == args.get('board'):
                board_id = board.id
                break
        if not board_id:
            print("There is no board matching: " + args.get('board'))
            return None

    sprints = jira.sprints(board_id)
    sprint_name = None
    for sprint in sprints:
        if sprint.state == "ACTIVE":
            sprint_name = sprint.name
            sprint_id = sprint.id
            break
    if not sprint_name:
        print("Could not find an active sprint in: " + args.get('board'))
        return None

    try:
        jira.add_issues_to_sprint(sprint_id, [issue_key])
    except JIRAError as err:
        print(issue_key + ': ' + err.text)
        return None
    print(issue_key + ": Added to sprint " + sprint_name)


def close_issue(issue_key, args, jira):
    """ Close Jira Issue
    """
    try:
        work = args.get('work')
        closed_id = None
        transitions = jira.transitions(issue_key)
        for transition in transitions:
            if "Close" in transition['name']:
                closed_id = transition['id']
                break

        if not closed_id:
            print(issue_key +
                  ': Close option not available.  Is it already closed?')
            return None
        jira.transition_issue(issue_key, closed_id, worklog=args.get('work'))
    except JIRAError as err:
        print(err.text)
        sys.exit(err.status_code)

    print(issue_key + ': Closed with ' + work + ' work')


def str2bool(test_string):
    """ Convert string to Boolean
    """
    if isinstance(test_string, bool):
        return test_string
    return test_string.lower() in ("yes", "true", "t", "1")


def make_list(string):
    """ Convert a string with comma or space separation into a list
    """
    return string.replace(',', ' ').split()


def main():
    """Main function
    """
    args = get_args()
    jira = get_session(args)

    if args.get('issue_key', False):
        issue_key = args.get('issue_key')
        issue = jira.issue(issue_key)
        issue_open = str(issue.fields.status) in ('Open', 'Reopened')
        if not issue_open:
            print(issue_key + ": Issue is not open so can not be modified")
            sys.exit(1)
    else:
        issue = create_issue(args, jira)
        issue_key = issue.raw['key']

    # for field in issue.raw['fields']:
    #     print(field, ' ', issue.raw['fields'][field])
    # sys.exit()

    if args.get('board', False) or args.get('board_id', False):
        add_to_sprint(issue_key, args, jira)

    if str2bool(args.get('close', False)):
        close_issue(issue_key, args, jira)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("\nReceived SIGINT, exiting...")
