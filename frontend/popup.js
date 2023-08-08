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
chrome.runtime.onMessage.addListener(function (message, sender, sendResponse) {
    if (message.action === "displayResponse") {
        const loading = document.getElementById("loading");
        if (loading && loading.parentNode) {
            loading.parentNode.removeChild(loading);
        }

        let ele = document.getElementById("result");
        let data = message.data;

        // Use Tailwind CSS to style the popup
        let result_display = `
            <section class="h-100 h-custom" style="background-color: #eee">
              <div class="container py-5 h-100">
                <div
                  class="row d-flex justify-content-center align-items-center h-100"
                >
                  <div class="col-lg-8 col-xl-6">
                    <div
                      class="card border-top border-bottom border-3"
                      style="border-color: #1da1f2 !important"
                    >
                      <div class="card-body p-5">
                        <div class="text-center">
                        <div style="background-color: #1da1f2; padding: 10px;">
                            <h3 class="mx-lg-5 px-5" style="color: #f2f2f2;">Newsful Report</h3>
                          </div>
                        </div>
                        </a>
                        <br /><br />
                        <div class="row">
                          <div class="col mb-2">
                            <a class="list-inline-item align-items-end">
                              <p
                                class="py-1 font-weight-bold"
                                style="color:#1da1f2"
                              >
                                Label
                              </p>
                            </a>
                            ${data.label ? "<p class='large text-success l-lg-3'> TRUE</p>" : "<p class='large text-danger l-lg-3'> FAKE</p>"}
                          </div>
                          <div class="col mb-2">
                            <a class="list-inline-item align-items-end">
                              <p
                              class="py-1 font-weight-bold"
                              style="color:#1da1f2"
                              >
                                Confidence
                              </p>
                            </a>
                            <p class="large text-success l-lg-3">${data.confidence}%</p>
                          </div>
                        </div>
                        <div
                          class="mx-n5 px-5 py-1"
                          style="background-color: #ffffff"
                        >
                          <div class="row">
                            <div class="col-md-8 col-md-4">
                              <a class="list-inline-item align-items-end">
                                <p
                                class="py-1 font-weight-bold"
                                style="color:#1da1f2"
                                >
                                  Response
                                </p>
                              </a>
                            </div>
                            <div class="col-md-4 col-lg-12">
                              <p>${data.response}</p>
                            </div>
                          </div>
                          <div>
                            <a class="list-inline-item align-items-end">
                              <p
                              class="py-1 font-weight-bold"
                              style="color:#1da1f2"
                              >
                                Archive
                              </p>
                            </a>
                            <p>
                              <a class="large text-info l-lg-3" href="${data.archive}"
                                >${data.archive}</a
                              >
                            </p>
                          </div>
                          <div
                            class="mx-n5 px-5 py-1"
                            style="background-color: #ffffff"
                          >
                            <div class="row">
                              <div class="col-md-8 col-md-4">
                                <a class="list-inline-item align-items-end">
                                  <p
                                  class="py-1 font-weight-bold"
                                  style="color:#1da1f2"
                                  >
                                    References
                                  </p>
                                </a>
                              </div>
                              <div class="col-md-4 mb-0 col-lg-12">
                                <ol>
                                    <li>
                                        <a class='large text-info l-lg-3' href=${data.references[0]}>${data.references[0]}</a>
                                    </li>
                                    <li>
                                        <a class='large text-info l-lg-3' href=${data.references[1]}>${data.references[1]}</a>
                                    </li>
                                    <li>
                                        <a class='large text-info l-lg-3' href=${data.references[2]}>${data.references[2]}</a>
                                    </li>
                                    <li>
                                        <a class='large text-info l-lg-3' href=${data.references[3]}>${data.references[3]}</a>
                                    </li>
                                    <li>
                                        <a class='large text-info l-lg-3' href=${data.references[4]}>${data.references[4]}</a>
                                    </li>
                                </ol>
                              </div >
                            </div >
                          </div >
                <div class="row">
                    <div class="col mb-2">
                        <a class="list-inline-item align-items-end">
                            <p
                            class="py-1 font-weight-bold"
                            style="color:#1da1f2"
                            >
                                Phishing Detection
                            </p>
                        </a>
                        ${data.isPhishing ? "<p class='large text-danger l-lg-3'><img src='https://www.nicepng.com/png/detail/47-479473_red-check-mark-png-clip-freeuse-library-red.png' alt='Green Tick' style='width: 15px; height: 15px; color: rgb(17, 224, 17);'> YES</p>" : "<p class='large text-success l-lg-3'><img src='https://www.seekpng.com/png/detail/442-4423412_x-mark-multiplications-sign.png' alt='Green Cross' style='width: 15px; height: 15px; color: rgb(17, 224, 17);'>  NO</p>"}
                    </div>
                    <div class="col mb-2">
                        <a class="list-inline-item align-items-end">
                            <p
                            class="py-1 font-weight-bold"
                            style="color:#1da1f2"
                            >
                                Credibility
                            </p>
                        </a>
                        ${data.isCredible ? "<p class='large text-success l-lg-3'><img src='https://clipart-library.com/new_gallery/2-21271_icons8-flat-checkmark-check-mark-thin-green.png' alt='Green Tick' style='width: 15px; height: 15px; color: rgb(17, 224, 17);'>  YES</p>" : "<p class='large text-danger l-lg-3'><img src='https://freepngimg.com/thumb/red_cross/28029-3-red-cross-file.png' alt='Red Cross' style='width: 15px; height: 15px; color: rgb(17, 224, 17);'>  NO</p>"}
                    </div>
                    </div>
                    <div class="text-center pt-4">
                        <a class="list-inline-item align-items-end" href="${download(data)}" download="NewsFul_Report">
                            <button type="button" class="btn text-white" style="background-color:#1da1f2">Download Report</button>
                        </a>
                    </div>
                        </div >
                      </div >
                    </div >
                  </div >
                </div >
              </div >
              <script
              src="https://code.jquery.com/jquery-3.3.1.slim.min.js"
              integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo"
              crossorigin="anonymous"
          ></script>
          <script
              src="https://cdn.jsdelivr.net/npm/popper.js@1.14.7/dist/umd/popper.min.js"
              integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1"
              crossorigin="anonymous"
          ></script>
          <script
              src="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/js/bootstrap.min.js"
              integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM"
              crossorigin="anonymous"
          ></script>
            </section > `;

        // download(data);
        ele.innerHTML = result_display;
        chrome.runtime.sendMessage({ action: "storeResponse", data: json });
        alert("sent");
    }
    else if (message.action === "check") {
        alert("test");
    }
});

const download = async (jsonData) => {
    const formattedString =
        `URL:
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

    let blob = new Blob([formattedString], { type: "text/plain" });

    return URL.createObjectURL(blob);

    // const pdfBlob = await generatePDF(formattedString);

    // return URL.createObjectURL(pdfBlob);
    // const pdf = new jsPDF();
    // pdf.text(formattedString, 10, 10);

    // const pdfBlob = pdf.output("blob");

    // return URL.createObjectURL(pdfBlob);
}


function generateRandomNonce(length) {
    const charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    let result = "";

    for (let i = 0; i < length; i++) {
        const randomIndex = Math.floor(Math.random() * charset.length);
        result += charset.charAt(randomIndex);
    }

    return result;
}
