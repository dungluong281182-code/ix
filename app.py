import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="PIXEL ESCAPE 2D", layout="centered")

# Nhúng Font chữ Pixel (Press Start 2P) cho Streamlit
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Press Start 2P', monospace !important;
    }
    h1, h2, h3, p, span, div {
        font-family: 'Press Start 2P', monospace !important;
    }
    .stApp {
        background-color: #0d0d11;
        color: #00ff66;
    }
    </style>
""", unsafe_allow_html=True)

st.title("PIXEL ESCAPE 2D")
st.text("DIEU KHIEN: PHIM MUI TEN (UP, DOWN, LEFT, RIGHT)")

# Code HTML5 Canvas + JavaScript Pixel Pure
game_html = """
<!DOCTYPE html>
<html>
<head>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Press Start 2P', monospace;
        }
        body {
            background-color: #0d0d11;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            color: #00ff66;
            overflow: hidden;
        }
        #gameContainer {
            text-align: center;
        }
        canvas {
            border: 4px solid #00ff66;
            background-color: #050508;
            image-rendering: pixelated;
            image-rendering: crisp-edges;
            box-shadow: 0 0 15px rgba(0, 255, 102, 0.2);
        }
        .info {
            margin-top: 15px;
            font-size: 12px;
            color: #ffffff;
            letter-spacing: 1px;
        }
        #score {
            color: #ff0055;
        }
    </style>
</head>
<body>
    <div id="gameContainer">
        <canvas id="gameCanvas" width="480" height="360"></canvas>
        <div class="info">
            SURVIVAL TIME: <span id="score">0</span>S
        </div>
    </div>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");
        const scoreEl = document.getElementById("score");

        // Tat blur anh de giu net pixel
        ctx.imageSmoothingEnabled = false;

        let gameOver = false;
        let startTime = Date.now();
        let score = 0;
        let frameCount = 0;

        const keys = {};
        window.addEventListener("keydown", e => keys[e.key] = true);
        window.addEventListener("keyup", e => keys[e.key] = false);

        // Nhan vat chinh (Kich thuoc 16x16 pixel)
        const player = {
            x: 232,
            y: 172,
            size: 16,
            speed: 2.5
        };

        // Quai vat Ac Ma (Kich thuoc 16x16 pixel)
        const monster = {
            x: 20,
            y: 20,
            size: 16,
            speed: 1.6
        };

        // Ma tran Pixel ve Nhan Vat (1 = diem anh xanh, 0 = trong suot)
        const playerSprite = [
            [0,0,1,1,1,1,0,0],
            [0,1,1,1,1,1,1,0],
            [1,1,0,1,1,0,1,1],
            [1,1,1,1,1,1,1,1],
            [1,1,1,1,1,1,1,1],
            [0,1,1,1,1,1,1,0],
            [0,1,0,0,0,0,1,0],
            [1,0,0,0,0,0,0,1]
        ];

        // Ma tran Pixel ve Quai Vat Ac Ma (1 = diem anh do)
        const monsterSprite = [
            [1,0,0,0,0,0,0,1],
            [1,1,0,0,0,0,1,1],
            [0,1,1,1,1,1,1,0],
            [1,1,0,1,1,0,1,1],
            [1,1,1,1,1,1,1,1],
            [1,0,1,1,1,1,0,1],
            [1,0,1,0,0,1,0,1],
            [0,1,0,0,0,0,1,0]
        ];

        // Hàm vẽ Sprite từng điểm Pixel (8x8 nhân đôi lên 16x16)
        function drawPixelSprite(sprite, posX, posY, color, animOffset = 0) {
            const pixelSize = 2; // Moi o ma tran = 2x2 pixel tren canvas
            ctx.fillStyle = color;
            for (let r = 0; r < 8; r++) {
                for (let c = 0; c < 8; c++) {
                    if (sprite[r][c] === 1) {
                        ctx.fillRect(posX + (c * pixelSize), posY + (r * pixelSize) + animOffset, pixelSize, pixelSize);
                    }
                }
            }
        }

        function update() {
            if (gameOver) return;

            frameCount++;

            if (keys["ArrowUp"] && player.y > 0) player.y -= player.speed;
            if (keys["ArrowDown"] && player.y < canvas.height - player.size) player.y += player.speed;
            if (keys["ArrowLeft"] && player.x > 0) player.x -= player.speed;
            if (keys["ArrowRight"] && player.x < canvas.width - player.size) player.x += player.speed;

            // AI Quai vat duoi theo
            let dx = player.x - monster.x;
            let dy = player.y - monster.y;
            let dist = Math.sqrt(dx * dx + dy * dy);

            if (dist > 0) {
                monster.x += (dx / dist) * monster.speed;
                monster.y += (dy / dist) * monster.speed;
            }

            score = Math.floor((Date.now() - startTime) / 1000);
            scoreEl.innerText = score;

            // Xử lý va chạm
            if (
                player.x < monster.x + monster.size &&
                player.x + player.size > monster.x &&
                player.y < monster.y + monster.size &&
                player.y + player.size > monster.y
            ) {
                gameOver = true;
            }
        }

        function draw() {
            ctx.fillStyle = "#050508";
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Ve luoi nen Pixel Retro
            ctx.strokeStyle = "#12121c";
            ctx.lineWidth = 1;
            for (let x = 0; x < canvas.width; x += 16) {
                ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
            }
            for (let y = 0; y < canvas.height; y += 16) {
                ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
            }

            // Hieu ung nhuc nhich (Bobbing animation) cho phong cach 8-bit
            let playerAnim = (Math.floor(frameCount / 15) % 2 === 0) ? 0 : -1;
            let monsterAnim = (Math.floor(frameCount / 10) % 2 === 0) ? 0 : 1;

            // Ve Nhan vat (Xanh la Pixel) & Quai vat (Do Pixel)
            drawPixelSprite(playerSprite, player.x, player.y, "#00ff66", playerAnim);
            drawPixelSprite(monsterSprite, monster.x, monster.y, "#ff0055", monsterAnim);

            // Game Over Screen
            if (gameOver) {
                ctx.fillStyle = "rgba(5, 5, 8, 0.9)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = "#ff0055";
                ctx.font = "16px 'Press Start 2P'";
                ctx.textAlign = "center";
                ctx.fillText("GAME OVER", canvas.width / 2, canvas.height / 2 - 15);

                ctx.fillStyle = "#ffffff";
                ctx.font = "8px 'Press Start 2P'";
                ctx.fillText("PRESS F5 TO RESTART", canvas.width / 2, canvas.height / 2 + 20);
            }
        }

        function gameLoop() {
            update();
            draw();
            requestAnimationFrame(gameLoop);
        }

        gameLoop();
    </script>
</body>
</html>
"""

components.html(game_html, height=450)

st.sidebar.title("BANG DIEU KHAN")
st.sidebar.text("Nhan vat: Xanh La")
st.sidebar.text("Quai vat: Do")
st.sidebar.text("Nhiem vu: Song sot")
