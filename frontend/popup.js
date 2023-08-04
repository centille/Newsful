// Display the response to the popup window
chrome.runtime.onMessage.addListener(
    function (message, sender, sendResponse) {
        if (message.action === "displayResponse") {
            const loading = document.getElementById("loading");

            if (loading && loading.parentNode) {
                loading.parentNode.removeChild(loading);
            }

            let ele = document.getElementById("result");

            console.log(message.data.references);

            let links = message.data.references.map((ref, index) => `${index + 1}) <a href="${ref}">${ref}</a>`);
            let data = message.data;
            let result_display = `<b>State of News :</b><br> ${data.label}<br><b>Response :</b><br> ${data.response}<br><b>Archived URL: </b>${data.archive}<br><b>Confidence :</b><br> ${data.confidence}<br><b>References :</b><br>${links.join("<br>")}<br><b>Credible:</b> ${data.isCredible}`;
            ele.innerHTML = result_display;
        }
    }
);
