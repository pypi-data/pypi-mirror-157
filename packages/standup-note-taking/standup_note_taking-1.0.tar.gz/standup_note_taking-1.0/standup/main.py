import argparse
import json
import logging as log
import os
import subprocess

from standup.standup import Standup

log.basicConfig(level=log.INFO, format='%(asctime)s - %(message)s',
                datefmt='%d-%b-%y %H:%M:%S')

global CONFIG
global EDITOR
EDITOR = os.environ.get('EDITOR', 'vim')


def parse_config() -> dict:
    '''
        This functions job is to parse the standup config file
    '''

    os.chdir('/tmp')

    with open("standup-config.json", 'r') as file:
        config = json.load(file)
        return config


def check_config():
    '''
        This function is meant to check if a config is available - 
        if not, it will create one
    '''

    for root, dirs, files in os.walk("/tmp"):
        for file in files:
            if file.__eq__("standup-config.json"):
                return parse_config()

        create_config()
        return parse_config()


def create_config():
    '''
        Creates the config
    '''

    os.chdir('/tmp')

    os.system('touch standup-config.json')
    initial_config = {
        "days": 7,
        "categories": ['DONE', 'IN-PROGRESS', 'BLOCKERS', 'NOTES'],
        "path": "/tmp"
    }
    with open("standup-config.json", "w") as f2:
        json.dump(initial_config, f2, indent=3)


def main():

    # Check config
    CONFIG = check_config()

    # Parse arguments
    parser = argparse.ArgumentParser(description='This script is meant to be used as a CLI tool \
                                     for meeting notes for a daily standup')

    parser.add_argument("--category",
                        required=False,
                        choices=CONFIG['categories'],
                        type=str)
    parser.add_argument("--config",
                        required=False,
                        action='store_true',
                        help="Used to open your config")
    parser.add_argument("sentence",
                        nargs='?',
                        type=str)
    parser.add_argument("-daysago", "--days_ago",
                        required=False,
                        default=0,
                        type=int)
    parser.add_argument("--open",
                        required=False,
                        action='store_true',
                        help="Used to open your standup text")

    args = parser.parse_args()

    category = None

    if args.category:
        category = args.category
    else:
        category = "NOTES"

    if args.config and not args.open:
        os.chdir('/tmp')
        popen = subprocess.Popen('vim standup-config.json', shell=True)
        popen.communicate()
        CONFIG = parse_config()

    standup = Standup(category, args.sentence, args.days_ago, CONFIG)

    # Check that a file exists for your standup notes
    standup.check_standup()

    # Logic for determining how to delegate arguments being passed in to the script
    if args.sentence and category:
        if args.days_ago:
            raise Exception("You can't update an older standup file")
        if args.open or args.config:
            log.info("--open --config should be standalone arguments")
        standup.append_standup()
    elif args.config and args.open:
        log.info("--open and --config should be standalone arguments")
    elif args.open and not args.config:
        standup.open_standup()

    standup.remove_old_standups()


if __name__ == '__main__':
    main()
