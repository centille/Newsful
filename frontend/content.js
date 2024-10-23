chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "getSelectedText") {
        sendResponse({ selectedText: window.getSelection().toString() });
    }
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "verifySelectedText") {
        const selectedText = window.getSelection().toString();
        if (selectedText) {
            chrome.runtime.sendMessage({
                action: "verifyText",
                url: window.location.href,
                content: selectedText
            });
        }
    }
});
