import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Game Bắn Bóng", layout="centered")

st.title("🎯 Game Bắn Bóng (Bubble Shooter)")
st.write("Dùng chuột để ngắm và click để bắn bóng!")

# Code HTML5 Canvas + JavaScript cho game bắn bóng trực quan
game_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        canvas {
            background: #222;
            display: block;
            margin: 0 auto;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        }
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="400" height="500"></canvas>
    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        let score = 0;
        const colors = ["#FF5733", "#33FF57", "#3357FF", "#F3FF33"];
        
        let shooter = { x: 200, y: 460, radius: 15, color: colors[0] };
        let bullet = null;
        
        // Tạo một số quả bóng ở trên
        let bubbles = [];
        for (let r = 0; r < 4; r++) {
            for (let c = 0; c < 8; c++) {
                bubbles.push({
                    x: 30 + c * 45,
                    y: 40 + r * 40,
                    radius: 15,
                    color: colors[Math.floor(Math.random() * colors.length)],
                    active: true
                });
            }
        }

        let mouseX = 200, mouseY = 0;
        canvas.addEventListener("mousemove", (e) => {
            const rect = canvas.getBoundingClientRect();
            mouseX = e.clientX - rect.left;
            mouseY = e.clientY - rect.top;
        });

        canvas.addEventListener("click", () => {
            if (!bullet) {
                let angle = Math.atan2(mouseY - shooter.y, mouseX - shooter.x);
                bullet = {
                    x: shooter.x,
                    y: shooter.y,
                    dx: Math.cos(angle) * 8,
                    dy: Math.sin(angle) * 8,
                    color: shooter.color
                };
                shooter.color = colors[Math.floor(Math.random() * colors.length)];
            }
        });

        function update() {
            if (bullet) {
                bullet.x += bullet.dx;
                bullet.y += bullet.dy;

                // Chạm tường bật lại
                if (bullet.x - 15 < 0 || bullet.x + 15 > canvas.width) bullet.dx *= -1;

                // Va chạm với bóng
                bubbles.forEach(b => {
                    if (b.active) {
                        let dist = Math.hypot(bullet.x - b.x, bullet.y - b.y);
                        if (dist < 30) {
                            if (bullet.color === b.color) {
                                b.active = false;
                                score += 10;
                            }
                            bullet = null;
                        }
                    }
                });

                if (bullet && bullet.y < 0) bullet = null;
            }
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Vẽ điểm
            ctx.fillStyle = "#FFF";
            ctx.font = "16px Arial";
            ctx.fillText("Điểm: " + score, 10, 25);

            // Vẽ các quả bóng
            bubbles.forEach(b => {
                if (b.active) {
                    ctx.beginPath();
                    ctx.arc(b.x, b.y, b.radius, 0, Math.PI * 2);
                    ctx.fillStyle = b.color;
                    ctx.fill();
                    ctx.closePath();
                }
            });

            // Vẽ hướng ngắm
            ctx.beginPath();
            ctx.moveTo(shooter.x, shooter.y);
            ctx.lineTo(mouseX, mouseY);
            ctx.strokeStyle = "rgba(255, 255, 255, 0.3)";
            ctx.stroke();

            // Vẽ đạn đang bay
            if (bullet) {
                ctx.beginPath();
                ctx.arc(bullet.x, bullet.y, 15, 0, Math.PI * 2);
                ctx.fillStyle = bullet.color;
                ctx.fill();
                ctx.closePath();
            }

            // Vẽ pháo bắn
            ctx.beginPath();
            ctx.arc(shooter.x, shooter.y, shooter.radius, 0, Math.PI * 2);
            ctx.fillStyle = shooter.color;
            ctx.fill();
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

components.html(game_code, height=520)
