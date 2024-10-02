// Function to create HTML for references
const createReferencesHTML = (references) => {
    return references.map((ref, index) => `
        <li>
            <a class='large text-info l-lg-3' href='${ref}'>${ref}</a>
        </li>
    `).join('');
};

// Function to create HTML for boolean values
const createBooleanHTML = (value, positiveText, negativeText) => {
    const className = value ? 'text-success' : 'text-danger';
    const icon = value ?
        "https://clipart-library.com/new_gallery/2-21271_icons8-flat-checkmark-check-mark-thin-green.png" :
        "https://freepngimg.com/thumb/red_cross/28029-3-red-cross-file.png";
    const text = value ? positiveText : negativeText;
    return `
        <p class='large ${className} l-lg-3'>
            <img src='${icon}' alt='${text}' style='width: 15px; height: 15px;'> ${text}
        </p>
    `;
};

// Function to generate result display HTML
const generateResultHTML = (data) => {
    return `
        <section class="h-100 h-custom" style="background-color: #eee">
            <div class="container py-5 h-100">
                <div class="row d-flex justify-content-center align-items-center h-100">
                    <div class="col-lg-8 col-xl-6">
                        <div class="card border-top border-bottom border-3" style="border-color: #1da1f2 !important">
                            <div class="card-body p-5">
                                <div class="text-center">
                                    <div style="background-color: #1da1f2; padding: 10px;">
                                        <h3 class="mx-lg-5 px-5" style="color: #f2f2f2;">Newsful Report</h3>
                                    </div>
                                </div>
                                <br /><br />
                                <div class="row">
                                    <div class="col mb-2">
                                        <p class="py-1 font-weight-bold" style="color:#1da1f2">Label</p>
                                        ${createBooleanHTML(data.label, "TRUE", "FAKE")}
                                    </div>
                                    <div class="col mb-2">
                                        <p class="py-1 font-weight-bold" style="color:#1da1f2">Confidence</p>
                                        <p class="large text-success l-lg-3">${data.confidence}%</p>
                                    </div>
                                </div>
                                <div class="mx-n5 px-5 py-1" style="background-color: #ffffff">
                                    <div class="row">
                                        <div class="col-md-8 col-md-4">
                                            <p class="py-1 font-weight-bold" style="color:#1da1f2">Response</p>
                                        </div>
                                        <div class="col-md-4 col-lg-12">
                                            <p>${data.response}</p>
                                        </div>
                                    </div>
                                    <div>
                                        <p class="py-1 font-weight-bold" style="color:#1da1f2">Archive</p>
                                        <p>
                                            <a class="large text-info l-lg-3" href="${data.archive}">${data.archive}</a>
                                        </p>
                                    </div>
                                    <div class="mx-n5 px-5 py-1" style="background-color: #ffffff">
                                        <div class="row">
                                            <div class="col-md-8 col-md-4">
                                                <p class="py-1 font-weight-bold" style="color:#1da1f2">References</p>
                                            </div>
                                            <div class="col-md-4 mb-0 col-lg-12">
                                                <ol>
                                                    ${createReferencesHTML(data.references)}
                                                </ol>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col mb-2">
                                            <p class="py-1 font-weight-bold" style="color:#1da1f2">Phishing Detection</p>
                                            ${createBooleanHTML(data.isPhishing, "YES", "NO")}
                                        </div>
                                        <div class="col mb-2">
                                            <p class="py-1 font-weight-bold" style="color:#1da1f2">Credibility</p>
                                            ${createBooleanHTML(data.isCredible, "YES", "NO")}
                                        </div>
                                    </div>
                                    <div class="text-center pt-4">
                                        <a class="list-inline-item align-items-end" href="${download(data)}" download="NewsFul_Report">
                                            <button type="button" class="btn text-white" style="background-color:#1da1f2">Download Report</button>
                                        </a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    `;
};

// Function to download report
const download = (jsonData) => {
    const formattedString = `
URL:
    ${jsonData.url}

Label:
    ${jsonData.label}

Authenticity:
    ${jsonData.confidence}%

Archive:
    ${jsonData.archive}

Summary:
    ${jsonData.summary}

Response:
    ${jsonData.response}

Data Type:
    ${jsonData.dataType}

References:
  - ${jsonData.references.join("\n  - ")}

Is Phishing:
    ${jsonData.isPhishing ? "YES" : "NO"}

Is Credible:
    ${jsonData.isCredible ? "YES" : "NO"}

Updated At:
    ${new Date(jsonData.updatedAt * 1000).toLocaleString()}
    `;

    const blob = new Blob([formattedString], { type: "text/plain" });
    return URL.createObjectURL(blob);
};

// Listen for messages
chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
    if (message.action === "displayResponse") {
        const loading = document.getElementById("loading");
        if (loading && loading.parentNode) {
            loading.parentNode.removeChild(loading);
        }

        const ele = document.getElementById("result");
        if (ele) {
            ele.innerHTML = generateResultHTML(message.data);
        }

        chrome.runtime.sendMessage({ action: "storeResponse", data: message.data });
    }
});

// Utility function (unused in the optimized version, but kept for potential future use)
function generateRandomNonce(length) {
    const charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    return Array.from({ length }, () => charset[Math.floor(Math.random() * charset.length)]).join('');
}
