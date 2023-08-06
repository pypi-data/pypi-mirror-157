# Copyright 2018 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
from os.path import join, dirname, expanduser, exists
from time import sleep

from ovos_utils.configuration import get_xdg_config_save_path, get_webcache_location, get_xdg_base, \
    get_config_filename, find_default_config as _fdc


def find_default_config():
    try:
        return _fdc()
    except FileNotFoundError:
        # mycroft-core not found
        return join(dirname(__file__), "mycroft.conf")


DEFAULT_CONFIG = find_default_config()
SYSTEM_CONFIG = os.environ.get('MYCROFT_SYSTEM_CONFIG',
                               f'/etc/{get_xdg_base()}/{get_config_filename()}')
# TODO: remove in 22.02
# Make sure we support the old location still
# Deprecated and will be removed eventually
OLD_USER_CONFIG = join(expanduser('~'), '.' + get_xdg_base(), get_config_filename())
USER_CONFIG = join(get_xdg_config_save_path(), get_config_filename())
REMOTE_CONFIG = "mycroft.ai"
WEB_CONFIG_CACHE = os.environ.get('MYCROFT_WEB_CACHE') or get_webcache_location()


def __ensure_folder_exists(path):
    """ Make sure the directory for the specified path exists.

        Args:
            path (str): path to config file
     """
    directory = dirname(path)
    if not exists(directory):
        try:
            os.makedirs(directory)
        except:
            sleep(0.2)
            if not exists(directory):
                try:
                    os.makedirs(directory)
                except Exception as e:
                    pass


__ensure_folder_exists(WEB_CONFIG_CACHE)
__ensure_folder_exists(USER_CONFIG)
