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

            let result_display = `<b>State of News :</b><br> ${message.data.label}<br><b>Response :</b><br> ${message.data.response}<br><b>Confidence :</b><br> ${message.data.confidence}<br><b>References :</b><br>${links.join("<br>")}`;
            ele.innerHTML = result_display;
        }
    }
);
