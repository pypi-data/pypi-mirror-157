function checkUserInput() {
    const obj = {};

    if (document.getElementsByTagName("html")[0].hasAttribute("data-nextfile-ui-button-clicked")) {
        var button = document.getElementsByTagName("html")[0].getAttribute("data-nextfile-ui-button-clicked");
        if (!button) {
            button = "";
        }
        if (button != "") {
            document.getElementsByTagName("html")[0].removeAttribute("data-nextfile-ui-button-clicked");
            obj["button_clicked"] = button;
        }
    }

    if (document.getElementsByTagName("html")[0].hasAttribute("data-nextfile-ui-directory-selected")) {
        var dir = document.getElementsByTagName("html")[0].getAttribute("data-nextfile-ui-directory-selected");
        if (!dir) {
            dir = "";
        }
        if (dir != "") {
            document.getElementsByTagName("html")[0].removeAttribute("data-nextfile-ui-directory-selected");
            obj["directory_selected"] = dir;
        }
    }

    if (document.getElementsByTagName("html")[0].hasAttribute("data-nextfile-ui-file-selected")) {
        var file = document.getElementsByTagName("html")[0].getAttribute("data-nextfile-ui-file-selected");
        if (!file) {
            file = "";
        }
        if (file != "") {
            document.getElementsByTagName("html")[0].removeAttribute("data-nextfile-ui-file-selected");
            obj["file_selected"] = file;

        }
    }

    if (document.getElementsByTagName("html")[0].hasAttribute("data-nextfile-ui-language-selected")) {
        var lang = document.getElementsByTagName("html")[0].getAttribute("data-nextfile-ui-language-selected");
        if (!lang) {
            lang = "";
        }
        if (lang != "") {
            document.getElementsByTagName("html")[0].removeAttribute("data-nextfile-ui-language-selected");
            obj["language_selected"] = lang;
        }
    }

    var nextButton = document.getElementById("NextFileUiNextButton");
    if (!nextButton) {
        obj["site_state"] = "no_setup";
    }

    if (nextButton && (nextButton.style.visibility == "visible")) {
        obj["buttons_state"] = "visible";
    }

    var resStr = JSON.stringify(obj);
    return resStr;
}

return checkUserInput();

