import streamlit as st
import streamlit.components.v1 as components
import base64

st.set_page_config(page_title="Game Bắn Bóng", layout="centered")

st.title("🎯 Game Bắn Bóng (Bubble Shooter)")
st.write("Phiên bản chuẩn gọn: Đã khắc phục triệt để lỗi đứt quãng chuỗi, chống xếp chồng dọc, rơi bóng lơ lửng và phản xạ tường có nếp gấp!")

html_code = '''<!DOCTYPE html>
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
const cvs = document.getElementById("c"), ctx = cvs.getContext("2d");
let score = 0, shots = 0, over = false, bullet = null, mx = 220, my = 0;
const cols = ["#FF5964", "#35A7FF", "#38B000", "#FFE600", "#9B5DE5"];
const rC = () => cols[Math.floor(Math.random() * cols.length)];
let shooter = { x: 220, y: 510, r: 18, color: rC() };
let bubbles = [], rad = 18, dia = 36, rH = 31.176;

function init() {
    bubbles = []; over = false; score = 0; shots = 0;
    for (let r = 0; r < 4; r++) {
        let numC = (r % 2 === 1) ? 9 : 10;
        let offX = (r % 2 === 1) ? rad : 0;
        for (let c = 0; c < numC; c++) {
            bubbles.push({row: r, col: c, x: 25 + rad + c * dia + offX, y: 25 + r * rH, r: rad, color: rC(), active: true});
        }
    }
}
init();

function addRow() {
    bubbles.forEach(b => { b.y += rH; b.row++; if (b.active && b.y >= 430) over = true; });
    for (let c = 0; c < 10; c++) {
        bubbles.unshift({row: 0, col: c, x: 25 + rad + c * dia, y: 25, r: rad, color: rC(), active: true});
    }
}

cvs.addEventListener("mousemove", e => {
    if (over) return;
    let rect = cvs.getBoundingClientRect();
    mx = e.clientX - rect.left; my = e.clientY - rect.top;
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

function snap(hitB, bCol) {
    let r = hitB.row, c = hitB.col;
    let neighbors = (r % 2 === 0) ? [{r: r-1, c: c-1}, {r: r-1, c: c}, {r: r, c: c-1}, {r: r, c: c+1}, {r: r+1, c: c-1}, {r: r+1, c: c}] : [{r: r-1, c: c}, {r: r-1, c: c+1}, {r: r, c: c-1}, {r: r, c: c+1}, {r: r+1, c: c}, {r: r+1, c: c+1}];
    let best = null, minD = Infinity;
    for (let n of neighbors) {
        let maxC = (n.r % 2 === 1) ? 9 : 10;
        if (n.r >= 0 && n.c >= 0 && n.c < maxC) {
            if (!bubbles.some(b => b.active && b.row === n.r && b.col === n.c)) {
                let offX = (n.r % 2 === 1) ? rad : 0;
                let tx = 25 + rad + n.c * dia + offX, ty = 25 + n.r * rH;
                if (n.r > hitB.row) continue;
                let d = Math.hypot(bullet.x - tx, bullet.y - ty);
                if (d < minD) { minD = d; best = {row: n.r, col: n.c, x: tx, y: ty}; }
            }
        }
    }
    if (!best) {
        let fr = Math.max(0, r - 1);
        let maxC = (fr % 2 === 1) ? 9 : 10;
        for (let fc = 0; fc < maxC; fc++) {
            if (!bubbles.some(b => b.active && b.row === fr && b.col === fc)) {
                let offX = (fr % 2 === 1) ? rad : 0;
                best = {row: fr, col: fc, x: 25 + rad + fc * dia + offX, y: 25 + fr * rH};
                break;
            }
        }
    }
    if (best) {
        let nb = {row: best.row, col: best.col, x: best.x, y: best.y, r: rad, color: bCol, active: true};
        bubbles.push(nb);
        if (nb.y >= 430) { over = true; return; }
        if (match(nb, bCol) > 0) floatCheck();
        else { shots++; if (shots >= 5) { addRow(); shots = 0; } }
    }
}

function snapCeiling(bCol) {
    let ac = Math.round((bullet.x - 25 - rad) / dia);
    ac = Math.max(0, Math.min(9, ac));
    let tx = 25 + rad + ac * dia, ty = 25;
    if (!bubbles.some(b => b.active && b.row === 0 && b.col === ac)) {
        let nb = {row: 0, col: ac, x: tx, y: ty, r: rad, color: bCol, active: true};
        bubbles.push(nb);
        if (match(nb, bCol) > 0) floatCheck();
        else { shots++; if (shots >= 5) { addRow(); shots = 0; } }
    }
}

function match(startB, tCol) {
    let vis = new Set(), q = [startB], matched = [];
    vis.add(startB);
    while(q.length > 0) {
        let cur = q.shift();
        if (cur.color === tCol && cur.active) {
            matched.push(cur);
            for (let b of bubbles) {
                if (b.active && !vis.has(b) && Math.hypot(cur.x - b.x, cur.y - b.y) < dia * 1.15) {
                    vis.add(b); q.push(b);
                }
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
    bubbles.forEach(b => { if (b.active && (b.row === 0 || b.y <= 25 + rad)) { vis.add(b); q.push(b); } });
    while(q.length > 0) {
        let cur = q.shift();
        bubbles.forEach(b => {
            if (b.active && !vis.has(b) && Math.hypot(cur.x - b.x, cur.y - b.y) < dia * 1.15) {
                vis.add(b); q.push(b);
            }
        });
    }
    bubbles.forEach(b => { if (b.active && !vis.has(b)) { b.active = false; score += 30; } });
}

function update() {
    if (over) return;
    if (bullet) {
        bullet.x += bullet.dx; bullet.y += bullet.dy;
        if (bullet.x - rad < 0 || bullet.x + rad > cvs.width) bullet.dx *= -1;
        if (bullet.y - rad <= 15) { snapCeiling(bullet.color); bullet = null; return; }
        for (let b of bubbles) {
            if (b.active && Math.hypot(bullet.
            
