
const fetchSearches = () => {
    chrome.storage.local.get(["searches"], function (result) {
        const searchesElement = document.getElementById("searches");
        if (result.searches && result.searches.length > 0) {
            const searchesHTML = result.searches.map((data) => `
                <div class="bg-white shadow-md rounded-lg p-4 mb-4">
                    <p class="font-bold">${data.url}</p>
                    <p>${data.summary}</p>
                    <p class="text-sm text-gray-500 mt-2">Label: ${String(data.label).toUpperCase()}</p>
                </div>
            `).join('');
            searchesElement.innerHTML = searchesHTML;
        } else {
            searchesElement.innerHTML = '<p class="text-center">No searches found.</p>';
        }
    });
};

document.addEventListener("DOMContentLoaded", fetchSearches);
