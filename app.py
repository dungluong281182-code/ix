import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="PIXEL DINO RUNNER - 4 SEASONS", layout="centered")

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
        background-color: #f0f4f8;
        color: #2d3748;
    }
    </style>
""", unsafe_allow_html=True)

st.title("DINO RUNNER: 4 SEASONS")
st.text("JUMP: [SPACE] / [UP] | RESTART: [SPACE] / [R]")

# Game HTML5 Canvas + JavaScript 4 Seasons Runner
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
            background-color: #e2e8f0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            overflow: hidden;
        }
        #gameContainer {
            text-align: center;
        }
        canvas {
            border: 4px solid #2d3748;
            image-rendering: pixelated;
            image-rendering: crisp-edges;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
            outline: none;
        }
        .info {
            margin-top: 15px;
            font-size: 10px;
            color: #2d3748;
            letter-spacing: 1px;
            display: flex;
            justify-content: space-between;
            width: 480px;
            font-weight: bold;
        }
        .score-val { color: #2b6cb0; }
        .hi-val { color: #c53030; }
        .season-val { color: #d69e2e; }
    </style>
</head>
<body>
    <div id="gameContainer">
        <canvas id="gameCanvas" width="480" height="240" tabindex="0"></canvas>
        <div class="info">
            <div>SEASON: <span id="seasonName" class="season-val">SPRING</span></div>
            <div>HI: <span id="highScore" class="hi-val">00000</span></div>
            <div>SCORE: <span id="score" class="score-val">00000</span></div>
        </div>
    </div>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");
        const scoreEl = document.getElementById("score");
        const highScoreEl = document.getElementById("highScore");
        const seasonNameEl = document.getElementById("seasonName");

        ctx.imageSmoothingEnabled = false;
        canvas.focus();

        // Tải nhạc nền Unity - TheFatRat
        const bgMusic = new Audio("https://ia801503.us.archive.org/15/items/TheFatRatUnity/TheFatRat%20-%20Unity.mp3");
        bgMusic.loop = true;
        bgMusic.volume = 0.5; // Mức âm lượng 50%

        function playMusic() {
            if (bgMusic.paused) {
                bgMusic.play().catch(e => console.log("Audio play error:", e));
            }
        }

        window.addEventListener("click", () => {
            canvas.focus();
            playMusic();
        });

        let gameOver = false;
        let gameStarted = false;
        let score = 0;
        let highScore = 0;
        let frameCount = 0;
        let gameSpeed = 3.5;

        // Bảng màu & thiết lập cho 4 mùa
        const SEASONS = {
            SPRING: { id: "SPRING", name: "SPRING", sky: "#bae6fd", ground: "#22c55e", dino: "#15803d", cactus: "#166534", particleColor: "#f472b6" },
            SUMMER: { id: "SUMMER", name: "SUMMER", sky: "#fef08a", ground: "#eab308", dino: "#15803d", cactus: "#854d0e", particleColor: "#f97316" },
            AUTUMN: { id: "AUTUMN", name: "AUTUMN", sky: "#ffedd5", ground: "#f97316", dino: "#9a3412", cactus: "#7c2d12", particleColor: "#ea580c" },
            WINTER: { id: "WINTER", name: "WINTER", sky: "#e2e8f0", ground: "#f8fafc", dino: "#1e293b", cactus: "#475569", particleColor: "#ffffff" }
        };

        let currentSeason = SEASONS.SPRING;

        const groundY = 190;
        
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

        let obstacles = [];
        let particles = [];
        let clouds = [
            { x: 100, y: 30, speed: 0.5 },
            { x: 300, y: 50, speed: 0.7 },
            { x: 420, y: 20, speed: 0.4 }
        ];

        // Khởi tạo các hạt thời tiết
        for(let i = 0; i < 25; i++) {
            particles.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                size: Math.random() * 2 + 1,
                speedY: Math.random() * 1 + 0.5,
                speedX: Math.random() * 1 - 0.5
            });
        }

        // Sprite 8x8 Ma trận Pixel
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

        const flowerSprite = [
            [0,1,1,0,0,1,1,0],
            [1,1,1,1,1,1,1,1],
            [1,1,0,1,1,0,1,1],
            [0,1,1,1,1,1,1,0],
            [0,0,0,1,1,0,0,0],
            [0,1,0,1,1,0,1,0],
            [0,0,1,1,1,1,0,0],
            [0,0,0,1,1,0,0,0]
        ];

        const birdSprite = [
            [0,0,0,1,1,0,0,0],
            [0,0,1,1,1,1,0,0],
            [1,1,1,1,1,1,1,1],
            [0,0,0,1,1,1,0,0],
            [0,0,0,0,1,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0]
        ];

        const sunSprite = [
            [0,1,0,1,1,0,1,0],
            [1,0,0,1,1,0,0,1],
            [0,0,1,1,1,1,0,0],
            [1,1,1,1,1,1,1,1],
            [1,1,1,1,1,1,1,1],
            [0,0,1,1,1,1,0,0],
            [1,0,0,1,1,0,0,1],
            [0,1,0,1,1,0,1,0]
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
            currentSeason = SEASONS.SPRING;
            
            // Tiếp tục phát nhạc nếu đang bị tạm dừng khi thua
            playMusic();
        }

        function jump() {
            playMusic();
            if (!gameStarted || gameOver) {
                resetGame();
                return;
            }
            if (!dino.isJumping) {
                dino.vy = dino.jumpPower;
                dino.isJumping = true;
            }
        }

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
            const minGap = 130;
            const lastObstacle = obstacles[obstacles.length - 1];

            if (!lastObstacle || (canvas.width - lastObstacle.x) > (minGap + Math.random() * 140)) {
                let rand = Math.random();

                if (currentSeason.id === "SPRING" && rand < 0.4) {
                    obstacles.push({
                        type: 'flower',
                        x: canvas.width,
                        y: groundY - 24,
                        width: 20,
                        height: 24
                    });
                } else if (rand > 0.65 && score > 80) {
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
            if (score > highScore) highScore = score;

            // Chuyển đổi 4 mùa theo số điểm (Mỗi 150 điểm đổi mùa)
            let seasonIndex = Math.floor(score / 150) % 4;
            if (seasonIndex === 0) currentSeason = SEASONS.SPRING;
            else if (seasonIndex === 1) currentSeason = SEASONS.SUMMER;
            else if (seasonIndex === 2) currentSeason = SEASONS.AUTUMN;
            else if (seasonIndex === 3) currentSeason = SEASONS.WINTER;

            if (frameCount % 300 === 0) gameSpeed += 0.25;

            // Vật lý Khủng long
            dino.vy += dino.gravity;
            dino.y += dino.vy;

            if (dino.y >= groundY - dino.height) {
                dino.y = groundY - dino.height;
                dino.vy = 0;
                dino.isJumping = false;
            }

            // Mây & Hạt thời tiết
            clouds.forEach(c => {
                c.x -= c.speed;
                if (c.x < -40) c.x = canvas.width + 10;
            });

            particles.forEach(p => {
                p.y += p.speedY;
                p.x += p.speedX;
                if (p.y > canvas.height) {
                    p.y = -5;
                    p.x = Math.random() * canvas.width;
                }
            });

            // Sinh & Di chuyển Vật cản
            spawnObstacle();

            for (let i = obstacles.length - 1; i >= 0; i--) {
                let obs = obstacles[i];
                obs.x -= gameSpeed;

                let padding = 4;
                if (
                    dino.x + padding < obs.x + obs.width - padding &&
                    dino.x + dino.width - padding > obs.x + padding &&
                    dino.y + padding < obs.y + obs.height - padding &&
                    dino.y + dino.height - padding > obs.y + padding
                ) {
                    gameOver = true;
                    bgMusic.pause(); // Tạm dừng nhạc khi thua
                }

                if (obs.x < -30) obstacles.splice(i, 1);
            }

            scoreEl.innerText = String(score).padStart(5, '0');
            highScoreEl.innerText = String(highScore).padStart(5, '0');
            seasonNameEl.innerText = currentSeason.name;
        }

        function draw() {
            // Background Bầu trời
            ctx.fillStyle = currentSeason.sky;
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Mặt trời Pixel
            drawPixelMatrix(sunSprite, 400, 20, 3, "#f59e0b");

            // Mây
            clouds.forEach(c => {
                ctx.fillStyle = "rgba(255, 255, 255, 0.8)";
                ctx.fillRect(c.x, c.y, 24, 8);
                ctx.fillRect(c.x + 4, c.y - 4, 16, 4);
            });

            // Hiệu ứng Hạt Thời Tiết
            ctx.fillStyle = currentSeason.particleColor;
            particles.forEach(p => {
                ctx.fillRect(p.x, p.y, p.size, p.size);
            });

            // Mặt đất Pixel
            ctx.strokeStyle = currentSeason.ground;
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.moveTo(0, groundY);
            ctx.lineTo(canvas.width, groundY);
            ctx.stroke();

            // Chi tiết dưới đất
            let groundOffset = (frameCount * gameSpeed) % 16;
            ctx.fillStyle = currentSeason.ground;
            for (let x = -groundOffset; x < canvas.width; x += 16) {
                ctx.fillRect(x, groundY + 6, 4, 2);
                ctx.fillRect(x + 8, groundY + 12, 2, 2);
            }

            // Vẽ Khủng long
            let currentDinoSprite = dino.isJumping 
                ? dinoSprite1 
                : ((Math.floor(frameCount / 6) % 2 === 0) ? dinoSprite1 : dinoSprite2);
            
            drawPixelMatrix(currentDinoSprite, dino.x, dino.y, 3, currentSeason.dino);

            // Vẽ Vật cản
            obstacles.forEach(obs => {
                if (obs.type === 'cactus') {
                    drawPixelMatrix(cactusSprite, obs.x, obs.y, 3, currentSeason.cactus);
                } else if (obs.type === 'flower') {
                    drawPixelMatrix(flowerSprite, obs.x, obs.y, 3, "#a855f7");
                } else {
                    drawPixelMatrix(birdSprite, obs.x, obs.y, 3, "#ef4444");
                }
            });

            // Màn hình Bắt đầu & Game Over
            if (!gameStarted) {
                ctx.fillStyle = "#1e293b";
                ctx.font = "12px 'Press Start 2P'";
                ctx.textAlign = "center";
                ctx.fillText("PRESS [SPACE] TO START", canvas.width / 2, canvas.height / 2);
            } else if (gameOver) {
                ctx.fillStyle = "rgba(255, 255, 255, 0.85)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = "#ef4444";
                ctx.font = "14px 'Press Start 2P'";
                ctx.textAlign = "center";
                ctx.fillText("GAME OVER", canvas.width / 2, canvas.height / 2 - 10);

                ctx.fillStyle = "#1e293b";
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

st.sidebar.title("4 SEASONS GAME")
st.sidebar.markdown("""
- **Nhạc nền**: *TheFatRat - Unity* (Tự động phát khi bấm bắt đầu chơi).
- **Mùa Xuân (SPRING)**: Có **Hoa Độc Tím (Poison Flower)** mọc dưới đất.
- **Mùa Hạ (SUMMER)**: Nắng vàng rực rỡ.
- **Mùa Thu (AUTUMN)**: Bầu trời cam, lá vàng rơi.
- **Mùa Đông (WINTER)**: Bầu trời lạnh, tuyết rơi.
""")
