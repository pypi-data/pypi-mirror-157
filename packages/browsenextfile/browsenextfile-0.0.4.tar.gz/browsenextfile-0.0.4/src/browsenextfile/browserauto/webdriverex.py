import os
import sys
import time

import selenium
if int(selenium.__version__.partition('.')[0]) >= 4:
    from selenium.webdriver.firefox.service import Service as FirefoxService
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.edge.service import Service as EdgeService
    if sys.platform == "win32":
        from subprocess import CREATE_NO_WINDOW

from selenium import webdriver
from selenium.common.exceptions import (NoSuchWindowException, WebDriverException, SessionNotCreatedException,
                                        InvalidSessionIdException, TimeoutException, UnexpectedAlertPresentException)
from selenium.webdriver.common.by import By


PAGE_READY_POLL_PERIOD_SEC = 1.5


class SwitchToEx:

    def __init__(self, driver_ex):
        self._driver_ex = driver_ex

    def default_content(self, exceptions=()):
        return self._driver_ex._try_get_bool(lambda d: d.switch_to.default_content(),
                                             (self._driver_ex._driver,), exceptions)

    def frame(self, frame_reference, exceptions=()):
        return self._driver_ex._try_get_bool(lambda d, x: d.switch_to.frame(x),
                                             (self._driver_ex._driver, frame_reference), exceptions)

    def parent_frame(self, exceptions=()):
        return self._driver_ex._try_get_bool(lambda d: d.switch_to.parent_frame(),
                                             (self._driver_ex._driver,), exceptions)

    def window(self, window_name, exceptions=()):
        return self._driver_ex._try_get_bool(lambda d, x: d.switch_to.window(x),
                                             (self._driver_ex._driver, window_name), exceptions)


class WebDriverEx:
    """
    Wraps the calls to WebDriver methods to handle cases
    when user closes the browser window or some browser tabs.
    """

    def __init__(self, browser, FIREFOX_PROFILE_PATH, CHROME_PROFILE_PATH, EDGE_PROFILE_PATH,
                 FIREFOX_DRIVER_FILE_NAME, CHROME_DRIVER_FILE_NAME, EDGE_DRIVER_FILE_NAME,
                 firefox_driver_path, chrome_driver_path, edge_driver_path):
        self.FIREFOX_PROFILE_PATH = FIREFOX_PROFILE_PATH
        self.CHROME_PROFILE_PATH = CHROME_PROFILE_PATH
        self.EDGE_PROFILE_PATH = EDGE_PROFILE_PATH

        self.FIREFOX_DRIVER_FILE_NAME = FIREFOX_DRIVER_FILE_NAME
        self.CHROME_DRIVER_FILE_NAME = CHROME_DRIVER_FILE_NAME
        self.EDGE_DRIVER_FILE_NAME = EDGE_DRIVER_FILE_NAME

        self.firefox_driver_path = firefox_driver_path
        self.chrome_driver_path = chrome_driver_path
        self.edge_driver_path = edge_driver_path

        self.err_msg = ""

        # Prevent the pop up of a console window from web driver in Windows.
        # We replace the original Popen that selenium tries to call with a prepared one with no window:
        if (int(selenium.__version__.partition('.')[0]) < 4) and (sys.platform == "win32"):
            import functools
            flag = 0x08000000  # No-Window flag
            # flag = 0x00000008  # Detached-Process flag, if first doesn't work
            webdriver.common.service.subprocess.Popen = functools.partial(
                webdriver.common.service.subprocess.Popen, creationflags=flag)

        if browser == "Firefox":
            self._start_firefox()
        elif browser == "Chrome":
            self._start_chrome()
        elif browser == "Edge":
            self._start_edge()
        elif browser == "Ie":
            self._start_ie()
        elif browser == "Safari":
            self._start_safari()
        elif browser == "Opera":
            self._start_opera()
        else:
            print(browser + " browser is not supported")
            sys.exit()
        self._switch_to = SwitchToEx(self)

    def _start_firefox(self):
        profile = self.FIREFOX_PROFILE_PATH
        if not os.path.exists(profile):
            os.makedirs(profile)

        options = webdriver.FirefoxOptions()
        if profile and os.path.isdir(profile):
            options.add_argument("-profile")
            options.add_argument(profile)

        if int(selenium.__version__.partition('.')[0]) >= 4:
            if self.firefox_driver_path and os.path.isfile(self.firefox_driver_path):
                service = FirefoxService(executable_path=self.firefox_driver_path, log_path=os.devnull)
            else:
                service = FirefoxService(executable_path=self.FIREFOX_DRIVER_FILE_NAME, log_path=os.devnull)
            if sys.platform == "win32":
                service.creationflags = CREATE_NO_WINDOW
            self._driver = webdriver.Firefox(options=options, service=service)
        else:
            if self.firefox_driver_path and os.path.isfile(self.firefox_driver_path):
                self._driver = webdriver.Firefox(executable_path=self.firefox_driver_path, options=options,
                                                 service_log_path=os.devnull)
            else:
                self._driver = webdriver.Firefox(executable_path=self.FIREFOX_DRIVER_FILE_NAME, options=options,
                                                 service_log_path=os.devnull)

    def _start_chrome(self):
        profile = self.CHROME_PROFILE_PATH
        if not os.path.exists(profile):
            os.makedirs(profile)

        options = webdriver.ChromeOptions() 
        if profile and os.path.isdir(profile):
            options.add_argument("user-data-dir=" + profile)

        try:
            if int(selenium.__version__.partition('.')[0]) >= 4:
                if self.chrome_driver_path and os.path.isfile(self.chrome_driver_path):
                    service = ChromeService(executable_path=self.chrome_driver_path)
                else:
                    service = ChromeService(executable_path=self.CHROME_DRIVER_FILE_NAME)
                if sys.platform == "win32":
                    service.creationflags = CREATE_NO_WINDOW
                self._driver = webdriver.Chrome(options=options, service=service)
            else:
                if self.chrome_driver_path and os.path.isfile(self.chrome_driver_path):
                    self._driver = webdriver.Chrome(executable_path=self.chrome_driver_path, options=options)
                else:
                    self._driver = webdriver.Chrome(executable_path=self.CHROME_DRIVER_FILE_NAME, options=options)
        except SessionNotCreatedException as inst:
            self.err_msg = self.err_msg + " " + inst.msg
            self._start_firefox()
        except WebDriverException as inst:
            self.err_msg = self.err_msg + " " + inst.msg
            self._start_firefox()

    def _start_edge(self):
        profile = self.EDGE_PROFILE_PATH
        if not os.path.exists(profile):
            os.makedirs(profile)

        if int(selenium.__version__.partition('.')[0]) >= 4:
            options = webdriver.EdgeOptions()
            if profile and os.path.isdir(profile):
                options.add_argument("user-data-dir=" + profile)

            if self.edge_driver_path and os.path.isfile(self.edge_driver_path):
                service = EdgeService(executable_path=self.edge_driver_path)
            else:
                service = EdgeService(executable_path=self.EDGE_DRIVER_FILE_NAME)
            if sys.platform == "win32":
                service.creationflags = CREATE_NO_WINDOW
            try:
                self._driver = webdriver.Edge(options=options, service=service)
            except SessionNotCreatedException as inst:
                self.err_msg = self.err_msg + " " + inst.msg
                self._start_firefox()
            except WebDriverException as inst:
                self.err_msg = self.err_msg + " " + inst.msg
                self._start_firefox()
        else:
            self.err_msg = self.err_msg + " " + "Edge: upgrade Selenium " + selenium.__version__ + " to version 4"
            self._start_firefox()

    def _start_ie(self):
        self._driver = webdriver.Ie()

    def _start_safari(self):
        self._driver = webdriver.Safari()

    def _start_opera(self):
        self._driver = webdriver.Opera()


    def _on_tab_closed(self):
        try:
            tab_handles = self._driver.window_handles
        except:
            #self._driver.quit()
            os._exit(1)
        tabs_count = len(tab_handles)
        if tabs_count == 0:
            #self._driver.quit()
            os._exit(1)
        try:
            self._driver.switch_to.window(tab_handles[0])
        except:
            #self._driver.quit()
            os._exit(1)

    def _try_get_bool(self, func, args, exceptions=()):
        try:
            func(*args)
        except exceptions as e:
            return False
        except (NoSuchWindowException, InvalidSessionIdException):
            # User has closed browser tab
            self._on_tab_closed()
            return False
        except WebDriverException as inst:
            if "target frame detached" in inst.msg:
                # User has closed browser window
                self._on_tab_closed()
            elif (("Failed to decode response from marionette" in inst.msg) or 
                  ("browsingContext.currentWindowGlobal is null" in inst.msg) or 
                  ("chrome not reachable" in inst.msg)):
                # User has closed browser window
                self._on_tab_closed()
            else:
                raise
            return False
        return True

    def _try_get_value(self, func, args, exceptions=()):
        try:
            return func(*args)
        except exceptions as e:
            return None
        except (NoSuchWindowException, InvalidSessionIdException):
            # User has closed browser tab
            self._on_tab_closed()
            return None
        except WebDriverException as inst:
            if "target frame detached" in inst.msg:
                # User has closed browser window
                self._on_tab_closed()
            elif (("Failed to decode response from marionette" in inst.msg) or 
                  ("browsingContext.currentWindowGlobal is null" in inst.msg) or 
                  ("chrome not reachable" in inst.msg)):
                # User has closed browser window
                self._on_tab_closed()
            else:
                raise
            return None


    def get(self, url, exceptions=()):
        return self._try_get_bool(lambda d, s: d.get(s), (self._driver, url), exceptions)

    def execute_script(self, script, *args, exceptions=()):
        return self._try_get_value(lambda d, s, a: d.execute_script(s, *a), (self._driver, script, args), exceptions)

    #@property
    def current_url(self, exceptions=()):
        return self._try_get_value(lambda d: d.current_url, (self._driver,), exceptions)

    #@property
    def current_window_handle(self, exceptions=()):
        return self._try_get_value(lambda d: d.current_window_handle, (self._driver,), exceptions)

    #@property
    def window_handles(self, exceptions=()):
        return self._try_get_value(lambda d: d.window_handles, (self._driver,), exceptions)

    @property
    def switch_to(self):
        return self._switch_to

    def set_page_load_timeout(self, time_to_wait, exceptions=()):
        return self._try_get_bool(lambda d, x: d.set_page_load_timeout(x), (self._driver, time_to_wait), exceptions)

    def find_elements(self, by=By.ID, value=None, exceptions=()):
        return self._try_get_value(lambda d, b, v: d.find_elements(b, v), (self._driver, by, value), exceptions)


    def _check_readystate(self):
        return self.execute_script("return document.readyState",
                                   exceptions=(NoSuchWindowException, TimeoutException,
                                               UnexpectedAlertPresentException)) == "complete"

    def wait_for_page(self):
        while True:
            res = self._check_readystate()
            if res:
                break
            time.sleep(PAGE_READY_POLL_PERIOD_SEC)
