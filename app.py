import streamlit as st
import streamlit.components.v1 as components
import base64

st.set_page_config(page_title="Game Bắn Bóng", layout="centered")
st.title("🎯 Game Bắn Bóng (Bubble Shooter)")

html_code = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8">
<style>
body { margin: 0; text-align: center; font-family: sans-serif; background: #0f0f1a; color: white; }
canvas { background: #1e1e2e; display: block; margin: 10px auto; border-radius: 12px; box-shadow: 0 8px 20px rgba(0,0,0,0.6); cursor: crosshair; }
</style>
</head>
<body>
<canvas id="c" width="440" height="540"></canvas>
<script>
const cvs = document.getElementById("c"), ctx = cvs.getContext("2d");
let score = 0, shots = 0, over = false, bullet = null, mx = 220, my = 0;
const cols = ["#FF5964", "#35A7FF", "#38B000", "#FFE600", "#9B5DE5"];
const rC = () => cols[Math.floor(Math.random() * cols.length)];
let shooter = { x: 220, y: 510, r: 18, color: rC() };
let bubbles = [], fallingBubbles = [], rad = 18, dia = 36, rH = 31.176;

function init() {
    bubbles = []; fallingBubbles = []; over = false; score = 0; shots = 0;
    for (let r = 0; r < 4; r++) {
        let numC = (r % 2 === 1) ? 9 : 10, offX = (r % 2 === 1) ? rad : 0;
        for (let c = 0; c < numC; c++) bubbles.push({ row: r, col: c, x: 25 + rad + c * dia + offX, y: 25 + r * rH, r: rad, color: rC(), active: true });
    }
}
init();

function addRow() {
    bubbles.forEach(b => { b.y += rH; b.row++; if (b.active && b.y >= 430) over = true; });
    for (let c = 0; c < 10; c++) bubbles.unshift({ row: 0, col: c, x: 25 + rad + c * dia, y: 25, r: rad, color: rC(), active: true });
}

cvs.addEventListener("mousemove", e => {
    if (over) return;
    let rct = cvs.getBoundingClientRect();
    mx = e.clientX - rct.left; my = e.clientY - rct.top;
});

cvs.addEventListener("click", () => {
    if (over) { init(); return; }
    if (!bullet) {
        let a = Math.atan2(my - shooter.y, mx - shooter.x);
        if (a > -0.1) a = -0.1; if (a < -Math.PI + 0.1) a = -Math.PI + 0.1;
        bullet = { x: shooter.x, y: shooter.y, dx: Math.cos(a) * 7, dy: Math.sin(a) * 7, color: shooter.color };
        shooter.color = rC();
    }
});

function getNeighbors(r, c) {
    return (r % 2 === 0) ? [{r: r-1, c: c-1}, {r: r-1, c: c}, {r: r, c: c-1}, {r: r, c: c+1}, {r: r+1, c: c-1}, {r: r+1, c: c}] : [{r: r-1, c: c}, {r: r-1, c: c+1}, {r: r, c: c-1}, {r: r, c: c+1}, {r: r+1, c: c}, {r: r+1, c: c+1}];
}

function snapToGrid(hitB, bCol) {
    let nList = getNeighbors(hitB.row, hitB.col);
    let bestCell = null, minScore = Infinity;
    let impactAngle = Math.atan2(bullet.y - hitB.y, bullet.x - hitB.x);

    // Tìm ô lân cận trống khớp nhất với góc va chạm của viên đạn
    for (let n of nList) {
        let maxC = (n.r % 2 === 1) ? 9 : 10;
        if (n.r >= 0 && n.r < 15 && n.c >= 0 && n.c < maxC) {
            let occupied = bubbles.some(b => b.active && b.row === n.r && b.col === n.c);
            if (!occupied) {
                let offX = (n.r % 2 === 1) ? rad : 0;
                let tx = 25 + rad + n.c * dia + offX;
                let ty = 25 + n.r * rH;
                
                let angleToCell = Math.atan2(ty - hitB.y, tx - hitB.x);
                let angleDiff = Math.abs(impactAngle - angleToCell);
                if (angleDiff > Math.PI) angleDiff = Math.PI * 2 - angleDiff;
                
                let dist = Math.hypot(bullet.x - tx, bullet.y - ty);
                let scoreVal = angleDiff * 20 + dist; // Kết hợp góc và khoảng cách để chọn ô chính xác nhất

                if (scoreVal < minScore) {
                    minScore = scoreVal;
                    bestCell = { row: n.r, col: n.c, x: tx, y: ty };
                }
            }
        }
    }

    // Nếu không tìm được ô lân cận theo góc, quét toàn bộ ô trống gần vị trí đạn nhất để tuyệt đối không mất bóng
    if (!bestCell) {
        let minD = Infinity;
        for (let r = 0; r < 15; r++) {
            let maxC = (r % 2 === 1) ? 9 : 10;
            let offX = (r % 2 === 1) ? rad : 0;
            for (let c = 0; c < maxC; c++) {
                if (!bubbles.some(b => b.active && b.row === r && b.col === c)) {
                    let tx = 25 + rad + c * dia + offX;
                    let ty = 25 + r * rH;
                    let d = Math.hypot(bullet.x - tx, bullet.y - ty);
                    if (d < minD) { minD = d; bestCell = { row: r, col: c, x: tx, y: ty }; }
                }
            }
        }
    }

    if (bestCell) {
        let nb = { row: bestCell.row, col: bestCell.col, x: bestCell.x, y: bestCell.y, r: rad, color: bCol, active: true };
        bubbles.push(nb);
        if (nb.y >= 430) { over = true; return; }
        if (match(nb, bCol) > 0) { floatCheck(); }
        else { shots++; if (shots >= 5) { addRow(); shots = 0; } }
    }
}

function snapCeiling(bCol) {
    let ac = Math.max(0, Math.min(9, Math.round((bullet.x - 25 - rad) / dia)));
    if (bubbles.some(b => b.active && b.row === 0 && b.col === ac)) {
        for (let c = 0; c < 10; c++) { if (!bubbles.some(b => b.active && b.row === 0 && b.col === c)) { ac = c; break; } }
    }
    let nb = { row: 0, col: ac, x: 25 + rad + ac * dia, y: 25, r: rad, color: bCol, active: true };
    bubbles.push(nb);
    if (match(nb, bCol) > 0) { floatCheck(); } else { shots++; if (shots >= 5) { addRow(); shots = 0; } }
}

function match(startB, tCol) {
    let vis = new Set(), q = [startB], matched = [];
    vis.add(startB);
    while (q.length > 0) {
        let cur = q.shift();
        if (cur.color === tCol && cur.active) {
            matched.push(cur);
            getNeighbors(cur.row, cur.col).forEach(n => {
                let nb = bubbles.find(b => b.active && !vis.has(b) && b.row === n.r && b.col === n.c);
                if (nb) { vis.add(nb); q.push(nb); }
            });
        }
    }
    if (matched.length >= 3) { matched.forEach(b => { b.active = false; score += 20; }); return matched.length; }
    return 0;
}

function floatCheck() {
    let vis = new Set(), q = [];
    bubbles.forEach(b => { if (b.active && b.row === 0) { vis.add(b); q.push(b); } });
    while (q.length > 0) {
        let cur = q.shift();
        getNeighbors(cur.row, cur.col).forEach(n => {
            let nb = bubbles.find(b => b.active && !vis.has(b) && b.row === n.r && b.col === n.c);
            if (nb) { vis.add(nb); q.push(nb); }
        });
    }
    bubbles.forEach(b => {
        if (b.active && !vis.has(b)) {
            b.active = false; score += 30;
            fallingBubbles.push({ x: b.x, y: b.y, r: rad, color: b.color, dx: (Math.random() - 0.5) * 4, dy: 2 + Math.random() * 2 });
        }
    });
}

function update() {
    if (over) return;
    if (bullet) {
        bullet.x += bullet.dx; bullet.y += bullet.dy;
        if (bullet.x - rad < 0) { bullet.x = rad; bullet.dx *= -1; }
        if (bullet.x + rad > cvs.width) { bullet.x = cvs.width - rad; bullet.dx *= -1; }
        if (bullet.y - rad <= 15) { snapCeiling(bullet.color); bullet = null; return; }
        for (let b of bubbles) {
            if (b.active && Math.hypot(bullet.x - b.x, bullet.y - b.y) <= dia) {
                snapToGrid(b, bullet.color);
                bullet = null;
                break;
            }
        }
    }
    fallingBubbles.forEach(fb =>
