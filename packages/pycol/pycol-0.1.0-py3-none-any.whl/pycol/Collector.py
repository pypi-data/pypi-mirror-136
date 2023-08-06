"""
File collector class.

author: Silvie Nemcova (nemcova.silva@gmail.com)
date: 2022-01-17
"""
import os.path
from zipfile import ZipFile

from pycol import util


class Collector:
    """
    Class that collects files from specified directories and saves them into an archive.
    """

    def __init__(self, dirs: list) -> None:
        self.dirs = dirs

    def collect_files(self) -> list:
        """
        Function collects all files from specified directories

        :return: list of paths to the files
        """
        files = []
        for d in self.dirs:
            files.append(util.get_files(d))
        return files

    def pack_files(self, dest: str = None) -> str:
        """
        Function packs the specified files

        :param dest: destination of the archive, if not specified,
        random directory will be created to store the archive
        :return: location of the archive
        """
        if not dest:
            dest = util.create_temp_file("/tmp/pycol/") + ".zip"
        else:
            dest += ".zip"

        files = self.collect_files()

        with ZipFile(dest, "w") as zfd:
            for f in files:
                if os.path.isfile(str(f)):
                    zfd.write(f)
        return dest
