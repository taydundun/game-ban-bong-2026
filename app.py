import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Game Bắn Bóng", layout="centered")

st.title("🎯 Game Bắn Bóng (Bubble Shooter)")
st.write("Bắn trúng bóng cùng màu để làm nổ cả cụm bóng liên kết!")

game_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; padding: 0; text-align: center; font-family: sans-serif; }
        canvas {
            background: #1e1e2e;
            display: block;
            margin: 0 auto;
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
        const colors = ["#FF5964", "#35A7FF", "#38B000", "#FFE600", "#9B5DE5"];
        
        function getRandomColor() {
            return colors[Math.floor(Math.random() * colors.length)];
        }

        let shooter = { x: 220, y: 500, radius: 16, color: getRandomColor() };
        let bullet = null;
        let mouseX = 220, mouseY = 0;

        let bubbles = [];
        const rows = 5;
        const cols = 9;
        const radius = 18;
        const rowHeight = 36;
        const colWidth = 44;

        function initBubbles() {
            bubbles = [];
            for (let r = 0; r < rows; r++) {
                for (let c = 0; c < cols; c++) {
                    bubbles.push({
                        row: r,
                        col: c,
                        x: 35 + c * colWidth,
                        y: 40 + r * rowHeight,
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
            });

            for (let c = 0; c < cols; c++) {
                bubbles.push({
                    row: 0,
                    col: c,
                    x: 35 + c * colWidth,
                    y: 40,
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

        // Thuật toán lan truyền tìm các quả bóng cùng màu liền kề (Flood Fill)
        function popCluster(startBubble, targetColor) {
            let visited = new Set();
            let queue = [startBubble];
            let matched = [];

            visited.add(startBubble);

            while (queue.length > 0) {
                let current = queue.shift();
                if (current.color === targetColor && current.active) {
                    matched.push(current);

                    // Tìm các bóng xung quanh gần nó
                    for (let b of bubbles) {
                        if (b.active && !visited.has(b)) {
                            let dist = Math.hypot(current.x - b.x, current.y - b.y);
                            if (dist < colWidth * 1.3) { // Khoảng cách hàng xóm
                                visited.add(b);
                                queue.push(b);
                            }
                        }
                    }
                }
            }

            // Nếu cụm từ 2 quả trở lên thì cho nổ hết
            if (matched.length >= 1) {
                matched.forEach(b => {
                    b.active = false;
                    score += 10;
                });
                addNewRow(); // Thêm hàng mới khi ăn được bóng
            }
        }

        function update() {
            if (bullet) {
                bullet.x += bullet.dx;
                bullet.y += bullet.dy;

                if (bullet.x - radius < 0 || bullet.x + radius > canvas.width) {
                    bullet.dx *= -1;
                }

                if (bullet.y - radius < 0) {
                    bullet = null;
                    return;
                }

                for (let b of bubbles) {
                    if (b.active) {
                        let dist = Math.hypot(bullet.x - b.x, bullet.y - b.y);
                        if (dist < radius * 2) {
                            popCluster(b, bullet.color);
                            bullet = null;
                            break;
                        }
                    }
                }
            }
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            ctx.fillStyle = "#FFFFFF";
            ctx.font = "bold 18px sans-serif";
            ctx.fillText("Điểm: " + score, 40, 25);

            bubbles.forEach(b => {
                if (b.active) {
                    ctx.beginPath();
                    ctx.arc(b.x, b.y, b.radius, 0, Math.PI * 2);
                    ctx.fillStyle = b.color;
                    ctx.fill();
                    ctx.lineWidth = 2;
                    ctx.strokeStyle = "rgba(255,255,255,0.2)";
                    ctx.stroke();
                    ctx.closePath();
                }
            });

            ctx.beginPath();
            ctx.moveTo(shooter.x, shooter.y);
            ctx.lineTo(mouseX, mouseY);
            ctx.setLineDash([4, 4]);
            ctx.strokeStyle = "rgba(255, 255, 255, 0.4)";
            ctx.stroke();
            ctx.setLineDash([]);

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
        }

        function loop() {
            update();
            draw();
            requestAnimationFrame(loop);
        }
        loop();
    </script>
</body>
</html>
"""

components.html(game_code, height=560)
