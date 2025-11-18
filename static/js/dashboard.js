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

document.addEventListener("DOMContentLoaded", async () => {
    try {
        // summary 読み込み
        const sres = await fetch("/api/dashboard/summary");
        const sdata = await sres.json();
        displaySummary(sdata.summary);

        // graphs 読み込み
        const gres = await fetch("/api/dashboard/graphs");
        const gdata = await gres.json();
        displayGraphs(gdata.graphs);

    } catch (err) {
        console.error("Dashboard load error:", err);
    }
});


// 6 グラフを .main に表示
function displayGraphs(graphs) {
    const main = document.getElementById("graphs-area");
    if (!main || !graphs) return;

    main.innerHTML = ""; // 一旦クリア

    // graphs は { key: json, ... } の形
    Object.entries(graphs).forEach(([key, figJson]) => {

        const wrap = document.createElement("div");
        wrap.className = "graph-container";

        // タイトル（key を見やすい日本語に変換したいならここで mapping）
        const title = document.createElement("div");
        title.className = "graph-title";
        title.textContent = getGraphTitle(key);
        wrap.appendChild(title);

        // Plotly グラフ本体
        const graphDiv = document.createElement("div");
        wrap.appendChild(graphDiv);

        // Plotly 描画
        const fig = JSON.parse(figJson);
        Plotly.newPlot(graphDiv, fig.data, fig.layout);

        main.appendChild(wrap);
    });
}


// Graph 名を人間用に変換
function getGraphTitle(key) {
    const titles = {
        assets: "🤑 総資産推移",
        returns: "🤑 トータルリターン",
        general_income_expenditure: "🤑 一般収入・支出",
        general_balance: "🤑 一般収支",
        special_income_expenditure: "🤑 特別収入・支出",
        special_balance: "🤑 特別収支"
    };
    return titles[key] || key;
}

