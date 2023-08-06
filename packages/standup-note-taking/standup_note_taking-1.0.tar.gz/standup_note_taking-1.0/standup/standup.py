import argparse
import json
import os
import sys
from datetime import datetime, timedelta, date

global DATE

DATE = datetime.now().strftime('%m-%d-%Y')


class Standup:

    def __init__(self, category: str, sentence: str, days_ago: int, config: dict):

        self.category = category
        self.sentence = sentence
        self.days_ago = days_ago
        self.config = config

    def check_path(self, path: str = None):

        if path:
            if os.path.isdir(path):
                try:
                    os.chdir(path)
                except:
                    raise Exception("The path in your config is NOT a proper path - \
                                    fix your config path")
        else:
            if os.path.isdir(self.config['path']):
                try:
                    os.chdir(self.config['path'])
                except:
                    raise Exception("The path in your config is NOT a proper path - \
                                    fix your config path")

    def check_standup(self):

        file = None
        self.check_path()

        for files in os.listdir(self.config['path']):
            if self.days_ago == 0:
                if files.__eq__(f"standup_{DATE}.txt"):
                    file = files
            else:
                day = (int(date.today().strftime('%d')) - self.days_ago)
                newtime = date.today().strftime(f'%m-{day}-%Y')
                if files.__eq__(f"standup_{newtime}.txt"):
                    file = files
        if file:
            return
        elif not file and self.days_ago == 0:
            self.create_standup()
        else:
            raise Exception(
                f"There isn't a file from {self.days_ago} days ago")

    def append_standup(self):

        self.check_path()

        if self.days_ago == 0:
            with open(f'standup_{DATE}.txt', 'r') as f:
                data = f.readlines()

            start = -1
            category_to_stop = ''
            for lines in data:
                if lines.__contains__(self.category):

                    categories = self.config['categories']
                    for x in range(len(categories)):
                        if categories[x].__contains__(self.category):
                            if self.category == 'NOTES':
                                category_to_stop = "stop"
                            else:
                                category_to_stop = categories[x+1]

                    start += 1
                    break
                start += 1

            current_line = ''
            i = -1
            for category_lines in data[start:]:
                current_line = category_lines
                if current_line.strip().__contains__(category_to_stop):
                    break
                i += 1

            if self.category == "NOTES":
                place_line = i + start
                data[place_line] = f"\t[{i-1}]: {self.sentence}\n\n"
            else:
                place_line = i + start
                data[place_line] = f"\t[{i-1}]: {self.sentence}\n\n"

            with open(f'standup_{DATE}.txt', 'w') as file:
                file.writelines(data)
        else:
            raise Exception("You can't update an older file")

    def open_standup(self):

        self.check_path()
        if self.days_ago == 0:
            os.system(f"vi standup_{DATE}.txt")
        else:
            day = (int(date.today().strftime('%d')) - self.days_ago)
            newtime = date.today().strftime(f'%m-{day}-%Y')
            os.system(f"vi standup_{newtime}.txt")

    def create_standup(self):

        with open(f'standup_{DATE}.txt', 'w') as file:
            categories = []
            for category in self.config['categories']:
                if category == 'NOTES':
                    categories.append(category + '\n\n\n')
                else:
                    categories.append(category)
            file.writelines('\n\n\n'.join(categories))

    def remove_old_standups(self):

        dates = []
        for i in range(self.config['days']+1):
            new_time = datetime.now() - timedelta(days=i)
            new_time = new_time.strftime(f"%m-%d-%Y")
            dates.append(str(new_time))

        # for time in dates:
        file_list = []
        os.chdir(self.config['path'])
        for root, dirs, files in os.walk(self.config['path']):
            for file in files:
                if file.__contains__("standup") and file != 'standup-config.json':
                    for time in dates:
                        if file.__contains__(time):
                            file_list.append(file)
                            continue
        for root, dirs, files in os.walk(self.config['path']):
            for file in files:
                if file.__contains__("standup") and file != 'standup-config.json':
                    if file not in file_list:
                        os.system(f'rm {file}')
