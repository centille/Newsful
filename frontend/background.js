chrome.contextMenus.create({
    id: "extractText",
    title: "Search selected text with Newsful",
    contexts: ["all"]
});

const create_popup = () => {
    chrome.windows.create({
        url: "./popup.html",
        type: "popup",
        width: 600,
        height: 600,
        focused: true
    }, function (window) {
        chrome.windows.update(window.id, { focused: true });
    });
}

chrome.runtime.onMessage.addListener(
    function (message, sender, sendResponse) {
        create_popup();
        if (message.action === "verifyImage") {
            fetch('http://localhost:8000/api/verify/image', {
                method: 'POST',
                body: JSON.stringify(message.data),
                headers: {
                    'Content-type': 'application/json; charset=UTF-8',
                },
            })
                .then(response => response.json())
                .then(json => chrome.runtime.sendMessage({ action: "displayResponse", data: json }))
                .catch(error => console.error(error));
        }
        else if (message.action === "verifyText") {
            fetch('http://localhost:8000/api/verify/text', {
                method: 'POST',
                body: JSON.stringify(message.data),
                headers: {
                    'Content-type': 'application/json; charset=UTF-8',
                },
            })
                .then(response => response.json())
                .then(json => chrome.runtime.sendMessage({ action: "displayResponse", data: json }))
                .catch(error => console.error(error));
        }
    }
);

chrome.contextMenus.onClicked.addListener(function (info, tab) {
    if (info.menuItemId === "extractText") {
        // If the selected text is an image, send it to the backend
        if (info?.mediaType && info?.mediaType === "image") {
            console.log("Image selected");
            const imgUrl = info.srcUrl;
            chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
                chrome.tabs.executeScript(tabs[0].id, {
                    code: `
                    var dt = {
                        picture_url: "${imgUrl}",
                        url: window.location.href
                    };

                    chrome.runtime.sendMessage({ action: "verifyImage", data: dt });
                    `
                });
            });
        }
        // Otherwise, send the selected text to the backend
        else {
            chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
                chrome.tabs.executeScript(tabs[0].id, {
                    code: `
                    var dt = {
                        content: window.getSelection().toString(),
                        url: window.location.href
                    };
                    console.log(dt);
                    chrome.runtime.sendMessage({ action: "verifyText", data: dt });
                    `
                });
            });
            console.log("Menu item clicked!");
        }
    }
});

document.addEventListener("DOMContentLoaded", function () {
    chrome.windows.getCurrent(function (window) {
        chrome.windows.update(window.id, { focused: true });
    });
});
