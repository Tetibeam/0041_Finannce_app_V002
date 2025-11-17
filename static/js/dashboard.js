document.addEventListener("DOMContentLoaded", async () => {
    try {
        // summary API を取得
        const res = await fetch("/api/dashboard/summary");
        const data = await res.json();
        displaySummary(data.summary);
    } catch (err) {
        console.error("Failed to load dashboard summary:", err);
    }
});

// サイドバー下に summary を表示
function displaySummary(summary) {
    const sidebar = document.querySelector(".sidebar");

    if (!sidebar || !summary) return;

    // 既存の div がある場合はクリア
    let summaryDiv = document.getElementById("dashboard-summary");
    if (!summaryDiv) {
        summaryDiv = document.createElement("div");
        summaryDiv.id = "dashboard-summary";
        summaryDiv.style.marginTop = "2vh";
        summaryDiv.style.fontSize = "2vh";
        sidebar.appendChild(summaryDiv);
    }

    summaryDiv.innerHTML = `
        <hr>
        <div>最新日: ${summary.latest_date}</div>
        <div>総資産: ${Math.floor(summary.total_assets).toLocaleString()} 円</div>
        <div>目標資産: ${Math.floor(summary.total_target_assets).toLocaleString()} 円</div>
        <div>総リターン: ${Math.floor(summary.total_returns).toLocaleString()} 円</div>
        <div>目標リターン: ${Math.floor(summary.total_target_returns).toLocaleString()} 円</div>
    `;
}
