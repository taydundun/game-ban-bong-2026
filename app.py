import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Game Bắn Bóng", layout="centered")

st.title("🎯 Game Bắn Bóng (Bubble Shooter)")
st.write("Game Bubble Shooter chuẩn chỉnh: Lưới bóng so le, ngắm bắn dính lưới, nổ cụm màu và tiến hàng mới!")

game_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; padding: 0; text-align: center; font-family: sans-serif; background: #0f0f1a; color: white; }
        canvas {
            background: #1e1e2e;
            display: block;
            margin: 10px auto;
            border-radius: 12px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.6);
            cursor: crosshair;
        }
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="440" height="540"></canvas>
    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        let score = 0;
        let shotsSinceLastRow = 0;
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
        const rowHeight = radius * Math.sqrt(3); // Khoảng cách chuẩn lưới lục giác

        function initBubbles() {
            bubbles = [];
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
            // Đẩy toàn bộ bóng cũ xuống
            bubbles.forEach(b => {
                b.y += rowHeight;
                b.row += 1;
            });

            // Thêm hàng mới ở trên cùng
            let r = 0;
            let colsInRow = (r % 2 === 1) ? cols - 1 : cols;
            let rowOffsetX = (r % 2 === 1) ? radius : 0;
            for (let c = 0; c < colsInRow; c++) {
                bubbles.unshift({
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

        canvas.addEventListener("mousemove", (e) => {
            const rect = canvas.getBoundingClientRect();
            mouseX = e.clientX - rect.left;
            mouseY = e.clientY - rect.top;
        });

        canvas.addEventListener("click", () => {
            if (!bullet) {
                let angle = Math.atan2(mouseY - shooter.y, mouseX - shooter.x);
                if (angle > -0.1) angle = -0.1;
                if (angle < -Math.PI + 0.1) angle = -Math.PI + 0.1;

                bullet = {
                    x: shooter.x,
                    y: shooter.y,
                    dx: Math.cos(angle) * 10,
                    dy: Math.sin(angle) * 10,
                    color: shooter.color
                };
                shooter.color = getRandomColor();
            }
        });

        function snapBulletToGrid(bColor) {
            // Tìm ô lưới gần nhất để gắn đạn vào vị trí chính xác
            let bestX = bullet.x;
            let bestY = bullet.y;
            
            let approxRow = Math.round((bullet.y - 25) / rowHeight);
            if (approxRow < 0) approxRow = 0;
            
            let rowOffsetX = (approxRow % 2 === 1) ? radius : 0;
            let approxCol = Math.round((bullet.x - 25 - radius - rowOffsetX) / diameter);
            
            let colsInRow = (approxRow % 2 === 1) ? cols - 1 : cols;
            if (approxCol < 0) approxCol = 0;
            if (approxCol >= colsInRow) approxCol = colsInRow - 1;

            let targetX = 25 + radius + approxCol * diameter + rowOffsetX;
            let targetY = 25 + approxRow * rowHeight;

            let newBubble = {
                row: approxRow,
                col: approxCol,
                x: targetX,
                y: targetY,
                radius: radius,
                color: bColor,
                active: true
            };

            bubbles.push(newBubble);

            // Kiểm tra cụm màu để nổ
            let poppedCount = checkMatch(newBubble, bColor);
            
            if (poppedCount === 0) {
                // Nếu bắn không nổ, tích lũy lượt bắn để đẩy hàng mới xuống
                shotsSinceLastRow++;
                if (shotsSinceLastRow >= 4) {
                    addNewRow();
                    shotsSinceLastRow = 0;
                }
            }
        }

        function checkMatch(startBubble, targetColor) {
            let visited = new Set();
            let queue = [startBubble];
            let matched = [];

            visited.add(startBubble);

            while (queue.length > 0) {
                let current = queue.shift();
                if (current.color === targetColor && current.active) {
                    matched.push(current);

                    for (let b of bubbles) {
                        if (b.active && !visited.has(b)) {
                            let dist = Math.hypot(current.x - b.x, current.y - b.y);
                            if (dist < diameter * 1.15) { // Khoảng cách hàng xóm chuẩn lục giác
                                visited.add(b);
                                queue.push(b);
                            }
                        }
                    }
                }
            }

            // Nếu từ 3 quả trở lên thì nổ
            if (matched.length >= 3) {
                matched.forEach(b => {
                    b.active = false;
                    score += 20;
                });
                return matched.length;
            } else {
                // Trả về 0 nếu không đủ cụm để nổ
                return 0;
            }
        }

        function update() {
            if (bullet) {
                bullet.x += bullet.dx;
                bullet.y += bullet.dy;

                // Va chạm tường trái/phải
                if (bullet.x - radius < 0 || bullet.x + radius > canvas.width) {
                    bullet.dx *= -1;
                }

                // Chạm trần trên cùng
                if (bullet.y - radius <= 15) {
                    snapBulletToGrid(bullet.color);
                    bullet = null;
                    return;
                }

                // Va chạm với các bóng khác trên lưới
                for (let b of bubbles) {
                    if (b.active) {
                        let dist = Math.hypot(bullet.x - b.x, bullet.y - b.y);
                        if (dist < diameter * 0.95) {
                            snapBulletToGrid(bullet.color);
                            bullet = null;
                            break
