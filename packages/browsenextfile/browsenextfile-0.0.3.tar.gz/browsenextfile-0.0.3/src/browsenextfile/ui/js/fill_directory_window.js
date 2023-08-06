var directoryNames = arguments[0];
var fileNames = arguments[1];
var selectName = arguments[2];

function lineClicked() {
    var selectedLines = document.getElementsByClassName("nextFileUiDialogContentSelectedLineClass");
    var i;
    for (i = 0; i < selectedLines.length; i++) {
        selectedLines[i].classList.remove("nextFileUiDialogContentSelectedLineClass");
    }

    this.classList.add("nextFileUiDialogContentSelectedLineClass");
}

function lineDoubleClicked() {
    var file_name = "";
    if (document.getElementsByTagName("html")[0].hasAttribute("data-nextfile-ui-file-selected")) {
        file_name = document.getElementsByTagName("html")[0].getAttribute("data-nextfile-ui-file-selected");
        if (!file_name)
            file_name = "";
    }

    if (file_name != "")
        return

    document.getElementsByTagName("html")[0].setAttribute("data-nextfile-ui-file-selected", this.innerHTML);
}

function addLine(parent, type, name, nameToSelect) {
    var line = document.createElement("DIV");
    line.classList.add("nextFileUiDialogContentLineClass");

    if (type == "dir") {
        line.classList.add("nextFileUiDialogContentDirLineClass");
    } else if (type == "file") {
        line.classList.add("nextFileUiDialogContentFileLineClass");
    }

    line.innerHTML = name;

    if (name == nameToSelect) {
        line.classList.add("nextFileUiDialogContentSelectedLineClass");
    }

    line.ondblclick = lineDoubleClicked;
    line.onclick = lineClicked;

    parent.appendChild(line);
}

function fillWindowContent(dirs, files, nameToSelect) {
    var content = document.getElementById("NextFileUiDialogContent");

    while (content.hasChildNodes()) {
        content.removeChild(content.firstChild);
    }

    var dirsArray = JSON.parse(dirs);
    var filesArray = JSON.parse(files);

    var i;
    for (i = 0; i < dirsArray.length; i++) {
        addLine(content, "dir", dirsArray[i], nameToSelect);
    }
    for (i = 0; i < filesArray.length; i++) {
        addLine(content, "file", filesArray[i], nameToSelect);
    }

    var selectedLines = document.getElementsByClassName("nextFileUiDialogContentSelectedLineClass");
    if (selectedLines.length > 0) {
        selectedLines[0].scrollIntoView();
    } else if (content.firstChild) {
        content.firstChild.scrollIntoView();
    }
}

fillWindowContent(directoryNames, fileNames, selectName);

