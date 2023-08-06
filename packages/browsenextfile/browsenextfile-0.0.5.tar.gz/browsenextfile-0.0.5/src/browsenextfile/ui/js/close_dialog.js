var lang = arguments[0];
var origLang = arguments[1];
var translations = arguments[2];

var dialog = document.getElementById("NextFileUiDialog");
if (dialog) {
    dialog.parentNode.removeChild(dialog);
}

if (document.title == "Next File") {
    document.documentElement.lang = lang;
}

if (lang != origLang) {
    var tr = JSON.parse(translations);

    var nextButton = document.getElementById("NextFileUiNextButton");
    if (nextButton)
        nextButton.title = tr["nextButton.title"];
    var prevButton = document.getElementById("NextFileUiPrevButton");
    if (prevButton)
        prevButton.title = tr["prevButton.title"];
    var zoomOutButton = document.getElementById("NextFileUiZoomOutButton");
    if (zoomOutButton)
        zoomOutButton.title = tr["zoomOutButton.title"];
    var zoomInButton = document.getElementById("NextFileUiZoomInButton");
    if (zoomInButton)
        zoomInButton.title = tr["zoomInButton.title"];
    var openFileButton = document.getElementById("NextFileUiOpenFileButton");
    if (openFileButton) {
        openFileButton.innerText = tr["openFileButton.innerText"];
        openFileButton.title = tr["openFileButton.title"];
    }
    var aboutButton = document.getElementById("NextFileUiAboutButton");
    if (aboutButton)
        aboutButton.title = tr["aboutButton.title"];
}

