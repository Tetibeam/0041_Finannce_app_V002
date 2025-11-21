async function main() {
    const status = document.getElementById('status');
    const updateStatus = (msg) => {
        status.innerHTML = `<div class="spinner"></div><span>${msg}</span>`;
    };

    try {
        // 1. Pyodideのロード
        updateStatus("Loading Python Environment...");
        let pyodide = await loadPyodide();
        
        // 2. 必要なパッケージのロード
        updateStatus("Loading Pandas...");
        await pyodide.loadPackage("pandas");

        // 3. DBファイルのダウンロードとマウント
        updateStatus("Downloading Secure Data...");
        const response = await fetch('/static/db/summary.db');
        if (!response.ok) throw new Error("Failed to download summary.db");
        const dbBuffer = await response.arrayBuffer();
        pyodide.FS.writeFile('/summary.db', new Uint8Array(dbBuffer));

        // 4. Pythonスクリプトの実行
        updateStatus("Analyzing Data...");
        const pythonScript = await (await fetch('/static/py/client_app.py')).text();
        
        // Pythonを実行し、結果(JSON文字列)を受け取る
        const resultJson = await pyodide.runPythonAsync(pythonScript);
        const data = JSON.parse(resultJson);

        if (data.error) {
            throw new Error(data.error);
        }

        // 5. グラフ描画
        updateStatus("Rendering Chart...");
        
        const layout = {
            title: {
                text: 'Total Assets Over Time',
                font: { color: '#f8fafc' }
            },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            xaxis: {
                gridcolor: 'rgba(255,255,255,0.1)',
                tickfont: { color: '#94a3b8' }
            },
            yaxis: {
                gridcolor: 'rgba(255,255,255,0.1)',
                tickfont: { color: '#94a3b8' }
            },
            margin: { t: 40, r: 20, l: 40, b: 40 }
        };

        const config = { responsive: true };

        Plotly.newPlot('chart-container', [data], layout, config);
        
        // 完了表示
        status.style.display = 'none';

    } catch (err) {
        console.error(err);
        status.innerHTML = `<span style="color: #ef4444;">Error: ${err.message}</span>`;
        status.style.borderColor = '#ef4444';
        status.style.background = 'rgba(239, 68, 68, 0.1)';
    }
}

main();
