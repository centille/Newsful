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
            <div>
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
                        <a class="list-inline-item align-items-center">
                          <blockquote class="blockquote text-center">
                            <h3
                              class="mx-lg-5 px-5"
                              style="align-items: center; color: #1d64f2"
                            >
                              Newsful Report
                            </h3>
                          </blockquote>
                        </a>
                        <br /><br />
                        <div class="row">
                          <div class="col mb-2">
                            <a class="list-inline-item align-items-end">
                              <p
                                class="py-1 px-3 rounded text-white"
                                style="background-color: #1da1f2"
                              >
                                Label
                              </p>
                            </a>
                            <p class="large text-success l-lg-3">
                            ${data.label}
                            </p>
                          </div>
                          <div class="col mb-2">
                            <a class="list-inline-item align-items-end">
                              <p
                                class="py-1 px-3 rounded text-white"
                                style="background-color: #1da1f2"
                              >
                                Confidence
                              </p>
                            </a>
                            <p class="large text-success l-lg-3">${data.confidence
            }</p>
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
                                  class="py-1 px-3 rounded text-white"
                                  style="background-color: #1da1f2"
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
                                class="py-1 px-3 rounded text-white"
                                style="background-color: #1da1f2"
                              >
                                Archive
                              </p>
                            </a>
                            <p>
                              <a class="large text-info l-lg-3" href="${data.archive
            }"
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
                                    class="py-1 px-3 rounded text-white"
                                    style="background-color: #1da1f2"
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
                                class="py-1 px-3 rounded text-white"
                                style="background-color: #1da1f2"
                            >
                                Phishing Detection
                            </p>
                        </a>
                        <p class="large text-danger l-lg-3">${data.isPhishing ? "YES" : "NO"}</p>
                    </div>
                    <div class="col mb-2">
                        <a class="list-inline-item align-items-end">
                            <p
                                class="py-1 px-3 rounded text-white"
                                style="background-color: #1da1f2"
                            >
                                Credibility
                            </p>
                        </a>
                        <p class="large text-danger l-lg-3">${data.isCredible ? "YES" : "NO"}</p>
                    </div>
                </div>
                        </div >
                      </div >
                    </div >
                  </div >
                </div >
              </div >
            </section >
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
          </div > `;
        ele.innerHTML = result_display;
        chrome.runtime.sendMessage({ action: "storeResponse", data: json });
        alert("sent");
    }
    else if (message.action === "check") {
        alert("test");
    }
});
