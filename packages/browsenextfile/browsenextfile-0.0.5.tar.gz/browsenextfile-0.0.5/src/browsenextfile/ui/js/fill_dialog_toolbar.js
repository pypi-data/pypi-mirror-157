var windowType = arguments[0];
var toolbarArray = arguments[1];
var translations = arguments[2];

function directoryButtonClicked() {
    var dir = "";
    if (document.getElementsByTagName("html")[0].hasAttribute("data-nextfile-ui-directory-selected")) {
        dir = document.getElementsByTagName("html")[0].getAttribute("data-nextfile-ui-directory-selected");
        if (!dir)
            dir = "";
    }

    if (dir != "")
        return

    document.getElementsByTagName("html")[0].setAttribute("data-nextfile-ui-directory-selected", this.value);
}

function languageButtonClicked() {
    var lang = "";
    if (document.getElementsByTagName("html")[0].hasAttribute("data-nextfile-ui-language-selected")) {
        lang = document.getElementsByTagName("html")[0].getAttribute("data-nextfile-ui-language-selected");
        if (!lang)
            lang = "";
    }

    if (lang != "")
        return

    document.getElementsByTagName("html")[0].setAttribute("data-nextfile-ui-language-selected", this.value);
}

function fillToolbarContent(dialogType, toolbarItems) {
    var toolbarContent = document.getElementById("NextFileUiDialogToolbarContent");

    var tr = JSON.parse(translations);

    while (toolbarContent.hasChildNodes()) {
        toolbarContent.removeChild(toolbarContent.firstChild);
    }

    var itemsArray = JSON.parse(toolbarItems);
    var i;
    for (i = 0; i < itemsArray.length; i++) {
        var value = itemsArray[i][0];
        var value_name = itemsArray[i][1];

        var button = document.createElement("BUTTON");
        button.className = "nextFileUiDialogToolbarContentButtonClass";

        button.type = "button";
        button.innerText = value_name;
        button.value = value;
        if (dialogType == "open") {
            button.title = tr["open:button.title"];
            button.onclick = directoryButtonClicked;
        } else {
            button.title = tr["about:button.title"];
            button.onclick = languageButtonClicked;
        }

        toolbarContent.appendChild(button);
    }

    if (toolbarContent.lastChild) {
        toolbarContent.lastChild.scrollIntoView(false);
    }
}

fillToolbarContent(windowType, toolbarArray);

