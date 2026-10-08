import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="PIXEL DINO RUNNER", layout="centered")

# Nhúng Font chữ Pixel Retro
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

st.title("DINO RUNNER PIXEL 2D")
st.text("DIEU KHIEN: PRESS [SPACE] OR [UP] TO JUMP")

# Game HTML5 Canvas + JavaScript Endless Runner
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
            outline: none;
        }
        .info {
            margin-top: 15px;
            font-size: 10px;
            color: #ffffff;
            letter-spacing: 1px;
            display: flex;
            justify-content: space-between;
            width: 480px;
        }
        .score-val { color: #00ff66; }
        .hi-val { color: #ff0055; }
    </style>
</head>
<body>
    <div id="gameContainer">
        <canvas id="gameCanvas" width="480" height="240" tabindex="0"></canvas>
        <div class="info">
            <div>HI: <span id="highScore" class="hi-val">00000</span></div>
            <div>SCORE: <span id="score" class="score-val">00000</span></div>
        </div>
    </div>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");
        const scoreEl = document.getElementById("score");
        const highScoreEl = document.getElementById("highScore");

        ctx.imageSmoothingEnabled = false;
        canvas.focus();

        // Tu dong focus vao canvas khi click chuot
        window.addEventListener("click", () => canvas.focus());

        let gameOver = false;
        let gameStarted = false;
        let score = 0;
        let highScore = 0;
        let frameCount = 0;
        let gameSpeed = 3.5;

        // Trong luc (Gravity) & Mat dat
        const groundY = 190;
        
        // Khung long Pixel (Dino)
        const dino = {
            x: 40,
            y: groundY - 24,
            width: 24,
            height: 24,
            vy: 0,
            gravity: 0.6,
            jumpPower: -10.5,
            isJumping: false
        };

        // Danh sach vat cản (Xuong rong, Chim)
        let obstacles = [];
        let clouds = [
            { x: 100, y: 30, speed: 0.5 },
            { x: 300, y: 50, speed: 0.7 },
            { x: 420, y: 20, speed: 0.4 }
        ];

        // Sprite 8x8 Ma tran Khung Long
        const dinoSprite1 = [
            [0,0,0,1,1,1,1,0],
            [0,0,0,1,0,1,1,0],
            [0,0,0,1,1,1,1,0],
            [0,0,0,1,1,1,0,0],
            [1,0,1,1,1,1,0,0],
            [1,1,1,1,1,0,0,0],
            [0,1,1,1,1,1,0,0],
            [0,0,1,0,0,1,0,0]
        ];

        const dinoSprite2 = [
            [0,0,0,1,1,1,1,0],
            [0,0,0,1,0,1,1,0],
            [0,0,0,1,1,1,1,0],
            [0,0,0,1,1,1,0,0],
            [1,0,1,1,1,1,0,0],
            [1,1,1,1,1,0,0,0],
            [0,1,1,1,1,1,0,0],
            [0,0,0,1,1,0,0,0]
        ];

        // Sprite Xuong rong
        const cactusSprite = [
            [0,0,1,1,0,0,0,0],
            [0,0,1,1,0,1,1,0],
            [1,1,1,1,0,1,1,0],
            [1,1,1,1,1,1,1,0],
            [0,0,1,1,1,1,0,0],
            [0,0,1,1,0,0,0,0],
            [0,0,1,1,0,0,0,0],
            [0,0,1,1,0,0,0,0]
        ];

        // Sprite Chim Pterodactyl
        const birdSprite1 = [
            [0,0,0,1,1,0,0,0],
            [0,0,1,1,1,1,0,0],
            [1,1,1,1,1,1,1,1],
            [0,0,0,1,1,1,0,0],
            [0,0,0,0,1,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0]
        ];

        function drawPixelMatrix(matrix, posX, posY, pixelSize, color) {
            ctx.fillStyle = color;
            for (let r = 0; r < 8; r++) {
                for (let c = 0; c < 8; c++) {
                    if (matrix[r][c] === 1) {
                        ctx.fillRect(posX + (c * pixelSize), posY + (r * pixelSize), pixelSize, pixelSize);
                    }
                }
            }
        }

        function resetGame() {
            gameOver = false;
            gameStarted = true;
            score = 0;
            frameCount = 0;
            gameSpeed = 3.5;
            dino.y = groundY - 24;
            dino.vy = 0;
            dino.isJumping = false;
            obstacles = [];
        }

        function jump() {
            if (!gameStarted) {
                resetGame();
                return;
            }
            if (gameOver) {
                resetGame();
                return;
            }
            if (!dino.isJumping) {
                dino.vy = dino.jumpPower;
                dino.isJumping = true;
            }
        }

        // Bat su kien ban phim
        window.addEventListener("keydown", (e) => {
            if (e.code === "Space" || e.code === "ArrowUp") {
                e.preventDefault();
                jump();
            }
            if (e.code === "KeyR" && gameOver) {
                resetGame();
            }
        });

        function spawnObstacle() {
            const minGap = 120;
            const lastObstacle = obstacles[obstacles.length - 1];
            if (!lastObstacle || (canvas.width - lastObstacle.x) > (minGap + Math.random() * 150)) {
                const isBird = Math.random() > 0.7 && score > 150;
                if (isBird) {
                    obstacles.push({
                        type: 'bird',
                        x: canvas.width,
                        y: groundY - 36 - (Math.random() * 20),
                        width: 24,
                        height: 18
                    });
                } else {
                    obstacles.push({
                        type: 'cactus',
                        x: canvas.width,
                        y: groundY - 24,
                        width: 18,
                        height: 24
                    });
                }
            }
        }

        function update() {
            if (!gameStarted || gameOver) return;

            frameCount++;
            score = Math.floor(frameCount / 4);
            if (score > highScore) {
                highScore = score;
            }

            // Tang toc do theo thoi gian
            if (frameCount % 300 === 0) {
                gameSpeed += 0.3;
            }

            // Vat ly Khung long
            dino.vy += dino.gravity;
            dino.y += dino.vy;

            if (dino.y >= groundY - dino.height) {
                dino.y = groundY - dino.height;
                dino.vy = 0;
                dino.isJumping = false;
            }

            // May troi
            clouds.forEach(c => {
                c.x -= c.speed;
                if (c.x < -40) c.x = canvas.width + 10;
            });

            // Sinh va Di chuyen Vat can
            spawnObstacle();

            for (let i = obstacles.length - 1; i >= 0; i--) {
                let obs = obstacles[i];
                obs.x -= gameSpeed;

                // Xu ly va cham (AABB Collision)
                let padding = 4;
                if (
                    dino.x + padding < obs.x + obs.width - padding &&
                    dino.x + dino.width - padding > obs.x + padding &&
                    dino.y + padding < obs.y + obs.height - padding &&
                    dino.y + dino.height - padding > obs.y + padding
                ) {
                    gameOver = true;
                }

                if (obs.x < -30) {
                    obstacles.splice(i, 1);
                }
            }

            // Cap nhat HUD
            scoreEl.innerText = String(score).padStart(5, '0');
            highScoreEl.innerText = String(highScore).padStart(5, '0');
        }

        function draw() {
            ctx.fillStyle = "#050508";
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Ve May
            clouds.forEach(c => {
                ctx.fillStyle = "#222233";
                ctx.fillRect(c.x, c.y, 24, 8);
                ctx.fillRect(c.x + 4, c.y - 4, 16, 4);
            });

            // Ve Duong Mat Dat Pixel
            ctx.strokeStyle = "#00ff66";
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(0, groundY);
            ctx.lineTo(canvas.width, groundY);
            ctx.stroke();

            // Ve Cac Chieu Xoay Mat Dat Pixel
            let groundOffset = (frameCount * gameSpeed) % 16;
            ctx.fillStyle = "#005522";
            for (let x = -groundOffset; x < canvas.width; x += 16) {
                ctx.fillRect(x, groundY + 6, 4, 2);
                ctx.fillRect(x + 8, groundY + 12, 2, 2);
            }

            // Ve Khung Long Pixel (Dino)
            let currentDinoSprite = dino.isJumping 
                ? dinoSprite1 
                : ((Math.floor(frameCount / 6) % 2 === 0) ? dinoSprite1 : dinoSprite2);
            
            drawPixelMatrix(currentDinoSprite, dino.x, dino.y, 3, "#00ff66");

            // Ve Vat Can
            obstacles.forEach(obs => {
                if (obs.type === 'cactus') {
                    drawPixelMatrix(cactusSprite, obs.x, obs.y, 3, "#00ff66");
                } else {
                    drawPixelMatrix(birdSprite1, obs.x, obs.y, 3, "#ff0055");
                }
            });

            // Man hinh Bat Dau & Game Over
            if (!gameStarted) {
                ctx.fillStyle = "#00ff66";
                ctx.font = "12px 'Press Start 2P'";
                ctx.textAlign = "center";
                ctx.fillText("PRESS [SPACE] TO START", canvas.width / 2, canvas.height / 2);
            } else if (gameOver) {
                ctx.fillStyle = "rgba(5, 5, 8, 0.85)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = "#ff0055";
                ctx.font = "14px 'Press Start 2P'";
                ctx.textAlign = "center";
                ctx.fillText("GAME OVER", canvas.width / 2, canvas.height / 2 - 10);

                ctx.fillStyle = "#ffffff";
                ctx.font = "8px 'Press Start 2P'";
                ctx.fillText("PRESS [SPACE] OR [R] TO RESTART", canvas.width / 2, canvas.height / 2 + 20);
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

components.html(game_html, height=320)

st.sidebar.title("THONG TIN GAME")
st.sidebar.text("Game: Pixel Dino Runner")
st.sidebar.text("Nhai: Space / ArrowUp")
st.sidebar.text("Choi lai: Space / R")
