import io
import os
import platform
import re
import stat
import subprocess
import zipfile
from functools import lru_cache

import requests
import ubelt as ub
from logzero import logger

from . import chrome_info, enviroment, version


@lru_cache(maxsize=1)
def _get_driver_zipfile():
    system_name = platform.system()
    if system_name == 'Windows':
        return "chromedriver_win32.zip"
    if system_name == 'Linux':
        return "chromedriver_linux64.zip"
    if system_name == 'Darwin':
        if enviroment.get_cpu_arch() == 'arm':
            return "chromedriver_mac64_m1.zip"
        else:
            return "chromedriver_mac64.zip"
    return None


@lru_cache(maxsize=1)
def _get_driver_filename():
    system_name = platform.system()
    if system_name == 'Windows':
        return "chromedriver.exe"
    if system_name == 'Linux':
        return "chromedriver"
    if system_name == 'Darwin':
        return "chromedriver"
    return None


def find_chromedriver_version(chrome_version):
    # Method from https://chromedriver.chromium.org/downloads/version-selection
    # Take the Chrome version number, remove the last part, and append the result to URL "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_"
    url_version = '.'.join(chrome_version.split('.')[:-1])
    url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{url_version}"
    r = requests.get(url)
    data = r.text.strip()
    logger.info(f"ChromeDriver version needed: {data}")
    return data


def download_chromedriver_zip(chromedriver_version):
    # Method from https://chromedriver.chromium.org/downloads/version-selection
    url = f"https://chromedriver.storage.googleapis.com/{chromedriver_version}/{_get_driver_zipfile()}"
    logger.debug(
        f"Downloading: {chromedriver_version}/{_get_driver_zipfile()}")
    r = requests.get(url)
    data = r.content
    logger.info(f"Downloaded: {len(data)} bytes")
    return data


def extract_zip(zip_data, folder="."):
    chromedriver_path = os.path.join(folder, _get_driver_filename())
    if os.path.exists(chromedriver_path):
        os.remove(chromedriver_path)

    with io.BytesIO(zip_data) as f:
        with zipfile.ZipFile(file=f, mode='r') as zip_ref:
            zip_ref.extractall(folder)
    os.chmod(chromedriver_path, mode=stat.S_IRWXU |
             stat.S_IXGRP | stat.S_IXOTH)
    logger.debug(f"Extracted executable into: {folder}")


def get_version(folder):
    chromedriver_path = os.path.join(folder, _get_driver_filename())
    if not os.path.exists(chromedriver_path):
        return None
    output = subprocess.check_output(
        '"%s" -v' % (chromedriver_path), shell=True)
    output_str = output.decode(encoding='ascii')
    version_str = version.extract_version(output_str)
    logger.debug(f"Downloaded ChromeDriver Version: {version_str}")
    return version_str


def download_only_if_needed(chrome_path=None, chromedriver_folder=None):
    if chromedriver_folder:
        dpath = chromedriver_folder
    else:
        dpath = ub.ensure_app_cache_dir('latest_chromedriver')

    cached_version = get_version(dpath)
    version = chrome_info.get_version(chrome_path=chrome_path)

    if version:
        online_version = find_chromedriver_version(version)
        if (not cached_version) or (online_version != cached_version):
            zip_data = download_chromedriver_zip(online_version)
            extract_zip(zip_data, dpath)

    return dpath
