chrome.contextMenus.create({
    id: "extractText",
    title: "Search selected text with Newsful",
    contexts: ["all"]
});

chrome.runtime.onMessage.addListener(
    function (message, sender, sendResponse) {
        if (message.action === "verifyImage") {
            chrome.windows.update(popupWindowId, { focused: true });

            fetch('http://localhost:8000/api/verify/image', {
                method: 'POST',
                body: JSON.stringify(message.data),
                headers: {
                    'Content-type': 'application/json; charset=UTF-8',
                },
            })
                .then(response => response.json())
                .then(json => {
                    chrome.runtime.sendMessage({ action: "displayResponse", data: json });
                })
                .catch(error => console.error(error));
        }
    }
);

let popupWindowId;

chrome.windows.getCurrent(function (window) {
    popupWindowId = window.id;
    console.log("Popup Window ID:", popupWindowId);
});

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
                    console.log(dt);

                    console.log(${popupWindowId});

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
                    var data = {
                        content: window.getSelection().toString(),
                        url: window.location.href
                    };
                    console.log(data);

                    var result;
                    fetch('http://localhost:8000/api/verify/text', {
                        method: 'POST',
                        body: JSON.stringify(data),
                        headers: {
                            'Content-type': 'application/json; charset=UTF-8',
                        },
                    })
                        .then(response => response.json())
                        .then(json => {
                            console.log(json);
                            result = json;
                        })
                        .then(() => {
                            console.log(result);
                            alert(result.label);
                        })
                        .catch(error => console.error(error));
                    `
                });
            });
            console.log("Menu item clicked!");
        }
    }
});
