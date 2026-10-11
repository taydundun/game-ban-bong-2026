import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Game Bắn Bóng", layout="centered")

st.title("🎯 Game Bắn Bóng (Bubble Shooter)")
st.write("Ngắm bằng chuột, Click bắn bóng cùng màu để ăn điểm và tạo hàng bóng mới!")

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
        const rows = 4;
        const cols = 9;
        const radius = 18;
        const rowHeight = 36;

        // Khởi tạo lưới bóng ban đầu
        function initBubbles() {
            bubbles = [];
            for (let r = 0; r < rows; r++) {
                for (let c = 0; c < cols; c++) {
                    bubbles.push({
                        x: 35 + c * 45,
                        y: 40 + r * rowHeight,
                        radius: radius,
                        color: getRandomColor(),
                        active: true
                    });
                }
            }
        }
        initBubbles();

        // Thêm 1 hàng bóng mới lên trên cùng và đẩy các hàng cũ xuống
        function addNewRow() {
            // Đẩy tất cả bóng cũ xuống dưới 1 hàng
            bubbles.forEach(b => {
                b.y += rowHeight;
            });

            // Tạo hàng mới ở trên cùng
            for (let c = 0; c < cols; c++) {
                bubbles.push({
                    x: 35 + c * 45,
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

        function update() {
            if (bullet) {
                bullet.x += bullet.dx;
                bullet.y += bullet.dy;

                // Bật tường trái/phải
                if (bullet.x - radius < 0 || bullet.x + radius > canvas.width) {
                    bullet.dx *= -1;
                }

                // Chạm trần
                if (bullet.y - radius < 0) {
                    bullet = null;
                    return;
                }

                // Kiểm tra va chạm với bóng
                for (let b of bubbles) {
                    if (b.active) {
                        let dist = Math.hypot(bullet.x - b.x, bullet.y - b.y);
                        if (dist < radius * 2) {
                            // CƠ CHẾ: Cùng màu mới ăn được điểm!
                            if (bullet.color === b.color) {
                                b.active = false;
                                score += 10;
                                // Ăn thành công -> Thêm 1 hàng bóng mới chồng lên trên
                                addNewRow();
                            }
                            bullet = null; // Hủy đạn sau khi va chạm
                            break;
                        }
                    }
                }
            }
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Hiển thị điểm số
            ctx.fillStyle = "#FFFFFF";
            ctx.font = "bold 18px sans-serif";
            ctx.fillText("Điểm: " + score, 40, 25);

            // Vẽ các quả bóng
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

            // Viên đạn chuẩn bị bắn ở súng
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
