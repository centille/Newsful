// function printText() {
//   console.log("test");
//   chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
//     console.log("test");
//     chrome.tabs.executeScript(tabs[0].id, {
//       code: `var crap = {content: document.body.innerText, url: window.location.href};
//       fetch('http://localhost:8000/test', {
//           method: 'GET',
//           body: JSON.stringify(crap),
//           headers: {
//             'Content-type': 'application/json; charset=UTF-8',
//           },
//         })
//         .then(response => response.json())
//         .catch(error => console.error(error))`
//     });
//   });
// }

// document.getElementById("extract").onclick = printText;


chrome.contextMenus.onClicked.addListener(function (info, tab) {
  if (info.menuItemId === "extractText") {
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
      chrome.tabs.executeScript(tabs[0].id, {
        code: `var crap = {content: window.getSelection().toString(), url:  window.location.href};
        console.log(crap);
        var result;
        fetch('http://localhost:8000/api/verify', {
                  method: 'POST',
                  body: JSON.stringify(crap),
                  headers: {
                    'Content-type': 'application/json; charset=UTF-8',
                  },
                })
                .then(response => response.json())
                .then(json => {console.log(json); result = json;})
                .then(() => {console.log(result); alert(result.label);})
                .catch(error => console.error(error));`
      });
    });
    console.log("Menu item clicked!");
  }
});
