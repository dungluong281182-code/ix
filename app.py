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

        window.addEventListener("click", () => canvas.focus());

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

        // Khởi tạo các hạt thời tiết (Hoa đào, Tuyết, Lá rơi)
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

        // Sprite Xương rồng
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

        // Sprite Hoa Độc (Poison Flower - Mùa Xuân)
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

        // Sprite Chim Pterodactyl
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

        // Sprite Mặt Trời Pixel
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
        }

        function jump() {
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

                // Nếu đang ở Mùa Xuân, có 40% xuất hiện Hoa Độc
                if (currentSeason.id === "SPRING" && rand < 0.4) {
                    obstacles.push({
                        type: 'flower',
                        x: canvas.width,
                        y: groundY - 24,
                        width: 20,
                        height: 24
                    });
                } else if (rand > 0.65 && score > 80) {
                    // Chim bay
                    obstacles.push({
                        type: 'bird',
                        x: canvas.width,
                        y: groundY - 36 - (Math.random() * 20),
                        width: 24,
                        height: 1
