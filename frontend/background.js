// Create a menu Item in the right click context menu of the browser
chrome.contextMenus.create({
    id: "extractText",
    title: "Verify with NewsFul",
    contexts: ["all"]
});

// Function to create a popup window to show the results
const create_popup = () => {
    chrome.windows.create({
        url: "./popup.html",
        type: "popup",
        width: 600,
        height: 600,
        focused: true
    }, function (window) {
        // Shift focus to the popup window
        chrome.windows.update(window.id, { focused: true });
    });
}

// Listen for the verifyImage and verifyText messages from the content script
chrome.runtime.onMessage.addListener(
    function (message, sender, sendResponse) {
        // Call the function to create the popup page and shift focus to it
        create_popup();

        // If the selected data is an image
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
        // If the selected data is text
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
        // Store the responses of the user to display in the widget
        else if (message.action === "storeResponse") {
            chrome.runtime.sendMessage({ action: "check", data: { test: "test" } });
            chrome.storage.local.get(["searches"], function (result) {
                if (result.hasOwnProperty("searches")) {
                    const existing = result.searches;
                    existing.push(message.data);
                    chrome.storage.local.set({ searches: existing });
                } else {
                    const fresh = [];
                    fresh.push(message.data);
                    chrome.storage.local.set({ searches: fresh });
                }
            });
        }
    }
);

// Listen for the click event on the menu item
chrome.contextMenus.onClicked.addListener(function (info, tab) {
    if (info.menuItemId === "extractText") {
        // If the selected data is an image, extract the image url and send the message to the content script
        if (info?.mediaType && info?.mediaType === "image") {
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
        // If the selected data is text, extract the text and send the message to the content script
        else {
            chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
                chrome.tabs.executeScript(tabs[0].id, {
                    code: `
                    var dt = {
                        content: window.getSelection().toString(),
                        url: window.location.href
                    };

                    chrome.runtime.sendMessage({ action: "verifyText", data: dt });
                    `
                });
            });
        }
    }
});
