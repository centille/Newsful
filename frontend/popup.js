const printText = () => {
    console.log("test");
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
        console.log("test");
        chrome.tabs.executeScript(tabs[0].id, {
            code: `var crap = {content: document.body.innerText, url:  window.location.href}; fetch('http://localhost:8000/test', {
                method: 'POST',
                body: JSON.stringify(crap),
                headers: {
                  'Content-type': 'application/json; charset=UTF-8',
                },
              })
              .then(response => response.json())
              .then(json => console.log(json))
              .catch(error => console.error(error));`
        });
    });
}

document.getElementById("extract").onclick = printText;