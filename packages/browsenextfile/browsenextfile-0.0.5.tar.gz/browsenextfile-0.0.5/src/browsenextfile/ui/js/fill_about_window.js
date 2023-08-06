var windowContent = arguments[0];

function fillWindowContent(mainContent) {
    var content = document.getElementById("NextFileUiDialogContent");
    content.innerHTML = mainContent;
}

fillWindowContent(windowContent);

