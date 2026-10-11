import streamlit as st
import streamlit.components.v1 as components
import base64

st.set_page_config(page_title="Game Bắn Bóng", layout="centered")

st.title("🎯 Game Bắn Bóng (Bubble Shooter)")
st.write("Phiên bản hoàn chỉnh: Sửa triệt để lỗi cú pháp, chống xếp chồng dọc, rơi bóng lơ lửng và đường ngắm phản xạ tường có nếp gấp!")

html_code = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { margin: 0; padding: 0; text-align: center; font-family: sans-serif; background: #0f0f1a; color: white; }
        canvas { background: #1e1e2e; display: block; margin: 10px auto; border-radius: 12px; box-shadow: 0 8px 20px rgba(0,0,0,0.6); cursor: crosshair; }
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="440" height="540"></canvas>
    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        let score = 0;
        let shotsSinceLastRow = 0;
        let gameOver = false;
        const colors = ["#FF5964", "#35A7FF", "#38B000", "#FFE600", "#9B5DE5"];
        
        function getRandomColor() {
            return colors[Math.floor(Math.random() * colors.length)];
        }

        let shooter = { x: 220, y: 510, radius: 18, color: getRandomColor() };
        let bullet = null;
        let mouseX = 220, mouseY = 0;

        let bubbles = [];
        const rows = 4;
        const cols = 10;
        const radius = 18;
        const diameter = radius * 2;
        const rowHeight = radius * 1.732;

        function initBubbles() {
            bubbles = [];
            gameOver = false;
            score = 0;
            shotsSinceLastRow = 0;
            for (let r = 0; r < rows; r++) {
                let colsInRow = (r % 2 === 1) ? cols - 1 : cols;
                let rowOffsetX = (r % 2 === 1) ? radius : 0;
                for (let c = 0; c < colsInRow; c++) {
                    bubbles.push({
                        row: r,
                        col: c,
                        x: 25 + radius + c * diameter + rowOffsetX,
                        y: 25 + r * rowHeight,
                        radius: radius,
                        color: getRandomColor(),
                        active: true
                    });
                }
            }
        }
        initBubbles();

        function addNewRow() {
            bubbles.forEach(b => {
                b.y += rowHeight;
                b.row += 1;
                if (b.active && b.y >= 430) {
                    gameOver = true;
                }
            });
            for (let c = 0; c < cols; c++) {
                bubbles.unshift({
                    row: 0,
                    col: c,
                    x: 25 + radius + c * diameter,
                    y: 25,
                    radius: radius,
                    color: getRandomColor(),
                    active: true
                });
            }
        }

        canvas.addEventListener("mousemove", (e) => {
            if (gameOver) return;
            const rect = canvas.getBoundingClientRect();
            mouseX = e.clientX - rect.left;
            mouseY = e.clientY - rect.top;
        });

        canvas.addEventListener("click", () => {
            if (gameOver) { initBubbles(); return; }
            if (!bullet) {
                let angle = Math.atan2(mouseY - shooter.y, mouseX - shooter.x);
                if (angle > -0.1) angle = -0.1;
                if (angle < -Math.PI + 0.1) angle = -Math.PI + 0.1;
                bullet = { x: shooter.x, y: shooter.y, dx: Math.cos(angle) * 7, dy: Math.sin(angle) * 7, color: shooter.color };
                shooter.color = getRandomColor();
            }
        });

        function snapToHitBubble(hitBubble, bColor) {
            let r = hitBubble.row;
            let c = hitBubble.col;
            let neighbors = (r % 2 === 0) ? [
                {r: r-1, c: c-1}, {r: r-1, c: c}, 
                {r: r, c: c-1}, {r: r, c: c+1}, 
                {r: r+1, c: c-1}, {r: r+1, c: c}
            ] : [
                {r: r-1, c: c}, {r: r-1, c: c+1}, 
                {r: r, c: c-1}, {r: r, c: c+1}, 
                {r: r+1, c: c}, {r: r+1, c: c+1}
            ];

            let bestSlot = null;
            let minDist = Infinity;

            for (let n of neighbors) {
                let colsInRow = (n.r % 2 === 1) ? cols - 1 : cols;
                if (n.r >= 0 && n.c >= 0 && n.c < colsInRow) {
                    let occupied = bubbles.some(b => b.active && b.row === n.r && b.col === n.c);
                    if (!occupied) {
                        let rowOffsetX = (n.r % 2 === 1) ? radius : 0;
                        let targetX = 25 + radius + n.c * diameter + rowOffsetX;
                        let targetY = 25 + n.r * rowHeight;

                        if (n.r > hitBubble.row) continue;

                        let dist = Math.hypot(bullet.x - targetX, bullet.y - targetY);
                        if (dist < minDist) {
                            minDist = dist;
                            bestSlot = { row: n.r, col: n.c, x: targetX, y: targetY };
                        }
                    }
                }
            }

            if (!bestSlot) {
                let fallbackR = Math.max(0, r - 1);
                let colsInRow = (fallbackR % 2 === 1) ? cols - 1 : cols;
                for (let fc = 0; fc < colsInRow; fc++) {
                    let occupied = bubbles.some(b => b.active && b.row === fallbackR && b.col === fc);
                    if (!occupied) {
                        let rowOffsetX = (fallbackR % 2 === 1) ? radius : 0;
                        bestSlot = {
                            row: fallbackR,
                            col: fc,
                            x: 25 + radius + fc * diameter + rowOffsetX,
                            y: 25 + fallbackR * rowHeight
                        };
                        break;
                    }
                }
            }

            if (bestSlot) {
                let newBubble = { row: bestSlot.row, col: bestSlot.col, x: bestSlot.x, y: bestSlot.y, radius: radius, color: bColor, active: true };
                bubbles.push(newBubble);
                if (newBubble.y >= 430) { gameOver = true; return; }
                
                if (checkMatch(newBubble, bColor) > 0) {
                    removeFloatingBubbles();
                } else {
                    shotsSinceLastRow++;
                    if (shotsSinceLastRow >= 5) {
                        addNewRow();
                        shotsSinceLastRow = 0;
                    }
                }
            }
        }

        function snapToCeiling(bColor) {
            let approxCol = Math.round((bullet.x - 25 - radius) / diameter);
            approxCol = Math.max(0, Math.min(cols - 1, approxCol));

            let targetX = 25 + radius + approxCol * diameter;
            let targetY = 25;

            let occupied = bubbles.some(b => b.active && b.row === 0 && b.col === approxCol);
            if (!occupied) {
                let newBubble = { row: 0, col: approxCol, x: targetX, y: targetY, radius: radius, color: bColor, active: true };
                bubbles.push(
