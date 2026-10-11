import streamlit as st
import streamlit.components.v1 as components
import base64

st.set_page_config(page_title="Game Bắn Bóng", layout="centered")

st.title("🎯 Game Bắn Bóng (Bubble Shooter)")
st.write("Phiên bản chuẩn xác tối ưu: Đã sửa lỗi đi xuyên, khớp đúng màu để nổ bóng và chống xếp chồng dọc tuyệt đối!")

html_code = '''<!DOCTYPE html>
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
            let r = 0;
            let colsInRow = cols;
            let rowOffsetX = 0;
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
                bullet = { x: shooter.x, y: shooter.y, dx: Math.cos(angle) * 10, dy: Math.sin(angle) * 10, color: shooter.color };
                shooter.color = getRandomColor();
            }
        });

        // HÀM BÁM LƯỚI CHUẨN XÁC: CHỈ TÌM Ô TRỐNG PHÍA TRÊN HOẶC NGANG, TUYỆT ĐỐI KHÔNG XẾP DƯỚI
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

                        // CHẶN ĐỨNG HOÀN TOÀN CÁC Ô PHÍA DƯỚI (CHỈ CHO PHÉP TRÊN VÀ NGANG)
                        if (n.r > hitBubble.row) continue;

                        let dist = Math.hypot(bullet.x - targetX, bullet.y - targetY);
                        if (dist < minDist) {
                            minDist = dist;
                            bestSlot = { row: n.r, col: n.c, x: targetX, y: targetY };
                        }
                    }
                }
            }

            // Fallback an toàn nếu không tìm được ô bên cạnh
            if (!bestSlot) {
                let fallbackR = Math.max(0, r - 1);
                let colsInRow = (fallbackR % 2 === 1) ? cols - 1 : cols;
                let fallbackC = Math.min(c, colsInRow - 1);
                let rowOffsetX = (fallbackR % 2 === 1) ? radius : 0;
                bestSlot = {
                    row: fallbackR,
                    col: fallbackC,
                    x: 25 + radius + fallbackC * diameter + rowOffsetX,
                    y: 25 + fallbackR * rowHeight
                };
            }

            if (bestSlot) {
                let newBubble = { row: bestSlot.row, col: bestSlot.col, x: bestSlot.x, y: bestSlot.y, radius: radius, color: bColor, active: true };
                bubbles.push(newBubble);
                if (newBubble.y >= 430) { gameOver = true; return; }
                
                let poppedCount = checkMatch(newBubble, bColor);
                if (poppedCount > 0) {
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
            if (approxCol < 0) approxCol = 0;
            if (approxCol >= cols) approxCol = cols - 1;

            let targetX = 25 + radius + approxCol * diameter;
            let targetY = 25;

            let occupied = bubbles.some(b => b.active && b.row === 0 && b.col === approxCol);
            if (!occupied) {
                let newBubble = { row: 0, col: approxCol, x: targetX, y: targetY, radius: radius, color: bColor, active: true };
                bubbles.push(newBubble);
                let poppedCount = checkMatch(newBubble, bColor);
                if (poppedCount > 0) {
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
                        if (b.active && !visited.has(b) && Math.hypot(current.x - b.x, current.y - b.y) < diameter * 1.15) {
                            visited.add(b);
                            queue.push(b);
                        }
                    }
                }
            }
            if (matched.length >= 3) {
                matched.forEach(b => {
                    b.active = false;
                    score += 20;
                });
                return matched.length;
            }
            return 0;
        }

        function removeFloatingBubbles() {
            let visited = new Set();
            let queue = [];
            for (let b of bubbles) {
                if (b.active && b.row === 0) {
                    visited.add(b);
                    queue.push(b);
                }
            }
            while (queue.length > 0) {
                let current = queue.shift();
                for (let b of bubbles) {
                    if (b.active && !visited.has(b) && Math.hypot(current.x - b.x, current.y - b.y) < diameter * 1.15) {
                        visited.add(b);
                        queue.push(b);
                    }
                }
            }
            bubbles.forEach(b => {
                if (b.active && !visited.has(b)) {
                    b.active = false;
                    score += 30;
                }
            });
        }

        function update() {
            if (gameOver) return;
            if (bullet) {
                bullet.x += bullet.dx;
                bullet.y += bullet.dy;

                if (bullet.x - radius < 0 || bullet.x + radius > canvas.width) {
                    bullet.dx *= -1;
                }

                if (bullet.y - radius <= 15) {
                    snapToCeiling(bullet.color);
                    bullet = null;
                    return;
                }

                // SỬA LỖI QUAN TRỌNG: GỌI ĐÚNG HÀM snapToHitBubble VỚI QUẢ BÓNG BỊ TRÚNG
                for (let b of bubbles) {
                    if (b.active && Math.hypot(bullet.x - b.x, bullet.y - b.y) < diameter * 0.95) {
                        snapToHitBubble(b, bullet.color);
                        bullet = null;
                        break;
                    }
                }
            }
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            ctx.fillStyle = "#FFFFFF";
            ctx.font = "bold 16px sans-serif";
            ctx.fillText("Điểm: " + score, 20, 25);
            ctx.fillText("Chờ hàng: " + (5 - shotsSinceLastRow), 310, 25);

            bubbles.forEach(b => {
                if (b.active) {
                    ctx.beginPath();
                    ctx.arc(b.x, b.y, b.radius, 0, Math.PI * 2);
                    ctx.fillStyle = b.color;
                    ctx.fill();
                    ctx.lineWidth = 2;
                    ctx.strokeStyle = "rgba(255,255,255,0.25)";
                    ctx.stroke();
                    ctx.closePath();
                }
            });

            if (!gameOver) {
                let angle = Math.atan2(mouseY - shooter.y, mouseX - shooter.x);
                let rx = shooter.x;
                let ry = shooter.y;
                let rdx = Math.cos(angle);
                let rdy = Math.sin(angle);

                ctx.beginPath();
                ctx.moveTo(rx, ry);

                for (let step = 0; step < 400; step++) {
                    rx += rdx * 3;
                    ry += rdy * 3;

                    if (rx - radius < 0) {
                        rx = radius;
                        rdx *= -1;
                        ctx.lineTo(rx, ry);
                    } else if (rx + radius > canvas.width) {
                        rx = canvas.width - radius;
                        rdx *= -1;
                        ctx.lineTo(rx, ry);
                    }

                    if (ry <= 25) {
                        ctx.lineTo(rx, ry);
                        break;
                    }

                    let hit = false;
                    for (let b of bubbles) {
                        if (b.active && Math.hypot(rx - b.x, ry - b.y) < radius * 1.8) {
                            hit = true;
                            break;
                        }
                    }
                    if (hit) {
                        ctx.lineTo(rx, ry);
                        break;
                    }
                }
                ctx.lineTo(rx, ry);
                ctx.strokeStyle = "rgba(255, 255, 255, 0.6)";
                ctx.setLineDash([4, 4]);
                ctx.stroke();
                ctx.setLineDash([]);
            }

            if (bullet) {
                ctx.beginPath();
                ctx.arc(bullet.x, bullet.y, radius, 0, Math.PI * 2);
                ctx.fillStyle = bullet.color;
                ctx.fill();
                ctx.closePath();
            }

            ctx.beginPath();
            ctx.arc(shooter.x, shooter.y, shooter.radius, 0, Math.PI * 2);
            ctx.fillStyle = shooter.color;
            ctx.fill();
            ctx.lineWidth = 3;
            ctx.strokeStyle = "#FFF";
            ctx.stroke();
            ctx.closePath();

            if (gameOver) {
                ctx.fillStyle = "rgba(0, 0, 0, 0.85)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = "#FF5964";
                ctx.font = "bold 32px sans-serif";
                ctx.textAlign = "center";
                ctx.fillText("GAME OVER", canvas.width / 2, canvas.height / 2 - 20);

                ctx.fillStyle = "#FFFFFF";
                ctx.font = "18px sans-serif";
                ctx.fillText("Tổng điểm: " + score, canvas.width / 2, canvas.height / 2 + 20);
                ctx.fillText("Click chuột để chơi lại", canvas.width / 2, canvas.height / 2 + 60);
                ctx.textAlign = "left";
            }
        }

        function loop() {
            update();
            draw();
            requestAnimationFrame(loop);
        }
        loop();
    </script>
</body>
</html>'''

encoded_html = base64.b64encode(html_code.encode("utf-8")).decode("utf-8")
components.iframe(f"data:text/html;base64,{encoded_html}", height=580)
