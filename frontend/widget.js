document.addEventListener("DOMContentLoaded", function () {
    // Call your function to fetch and display the data
    fetchSearches();
});

const fetchSearches = () => {
    chrome.storage.local.get(["searches"], function (result) {
        console.log(1);
        console.log(result.searches);
        if (result.hasOwnProperty("searches")) {
            console.log(2);
            let searches = result.searches;
            let display = searches.map((data) => {
                return `<p>${data}</p>`
            })
            let ele = document.getElementById("searches");
            ele.innerHTML = display;
        }
    });
}
