const BASE_URL = 'http://localhost:8000';

chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: "extractText",
        title: "Verify with NewsFul",
        contexts: ["all"]
    });
});

// Function to create a popup window to show the results
const createPopup = async () => {
    const window = await chrome.windows.create({
        url: "./popup.html",
        type: "popup",
        width: 600,
        height: 600,
        focused: true
    });
    await chrome.windows.update(window.id, { focused: true });
};

const handleApiRequest = async (endpoint, data) => {
    try {
        const response = await fetch(`${BASE_URL}/verify/${endpoint}`, {
            method: 'POST',
            body: JSON.stringify(data),
            headers: {
                'Content-type': 'application/json; charset=UTF-8',
            },
        });
        const json = await response.json();
        chrome.runtime.sendMessage({ action: "displayResponse", data: json });
    } catch (error) {
        console.error('API request failed:', error);
        chrome.runtime.sendMessage({ action: "displayError", error: error.message });
    }
};

// Function to store user responses
const storeResponse = async (data) => {
    const result = await chrome.storage.local.get("searches");
    const searches = result.searches || [];
    searches.push(data);
    await chrome.storage.local.set({ searches });
};

// Listen for messages from content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "verifyImage" || message.action === "verifyText") {
        createPopup();
        handleApiRequest(message.action === "verifyImage" ? "image" : "text", message.data);
    } else if (message.action === "storeResponse") {
        storeResponse(message.data);
    }
});

// Listen for the click event on the menu item
chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "extractText") {
        const isImage = info?.mediaType === "image";
        const code = isImage
            ? `chrome.runtime.sendMessage({
                action: "verifyImage",
                data: {
                    picture_url: "${info.srcUrl}",
                    url: window.location.href
                }
            });`
            : `chrome.runtime.sendMessage({
                action: "verifyText",
                data: {
                    content: window.getSelection().toString(),
                    url: window.location.href
                }
            });`;

        chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: new Function(code)
        });
    }
});
