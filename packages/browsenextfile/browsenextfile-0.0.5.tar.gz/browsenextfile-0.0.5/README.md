# browsenextfile


[![en](https://img.shields.io/badge/lang-en-blue.svg)](README.md)
[![ru](https://img.shields.io/badge/язык-рус-red.svg)](README.ru.md)


This program can be used to view local files (images or videos) using web browser. Change to next or previous file in the directory by a mouse click. All image and video file formats supported by the browser can be opened.


## Prerequisites:

- Python 3
- Mozilla Firefox web browser


## Installation:

On Linux, open command line and type:
```
~> python3 -m pip install --no-cache-dir browsenextfile
```

On Windows, open command line or Windows PowerShell and type:
```
~> py -m pip install --no-cache-dir browsenextfile
```


## Usage:

Run the program. If the program was installed as shown above, a shortcut (`NextFile` icon) was automatically created on the Desktop and in the Applications menu. In this case the program can be launched by double-clicking on this shortcut, or by right-clicking on the image file which we want to open and selecting `NextFile` program from the drop-down menu.

Technically, the program `nextfile.py` can also be run as a Python script from command line as follows:
```
~> python3 nextfile.py
```

Wait for a new browser window to appear. It may take up to a minute.

The home page will open with information about the program.

In the browser window, navigate to any local file by clicking the `Open` button on the upper side of the screen. (Alternative method: In Firefox press `Alt` key to open the browser menu and choose `File--Open File`. In Chrome and Edge press `Ctrl+O`.)

To open next file in the directory, click `>` button on the right side of the screen.

To open previous file in the directory, click `<` button on the left side of the screen.

To zoom in, click `+` button at the bottom of the screen, or drag the image down with the middle mouse button (wheel) pressed.

To zoom out, click `-` button at the bottom of the screen, or drag the image up with the middle mouse button (wheel) pressed.

To scroll the image, use scroll bars, or drag the image with the left mouse button pressed.

If several tabs are open in the browser, only one tab (usually the first one) is controlled by the buttons.

The buttons are present only if a local file from this computer is opened in the browser. If a page from internet is opened, there are no buttons.


## Changing the program's options:

The `nextfile_options.txt` text file contains several options which users can edit to change the way the program behaves.
This file is located in the application's editable data directory:

On Linux:
```
/home/<user_name>/.local/share/nextfile/nextfile_options.txt
```

On Windows:
```
C:\Users\<user_name>\AppData\Local\dmitrish\nextfile\nextfile_options.txt
```

Exact location of this and other files used by the program can be found on the informational page - the first page opened by the browser when the program starts.

Available options:

*browser*: By default, the program opens Firefox browser. To use another browser, change the *value* of the *browser* option in the options file correspondingly. So far, the program was tested with Firefox, Chrome, and Edge browsers.


## Browser data:

When this program opens a web browser, it uses a browser user's profile which is different from default profile used when the browser is opened standard way. All browser data (including user preferences, browser cache, history, bookmarks, installed extensions, etc.) used by web browsers opened by this program are stored in the following location. If a profile here is deleted, a clean profile will be created instead:

On Linux:
```
home/<user_name>/.local/share/nextfile/profiles/
```

On Windows:
```
C:\Users\<user_name>\AppData\Local\dmitrish\nextfile\profiles\
```

Exact location of this and other files used by the program can be found on the informational page - the first page opened by the browser when the program starts.


## Installing the Web Driver (optional):

The program comes with a pre-installed Web Driver for Firefox browser, so if you want to use Firefox it will work out of the box. However, if you want to use another browser like Chrome or Edge, you have to install corresponding Web Driver manually as described below. Also, in case of Chrome or Edge you will have to periodically upgrade the Web Driver to match the current version of automatically upgraded Chrome or Edge browser.

Install the Web Driver for the browser you want to use. The download links are on the site:

[Download a Web Driver](https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/#quick-reference)

**Important**: For all browsers except Firefox, the version of Web Driver file should match the current version of your browser.

Open the downloaded archive and extract the Web Driver executable. For Firefox browser the Web Driver file name is usually `geckodriver`. For Chrome browser the Web Driver file name is usually `chromedriver`. For Edge browser the Web Driver file name is usually `msedgedriver.exe`.

Place the Web Driver file into the corresponding sub-directory of the program's data directory:

On Linux:
```
/home/<user_name>/.local/share/nextfile/web_driver/linux64
```

On Windows:
```
C:\Users\<user_name>\AppData\Local\dmitrish\nextfile\web_driver\win64
```

Exact location of this and other files used by the program can be found on the informational page - the first page opened by the browser when the program starts.


## Supported platforms:

This code was tested on Linux (Ubuntu) with Firefox and Chrome browsers, and on Windows with Firefox, Chrome, and Edge browsers.

Following software is used by the program (If the program is installed using PIP, everything is installed automatically):

"Selenium" project to control the browser:

[https://www.selenium.dev/selenium/docs/api/py/api.html](https://www.selenium.dev/selenium/docs/api/py/api.html)






