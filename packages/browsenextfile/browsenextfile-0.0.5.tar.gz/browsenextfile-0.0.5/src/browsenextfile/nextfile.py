import os
import sys
import time
import bisect
import json

from selenium.common.exceptions import UnexpectedAlertPresentException, TimeoutException

try:
    from urllib.parse import urlparse, urljoin
    from urllib.request import url2pathname, pathname2url
except ImportError:
    # backwards compatability
    from urlparse import urlparse, urljoin
    from urllib import url2pathname, pathname2url

if sys.platform == "win32":
    import string

#try:
#    import importlib.resources as dist_resources
#except ImportError:
    # Try backported to PY<37 `importlib_resources`.
import importlib_resources as dist_resources

if __name__ == '__main__':
    import nextfile_options, ui, web_driver
    from browserauto.webdriverex import WebDriverEx
    from ui.i18n.data_dirs.appdata import get_user_data_dir, install_resource, install_and_read_resource
    from ui.i18n.languages import init_languages, set_language, get_languages_dict, get_language
    from ui import translations
else:
    from . import nextfile_options, ui, web_driver
    from .browserauto.webdriverex import WebDriverEx
    from .ui.i18n.data_dirs.appdata import get_user_data_dir, install_resource, install_and_read_resource
    from .ui.i18n.languages import init_languages, set_language, get_languages_dict, get_language
    from .ui import translations

import struct
def is_64bit():
    return (struct.calcsize('P') * 8 == 64)


SHORT_POLL_PERIOD_SEC = 0.3
LONG_POLL_PERIOD_SEC = 1.5
GET_TIMEOUT_SEC = 10


OPTIONS_FILE_NAME = "nextfile_options.txt"

PROFILES_DIR_NAME = "profiles"

FIREFOX_PROFILE_NAME = "firefox"
CHROME_PROFILE_NAME = "chrome"
EDGE_PROFILE_NAME = "edge"

START_PAGE_DIR = "start"

WEB_DRIVER_DIR = "web_driver"
WEB_DRIVER_SUBDIR = None
FIREFOX_DRIVER_FILE_NAME = None
CHROME_DRIVER_FILE_NAME = None
EDGE_DRIVER_FILE_NAME = None
if sys.platform == "linux" or sys.platform == "linux2":
    if is_64bit():
        WEB_DRIVER_SUBDIR = "linux64"
    else:
        WEB_DRIVER_SUBDIR = "linux32"
    FIREFOX_DRIVER_FILE_NAME = "geckodriver"
    CHROME_DRIVER_FILE_NAME = "chromedriver"
    EDGE_DRIVER_FILE_NAME = 'msedgedriver'
elif sys.platform == "darwin":
    if is_64bit():
        WEB_DRIVER_SUBDIR = "macos64"
    else:
        WEB_DRIVER_SUBDIR = "macos32"
    FIREFOX_DRIVER_FILE_NAME = "geckodriver"
    CHROME_DRIVER_FILE_NAME = "chromedriver"
    EDGE_DRIVER_FILE_NAME = 'msedgedriver'
elif sys.platform == "win32":
    if is_64bit():
        WEB_DRIVER_SUBDIR = "win64"
    else:
        WEB_DRIVER_SUBDIR = "win32"
    FIREFOX_DRIVER_FILE_NAME = "geckodriver.exe"
    CHROME_DRIVER_FILE_NAME = "chromedriver.exe"
    EDGE_DRIVER_FILE_NAME = 'msedgedriver.exe'

JS_DIR = "js"
CSS_DIR = "css"

SITE_SETUP_CSS_FILE_NAME = "site_setup.css"
DIALOG_SETUP_CSS_FILE_NAME = "dialog_setup.css"

START_PAGE_FILE_NAME = "nextfile.html"

SITE_SETUP_JS_FILE_NAME = "site_setup.js"
CHECK_USER_INPUT_JS_FILE_NAME = "check_user_input.js"
DIALOG_SETUP_JS_FILE_NAME = "dialog_setup.js"
CLOSE_DIALOG_JS_FILE_NAME = "close_dialog.js"
FILL_DIALOG_TOOLBAR_JS_FILE_NAME = "fill_dialog_toolbar.js"
FILL_DIRECTORY_WINDOW_JS_FILE_NAME = "fill_directory_window.js"
FILL_ABOUT_WINDOW_JS_FILE_NAME = "fill_about_window.js"
OPTIONS_PAGE_SETUP_JS_FILE_NAME = "options_page_setup.js"


APP_DATA_DIR = get_user_data_dir()


s = install_and_read_resource(APP_DATA_DIR, nextfile_options, OPTIONS_FILE_NAME)
options_file_dict = eval(s)
options_file_path = os.path.join(APP_DATA_DIR, OPTIONS_FILE_NAME)

profiles_dir_path = os.path.join(APP_DATA_DIR, PROFILES_DIR_NAME)


WEB_DRIVER_DATA_DIR = os.path.join(APP_DATA_DIR, WEB_DRIVER_DIR, WEB_DRIVER_SUBDIR)

firefox_driver_path = install_resource(WEB_DRIVER_DATA_DIR, 
                                       web_driver, FIREFOX_DRIVER_FILE_NAME, WEB_DRIVER_SUBDIR)

chrome_driver_path = install_resource(WEB_DRIVER_DATA_DIR, 
                                      web_driver, CHROME_DRIVER_FILE_NAME, WEB_DRIVER_SUBDIR)

edge_driver_path = install_resource(WEB_DRIVER_DATA_DIR, 
                                    web_driver, EDGE_DRIVER_FILE_NAME, WEB_DRIVER_SUBDIR)


BROWSER = options_file_dict['options']['browser']['value']


FIREFOX_PROFILE_PATH = os.path.join(APP_DATA_DIR, PROFILES_DIR_NAME, FIREFOX_PROFILE_NAME)
CHROME_PROFILE_PATH = os.path.join(APP_DATA_DIR, PROFILES_DIR_NAME, CHROME_PROFILE_NAME)
EDGE_PROFILE_PATH = os.path.join(APP_DATA_DIR, PROFILES_DIR_NAME, EDGE_PROFILE_NAME)


driver = None


site_setup_css = install_and_read_resource(os.path.join(APP_DATA_DIR, CSS_DIR), 
                                           ui, SITE_SETUP_CSS_FILE_NAME, JS_DIR, CSS_DIR)

dialog_setup_css = install_and_read_resource(os.path.join(APP_DATA_DIR, CSS_DIR),
                                             ui, DIALOG_SETUP_CSS_FILE_NAME, JS_DIR, CSS_DIR)


site_setup_script = dist_resources.files(ui).joinpath(JS_DIR).joinpath(SITE_SETUP_JS_FILE_NAME).read_text(encoding='utf-8')

check_user_input_script = dist_resources.files(ui).joinpath(JS_DIR).joinpath(CHECK_USER_INPUT_JS_FILE_NAME).read_text(encoding='utf-8')

dialog_setup_script = dist_resources.files(ui).joinpath(JS_DIR).joinpath(DIALOG_SETUP_JS_FILE_NAME).read_text(encoding='utf-8')

close_dialog_script = dist_resources.files(ui).joinpath(JS_DIR).joinpath(CLOSE_DIALOG_JS_FILE_NAME).read_text(encoding='utf-8')

fill_dialog_toolbar_script = dist_resources.files(ui).joinpath(JS_DIR).joinpath(FILL_DIALOG_TOOLBAR_JS_FILE_NAME).read_text(encoding='utf-8')

fill_directory_window_script = dist_resources.files(ui).joinpath(JS_DIR).joinpath(FILL_DIRECTORY_WINDOW_JS_FILE_NAME).read_text(encoding='utf-8')

fill_about_window_script = dist_resources.files(ui).joinpath(JS_DIR).joinpath(FILL_ABOUT_WINDOW_JS_FILE_NAME).read_text(encoding='utf-8')


options_page_setup_script = dist_resources.files(ui).joinpath(JS_DIR).joinpath(OPTIONS_PAGE_SETUP_JS_FILE_NAME).read_text(encoding='utf-8')

start_page_path = install_resource(os.path.join(APP_DATA_DIR, START_PAGE_DIR), 
                                   ui, START_PAGE_FILE_NAME, START_PAGE_DIR)

s = ""
with open(start_page_path, 'r', encoding='utf_8') as f:
    s = f.read()
s = s.replace("application_data_directory", APP_DATA_DIR)
s = s.replace("options_text_file", options_file_path)
s = s.replace("browser_profiles_directory", profiles_dir_path)
s = s.replace("web_driver_directory", WEB_DRIVER_DATA_DIR)
with open(start_page_path, 'w', encoding='utf_8') as f:
    f.write(s)


def url_is_local(url):
    parsed = urlparse(url)
    return (parsed.scheme == "file")

def uri2path(uri):
    parsed = urlparse(uri)
    host = "{0}{0}{mnt}{0}".format(os.path.sep, mnt=parsed.netloc)
    return os.path.normpath(
        os.path.join(host, url2pathname(parsed.path))
    )

def path2url(path):
    return urljoin('file:', pathname2url(path))


current_url = path2url(start_page_path)


def try_navigate_to(url):
    driver.execute_script("window.stop()")
    driver.execute_script("window.location.href='" + url + "'")

def try_alternative_navigate(url):
    driver.set_page_load_timeout(GET_TIMEOUT_SEC)
    driver.get(url) #may block

def alternative_navigate(url):
    try:
        try_alternative_navigate(url)
    except:
        pass

def navigate_to(url):
    try:
        try_navigate_to(url)
    except:
        alternative_navigate(url)

def go_to_start():
    global current_url

    current_url = path2url(start_page_path)
    while True:
        driver.wait_for_page()
        time.sleep(1)
        try:
            try_alternative_navigate(current_url)
            break
        except:
            pass
    if driver.err_msg != '':
        driver.execute_script(options_page_setup_script, driver.err_msg)


next_url = current_url

def site_setup():
    global next_url
    global current_url

    current_url = driver.current_url()
    if not url_is_local(current_url):
        return

    driver.execute_script(site_setup_script, site_setup_css, translations.site_setup())
    next_url = current_url

def navigate_to_next_prev(button_type):
    global next_url

    if not url_is_local(next_url):
        return

    file_path = uri2path(next_url)

    dir_path = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    file_name_list = os.listdir(path=dir_path)
    file_name_list2 = []
    file_found = False
    for name in file_name_list:
        path = os.path.join(dir_path, name)
        if os.path.isfile(path):
            file_name_list2.append(name)
            if os.path.samefile(path, file_path):
                file_found = True
                file_name = name
    if not file_found:
        return
    file_name_list2.sort()
    if button_type == "next":
        i_next = bisect.bisect_right(file_name_list2, file_name)
        if i_next == len(file_name_list2):
            i_next = 0
    elif button_type == "prev":
        i_next = bisect.bisect_left(file_name_list2, file_name)-1
        if i_next == -1:
            i_next = len(file_name_list2)-1
    else:
        return
    next_file_name = file_name_list2[i_next]
    next_file_path = os.path.join(dir_path, next_file_name)

    next_url = path2url(next_file_path)

    if next_url != current_url:
        navigate_to(next_url)


dialog_dir = "/"

def get_dialog_dir(dir_path):
    if os.path.exists(dir_path):
        return dir_path
    return "/"

def get_dir_contents(dir_path):
    #We use "/" to denote file system root. In Windows all available drives should be displayed.
    if dir_path == "/" and sys.platform == "win32":
        name_list = ['%s:\\' % d for d in string.ascii_uppercase if os.path.exists('%s:\\' % d)]
    else:
        name_list = os.listdir(path=dir_path)
    return name_list

def refresh_open_dialog():
    split_dir = []
    file_path = dialog_dir
    while True:
        dir_path = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        if file_name == "":
            split_dir.append([file_path, file_path])
            break
        split_dir.append([file_path, file_name])
        file_path = dir_path
    if not ["/", "/"] in split_dir:
        split_dir.append(["/", "/"])
    split_dir.reverse()

    driver.execute_script(fill_dialog_toolbar_script, "open", json.dumps(split_dir), translations.fill_dialog_toolbar())

    current_url_path = ""
    if url_is_local(current_url):
        current_url_path = uri2path(current_url)

    name_list = get_dir_contents(dialog_dir)
    dir_name_list = []
    file_name_list = []
    select_name = ""
    for name in name_list:
        path = os.path.join(dialog_dir, name)
        if os.path.isdir(path):
            dir_name_list.append(name)
        elif os.path.isfile(path):
            file_name_list.append(name)
        if path == current_url_path:
            select_name = name
    dir_name_list.sort()
    file_name_list.sort()

    driver.execute_script(fill_directory_window_script, json.dumps(dir_name_list), json.dumps(file_name_list), select_name)

def refresh_about_dialog():
    languages_list = []
    languages_dict = get_languages_dict()
    for lang, v in languages_dict.items():
        languages_list.append([lang, v["name"]])

    driver.execute_script(fill_dialog_toolbar_script, "about", json.dumps(languages_list), translations.fill_dialog_toolbar())
    html = translations.about()
    driver.execute_script(fill_about_window_script, html)

def navigate_to_selected_file(file_name):
    global dialog_dir

    file_path = os.path.join(dialog_dir, file_name)
    if os.path.isdir(file_path):
        dialog_dir = get_dialog_dir(file_path)
        refresh_open_dialog()
    elif os.path.isfile(file_path):
        url = path2url(file_path)
        if url != current_url:
            navigate_to(url)

orig_lang = ""

def setup_open_dialog():
    global dialog_dir
    global orig_lang

    orig_lang = get_language()

    if url_is_local(current_url):
        file_path = uri2path(current_url)
        file_dir = os.path.dirname(file_path)
        dialog_dir = get_dialog_dir(file_dir)
    else:
        dialog_dir = "/"

    driver.execute_script(dialog_setup_script, dialog_setup_css, translations.dialog_setup())
    refresh_open_dialog()

def setup_about_dialog():
    global orig_lang

    orig_lang = get_language()

    driver.execute_script(dialog_setup_script, dialog_setup_css, translations.dialog_setup())
    refresh_about_dialog()

def close_dialog():
    lang = get_language()
    driver.execute_script(close_dialog_script, lang, orig_lang, translations.site_setup())


def on_button_pressed(button_type):
    if (button_type == "next") or (button_type == "prev"):
        navigate_to_next_prev(button_type)
    elif button_type == "open":
        setup_open_dialog()
    elif button_type == "about":
        setup_about_dialog()
    elif button_type == "close_dialog":
        close_dialog()
    else:
        return


def run_loop():
    global dialog_dir

    poll_period = LONG_POLL_PERIOD_SEC

    while True:
        resStr = driver.execute_script(check_user_input_script,
                                       exceptions=(UnexpectedAlertPresentException,))

        resDict = None
        if resStr and (resStr != ""):
            try:
                resDict = json.loads(resStr)
            except:
                pass

        poll_period = LONG_POLL_PERIOD_SEC
        if resDict:
            site_state = resDict.get("site_state")
            if site_state and site_state == "no_setup":
                site_setup()
                poll_period = SHORT_POLL_PERIOD_SEC

            buttons_state = resDict.get("buttons_state")
            if buttons_state and buttons_state == "visible":
                poll_period = SHORT_POLL_PERIOD_SEC

            button_clicked = resDict.get("button_clicked")
            if button_clicked and button_clicked != "":
                on_button_pressed(button_clicked)

            directory_selected = resDict.get("directory_selected")
            if directory_selected and directory_selected != "":
                dialog_dir = get_dialog_dir(directory_selected)
                refresh_open_dialog()

            file_selected = resDict.get("file_selected")
            if file_selected and file_selected != "":
                navigate_to_selected_file(file_selected)

            language_selected = resDict.get("language_selected")
            if language_selected and language_selected != "":
                lang = get_language()
                if language_selected != lang:
                    set_language(language_selected)
                    refresh_about_dialog()

        time.sleep(poll_period)


def open_file(args):
    global current_url

    if (len(args) >= 1) and os.path.isfile(args[0]):
        current_url = path2url(args[0])

        driver.wait_for_page()
        time.sleep(1)
        try:
            try_alternative_navigate(current_url)
        except TimeoutException:
            driver.wait_for_page()
            time.sleep(1)
            url = driver.current_url()
            hasBody = driver.execute_script("return (document.body != null)")
            if (url != current_url) or not hasBody:
                go_to_start()
        except:
            go_to_start()
    else:
        go_to_start()


def run_main(*args):
    global driver

    print("""\nWait for new browser window to open.\n""")

    driver = WebDriverEx(BROWSER, FIREFOX_PROFILE_PATH, CHROME_PROFILE_PATH, EDGE_PROFILE_PATH,
                         FIREFOX_DRIVER_FILE_NAME, CHROME_DRIVER_FILE_NAME, EDGE_DRIVER_FILE_NAME,
                         firefox_driver_path, chrome_driver_path, edge_driver_path)
    open_file(args)
    init_languages()
    set_language("en")
    run_loop()

if __name__ == '__main__':
    run_main(*sys.argv[1:])

