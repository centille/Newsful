// type Message = {
//     url: string;
//     archive: string;
//     summary: string;
//     response: string;
//     label: Boolean;
//     confidence: number;
//     references: string[];
//     isCredible: Boolean;
//     isPhishing: Boolean;
// }

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

            let data = message.data;
            // Use Tailwind CSS to style the popup
            let result_display = `
            <div class="text-2xl font-bold mb-2">
                <b style="color: #3B82F6;">
                    State of News:
                </b>
                <span> ${data.label}</span>
            </div>
            <div class="text-xl font-bold mb-2">
                <b style="color: #3B82F6;">
                    Response:
                </b>
                <span> ${data.response}</span>
            </div>
            <div class="text-xl font-bold mb-2">
                <b style="color: #3B82F6;">
                    Archived URL:
                </b>
                <span>${data.archive}</span>
            </div>
            <div class="text-xl font-bold mb-2">
                <b style="color: #3B82F6;">
                    Confidence:
                </b>
                <span> ${data.confidence}</span>
            </div>
            <div class="text-xl font-bold mb-2">
                <b style="color: #3B82F6;">
                    References:
                </b>
                <ul class="list-disc list-inside">
                ${data.references.map((ref) => `<li><a href="${ref}">${ref}</a></li>`).join()}
                </ul>
            </div>
            <div class="text-xl font-bold mb-2">
                <b style="color: #3B82F6;">
                    Credible:
                </b>
                <span>${data.isCredible}</span>
            </div>
            `;
            ele.innerHTML = result_display;
        }
    }
);
