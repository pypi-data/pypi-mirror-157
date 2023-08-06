var cssString = arguments[0];
var translations = arguments[1];

function closeButtonClicked() {
    var button = "";
    if (document.getElementsByTagName("html")[0].hasAttribute("data-nextfile-ui-button-clicked")) {
        button = document.getElementsByTagName("html")[0].getAttribute("data-nextfile-ui-button-clicked");
        if (!button)
            button = "";
    }

    if (button != "")
        return

    document.getElementsByTagName("html")[0].setAttribute("data-nextfile-ui-button-clicked", "close_dialog");
}

function mouseMoved(e) {
    if (e.buttons == 1) {
        // 1: Primary button (usually the left button)
        e.stopPropagation();
    } else if (e.buttons == 4) {
        // 4: Auxiliary button (usually the mouse wheel button or middle button)
        e.stopPropagation();
    }
}


function zIndexInfo(elem, level, info) {
    if ((elem.id == "NextFileUiDialog") || 
    (elem.id == "NextFileUiDialogCloseButton") || 
    (elem.id == "NextFileUiDialogContent") || 
    (elem.id == "NextFileUiDialogToolbarContent"))
        return;

    var cssObj = window.getComputedStyle(elem, null);
    var indStr = cssObj.getPropertyValue("z-index");
    var ind = parseInt(indStr, 10);
    if (isNaN(ind)) {
        // total count of "auto" elements
        info[0] = info[0] + 1;
    } else {
        // maximum value of zIndex
        if (ind > info[1]) {
            info[1] = ind;
        }
    }
    var i;
    for (i = 0; i < elem.children.length; i++) {
        child = elem.children[i];
        zIndexInfo(child, level+1, info);
    }
}

function showOnTop() {
    var info = [0, 0];
    zIndexInfo(document.body, 0, info);
    var zMax = info[1] + info[0];

    var dialog = document.getElementById("NextFileUiDialog");
    if (dialog) {
        zMax++;
        dialog.style.zIndex = zMax.toString();
    }

    var dialogCloseButton = document.getElementById("NextFileUiDialogCloseButton");
    if (dialogCloseButton) {
        zMax++;
        dialogCloseButton.style.zIndex = zMax.toString();
    }

    var dialogContent = document.getElementById("NextFileUiDialogContent");
    if (dialogContent) {
        zMax++;
        dialogContent.style.zIndex = zMax.toString();
    }

    var dialogToolbarContent = document.getElementById("NextFileUiDialogToolbarContent");
    if (dialogToolbarContent) {
        zMax++;
        dialogToolbarContent.style.zIndex = zMax.toString();
    }
}


var createDialogCallCount = 0;

function createDialog(cssStr) {
    if (createDialogCallCount > 0)
        return;
    createDialogCallCount++;

    if (!document.getElementsByTagName("HEAD")[0]) {
        createDialogCallCount--;
        return;
    }

    if (!document.body) {
        createDialogCallCount--;
        return;
    }

    var styleElem = document.getElementById("NextFileUiDialogStyle");
    if (!styleElem) {
        styleElem = document.createElement("STYLE");
        styleElem.id = "NextFileUiDialogStyle";
        styleElem.innerHTML = cssStr;
        document.getElementsByTagName("HEAD")[0].appendChild(styleElem);
    }

    var tr = JSON.parse(translations);

    var dialog = document.createElement("DIV");
    dialog.id = "NextFileUiDialog";
    dialog.className = "nextFileUiDialogClass";
    dialog.onmousemove = mouseMoved;
    document.body.appendChild(dialog);

    var toolbar = document.createElement("DIV");
    toolbar.id = "NextFileUiDialogToolbar";
    toolbar.className = "nextFileUiDialogToolbarClass";
    dialog.appendChild(toolbar);

    var closeButton = document.createElement("BUTTON");
    closeButton.id = "NextFileUiDialogCloseButton";
    closeButton.className = "nextFileUiDialogCloseButtonClass";
    closeButton.type = "button";
    closeButton.innerText = "X";
    closeButton.title = tr["closeButton.title"];
    closeButton.onclick = closeButtonClicked;
    toolbar.appendChild(closeButton);

    var toolbarContent = document.createElement("DIV");
    toolbarContent.id = "NextFileUiDialogToolbarContent";
    toolbarContent.className = "nextFileUiDialogToolbarContentClass";
    toolbar.appendChild(toolbarContent);

    var content = document.createElement("DIV");
    content.id = "NextFileUiDialogContent";
    content.className = "nextFileUiDialogContentClass";
    dialog.appendChild(content);

    showOnTop();

    createDialogCallCount--;
}

var ui = document.getElementById("NextFileUiNextButton");
var dialog = document.getElementById("NextFileUiDialog");
if (document.body && ui && (!dialog)) {
    createDialog(cssString);
}

