document.addEventListener("DOMContentLoaded", async () => {
    try {
        // summary API を取得
        const res = await fetch("/api/dashboard/summary");
        const data = await res.json();
        displaySummary(data.summary);

        // graphs
        const gres = await fetch("/api/dashboard/graphs");
        const gdata = await gres.json();
        //displayGraphs(gdata.graphs);
        const figJson = gdata.graphs["assets"];
        displaySingleGraph(figJson, "🤑 総資産推移");

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
        //summaryDiv.style.marginTop = "60vh";
        summaryDiv.style.fontSize = "2vh";
        sidebar.appendChild(summaryDiv);
    }

    summaryDiv.innerHTML = `
        <hr>
        <div class="summary-grid">
            <div>最新日:</div><div>${summary.latest_date}</div>
            <div>総資産:</div><div>${summary.total_assets.toLocaleString()} 円</div>
            <div>目標資産:</div><div>${summary.total_target_assets.toLocaleString()} 円</div>
            <div>総リターン:</div><div>${summary.total_returns.toLocaleString()} 円</div>
            <div>目標リターン:</div><div>${summary.total_target_returns.toLocaleString()} 円</div>
        </div>
    `;
}

// 単体グラフを .main に表示
function displaySingleGraph(figJson, titleText) {
    const main = document.getElementById("graphs-area");
    if (!main || !figJson) return;

    main.innerHTML = ""; // 既存内容クリア

    const wrap = document.createElement("div");
    wrap.className = "graph-container";

    // タイトル
    const title = document.createElement("div");
    title.className = "graph-title";
    title.textContent = titleText;
    wrap.appendChild(title);

    // Plotly グラフ本体
    const graphDiv = document.createElement("div");
    wrap.appendChild(graphDiv);

    const fig = typeof figJson === "string" ? JSON.parse(figJson) : figJson;
    
    Plotly.newPlot(graphDiv, fig.data, fig.layout,{responsive: true});

    main.appendChild(wrap);
}