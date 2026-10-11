import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Game Bắn Bóng", layout="centered")

st.title("🎯 Game Bắn Bóng (Bubble Shooter)")
st.write("Di chuyển chuột để ngắm và Click chuột trái để bắn bóng!")

# Code HTML5 Canvas + JavaScript đã fix lỗi đơ/kẹt đạn
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
    <canvas id="gameCanvas" width="440" height="520"></canvas>
    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        let score = 0;
        const colors = ["#FF5964", "#35A7FF", "#38B000", "#FFE600", "#9B5DE5"];
        
        function getRandomColor() {
            return colors[Math.floor(Math.random() * colors.length)];
        }

        let shooter = { x: 220, y: 480, radius: 16, color: getRandomColor() };
        let bullet = null;
        let mouseX = 220, mouseY = 0;

        // Khởi tạo lưới bóng
        let bubbles = [];
        const rows = 5;
        const cols = 9;
        const radius = 18;

        function initBubbles() {
            bubbles = [];
            for (let r = 0; r < rows; r++) {
                for (let c = 0; c < cols; c++) {
                    bubbles.push({
                        x: 40 + c * 44,
                        y: 40 + r * 40,
                        radius: radius,
                        color: getRandomColor(),
                        active: true
                    });
                }
            }
        }
        initBubbles();

        canvas.addEventListener("mousemove", (e) => {
            const rect = canvas.getBoundingClientRect();
            mouseX = e.clientX - rect.left;
            mouseY = e.clientY - rect.top;
        });

        canvas.addEventListener("click", () => {
            if (!bullet) {
                let angle = Math.atan2(mouseY - shooter.y, mouseX - shooter.x);
                // Giới hạn không cho bắn ngược xuống dưới
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

        function update() {
            if (bullet) {
                bullet.x += bullet.dx;
                bullet.y += bullet.dy;

                // Bật tường trái/phải
                if (bullet.x - radius < 0 || bullet.x + radius > canvas.width) {
                    bullet.dx *= -1;
                }

                // Chạm trần trên cùng -> hủy đạn
                if (bullet.y - radius < 0) {
                    bullet = null;
                    return;
                }

                // Va chạm với các quả bóng
                if (bullet) {
                    for (let b of bubbles) {
                        if (b.active) {
                            let dist = Math.hypot(bullet.x - b.x, bullet.y - b.y);
                            if (dist < radius * 2) {
                                // Xóa bóng nếu trúng
                                b.active = false;
                                score += 10;
                                bullet = null; // Reset đạn để bắn tiếp
                                break;
                            }
                        }
                    }
                }
            }
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Bảng điểm
            ctx.fillStyle = "#FFFFFF";
            ctx.font = "bold 18px Segoe UI, sans-serif";
            ctx.fillText("Điểm: " + score, 15, 25);

            // Vẽ các quả bóng mục tiêu
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

            // Vẽ đường định hướng ngắm
            ctx.beginPath();
            ctx.moveTo(shooter.x, shooter.y);
            ctx.lineTo(mouseX, mouseY);
            ctx.setLineDash([4, 4]);
            ctx.strokeStyle = "rgba(255, 255, 255, 0.4)";
            ctx.stroke();
            ctx.setLineDash([]);

            // Vẽ đạn đang bay
            if (bullet) {
                ctx.beginPath();
                ctx.arc(bullet.x, bullet.y, radius, 0, Math.PI * 2);
                ctx.fillStyle = bullet.color;
                ctx.fill();
                ctx.closePath();
            }

            // Vẽ súng/bóng chuẩn bị bắn
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

components.html(game_code, height=540)
