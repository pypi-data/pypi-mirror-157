import os
import platform
import re
import shutil
import subprocess
from functools import lru_cache

import ubelt as ub
from logzero import logger

from . import version
from . import enviroment


@lru_cache(maxsize=1)
def _get_chrome_executable():
    system_name = platform.system()
    if system_name == 'Windows':
        return "chrome.exe"
    if system_name == 'Linux':
        return "google-chrome"
    if system_name == 'Darwin':
        return "Google Chrome"
    return None


def _windows_program_locations():
    possible_folders = [os.environ.get(
        i) for i in ["ProgramFiles(x86)", "ProgramW6432"]]
    possible_folders.append(str(ub.Path.home()))
    for folder in possible_folders:
        if folder:
            logger.debug(f"Searching in: {folder}")
            yield folder


def _darwin_applications():
    possible_folders = ['/Applications', '/']
    for folder in possible_folders:
        if folder:
            logger.debug(f"Searching in: {folder}")
            yield folder


def _is_exe(fpath):
    return os.path.exists(fpath) and os.access(fpath, os.X_OK) and os.path.isfile(fpath)


def _find_chrome_in_subfolders(folder):
    if enviroment.is_fs_case_sensitive():
        search_filename = _get_chrome_executable().strip()
    else:
        search_filename = _get_chrome_executable().casefold().strip()

    for root, dirs, files in os.walk(folder):
        for filename in files:
            if enviroment.is_fs_case_sensitive():
                case_filename = filename
            else:
                case_filename = filename.casefold()
            if case_filename == search_filename:
                filepath = os.path.join(root, filename)
                if _is_exe(filepath):
                    return filepath
    return None


@lru_cache(maxsize=1)
def get_path():
    logger.debug("Searching for Google Chrome installations...")
    system_name = platform.system()

    if enviroment.is_fs_case_sensitive():
        search_filename = _get_chrome_executable().strip()
    else:
        search_filename = _get_chrome_executable().casefold().strip()
    in_path = shutil.which(search_filename)
    if in_path:
        return in_path

    if system_name == 'Windows':
        for folder in _windows_program_locations():
            filepath = _find_chrome_in_subfolders(folder)
            if filepath:
                return filepath

    if system_name == 'Darwin':
        for folder in _darwin_applications():
            filepath = _find_chrome_in_subfolders(folder)
            if filepath:
                return filepath

    logger.error("Google Chrome wasn't found in the usual locations")
    return None


@lru_cache(maxsize=None)
def get_version(chrome_path=None):
    system_name = platform.system()
    if chrome_path:
        if not _is_exe(chrome_path):
            logger.error(
                f"{chrome_path} is not a valid Google Chrome executable.")
            return None
    else:
        chrome_path = get_path()

    version_str = None
    if chrome_path:
        if system_name == 'Windows':
            output = subprocess.check_output(
                'powershell -command "&{(Get-Item \'%s\').VersionInfo.ProductVersion}"' % (chrome_path), shell=True)
        else:
            output = subprocess.check_output(
                '"%s" --version' % (chrome_path), shell=True)
        output_str = output.decode(encoding='ascii')
        version_str = version.extract_version(output_str)
        logger.debug(f"Google Chrome Version: {version_str}")
    return version_str
