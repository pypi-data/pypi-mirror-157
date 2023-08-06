import os
import sys
import shutil
import tempfile
from setuptools import setup
from setuptools.command.install import install

PACKAGE_NAME = "browsenextfile"
APP_NAME = "py.launcher"
    # We use the name "py.launcher" instead of "launcher.py" as a workaround
    # because of an issue with make_shortcut function if it is called from Windows.
ICON_NAME = "py.ico"
APP_PATH_IN_PACKAGE = os.path.join("launcher", "bin", APP_NAME)
ICON_PATH_IN_PACKAGE = os.path.join("launcher", "bin", ICON_NAME)

APPNAME = "nextfile"
APPAUTHOR = "dmitrish"

DATA_DIR_NAME = "app_data"
APP_DIR_IN_DATA_DIR = "launcher"

SHORTCUT_NAME = 'NextFile'
SHORTCUT_DESCRIPTION = 'View image files with web browser'
SHORTCUT_ARGS = ''
if sys.platform == "linux" or sys.platform == "linux2":
    SHORTCUT_ARGS = ' %f'

def is_venv():
    return (hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))

def in_venv(dirname, appname):
    return os.path.join(sys.prefix, dirname, appname)


def is_temp(path):
    tmp_dir = tempfile.gettempdir()
    common_path = os.path.commonpath((tmp_dir, path))
    return os.path.samefile(tmp_dir, common_path)


class PostInstallCommand(install):
    def run(self):
        install.run(self)
        self.post_install()

    def post_install(self):
        from platformdirs import user_data_dir
        from pyshortcuts import make_shortcut

        def get_user_data_dir():
            if is_venv():
                app_data_dir = in_venv(DATA_DIR_NAME, APPNAME)
            else:
                app_data_dir = user_data_dir(APPNAME, APPAUTHOR)
            if not os.path.exists(app_data_dir):
                os.makedirs(app_data_dir)
            return app_data_dir

        src_app_path = os.path.join(self.install_lib, PACKAGE_NAME, APP_PATH_IN_PACKAGE)
        src_icon_path = os.path.join(self.install_lib, PACKAGE_NAME, ICON_PATH_IN_PACKAGE)
        if os.path.isfile(src_app_path):
            user_app_dir = get_user_data_dir()
            if not is_temp(user_app_dir):
                dest_app_dir = os.path.join(user_app_dir, APP_DIR_IN_DATA_DIR)
                if not os.path.exists(dest_app_dir):
                    os.makedirs(dest_app_dir)
                dest_app_path = os.path.join(dest_app_dir, APP_NAME)
                if not os.path.isfile(dest_app_path):
                    shutil.copy2(src_app_path, dest_app_path)
                dest_icon_path = os.path.join(dest_app_dir, ICON_NAME)
                if not os.path.isfile(dest_icon_path) and os.path.isfile(src_icon_path):
                    shutil.copy2(src_icon_path, dest_icon_path)
                if os.path.isabs(dest_app_path) and os.path.isfile(dest_app_path):
                    executable = None
                    if sys.platform == "win32":
                        # On Windows, we specify Python executable explicitly
                        # because of an issue with make_shortcut function if
                        # it is called from a virtual environment (venv).
                        pyexe = 'pythonw.exe'
                        pydir = os.path.dirname(sys.executable)
                        executable = os.path.normpath(os.path.join(pydir, pyexe))
                    make_shortcut(dest_app_path + SHORTCUT_ARGS,
                                  name=SHORTCUT_NAME,
                                  description=SHORTCUT_DESCRIPTION,
                                  icon=dest_icon_path,
                                  terminal=False,
                                  executable=executable)

setup(cmdclass = {
          'install': PostInstallCommand,
          }
      )

