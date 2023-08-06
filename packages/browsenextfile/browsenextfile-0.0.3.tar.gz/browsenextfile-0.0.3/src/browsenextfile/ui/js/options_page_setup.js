var errMsg = arguments[0];

function fillClassElements(className, elementHtml) {
    const collection = document.getElementsByClassName(className);
    for (let i = 0; i < collection.length; i++) {
        collection[i].innerHTML = elementHtml;
    }
}

fillClassElements("err_msg", errMsg);

document.body.className='nextfile_options';

