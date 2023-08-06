var cssString = arguments[0];
var translations = arguments[1];

function nextClicked() {
    var button = "";
    if (document.getElementsByTagName("html")[0].hasAttribute("data-nextfile-ui-button-clicked")) {
        button = document.getElementsByTagName("html")[0].getAttribute("data-nextfile-ui-button-clicked");
        if (!button)
            button = "";
    }

    if (button != "")
        return

    document.getElementsByTagName("html")[0].setAttribute("data-nextfile-ui-button-clicked", "next");
}

function prevClicked() {
    var button = "";
    if (document.getElementsByTagName("html")[0].hasAttribute("data-nextfile-ui-button-clicked")) {
        button = document.getElementsByTagName("html")[0].getAttribute("data-nextfile-ui-button-clicked");
        if (!button)
            button = "";
    }

    if (button != "")
        return

    document.getElementsByTagName("html")[0].setAttribute("data-nextfile-ui-button-clicked", "prev");
}

function openFileClicked() {
    var button = "";
    if (document.getElementsByTagName("html")[0].hasAttribute("data-nextfile-ui-button-clicked")) {
        button = document.getElementsByTagName("html")[0].getAttribute("data-nextfile-ui-button-clicked");
        if (!button)
            button = "";
    }

    if (button != "")
        return

    document.getElementsByTagName("html")[0].setAttribute("data-nextfile-ui-button-clicked", "open");
}

function aboutClicked() {
    var button = "";
    if (document.getElementsByTagName("html")[0].hasAttribute("data-nextfile-ui-button-clicked")) {
        button = document.getElementsByTagName("html")[0].getAttribute("data-nextfile-ui-button-clicked");
        if (!button)
            button = "";
    }

    if (button != "")
        return

    document.getElementsByTagName("html")[0].setAttribute("data-nextfile-ui-button-clicked", "about");
}


function zIndexInfo(elem, level, info) {
    if ((elem.id == "NextFileUiNextButton") || 
    (elem.id == "NextFileUiPrevButton") || 
    (elem.id == "NextFileUiZoomInButton") || 
    (elem.id == "NextFileUiZoomOutButton") || 
    (elem.id == "NextFileUiZoomInfo") || 
    (elem.id == "NextFileUiOpenFileButton") || 
    (elem.id == "NextFileUiAboutButton") || 
    (elem.id == "NextFileUiDialog") || 
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


function showButtons() {
    var info = [0, 0];
    zIndexInfo(document.body, 0, info);
    var zMax = info[1] + info[0];

    var nextButton = document.getElementById("NextFileUiNextButton");
    zMax++;
    nextButton.style.zIndex = zMax.toString();
    nextButton.style.visibility = "visible";

    var prevButton = document.getElementById("NextFileUiPrevButton");
    zMax++;
    prevButton.style.zIndex = zMax.toString();
    prevButton.style.visibility = "visible";

    var zoomInButton = document.getElementById("NextFileUiZoomInButton");
    zMax++;
    zoomInButton.style.zIndex = zMax.toString();
    zoomInButton.style.visibility = "visible";

    var zoomOutButton = document.getElementById("NextFileUiZoomOutButton");
    zMax++;
    zoomOutButton.style.zIndex = zMax.toString();
    zoomOutButton.style.visibility = "visible";

    var zoomInfo = document.getElementById("NextFileUiZoomInfo");
    zMax++;
    zoomInfo.style.zIndex = zMax.toString();
    zoomInfo.style.visibility = "visible";

    var openFileButton = document.getElementById("NextFileUiOpenFileButton");
    zMax++;
    openFileButton.style.zIndex = zMax.toString();
    openFileButton.style.visibility = "visible";

    var aboutButton = document.getElementById("NextFileUiAboutButton");
    zMax++;
    aboutButton.style.zIndex = zMax.toString();
    aboutButton.style.visibility = "visible";

    // temporary popup windows

    var dialog = document.getElementById("NextFileUiDialog");
    if (dialog) {
        zMax++;
        dialog.style.zIndex = zMax.toString();
        dialog.style.visibility = "visible";
    }

    var dialogCloseButton = document.getElementById("NextFileUiDialogCloseButton");
    if (dialogCloseButton) {
        zMax++;
        dialogCloseButton.style.zIndex = zMax.toString();
        dialogCloseButton.style.visibility = "visible";
    }

    var dialogContent = document.getElementById("NextFileUiDialogContent");
    if (dialogContent) {
        zMax++;
        dialogContent.style.zIndex = zMax.toString();
        dialogContent.style.visibility = "visible";
    }

    var dialogToolbarContent = document.getElementById("NextFileUiDialogToolbarContent");
    if (dialogToolbarContent) {
        zMax++;
        dialogToolbarContent.style.zIndex = zMax.toString();
        dialogToolbarContent.style.visibility = "visible";
    }
}

function hideButtons() {
    var nextButton = document.getElementById("NextFileUiNextButton");
    nextButton.style.visibility = "hidden";

    var prevButton = document.getElementById("NextFileUiPrevButton");
    prevButton.style.visibility = "hidden";

    var zoomInButton = document.getElementById("NextFileUiZoomInButton");
    zoomInButton.style.visibility = "hidden";

    var zoomOutButton = document.getElementById("NextFileUiZoomOutButton");
    zoomOutButton.style.visibility = "hidden";

    var zoomInfo = document.getElementById("NextFileUiZoomInfo");
    zoomInfo.style.visibility = "hidden";

    var openFileButton = document.getElementById("NextFileUiOpenFileButton");
    openFileButton.style.visibility = "hidden";

    var aboutButton = document.getElementById("NextFileUiAboutButton");
    aboutButton.style.visibility = "hidden";
}


var image = null;
var isVideo = false;

function getImg() {
    if (image) {
        return image;
    }
    var images = document.getElementsByTagName("IMG");
    isVideo = false;
    if ((!images) || (images.length == 0)) {
        images = document.getElementsByTagName("VIDEO");
        if ((!images) || (images.length == 0)) {
            var zoomInfo = document.getElementById("NextFileUiZoomInfo");
            zoomInfo.innerHTML = "";
            return null;
        }
        isVideo = true;
    }

    image = images[0];
    return image;
}

function showZoomPercentage() {
    getImg();
    if (!image)
        return;

    var origHeight;
    var currentHeight;
    if (isVideo) {
        origHeight = image.videoHeight;
        currentHeight = image.height;
        if (currentHeight == 0)
            currentHeight = image.offsetHeight;
    } else {
        origHeight = image.naturalHeight;
        currentHeight = image.height;
    }

    var percentH = Math.round((currentHeight / origHeight) * 100);
    var zoomInfo = document.getElementById("NextFileUiZoomInfo");
    zoomInfo.innerHTML = percentH.toString() + "%";
}


function zoomImg(addPercent) {
    getImg();
    if (!image)
        return;

    var origWidth;
    var origHeight;
    var currentHeight;
    if (isVideo) {
        origWidth = image.videoWidth;
        origHeight = image.videoHeight;
        currentHeight = image.height;
        if (currentHeight == 0)
            currentHeight = image.offsetHeight;
    } else {
        origWidth = image.naturalWidth;
        origHeight = image.naturalHeight;
        currentHeight = image.height;
    }

    var ratioWH = origWidth / origHeight;
    var percentH = Math.round((currentHeight / origHeight) * 100);
    var newPercentH = percentH + addPercent;
    if (newPercentH <= 0) {
            return;
    }
    image.style.marginTop = "0";

    var coeff = newPercentH / percentH;
    var h = currentHeight;
    image.height = h * coeff;

    h = image.height;
    var w = h * ratioWH;
    image.width = w;

    showZoomPercentage();
}

function zoomIn() {
    zoomImg(10);
}

function zoomOut() {
    zoomImg(-10);
}


var imgSetupDone = false;

function imgSetup() {
    if (!imgSetupDone) {
        getImg();
        if (image) {
            image.setAttribute('draggable', false);
            image.style.marginTop = "0";
            showZoomPercentage();
            image.addEventListener("click", showZoomPercentage);
            imgSetupDone = true;
        }
    }
}


var firstMouseScrollX = undefined;
var firstMouseScrollY = undefined;
var lastMouseScrollX = undefined;
var lastMouseScrollY = undefined;
const MOUSE_SCROLL_STEP = 3;

var lastMouseZoomY = undefined;
const MOUSE_ZOOM_STEP = 5;

function scrollByMouse(e) {
    var eventX = e.clientX;
    var eventY = e.clientY;
    var dX = 0;
    var dY = 0;
    if (!lastMouseScrollX) {
        lastMouseScrollX = eventX;
    } else if ((eventX - lastMouseScrollX >= MOUSE_SCROLL_STEP) ||
    (eventX - lastMouseScrollX <= -MOUSE_SCROLL_STEP)) {
        dX = eventX - lastMouseScrollX;
        lastMouseScrollX = eventX;
    }
    if (!lastMouseScrollY) {
        lastMouseScrollY = eventY;
    } else if ((eventY - lastMouseScrollY >= MOUSE_SCROLL_STEP) ||
    (eventY - lastMouseScrollY <= -MOUSE_SCROLL_STEP)) {
        dY = eventY - lastMouseScrollY;
        lastMouseScrollY = eventY;
    }
    if ((dX != 0) || (dY != 0)) {
        imgSetup();
        if (image) {
            image.style.cursor = "all-scroll";
        }
        window.scrollBy(-dX, -dY);
    }
}

function zoomByMouse(e) {
    var eventY = e.clientY;
    if (!lastMouseZoomY) {
        lastMouseZoomY = eventY;
    } else if ((eventY - lastMouseZoomY >= MOUSE_ZOOM_STEP) ||
    (eventY - lastMouseZoomY <= -MOUSE_ZOOM_STEP)) {
        if (image) {
            image.style.cursor = "ns-resize";
        }
        zoomImg(((eventY - lastMouseZoomY) / window.innerHeight) * 100);
        lastMouseZoomY = eventY;
    }
}

function overcomeImgClick() {
    getImg();
    if (!image)
        return;

    var currentWidth;
    var currentHeight;
    if (isVideo) {
        currentWidth = image.width;
        currentHeight = image.height;
        if (currentWidth == 0)
            currentWidth = image.offsetWidth;
        if (currentHeight == 0)
            currentHeight = image.offsetHeight;
    } else {
        currentWidth = image.width;
        currentHeight = image.height;
    }

    var xScroll = window.pageXOffset;
    var yScroll = window.pageYOffset;

    function restoreImg() {
        image.height = currentHeight;
        image.width = currentWidth;

        window.scrollTo(xScroll, yScroll);

        image.removeEventListener("click", restoreImg);
        image.addEventListener("click", showZoomPercentage);
    }
    image.removeEventListener("click", showZoomPercentage);
    image.addEventListener("click", restoreImg);
}

function mouseUp(e) {
    if (e.which == 1) {
        // 1 : Left mouse button
        if (image) {
            image.style.cursor = "auto";
        }
        if (lastMouseScrollX && firstMouseScrollX && lastMouseScrollY && firstMouseScrollY &&
        (lastMouseScrollX != firstMouseScrollX) && (lastMouseScrollY != firstMouseScrollY)) {
            overcomeImgClick();
        }
        lastMouseScrollX = undefined;
        lastMouseScrollY = undefined;
        firstMouseScrollX = undefined;
        firstMouseScrollY = undefined;
    } else if (e.which == 2) {
        // 2 : Wheel button or middle button (if present)
        e.preventDefault();
        document.documentElement.style.overflow = "auto";
        if (image) {
            image.style.cursor = "auto";
        }
        lastMouseZoomY = undefined;
    }
}

function mouseDown(e) {
    if (e.which == 1) {
        // 1 : Left mouse button
        var eventX = e.clientX;
        var eventY = e.clientY;
        firstMouseScrollX = eventX;
        firstMouseScrollY = eventY;
    } else if (e.which == 2) {
        // 2 : Wheel button or middle button (if present)
        e.preventDefault();
        document.documentElement.style.overflow = "hidden";
    }
}


const CHECK_PERIOD_MS = 2000;

var timeoutId = undefined;
var mouseWasMoved = false;

function hideButtonsEx() {
    if (timeoutId) {
        hideButtons();
        clearTimeout(timeoutId);
        timeoutId = undefined;
    }
}

function timeoutFunction() {
    if (mouseWasMoved) {
        timeoutId = setTimeout(timeoutFunction, CHECK_PERIOD_MS);
        mouseWasMoved = false;
    } else {
        hideButtonsEx();
    }
}

function temporarilyShowButtons() {
    mouseWasMoved = true;
    if (!timeoutId) {
        timeoutId = setTimeout(timeoutFunction, CHECK_PERIOD_MS);
        showButtons();
    }
}

function mouseMoved(e) {
    if (e.buttons == 1) {
        // 1: Primary button (usually the left button)
        hideButtonsEx();
        scrollByMouse(e);
    } else if (e.buttons == 4) {
        // 4: Auxiliary button (usually the mouse wheel button or middle button)
        temporarilyShowButtons();
        zoomByMouse(e);
    } else {
        temporarilyShowButtons();
    }
}

function mouseMovedOnButton(e) {
    if (e.buttons == 1) {
        // 1: Primary button (usually the left button)
        e.stopPropagation();
    }
}

function windowScrolled() {
    hideButtonsEx();
}


var createButtonsCallCount = 0;

function createButtons(cssStr) {
    if (createButtonsCallCount > 0)
        return;
    createButtonsCallCount++;

    if (!document.getElementsByTagName("HEAD")[0]) {
        createButtonsCallCount--;
        return;
    }

    if (!document.body) {
        createButtonsCallCount--;
        return;
    }

    var styleElem = document.getElementById("NextFileUiStyle");
    if (!styleElem) {
        styleElem = document.createElement("STYLE");
        styleElem.id = "NextFileUiStyle";
        styleElem.innerHTML = cssStr;
        document.getElementsByTagName("HEAD")[0].appendChild(styleElem);
    }

    var tr = JSON.parse(translations);

    var nextButton = document.createElement("BUTTON");
    nextButton.id = "NextFileUiNextButton";
    nextButton.classList.add("nextFileUiButtonClass");
    nextButton.classList.add("nextFileUiSideButtonClass");
    nextButton.classList.add("nextFileUiNextSideButtonClass");
    nextButton.type = "button";
    nextButton.innerText = ">";
    nextButton.title = tr["nextButton.title"];
    nextButton.onclick = nextClicked;
    nextButton.onmousemove = mouseMovedOnButton;

    document.body.appendChild(nextButton);

    var prevButton = document.createElement("BUTTON");
    prevButton.id = "NextFileUiPrevButton";
    prevButton.classList.add("nextFileUiButtonClass");
    prevButton.classList.add("nextFileUiSideButtonClass");
    prevButton.classList.add("nextFileUiPrevSideButtonClass");
    prevButton.type = "button";
    prevButton.innerText = "<";
    prevButton.title = tr["prevButton.title"];
    prevButton.onclick = prevClicked;
    prevButton.onmousemove = mouseMovedOnButton;

    document.body.appendChild(prevButton);

    var zoomOutButton = document.createElement("BUTTON");
    zoomOutButton.id = "NextFileUiZoomOutButton";
    zoomOutButton.classList.add("nextFileUiButtonClass");
    zoomOutButton.classList.add("nextFileUiBottomButtonClass");
    zoomOutButton.classList.add("nextFileUiZoomOutBottomButtonClass");
    zoomOutButton.type = "button";
    zoomOutButton.innerText = "-";
    zoomOutButton.title = tr["zoomOutButton.title"];
    zoomOutButton.onclick = zoomOut;
    zoomOutButton.onmousemove = mouseMovedOnButton;

    document.body.appendChild(zoomOutButton);

    var zoomInfo = document.createElement("DIV");
    zoomInfo.id = "NextFileUiZoomInfo";
    zoomInfo.classList.add("nextFileUiButtonClass");
    zoomInfo.classList.add("nextFileUiBottomButtonClass");
    zoomInfo.classList.add("nextFileUiZoomInfoBottomButtonClass");
    zoomInfo.innerHTML = "";
    zoomInfo.onmousemove = mouseMovedOnButton;

    document.body.appendChild(zoomInfo);

    var zoomInButton = document.createElement("BUTTON");
    zoomInButton.id = "NextFileUiZoomInButton";
    zoomInButton.classList.add("nextFileUiButtonClass");
    zoomInButton.classList.add("nextFileUiBottomButtonClass");
    zoomInButton.classList.add("nextFileUiZoomInBottomButtonClass");
    zoomInButton.type = "button";
    zoomInButton.innerText = "+";
    zoomInButton.title = tr["zoomInButton.title"];
    zoomInButton.onclick = zoomIn;
    zoomInButton.onmousemove = mouseMovedOnButton;

    document.body.appendChild(zoomInButton);

    var openFileButton = document.createElement("BUTTON");
    openFileButton.id = "NextFileUiOpenFileButton";
    openFileButton.classList.add("nextFileUiButtonClass");
    openFileButton.classList.add("nextFileUiTopButtonClass");
    openFileButton.classList.add("nextFileUiOpenFileTopButtonClass");
    openFileButton.type = "button";
    openFileButton.innerText = tr["openFileButton.innerText"];
    openFileButton.title = tr["openFileButton.title"];
    openFileButton.onclick = openFileClicked;
    openFileButton.onmousemove = mouseMovedOnButton;

    document.body.appendChild(openFileButton);

    var aboutButton = document.createElement("BUTTON");
    aboutButton.id = "NextFileUiAboutButton";
    aboutButton.classList.add("nextFileUiButtonClass");
    aboutButton.classList.add("nextFileUiTopButtonClass");
    aboutButton.classList.add("nextFileUiAboutTopButtonClass");
    aboutButton.type = "button";
    aboutButton.innerText = "?";
    aboutButton.title = tr["aboutButton.title"];
    aboutButton.onclick = aboutClicked;
    aboutButton.onmousemove = mouseMovedOnButton;

    document.body.appendChild(aboutButton);


    document.documentElement.style.removeProperty('height');
    imgSetup();
    document.body.onresize = showZoomPercentage;

    window.onmousemove = mouseMoved;
    window.onmouseup = mouseUp;
    window.onmousedown = mouseDown;
    window.onscroll = windowScrolled;

    temporarilyShowButtons();

    createButtonsCallCount--;
}

var ui = document.getElementById("NextFileUiNextButton");
if (document.body && (!ui)) {
    createButtons(cssString);
}

