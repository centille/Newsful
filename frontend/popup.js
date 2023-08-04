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
            let data = message.data;
            console.log(data.references);

            // Use Tailwind CSS to style the popup
            let result_display = `
            <div class="flex my-4">
                <div class="text-md font-bold w-1/2 block mx-1">
                    <div class="bg-blue-400 w-full text-center py-2 text-white rounded">
                        State of News
                    </div>
                    <div class="text-md px-2">
                        ${data.label}
                    </div>
                </div>
                <div class="text-md font-bold w-1/2 block mx-1">
                    <div class="bg-blue-400 w-full text-center py-2 text-white rounded">
                        Confidence
                    </div>
                    <div class="text-md px-2 flex-wrap">
                        ${data.confidence}
                    </div>
                </div>
            </div>
            <div class="flex my-3">
                <div class="text-md font-bold w-1/2 block mx-1">
                    <div class="bg-blue-400 w-full text-center py-2 text-white rounded">
                        Phishing
                    </div>
                    <div class="text-md px-2">
                        ${data.isPhishing?"YES":"NO"}
                    </div>
                </div>
                <div class="text-md font-bold w-1/2 block mx-1">
                    <div class="bg-blue-400 w-full text-center py-2 text-white rounded">
                        Credible
                    </div>
                    <div class="text-md px-2 flex-wrap">
                        ${data.isCredible?"YES":"NO"}
                    </div>
                </div>
            </div>
            <div class="text-md font-bold block mx-1">
                <div class="bg-blue-400 w-full text-center py-2 text-white rounded">
                    Archive URL
                </div>
                <div class="text-md px-2">
                    ${data.archiveUrl}
                </div>
            </div>
            <div class="text-md font-bold block mx-1">
                <div class="bg-blue-400 w-full text-center py-2 text-white rounded">
                    References
                </div>
                <ol class="text-md px-2">
                        ${
                            data.references.map((ref)=>{
                                return "<li class='text-md px-2'>" + ref + "</li>"
                            })
                        }
                </ol>
            </div>
            `;
            ele.innerHTML = result_display;
        }
    }
);
