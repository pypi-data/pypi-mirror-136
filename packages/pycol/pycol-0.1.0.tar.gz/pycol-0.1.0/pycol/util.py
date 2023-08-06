import os
import random
import shutil
import string


def create_random_string(length: int = 10) -> str:
    """
    Function creates random string of specified length

    :param length: desired length of random string
    :return: generated random string
    """
    return "".join(
        random.choices(string.ascii_letters + string.digits, k=length))


def get_files(directory: str) -> list:
    """
    Function recursively lists all files within a directory

    :param directory: directory name
    :return: list of full filenames
    """
    files = []
    root_dir = os.listdir(directory)
    for e in root_dir:
        full = os.path.join(directory, e)
        if os.path.isdir(full):
            if e in ["..", "."]:
                continue
            files.append(get_files(full))
        else:
            files.append(full)
    return files


def prepare_temp_directory() -> str:
    """
    Function prepares base temporary directory in /tmp/

    :return: path to temp directory
    """
    base_temp_dir = os.path.join("/tmp", create_random_string())
    if not os.path.isdir(base_temp_dir):
        os.mkdir(base_temp_dir)

    return base_temp_dir


def create_temp_directory(directory: str = None) -> str:
    """
    Function creates temporary directory with random name

    :param directory: base directory
    :return: path of created directory
    """
    temp_path = prepare_temp_directory()
    name = create_random_string()
    if directory:
        fullname = os.path.join(directory, name)
    else:
        fullname = os.path.join("/tmp", temp_path, name)
    os.mkdir(fullname)
    return fullname


def create_temp_file(directory: str) -> str:
    """
    Function creates temporary empty file with random name in specified directory

    :param directory: path where to create the random file
    :return: path to the file
    """
    if not os.path.isdir(directory):
        return ""
    name = create_random_string(15)
    fullname = os.path.join(directory, name)
    fd = open(fullname, "w")
    fd.close()
    return fullname


def create_temp_files(temp_dirs: list, count: int = 5) -> None:
    """
    Creates specified number of empty files

    :param temp_dirs: location
    :param count: number of files to create
    :return:
    """
    for td in temp_dirs:
        for _ in range(count):
            create_temp_file(td)


def clean_temp_directories(p: str) -> None:
    """
    Function deletes the base temporary directory and everything that
    it contains

    :param p: path to temporary files
    :return:
    """
    if not os.path.isdir(p):
        return
    shutil.rmtree(p)
