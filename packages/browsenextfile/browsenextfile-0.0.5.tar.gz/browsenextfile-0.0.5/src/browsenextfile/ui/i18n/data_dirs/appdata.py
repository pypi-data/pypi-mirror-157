import os
import sys
from platformdirs import user_data_dir, user_log_dir

#try:
#    import importlib.resources as dist_resources
#except ImportError:
    # Try backported to PY<37 `importlib_resources`.
import importlib_resources as dist_resources

import shutil

APPNAME = "nextfile"
APPAUTHOR = "dmitrish"

DATA_DIR_NAME = "app_data"
LOG_DIR_NAME = "app_log"

def is_venv():
    return (hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))

def in_venv(dirname, appname):
    return os.path.join(sys.prefix, dirname, appname)


def get_user_data_dir():
    if is_venv():
        app_data_dir = in_venv(DATA_DIR_NAME, APPNAME)
    else:
        app_data_dir = user_data_dir(APPNAME, APPAUTHOR)
    if not os.path.exists(app_data_dir):
        os.makedirs(app_data_dir)
    return app_data_dir

def get_user_log_dir():
    if is_venv():
        app_log_dir = in_venv(LOG_DIR_NAME, APPNAME)
    else:
        app_log_dir = user_log_dir(APPNAME, APPAUTHOR)
    if not os.path.exists(app_log_dir):
        os.makedirs(app_log_dir)
    return app_log_dir

def install_resource(dir_path, package, resource, *dirs_to_resource):
    file_path = os.path.join(dir_path, resource)
    if os.path.isfile(file_path):
        return file_path

    trav = dist_resources.files(package)
    for dir_name in dirs_to_resource:
        trav = trav.joinpath(dir_name)
    trav = trav.joinpath(resource)
    with dist_resources.as_file(trav) as res_path:
        if os.path.isfile(res_path):
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            shutil.copy2(res_path, file_path)
        else:
            file_path = None
    return file_path

def install_and_read_resource(dir_path, package, resource, *dirs_to_resource):
    file_path = install_resource(dir_path, package, resource, *dirs_to_resource)
    if not file_path or not os.path.isfile(file_path):
        return ""

    text = ""
    with open(file_path, encoding='utf_8') as f:
        text = f.read()
    return text

