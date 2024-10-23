
function handlePopupMessage(message, sender, sendResponse) {
    const resultDiv = document.getElementById('result');
    if (message.action === "showPopup") {
        // clear everything in resultDiv
        resultDiv.innerHTML = '';
        if (message.error) {
            resultDiv.textContent = `Error: ${message.error}`;
        } else {
            // label
            labelContainer = document.appendChild("div");
            labelContainerHeader = labelContainer.appendChild("div");
            labelContainerHeader.classList.append("label");
            labelContainerHeader.textContent = "Label: ";
            labelContainerContent = labelContainer.appendChild("div");
            labelContainerContent.classList.append("content");
            labelContainerContent.textContent = message.result.label;

            // response
            responseContainer = document.appendChild("div");
            responseContainerHeader = responseContainer.appendChild("div");
            responseContainerHeader.classList.append("label");
            responseContainerHeader.textContent = "Response: ";
            responseContainerContent = responseContainer.appendChild("div");
            responseContainerContent.classList.append("content");
            responseContainerContent.textContent = message.result.response;

            // isSafe
            isSafeContainer = document.appendChild("div");
            isSafeContainerHeader = isSafeContainer.appendChild("div");
            isSafeContainerHeader.classList.append("label");
            isSafeContainerHeader.textContent = "Is Safe: ";
            isSafeContainerContent = isSafeContainer.appendChild("div");
            isSafeContainerContent.classList.append("content");
            isSafeContainerContent.textContent = message.result.isSafe;

            // archive
            archiveContainer = document.appendChild("div");
            archiveContainerHeader = archiveContainer.appendChild("div");
            archiveContainerHeader.classList.append("label");
            archiveContainerHeader.textContent = "Archive: ";
            archiveContainerContent = archiveContainer.appendChild("div");
            archiveContainerContent.classList.append("content");
            archiveContainerContent.textContent = message.result.archive || "None";

            // references
            referencesContainer = document.appendChild("div");
            referencesContainerHeader = referencesContainer.appendChild("div");
            referencesContainerHeader.classList.append("label");
            referencesContainerHeader.textContent = "References: ";
            referencesContainerContent = referencesContainer.appendChild("div");
            referencesContainerContent.classList.append("content");
            referencesContainerContent.textContent = message.result.references;
        }
    }
}
browser.runtime.onMessage.addListener(handlePopupMessage);
