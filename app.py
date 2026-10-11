import streamlit as st
import streamlit.components.v1 as components
import base64

st.set_page_config(page_title="Game Bắn Bóng", layout="centered")

st.title("🎯 Game Bắn Bóng (Bubble Shooter)")

html_code = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { margin: 0; text-align: center; font-family: sans-serif; background: #0f0f1a; color: white; }
        canvas { background: #1e1e2e; display: block; margin: 10px auto; border-radius: 12px; box-shadow: 0 8px 20px rgba(0,0,0,0.6); cursor: crosshair; }
    </style>
</head>
<body>
    <canvas id="c" width="440" height="540"></canvas>
    <script>
        const cvs = document.getElementById("c");
        const ctx = cvs.getContext("2d");
        let score = 0, shots = 0, over = false, bullet = null, mx = 220, my = 0;
        const cols = ["#FF5964", "#35A7FF", "#38B000", "#FFE600", "#9B5DE5"];
        const rC = () => cols[Math.floor(Math.random() * cols.length)];
        let shooter = { x: 220, y: 510, r: 18, color: rC() };
        let bubbles = [], fallingBubbles = [], rad = 18, dia = 36, rH = 31.176;

        function init() {
            bubbles = []; fallingBubbles = []; over = false; score = 0; shots = 0;
            for (let r = 0; r < 4; r++) {
                let numC = (r % 2 === 1) ? 9 : 10;
                let offX = (r % 2 === 1) ? rad : 0;
                for (let c = 0; c < numC; c++) {
                    bubbles.push({ row: r, col: c, x: 25 + rad + c * dia + offX, y: 25 + r * rH, r: rad, color: rC(), active: true });
                }
            }
        }
        init();

        function addRow() {
            bubbles.forEach(b => { b.y += rH; b.row++; if (b.active && b.y >= 430) over = true; });
            for (let c = 0; c < 10; c++) {
                bubbles.unshift({ row: 0, col: c, x: 25 + rad + c * dia, y: 25, r: rad, color: rC(), active: true });
            }
        }

        cvs.addEventListener("mousemove", e => {
            if (over) return;
            let rect = cvs.getBoundingClientRect();
            mx = e.clientX - rect.left;
            my = e.clientY - rect.top;
        });

        cvs.addEventListener("click", () => {
            if (over) { init(); return; }
            if (!bullet) {
                let a = Math.atan2(my - shooter.y, mx - shooter.x);
                if (a > -0.1) a = -0.1;
                if (a < -Math.PI + 0.1) a = -Math.PI + 0.1;
                bullet = { x: shooter.x, y: shooter.y, dx: Math.cos(a) * 7, dy: Math.sin(a) * 7, color: shooter.color };
                shooter.color = rC();
            }
        });

        function getNeighbors(r, c) {
            return (r % 2 === 0) ? [
                {r: r-1, c: c-1}, {r: r-1, c: c}, 
                {r: r, c: c-1}, {r: r, c: c+1}, 
                {r: r+1, c: c-1}, {r: r+1, c: c}
            ] : [
                {r: r-1, c: c}, {r: r-1, c: c+1}, 
                {r: r, c: c-1}, {r: r, c: c+1}, 
                {r: r+1, c: c}, {r: r+1, c: c+1}
            ];
        }

        function snap(hitB, bCol) {
            let bestN = null, minAngleDiff = Infinity;
            let nList = getNeighbors(hitB.row, hitB.col);
            let impactAngle = Math.atan2(bullet.y - hitB.y, bullet.x - hitB.x);

            for (let n of nList) {
                let maxC = (n.r % 2 === 1) ? 9 : 10;
                if (n.r >= 0 && n.r < 15 && n.c >= 0 && n.c < maxC) {
                    let occupied = bubbles.some(b => b.active && b.row === n.r && b.col === n.c);
                    if (!occupied) {
                        let offX = (n.r % 2 === 1) ? rad : 0;
                        let tx = 25 + rad + n.c * dia + offX;
                        let ty = 25 + n.r * rH;
                        let angleToN = Math.atan2(ty - hitB.y, tx - hitB.x);
                        let diff = Math.abs(impactAngle - angleToN);
                        if (diff > Math.PI) diff = Math.PI * 2 - diff;
                        if (diff < minAngleDiff) {
                            minAngleDiff = diff;
                            bestN = { row: n.r, col: n.c, x: tx, y: ty };
                        }
                    }
                }
            }

            if (bestN) {
                let doubleCheck = bubbles.some(b => b.active && b.row === bestN.row && b.col === bestN.col);
                if (!doubleCheck) {
                    let nb = { row: bestN.row, col: bestN.col, x: bestN.x, y: bestN.y, r: rad, color: bCol, active: true };
                    bubbles.push(nb);
                    if (nb.y >= 430) { over = true; return; }
                    if (match(nb, bCol) > 0) { floatCheck(); }
                    else { shots++; if (shots >= 5) { addRow(); shots = 0; } }
                    return;
                }
            }

            let fallback = null, minD = Infinity;
            for (let n of nList) {
                let maxC = (n.r % 2 === 1) ? 9 : 10;
                if (n.r >= 0 && n.r < 15 && n.c >= 0 && n.c < maxC) {
                    let occupied = bubbles.some(b => b.active && b.row === n.r && b.col === n.c);
                    if (!occupied) {
                        let offX = (n.r % 2 === 1) ? rad : 0;
                        let tx = 25 + rad + n.c * dia + offX;
                        let ty = 25 + n.r * rH;
                        let d = Math.hypot(bullet.x - tx, bullet.y - ty);
                        if (d < minD) { minD = d; fallback = { row: n.r, col: n.c, x: tx, y: ty }; }
                    }
                }
            }

            if (fallback) {
                let doubleCheck = bubbles.some(b => b.active && b.row === fallback.row && b.col === fallback.col);
                if (!doubleCheck) {
                    let nb = { row: fallback.row, col: fallback.col, x: fallback.x, y: fallback.y, r: rad, color: bCol, active: true };
                    bubbles.push(nb);
                    if (nb.y >= 430) { over = true; return; }
                    if (match(nb, bCol) > 0) { floatCheck(); }
                    else { shots++; if (shots >= 5) { addRow(); shots = 0; } }
                }
            }
        }

        function snapCeiling(bCol) {
            let ac = Math.round((bullet.x - 25 - rad) / dia);
            ac = Math.max(0, Math.min(9, ac));
            let tx = 25 + rad + ac * dia;
            let ty = 25;
            if (bubbles.some(b => b.active && b.row === 0 && b.col === ac)) {
                let minD = Infinity, bestC = ac;
                for (let c = 0; c < 10; c++) {
                    if (!bubbles.some(b => b.active && b.row === 0 && b.col === c)) {
                        let cx = 25 + rad + c * dia;
                        let d = Math.abs(cx - bullet.x);
                        if (d < minD) { minD = d; bestC = c; }
                    }
                }
                ac = bestC; tx = 25 + rad + ac * dia;
            }
            let doubleCheck = bubbles.some(b => b.active && b.row === 0 && b.col === ac);
            if (!doubleCheck) {
                let nb = { row: 0, col: ac, x: tx, y: ty, r: rad, color: bCol, active: true };
                bubbles.push(nb);
                if (match(nb, bCol) > 0) { floatCheck(); }
                else { shots++; if (shots >= 5) { addRow(); shots = 0; } }
            }
        }

        function match(startB, tCol) {
            let vis = new Set(), q = [startB], matched = [];
            vis.add(startB);
            while (q.length > 0) {
                let cur = q.shift();
                if (cur.color === tCol && cur.active) {
                    matched.push(cur);
                    let nList = getNeighbors(cur.row, cur.col);
                    for (let n of nList) {
                        let neighbor = bubbles.find(b => b.active && !vis.has(b) && b.row === n.r && b.col === n.c);
                        if (neighbor) { vis.add(neighbor); q.push(neighbor); }
                    }
                }
            }
            if (matched.length >= 3) {
                matched.forEach(b => { b.active = false; score += 20; });
                return matched.length;
            }
            return 0;
        }

        function floatCheck() {
            let vis = new Set(), q = [];
            bubbles.forEach(b => { if (b.active && b.row === 0) { vis.add(b); q.push(b); } });
            while (q.length > 0) {
                let cur = q.shift();
                let nList = getNeighbors(cur.row, cur.col);
                for (let n of nList) {
                    let neighbor = bubbles.find(b => b.active && !vis.has(b) && b.row === n.r && b.col === n.c);
                    if (neighbor) { vis.add(neighbor); q.push(neighbor); }
                }
            }
            bubbles.forEach(b => {
                if (b.active && !vis.has(b)) {
                    b.active = false;
                    score += 30;
                    fallingBubbles.push({ x: b.x, y: b.y, r: rad, color: b.color, dx: (Math.random() - 0.5) * 4, dy: 2 + Math.random() * 2 });
                }
            });
        }

        function update() {
            if (over) return;
            if (bullet) {
                bullet.x += bullet.dx;
                bullet.y += bullet.dy;
                if (bullet.x - rad < 0 || bullet.x + rad > cvs.width) bullet.dx *= -1;
                if (
