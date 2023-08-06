import json

def about():
    return ('<div>' +
            '<h2>' + _('Usage:') + '</h2>' +
            '<h3>' + _('View local files (images or videos) using the browser. Change to next or previous file in the directory by mouse click.') + '</h3>' +
            '<br>' +
            '<p>' +
            _('Navigate to any local file (In Firefox press "Alt" key to open the browser menu and choose File--Open File. In Chrome and Edge press "Ctrl+O". Or click "Open" button on the upper side of the screen).') +
            '</p>' +
            '<p>' +
            _('To open next file in the directory, click ">" button on the right side of the screen.') +
            '</p>' +
            '<p>' +
            _('To open previous file in the directory, click "<" button on the left side of the screen.') +
            '</p>' +
            '<br>' +
            '<p>' +
            _('To zoom in, click "+" button at the bottom of the screen, or drag the image down with the middle mouse button (wheel) pressed.') +
            '</p>' +
            '<p>' +
            _('To zoom out, click "-" button at the bottom of the screen, or drag the image up with the middle mouse button (wheel) pressed.') +
            '</p>' +
            '<p>' +
            _('To scroll the image, use scroll bars, or drag the image with the left mouse button pressed.') +
            '</p>' +
            '</div>')

def site_setup():
    tr = {}
    tr["nextButton.title"] = _("Go to the next image of the gallery")
    tr["prevButton.title"] = _("Go to the previous image of the gallery")
    tr["zoomOutButton.title"] = _("Zoom out (or drag UP with mouse wheel pressed)")
    tr["zoomInButton.title"] = _("Zoom in (or drag DOWN with mouse wheel pressed)")
    tr["openFileButton.innerText"] = _("Open")
    tr["openFileButton.title"] = _("Change directory and select a file")
    tr["aboutButton.title"] = _("Show usage information")
    return json.dumps(tr)

def dialog_setup():
    tr = {}
    tr["closeButton.title"] = _("Close the window")
    return json.dumps(tr)

def fill_dialog_toolbar():
    tr = {}
    tr["open:button.title"] = _("Select directory")
    tr["about:button.title"] = _("Select language")
    return json.dumps(tr)

