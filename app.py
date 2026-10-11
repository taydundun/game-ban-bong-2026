import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Game Bắn Bóng", layout="centered")

st.title("🎯 Game Bắn Bóng (Bubble Shooter)")
st.write("Bắn bóng dính vào lưới, khớp màu để nổ và chồng hàng mới!")

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
        const colors = ["#FF5964", "#35A7FF", "#38B000", "#FFE600", "#9B5DE5"];
        
        function getRandomColor() {
            return colors[Math.floor(Math.random() * colors.length)];
        }

        let shooter = { x: 220, y: 510, radius: 16, color: getRandomColor() };
        let bullet = null;
        let mouseX = 220, mouseY = 0;

        let bubbles = [];
        const rows = 4;
        const cols = 9;
        const radius = 18;
        const rowHeight = 32;
        const colWidth = 44;

        function initBubbles() {
            bubbles = [];
            for (let r = 0; r < rows; r++) {
                for (let c = 0; c < cols; c++) {
                    let xOffset = (r % 2 === 1) ? colWidth / 2 : 0;
                    bubbles.push({
                        row: r,
                        col: c,
                        x: 35 + c * colWidth + xOffset,
                        y: 35 + r * rowHeight,
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
            for (let c = 0; c < cols; c++) {
                bubbles.push({
                    row: 0,
                    col: c,
                    x: 35 + c * colWidth,
                    y: 35,
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
            // Tìm vị trí lưới gần nhất để đạn dính vào và trở thành một quả bóng mới
            let minDst = Infinity;
            let bestX = bullet.x;
            let bestY = bullet.y;
            let bestRow = 0;
            let bestCol = 0;

            // Tính toán vị trí bám vào lưới gần nhất
            let approxRow = Math.round((bullet.y - 35) / rowHeight);
            let approxCol = Math.round((bullet.x - 35) / colWidth);
            
            let xOffset = (approxRow % 2 === 1) ? colWidth / 2 : 0;
            let targetX = 35 + approxCol * colWidth + xOffset;
            let targetY = 35 + approxRow * rowHeight;

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

            // Kiểm tra lan truyền màu (Match-3+)
            checkMatch(newBubble, bColor);
            
            // Sau khi bắn xong và dính bóng, đẩy hàng mới xuống thêm thử thách
            addNewRow();
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
                            if (dist < colWidth * 1.35) {
                                visited.add(b);
                                queue.add ? queue.push(b) : queue.push(b);
                            }
                        }
                    }
                }
            }

            // Nếu cụm từ 2 hoặc 3 quả cùng màu trở lên thì nổ
            if (matched.length >= 2) {
                matched.forEach(b => {
                    b.active = false;
                    score += 15;
                });
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

                // Chạm trần trên cùng -> Dính bóng ngay
                if (bullet.y - radius <= 20) {
                    snapBulletToGrid(bullet.color);
                    bullet = null;
                    return;
                }

                // Va chạm với các quả bóng đang có trên lưới -> Dính bóng
                for (let b of bubbles) {
                    if (b.active) {
                        let dist = Math.hypot(bullet.x - b.x, bullet.y - b.y);
                        if (dist < radius * 1.8) {
                            snapBulletToGrid(bullet.color);
                            bullet = null;
                            break;
                        }
                    }
                }
            }
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Điểm số
            ctx.fillStyle = "#FFFFFF";
            ctx.font = "bold 18px sans-serif";
            ctx.fillText("Điểm: " + score, 25, 25);

            // Vẽ các bóng
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

            // Đường ngắm
            ctx.beginPath();
            ctx.moveTo(shooter.x, shooter.y);
            ctx.lineTo(mouseX, mouseY);
            ctx.setLineDash([4, 4]);
            ctx.strokeStyle = "rgba(255, 255, 255, 0.4)";
            ctx.stroke();
            ctx.setLineDash([]);

            // Đạn đang bay
            if (bullet) {
                ctx.beginPath();
                ctx.arc(bullet.x, bullet.y, radius, 0, Math.PI * 2);
                ctx.fillStyle = bullet.color;
                ctx.fill();
                ctx.closePath();
            }

            // Súng bắn phía dưới
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
