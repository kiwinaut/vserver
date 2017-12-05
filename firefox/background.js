browser.contextMenus.create({
    id: "vip",
    title: "VIP",
    contexts: ["link"],
});
browser.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "vip") {
        const safeUrl = 'http://localhost:8000/page/' + encodeURIComponent(info.linkUrl);
        console.log(safeUrl)
        var creating = browser.tabs.create({
		  url:safeUrl
        });
    }
});

function escapeHTML(str) {
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/"/g, "&quot;").replace(/'/g, "&#39;")
        .replace(/</g, "&lt;").replace(/>/g, "&gt;");
}