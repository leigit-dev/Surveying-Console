<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>加速度监测 · 原始 & 投影</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        :root {
            --bg-primary: #0b0e1a;
            --bg-card: #141a2b;
            --text-primary: #e8edf5;
            --text-secondary: #8a9bb5;
            --accent-cyan: #00d4ff;
            --accent-green: #00e676;
            --accent-purple: #7c4dff;
            --accent-orange: #ff9100;
            --accent-pink: #ff4081;
            --accent-yellow: #ffea00;
            --radius: 18px;
            --safe-top: env(safe-area-inset-top, 12px);
            --safe-bottom: env(safe-area-inset-bottom, 12px);
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            padding: var(--safe-top) 12px var(--safe-bottom) 12px;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .app-scroll { flex:1; overflow-y:auto; display:flex; flex-direction:column; gap:14px; padding-bottom:8px; -webkit-overflow-scrolling:touch; }
        .card { background:var(--bg-card); border-radius:var(--radius); padding:16px 18px; border:1px solid rgba(255,255,255,0.04); backdrop-filter:blur(2px); }
        .card-title { font-size:13px; font-weight:600; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.6px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center; }
        .header-card { padding:14px 18px; background:linear-gradient(145deg,#141a2b,#0f1422); }
        .header-row { display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:6px; }
        .app-title { font-size:20px; font-weight:700; background:linear-gradient(135deg,var(--accent-cyan),var(--accent-purple)); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
        .app-title small { font-size:12px; -webkit-text-fill-color:var(--text-secondary); background:none; margin-left:6px; }
        .status-badge { display:flex; align-items:center; gap:8px; font-size:12px; color:var(--text-secondary); background:rgba(255,255,255,0.04); padding:4px 12px 4px 8px; border-radius:30px; }
        .status-dot { width:8px; height:8px; border-radius:50%; background:#4a4a5a; transition:background 0.3s; }
        .status-dot.active { background:var(--accent-green); box-shadow:0 0 12px rgba(0,230,118,0.4); animation:pulse-dot 1.2s ease-in-out infinite; }
        .status-dot.calibrated { background:var(--accent-cyan); }
        @keyframes pulse-dot { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.6;transform:scale(0.85)} }

        .btn-group { display:flex; gap:8px; margin-top:12px; flex-wrap:wrap; }
        .btn { flex:1; min-width:50px; padding:10px 12px; border:none; border-radius:12px; font-size:14px; font-weight:600; color:#fff; background:rgba(255,255,255,0.06); transition:all 0.2s; cursor:pointer; touch-action:manipulation; display:flex; align-items:center; justify-content:center; gap:6px; }
        .btn:active { transform:scale(0.96); }
        .btn-primary { background:linear-gradient(135deg,var(--accent-cyan),#4a7cf7); box-shadow:0 4px 20px rgba(0,212,255,0.2); }
        .btn-primary.active { background:linear-gradient(135deg,var(--accent-orange),var(--accent-pink)); }
        .btn-secondary { background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.08); }
        .btn-calibrate { background:rgba(0,230,118,0.15); color:var(--accent-green); border:1px solid rgba(0,230,118,0.2); }
        .btn-calibrate.active { background:var(--accent-green); color:#000; }
        .btn-icon { font-size:16px; }

        .refresh-control { display:flex; align-items:center; gap:8px; font-size:12px; color:var(--text-secondary); }
        .refresh-control select { background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.1); color:#fff; padding:4px 8px; border-radius:8px; font-size:12px; }

        .data-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:8px; margin-top:2px; }
        .data-item { background:rgba(255,255,255,0.03); border-radius:12px; padding:8px 10px; text-align:center; border:1px solid rgba(255,255,255,0.04); }
        .data-item .label { font-size:9px; text-transform:uppercase; color:var(--text-secondary); font-weight:500; }
        .data-item .value { font-size:18px; font-weight:700; font-variant-numeric:tabular-nums; margin-top:2px; }
        .data-item .value.cyan { color:var(--accent-cyan); }
        .data-item .value.green { color:var(--accent-green); }
        .data-item .value.purple { color:var(--accent-purple); }
        .data-item .value.orange { color:var(--accent-orange); }
        .data-item .unit { font-size:9px; color:var(--text-secondary); margin-left:2px; }

        .wave-grid { display:flex; flex-direction:column; gap:8px; margin-top:4px; }
        .wave-row { display:flex; align-items:center; gap:8px; }
        .wave-row .axis-label { width:32px; font-size:12px; font-weight:700; color:var(--text-secondary); text-align:right; flex-shrink:0; }
        .wave-row .wave-container { flex:1; height:80px; background:rgba(0,0,0,0.3); border-radius:8px; overflow:hidden; position:relative; min-height:60px; }
        .wave-row .wave-container canvas { display:block; width:100%; height:100%; touch-action:none; }
        .wave-row .wave-container .wave-label { position:absolute; bottom:2px; right:6px; font-size:8px; color:rgba(255,255,255,0.2); pointer-events:none; }
        .wave-info { display:flex; justify-content:space-between; margin-top:4px; font-size:10px; color:var(--text-secondary); }

        .toast { position:fixed; bottom:30px; left:50%; transform:translateX(-50%); background:rgba(0,0,0,0.85); backdrop-filter:blur(12px); padding:12px 24px; border-radius:16px; font-size:14px; color:#fff; border:1px solid rgba(255,255,255,0.08); box-shadow:0 8px 40px rgba(0,0,0,0.5); z-index:999; opacity:0; transform:translateX(-50%) translateY(20px); transition:all 0.4s cubic-bezier(0.16,1,0.3,1); pointer-events:none; max-width:85%; text-align:center; }
        .toast.show { opacity:1; transform:translateX(-50%) translateY(0); }

        .flex-row { display:flex; align-items:center; gap:8px; flex-wrap:wrap; }
        .mt-1 { margin-top:6px; }
        .calib-info { font-size:11px; color:var(--text-secondary); margin-top:4px; display:flex; gap:16px; flex-wrap:wrap; }
        .calib-info span { color:var(--text-primary); }

        @media (max-width:420px) {
            .data-grid { grid-template-columns:repeat(3,1fr); gap:5px; }
            .data-item .value { font-size:15px; }
            .app-title { font-size:17px; }
            .btn { font-size:12px; padding:8px 10px; min-width:50px; }
            .card { padding:12px 14px; }
            .wave-row .wave-container { height:60px; }
        }
        .app-scroll::-webkit-scrollbar { width:3px; }
        .app-scroll::-webkit-scrollbar-track { background:transparent; }
        .app-scroll::-webkit-scrollbar-thumb { background:rgba(255,255,255,0.15); border-radius:10px; }
    </style>
</head>
<body>

<div id="toast" class="toast"></div>

<div class="app-scroll" id="appScroll">

    <!-- ===== 头部 ===== -->
    <div class="card header-card">
        <div class="header-row">
            <div class="app-title">📊 加速度监测 <small>原始 & 投影</small></div>
            <div class="status-badge">
                <span class="status-dot" id="statusDot"></span>
                <span id="statusText">待机</span>
            </div>
        </div>
        <div class="btn-group">
            <button class="btn btn-primary" id="btnStart"><span class="btn-icon">▶</span> 开始</button>
            <button class="btn btn-secondary" id="btnReset"><span class="btn-icon">⟳</span> 重置</button>
            <button class="btn btn-secondary" id="btnExport"><span class="btn-icon">⬇</span> 导出</button>
            <button class="btn btn-calibrate" id="btnCalibrate"><span class="btn-icon">⚖</span> 校准</button>
        </div>
        <div class="flex-row mt-1" style="justify-content:space-between;">
            <span style="font-size:11px;color:var(--text-secondary);">数据点: <strong id="pointCount">0</strong></span>
            <span style="font-size:11px;color:var(--text-secondary);">时长: <strong id="durationDisplay">0s</strong></span>
            <div class="refresh-control">
                <label>刷新率</label>
                <select id="fpsSelect">
                    <option value="20">20 Hz</option>
                    <option value="50" selected>50 Hz</option>
                    <option value="100">100 Hz</option>
                    <option value="200">200 Hz</option>
                    <option value="0">无限制</option>
                </select>
            </div>
        </div>
        <div class="calib-info" id="calibInfo">
            <span>重力校准 (设备坐标系): <span id="calibStatus">未校准</span></span>
            <span id="calibVector" style="display:none;">g: <span id="calibGx">0.00</span>, <span id="calibGy">0.00</span>, <span id="calibGz">0.00</span> m/s²</span>
        </div>
    </div>

    <!-- ===== 数据面板 ===== -->
    <div class="card">
        <div class="card-title"><span>📊 实时加速度</span></div>
        <div class="data-grid">
            <div class="data-item">
                <div class="label">原始 X</div>
                <div class="value cyan" id="dispRawX">0.00 <span class="unit">m/s²</span></div>
            </div>
            <div class="data-item">
                <div class="label">原始 Y</div>
                <div class="value cyan" id="dispRawY">0.00 <span class="unit">m/s²</span></div>
            </div>
            <div class="data-item">
                <div class="label">原始 Z</div>
                <div class="value cyan" id="dispRawZ">0.00 <span class="unit">m/s²</span></div>
            </div>
            <div class="data-item">
                <div class="label">水平投影</div>
                <div class="value green" id="dispHoriz">0.00 <span class="unit">m/s²</span></div>
            </div>
            <div class="data-item">
                <div class="label">竖直投影 (线性)</div>
                <div class="value purple" id="dispVert">0.00 <span class="unit">m/s²</span></div>
            </div>
            <div class="data-item">
                <div class="label">总大小</div>
                <div class="value orange" id="dispTotal">0.00 <span class="unit">m/s²</span></div>
            </div>
        </div>
    </div>

    <!-- ===== 六个波形图 ===== -->
    <div class="card">
        <div class="card-title"><span>📉 加速度波形 (可滑动)</span><span style="font-size:10px;color:var(--text-secondary);">← 左右滑动查看历史 →</span></div>
        <div class="wave-grid" id="waveGrid">
            <div class="wave-row"><span class="axis-label">Raw X</span><div class="wave-container" id="waveRawX"><canvas id="canvasRawX"></canvas><span class="wave-label" style="color:#00d4ff;">ax</span></div></div>
            <div class="wave-row"><span class="axis-label">Raw Y</span><div class="wave-container" id="waveRawY"><canvas id="canvasRawY"></canvas><span class="wave-label" style="color:#00e676;">ay</span></div></div>
            <div class="wave-row"><span class="axis-label">Raw Z</span><div class="wave-container" id="waveRawZ"><canvas id="canvasRawZ"></canvas><span class="wave-label" style="color:#7c4dff;">az</span></div></div>
            <div class="wave-row"><span class="axis-label">水平</span><div class="wave-container" id="waveHoriz"><canvas id="canvasHoriz"></canvas><span class="wave-label" style="color:#ff9100;">horiz</span></div></div>
            <div class="wave-row"><span class="axis-label">竖直</span><div class="wave-container" id="waveVert"><canvas id="canvasVert"></canvas><span class="wave-label" style="color:#ff4081;">vert</span></div></div>
            <div class="wave-row"><span class="axis-label">总</span><div class="wave-container" id="waveTotal"><canvas id="canvasTotal"></canvas><span class="wave-label" style="color:#ffea00;">total</span></div></div>
        </div>
        <div class="wave-info">
            <span id="waveInfo">窗口: 最新 200 点</span>
            <span>拖动任意波形平移</span>
        </div>
    </div>

    <div style="height:4px;"></div>
</div>

<script>
(function(){
    'use strict';

    // ---------- DOM ----------
    const $ = (s) => document.querySelector(s);
    const statusDot = $('#statusDot');
    const statusText = $('#statusText');
    const btnStart = $('#btnStart');
    const btnReset = $('#btnReset');
    const btnExport = $('#btnExport');
    const btnCalibrate = $('#btnCalibrate');
    const pointCount = $('#pointCount');
    const durationDisplay = $('#durationDisplay');
    const toast = $('#toast');
    const fpsSelect = $('#fpsSelect');

    const dispRawX = $('#dispRawX'), dispRawY = $('#dispRawY'), dispRawZ = $('#dispRawZ');
    const dispHoriz = $('#dispHoriz'), dispVert = $('#dispVert'), dispTotal = $('#dispTotal');
    const calibStatus = $('#calibStatus');
    const calibVector = $('#calibVector');
    const calibGx = $('#calibGx'), calibGy = $('#calibGy'), calibGz = $('#calibGz');

    // 波形容器映射
    const waveMap = {
        rawX: { container: document.getElementById('waveRawX'), canvas: document.getElementById('canvasRawX'), color: '#00d4ff' },
        rawY: { container: document.getElementById('waveRawY'), canvas: document.getElementById('canvasRawY'), color: '#00e676' },
        rawZ: { container: document.getElementById('waveRawZ'), canvas: document.getElementById('canvasRawZ'), color: '#7c4dff' },
        horiz: { container: document.getElementById('waveHoriz'), canvas: document.getElementById('canvasHoriz'), color: '#ff9100' },
        vert: { container: document.getElementById('waveVert'), canvas: document.getElementById('canvasVert'), color: '#ff4081' },
        total: { container: document.getElementById('waveTotal'), canvas: document.getElementById('canvasTotal'), color: '#ffea00' }
    };
    const waveKeys = ['rawX','rawY','rawZ','horiz','vert','total'];
    const waveInfo = $('#waveInfo');

    let toastTimer = null;

    // ---------- 状态 ----------
    let isRecording = false;
    let startTime = 0;
    let lastSensorTime = 0;
    let dataCount = 0;

    // 重力校准 (设备坐标系)
    let calibGravity = { x:0, y:0, z:0 };
    let isCalibrated = false;
    let isCalibrating = false;
    let calibSamples = [];

    // 原始加速度 (设备坐标系)
    let rawAccel = { x:0, y:0, z:0 };

    // 历史数据 (设备坐标系原始加速度)
    const history = {
        time: [],
        rawX: [], rawY: [], rawZ: [],
        horiz: [], vert: [], total: []
    };

    // 当前值 (线性加速度)
    let current = {
        rawX:0, rawY:0, rawZ:0,
        horiz:0, vert:0, total:0
    };

    let sampleInterval = 20;
    fpsSelect.addEventListener('change', function() {
        const val = parseInt(this.value);
        sampleInterval = val === 0 ? 0 : 1000 / val;
    });

    // ---------- 处理传感器 ----------
    function onDeviceMotion(event) {
        if (!isRecording) return;
        const now = performance.now();
        if (sampleInterval > 0 && (now - lastSensorTime) < sampleInterval) return;
        const accel = event.acceleration;
        if (!accel) return;
        const ax = accel.x || 0, ay = accel.y || 0, az = accel.z || 0;
        rawAccel.x = ax;
        rawAccel.y = ay;
        rawAccel.z = az;

        let dt = (now - lastSensorTime) / 1000;
        if (lastSensorTime === 0) dt = 0.016;
        if (dt > 0.05) dt = 0.016;
        lastSensorTime = now;

        // 扣除重力 (设备坐标系)
        let linX = ax, linY = ay, linZ = az;
        if (isCalibrated) {
            linX -= calibGravity.x;
            linY -= calibGravity.y;
            linZ -= calibGravity.z;
        }

        // 计算投影
        const horiz = Math.sqrt(linX*linX + linY*linY);
        const vert = linZ;          // 竖直方向线性加速度
        const total = Math.sqrt(linX*linX + linY*linY + linZ*linZ);

        // 更新当前值
        current.rawX = linX;
        current.rawY = linY;
        current.rawZ = linZ;
        current.horiz = horiz;
        current.vert = vert;
        current.total = total;

        const t = (now - startTime) / 1000;
        history.time.push(t);
        history.rawX.push(linX);
        history.rawY.push(linY);
        history.rawZ.push(linZ);
        history.horiz.push(horiz);
        history.vert.push(vert);
        history.total.push(total);

        if (history.time.length > 3000) {
            const trim = history.time.length - 3000;
            for (let key in history) history[key].splice(0, trim);
        }
        dataCount = history.time.length;
    }

    function onDeviceOrientation(event) {
        // 仅用于姿态显示，此处不处理
    }

    // ---------- 重力校准 ----------
    function performCalibration() {
        if (isCalibrating) return;
        isCalibrating = true;
        btnCalibrate.textContent = '校准中…';
        btnCalibrate.disabled = true;
        calibSamples = [];
        showToast('⚖ 请保持手机静止 2 秒…', 2500);

        let count = 0;
        const maxSamples = 60;
        function collect(e) {
            const accel = e.acceleration;
            if (!accel) return;
            const ax = accel.x||0, ay = accel.y||0, az = accel.z||0;
            calibSamples.push({ x: ax, y: ay, z: az });
            count++;
            if (count >= maxSamples) {
                window.removeEventListener('devicemotion', collect);
                let sumX=0, sumY=0, sumZ=0;
                for (let s of calibSamples) { sumX += s.x; sumY += s.y; sumZ += s.z; }
                calibGravity.x = sumX / calibSamples.length;
                calibGravity.y = sumY / calibSamples.length;
                calibGravity.z = sumZ / calibSamples.length;
                isCalibrated = true;
                isCalibrating = false;
                btnCalibrate.textContent = '⚖ 校准';
                btnCalibrate.disabled = false;
                btnCalibrate.classList.add('active');
                calibStatus.textContent = '已校准';
                calibVector.style.display = 'inline';
                calibGx.textContent = calibGravity.x.toFixed(2);
                calibGy.textContent = calibGravity.y.toFixed(2);
                calibGz.textContent = calibGravity.z.toFixed(2);
                statusDot.className = 'status-dot calibrated';
                showToast('✅ 重力校准完成', 1500);
                // 重置历史
                for (let key in history) history[key] = [];
                dataCount = 0;
                pointCount.textContent = '0';
                durationDisplay.textContent = '0s';
            }
        }
        window.addEventListener('devicemotion', collect, { passive: true });
        setTimeout(() => {
            if (isCalibrating && count < maxSamples) {
                window.removeEventListener('devicemotion', collect);
                if (count > 5) {
                    let sumX=0, sumY=0, sumZ=0;
                    for (let s of calibSamples) { sumX += s.x; sumY += s.y; sumZ += s.z; }
                    calibGravity.x = sumX / calibSamples.length;
                    calibGravity.y = sumY / calibSamples.length;
                    calibGravity.z = sumZ / calibSamples.length;
                    isCalibrated = true;
                    isCalibrating = false;
                    btnCalibrate.textContent = '⚖ 校准';
                    btnCalibrate.disabled = false;
                    btnCalibrate.classList.add('active');
                    calibStatus.textContent = '已校准';
                    calibVector.style.display = 'inline';
                    calibGx.textContent = calibGravity.x.toFixed(2);
                    calibGy.textContent = calibGravity.y.toFixed(2);
                    calibGz.textContent = calibGravity.z.toFixed(2);
                    statusDot.className = 'status-dot calibrated';
                    showToast('⚖ 校准完成 (部分数据)', 1500);
                    for (let key in history) history[key] = [];
                    dataCount = 0;
                    pointCount.textContent = '0';
                } else {
                    isCalibrating = false;
                    btnCalibrate.textContent = '⚖ 校准';
                    btnCalibrate.disabled = false;
                    showToast('⚠️ 校准失败，数据不足', 2000);
                }
            }
        }, 3000);
    }

    // ---------- 绘图辅助 ----------
    function resizeCanvas(canvas, container) {
        const rect = container.getBoundingClientRect();
        const dpr = window.devicePixelRatio || 1;
        const w = rect.width || container.clientWidth || 300;
        const h = rect.height || container.clientHeight || 200;
        canvas.width = w * dpr;
        canvas.height = h * dpr;
        canvas.style.width = w + 'px';
        canvas.style.height = h + 'px';
        const ctx = canvas.getContext('2d');
        ctx.scale(dpr, dpr);
        return { w, h, ctx };
    }

    function drawAxisTicks(ctx, w, h, margin, xMin, xMax, yMin, yMax, xUnit, yUnit, xLabel, yLabel) {
        ctx.save();
        ctx.strokeStyle = 'rgba(255,255,255,0.12)';
        ctx.lineWidth = 1;
        ctx.strokeRect(margin, margin, w - 2*margin, h - 2*margin);

        const xRange = xMax - xMin || 1;
        const numXTicks = Math.min(5, Math.floor((w - 2*margin) / 50));
        ctx.fillStyle = 'rgba(255,255,255,0.3)';
        ctx.font = '7px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';
        for (let i=0; i<=numXTicks; i++) {
            const t = i / numXTicks;
            const x = margin + t * (w - 2*margin);
            const val = xMin + t * xRange;
            ctx.fillText(val.toFixed(1), x, h - margin + 2);
            ctx.strokeStyle = 'rgba(255,255,255,0.06)';
            ctx.lineWidth = 0.5;
            ctx.beginPath();
            ctx.moveTo(x, h - margin);
            ctx.lineTo(x, h - margin + 4);
            ctx.stroke();
        }
        ctx.fillStyle = 'rgba(255,255,255,0.2)';
        ctx.font = '6px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';
        ctx.fillText(xLabel, w/2, h - margin + 10);

        const yRange = yMax - yMin || 1;
        const numYTicks = Math.min(4, Math.floor((h - 2*margin) / 40));
        ctx.textAlign = 'right';
        ctx.textBaseline = 'middle';
        for (let i=0; i<=numYTicks; i++) {
            const t = i / numYTicks;
            const y = margin + (1 - t) * (h - 2*margin);
            const val = yMin + t * yRange;
            ctx.fillStyle = 'rgba(255,255,255,0.3)';
            ctx.fillText(val.toFixed(1), margin - 4, y);
            ctx.strokeStyle = 'rgba(255,255,255,0.06)';
            ctx.lineWidth = 0.5;
            ctx.beginPath();
            ctx.moveTo(margin, y);
            ctx.lineTo(margin - 4, y);
            ctx.stroke();
        }
        ctx.save();
        ctx.translate(10, h/2);
        ctx.rotate(-Math.PI/2);
        ctx.fillStyle = 'rgba(255,255,255,0.2)';
        ctx.font = '6px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(yLabel, 0, 0);
        ctx.restore();
        ctx.restore();
    }

    // ---------- 六个波形图 ----------
    const waveWindow = { start:0, end:0, maxPoints:200, userSlid:false };
    function updateWaveWindow() {
        const n = history.time.length;
        if (n === 0) { waveWindow.start = 0; waveWindow.end = 0; return; }
        if (!waveWindow.userSlid) {
            waveWindow.end = n;
            waveWindow.start = Math.max(0, n - waveWindow.maxPoints);
        } else {
            if (waveWindow.end > n) { waveWindow.end = n; waveWindow.start = Math.max(0, n - (waveWindow.end - waveWindow.start)); }
            if (waveWindow.start < 0) waveWindow.start = 0;
            if (waveWindow.end > n) waveWindow.end = n;
            if (waveWindow.end - waveWindow.start > waveWindow.maxPoints) waveWindow.start = waveWindow.end - waveWindow.maxPoints;
        }
        if (waveWindow.end - waveWindow.start < 2) {
            waveWindow.start = Math.max(0, n - 2);
            waveWindow.end = n;
        }
        waveInfo.textContent = `窗口: ${waveWindow.start}~${waveWindow.end-1} (共${n}点)`;
    }
    function slideWaveWindow(delta) {
        const n = history.time.length;
        if (n === 0) return;
        const range = waveWindow.end - waveWindow.start;
        let newStart = waveWindow.start + delta;
        let newEnd = waveWindow.end + delta;
        if (newStart < 0) { newStart = 0; newEnd = Math.min(range, n); }
        if (newEnd > n) { newEnd = n; newStart = Math.max(0, n - range); }
        if (newEnd - newStart < 2) return;
        waveWindow.start = newStart;
        waveWindow.end = newEnd;
        waveWindow.userSlid = true;
        drawWaveforms();
    }

    function drawWaveforms() {
        const keys = ['rawX','rawY','rawZ','horiz','vert','total'];
        const colors = ['#00d4ff','#00e676','#7c4dff','#ff9100','#ff4081','#ffea00'];
        const units = ['m/s²','m/s²','m/s²','m/s²','m/s²','m/s²'];

        const n = history.time.length;
        if (n === 0) {
            for (let key of keys) {
                const { container, canvas } = waveMap[key];
                const { w, h, ctx } = resizeCanvas(canvas, container);
                ctx.clearRect(0,0,w,h);
                ctx.fillStyle = 'rgba(255,255,255,0.08)';
                ctx.font = '12px sans-serif';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText('无数据', w/2, h/2);
            }
            return;
        }

        updateWaveWindow();
        const startIdx = waveWindow.start;
        const endIdx = waveWindow.end;
        const count = endIdx - startIdx;
        if (count < 2) {
            for (let key of keys) {
                const { container, canvas } = waveMap[key];
                const { w, h, ctx } = resizeCanvas(canvas, container);
                ctx.clearRect(0,0,w,h);
                ctx.fillStyle = 'rgba(255,255,255,0.08)';
                ctx.font = '12px sans-serif';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText('数据不足', w/2, h/2);
            }
            return;
        }

        for (let idx=0; idx<keys.length; idx++) {
            const key = keys[idx];
            const { container, canvas, color } = waveMap[key];
            const { w, h, ctx } = resizeCanvas(canvas, container);
            ctx.clearRect(0,0,w,h);

            const dataArr = history[key];
            const slice = dataArr.slice(startIdx, endIdx);
            const timeSlice = history.time.slice(startIdx, endIdx);
            let minVal = Math.min(...slice);
            let maxVal = Math.max(...slice);
            const range = maxVal - minVal || 0.01;
            const margin = 18;
            const plotW = w - 2*margin;
            const plotH = h - 2*margin;

            function mapY2(val) { return margin + (maxVal - val) / range * plotH; }
            function mapX2(i) { return margin + (i / (count-1)) * plotW; }

            ctx.strokeStyle = 'rgba(255,255,255,0.04)';
            ctx.lineWidth = 0.5;
            for (let i=0; i<5; i++) {
                const y = margin + (i/4) * plotH;
                ctx.beginPath();
                ctx.moveTo(margin, y);
                ctx.lineTo(margin + plotW, y);
                ctx.stroke();
            }

            const zeroY2 = mapY2(0);
            if (zeroY2 >= margin && zeroY2 <= margin + plotH) {
                ctx.strokeStyle = 'rgba(255,255,255,0.08)';
                ctx.lineWidth = 1;
                ctx.setLineDash([2,3]);
                ctx.beginPath();
                ctx.moveTo(margin, zeroY2);
                ctx.lineTo(margin + plotW, zeroY2);
                ctx.stroke();
                ctx.setLineDash([]);
            }

            ctx.beginPath();
            for (let i=0; i<count; i++) {
                const x = mapX2(i);
                const y = mapY2(slice[i]);
                if (i===0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }
            ctx.strokeStyle = color;
            ctx.lineWidth = 1.8;
            ctx.shadowColor = color + '40';
            ctx.shadowBlur = 6;
            ctx.stroke();
            ctx.shadowBlur = 0;

            if (count > 0) {
                const lastVal = slice[count-1];
                const lx = mapX2(count-1);
                const ly = mapY2(lastVal);
                ctx.fillStyle = color;
                ctx.beginPath();
                ctx.arc(lx, ly, 3, 0, Math.PI*2);
                ctx.fill();
            }

            const tStart = timeSlice[0];
            const tEnd = timeSlice[timeSlice.length-1];
            const tRange2 = tEnd - tStart || 1;
            ctx.save();
            ctx.strokeStyle = 'rgba(255,255,255,0.12)';
            ctx.lineWidth = 1;
            ctx.strokeRect(margin, margin, plotW, plotH);
            const numXTicks2 = Math.min(4, Math.floor(plotW / 50));
            ctx.fillStyle = 'rgba(255,255,255,0.3)';
            ctx.font = '7px sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'top';
            for (let i=0; i<=numXTicks2; i++) {
                const t = i / numXTicks2;
                const x = margin + t * plotW;
                const val = tStart + t * tRange2;
                ctx.fillText(val.toFixed(1), x, margin + plotH + 2);
                ctx.strokeStyle = 'rgba(255,255,255,0.06)';
                ctx.lineWidth = 0.5;
                ctx.beginPath();
                ctx.moveTo(x, margin + plotH);
                ctx.lineTo(x, margin + plotH + 4);
                ctx.stroke();
            }
            ctx.fillStyle = 'rgba(255,255,255,0.2)';
            ctx.font = '6px sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'top';
            ctx.fillText('时间 (s)', margin + plotW/2, margin + plotH + 10);

            const numYTicks2 = Math.min(3, Math.floor(plotH / 40));
            ctx.textAlign = 'right';
            ctx.textBaseline = 'middle';
            for (let i=0; i<=numYTicks2; i++) {
                const t = i / numYTicks2;
                const y = margin + (1 - t) * plotH;
                const val = minVal + t * range;
                ctx.fillStyle = 'rgba(255,255,255,0.3)';
                ctx.fillText(val.toFixed(1), margin - 4, y);
                ctx.strokeStyle = 'rgba(255,255,255,0.06)';
                ctx.lineWidth = 0.5;
                ctx.beginPath();
                ctx.moveTo(margin, y);
                ctx.lineTo(margin - 4, y);
                ctx.stroke();
            }
            ctx.save();
            ctx.translate(10, margin + plotH/2);
            ctx.rotate(-Math.PI/2);
            ctx.fillStyle = 'rgba(255,255,255,0.2)';
            ctx.font = '6px sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(units[idx], 0, 0);
            ctx.restore();
            ctx.restore();
        }
        waveInfo.textContent = `窗口: ${waveWindow.start}~${waveWindow.end-1} (共${history.time.length}点)`;
    }

    // ---------- UI更新 ----------
    function updateUI() {
        dispRawX.textContent = current.rawX.toFixed(2);
        dispRawY.textContent = current.rawY.toFixed(2);
        dispRawZ.textContent = current.rawZ.toFixed(2);
        dispHoriz.textContent = current.horiz.toFixed(2);
        dispVert.textContent = current.vert.toFixed(2);
        dispTotal.textContent = current.total.toFixed(2);
        pointCount.textContent = dataCount;
        if (startTime > 0) {
            durationDisplay.textContent = ((performance.now() - startTime) / 1000).toFixed(1) + 's';
        }
    }

    // ---------- 动画循环 ----------
    let animFrameId = null;
    function renderLoop() {
        drawWaveforms();
        updateUI();
        animFrameId = requestAnimationFrame(renderLoop);
    }

    // ---------- 控制 ----------
    function showToast(msg, duration=2000) {
        toast.textContent = msg;
        toast.classList.add('show');
        clearTimeout(toastTimer);
        toastTimer = setTimeout(() => toast.classList.remove('show'), duration);
    }

    function setStatus(text, isActive, isError=false) {
        statusText.textContent = text;
        statusDot.className = 'status-dot';
        if (isActive) statusDot.classList.add('active');
        if (isError) statusDot.classList.add('error');
    }

    function startRecording() {
        if (isRecording) {
            isRecording = false;
            btnStart.innerHTML = '<span class="btn-icon">▶</span> 开始';
            btnStart.classList.remove('active');
            setStatus('已停止', false);
            showToast('⏸ 已停止记录');
            return;
        }
        if (!window.DeviceMotionEvent) {
            showToast('❌ 设备不支持加速度传感器', 3000);
            setStatus('不支持', false, true);
            return;
        }
        const initSensors = () => {
            try {
                resetData();
                window.addEventListener('devicemotion', onDeviceMotion, { passive: true });
                isRecording = true;
                startTime = performance.now();
                lastSensorTime = 0;
                btnStart.innerHTML = '<span class="btn-icon">⏹</span> 停止';
                btnStart.classList.add('active');
                setStatus('记录中', true);
                showToast('🔴 开始记录', 1500);
                if (!animFrameId) renderLoop();
            } catch (e) {
                showToast('❌ 启动失败', 3000);
                setStatus('错误', false, true);
                isRecording = false;
            }
        };
        // 对于iOS权限，简化为直接启动
        initSensors();
    }

    function resetData() {
        for (let key in history) history[key] = [];
        dataCount = 0;
        current.rawX = 0; current.rawY = 0; current.rawZ = 0;
        current.horiz = 0; current.vert = 0; current.total = 0;
        startTime = performance.now();
        lastSensorTime = 0;
        pointCount.textContent = '0';
        durationDisplay.textContent = '0s';
        waveWindow.start = 0; waveWindow.end = 0; waveWindow.userSlid = false;
        waveInfo.textContent = '窗口: 0 点';
    }

    function fullReset() {
        if (isRecording) {
            isRecording = false;
            window.removeEventListener('devicemotion', onDeviceMotion);
        }
        resetData();
        btnStart.innerHTML = '<span class="btn-icon">▶</span> 开始';
        btnStart.classList.remove('active');
        setStatus('已重置', false);
        showToast('🔄 已重置', 1200);
        drawWaveforms();
        updateUI();
    }

    function exportData() {
        if (history.time.length < 2) { showToast('⚠️ 没有数据', 2000); return; }
        try {
            const rows = ['time,rawX,rawY,rawZ,horiz,vert,total'];
            for (let i=0; i<history.time.length; i++) {
                rows.push([
                    history.time[i].toFixed(4),
                    history.rawX[i].toFixed(6),
                    history.rawY[i].toFixed(6),
                    history.rawZ[i].toFixed(6),
                    history.horiz[i].toFixed(6),
                    history.vert[i].toFixed(6),
                    history.total[i].toFixed(6),
                ].join(','));
            }
            const csv = rows.join('\n');
            const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            const url = URL.createObjectURL(blob);
            link.href = url;
            const dateStr = new Date().toISOString().slice(0,19).replace(/[:-]/g,'');
            link.download = `accel_data_${dateStr}.csv`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
            showToast(`✅ 导出 ${history.time.length} 条数据`, 2000);
        } catch (e) { showToast('❌ 导出失败', 3000); }
    }

    // ---------- 波形滑动触摸 ----------
    function setupWaveTouch() {
        const containers = Object.values(waveMap).map(v => v.container);
        let activeIdx = -1, startX = 0, startIdx = 0;
        function onTouchStart(e) {
            const touch = e.touches[0];
            for (let i=0; i<containers.length; i++) {
                const rect = containers[i].getBoundingClientRect();
                if (touch.clientX >= rect.left && touch.clientX <= rect.right &&
                    touch.clientY >= rect.top && touch.clientY <= rect.bottom) {
                    activeIdx = i; startX = touch.clientX; startIdx = waveWindow.start;
                    e.preventDefault(); break;
                }
            }
        }
        function onTouchMove(e) {
            if (activeIdx === -1) return;
            const touch = e.touches[0];
            const dx = touch.clientX - startX;
            const containerWidth = containers[activeIdx].clientWidth;
            const deltaIdx = -Math.round(dx / containerWidth * waveWindow.maxPoints * 0.3);
            if (deltaIdx !== 0) {
                const n = history.time.length;
                const range = waveWindow.end - waveWindow.start;
                let newStart = startIdx + deltaIdx;
                let newEnd = newStart + range;
                if (newStart < 0) { newStart = 0; newEnd = Math.min(range, n); }
                if (newEnd > n) { newEnd = n; newStart = Math.max(0, n - range); }
                if (newEnd - newStart < 2) return;
                waveWindow.start = newStart; waveWindow.end = newEnd;
                waveWindow.userSlid = true;
                drawWaveforms();
                startIdx = waveWindow.start; startX = touch.clientX;
            }
            e.preventDefault();
        }
        function onTouchEnd(e) { activeIdx = -1; }
        for (const container of containers) {
            container.addEventListener('touchstart', onTouchStart, { passive: false });
            container.addEventListener('touchmove', onTouchMove, { passive: false });
            container.addEventListener('touchend', onTouchEnd, { passive: false });
            container.addEventListener('touchcancel', onTouchEnd, { passive: false });
        }
    }

    // ---------- 窗口事件 ----------
    let resizeTimer = null;
    function handleResize() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            for (let key of waveKeys) {
                const { container, canvas } = waveMap[key];
                resizeCanvas(canvas, container);
            }
            drawWaveforms();
        }, 100);
    }

    // ---------- 初始化 ----------
    function init() {
        setTimeout(() => {
            for (let key of waveKeys) {
                const { container, canvas } = waveMap[key];
                resizeCanvas(canvas, container);
            }
            drawWaveforms();
        }, 50);

        btnStart.addEventListener('click', startRecording);
        btnReset.addEventListener('click', fullReset);
        btnExport.addEventListener('click', exportData);
        btnCalibrate.addEventListener('click', performCalibration);

        window.addEventListener('resize', handleResize);
        window.addEventListener('orientationchange', () => setTimeout(handleResize, 300));

        setStatus('待机', false);
        updateUI();
        setupWaveTouch();

        if (!animFrameId) renderLoop();
        console.log('📊 加速度监测 · 原始 & 投影已启动');
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
</script>
</body>
</html>
