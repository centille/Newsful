
function handlePopupMessage(message, sender, sendResponse) {
    if (message.action === "showPopup") {
        const resultDiv = document.getElementById('result');
        if (message.error) {
            resultDiv.textContent = `Error: ${message.error}`;
        } else {
            resultDiv.textContent = JSON.stringify(message.result, null, 2);
        }
    }
}
chrome.runtime.onMessage.addListener(handlePopupMessage);
