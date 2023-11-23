import os


def create_flag_file(path):
    with open(path, 'a'):
        pass


def remove_flag_file(path):
    if os.path.exists(path):
        os.remove(path)
