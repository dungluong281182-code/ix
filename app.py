import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="4 Seasons Game", layout="centered")

game_html = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>4 Seasons Game</title>
    <style>
        * { box-sizing: border-box; }
        body {
            margin: 0;
            padding: 0;
            background-color: #0f0f0f;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            font-family: 'Courier New', Courier, monospace;
        }
        canvas {
            border: 4px solid #fff;
            image-rendering: pixelated;
            image-rendering: crisp-edges;
            box-shadow: 0 0 25px rgba(46, 204, 113, 0.4);
            background: #70c5ce;
            display: block;
        }
        .btn-container {
            margin-top: 12px;
            display: flex;
            gap: 15px;
        }
        .game-btn {
            background-color: #2ecc71;
            color: white;
            border: 3px solid #fff;
            padding: 10px 25px;
            font-size: 18px;
            font-weight: bold;
            font-family: 'Courier New', Courier, monospace;
            cursor: pointer;
            box-shadow: 0 4px 0 #27ae60;
            border-radius: 6px;
        }
        .game-btn:active {
            transform: translateY(4px);
            box-shadow: 0 0 0 #27ae60;
        }
        .duck-btn {
            background-color: #e67e22;
            box-shadow: 0 4px 0 #ca6f1e;
        }
        .duck-btn:active {
            box-shadow: 0 0 0 #ca6f1e;
        }
    </style>
</head>
<body>

<audio id="bgMusic" loop src="https://archive.org/download/gdps-2.2-song-621134/621134.mp3" preload="auto"></audio>

<canvas id="gameCanvas" width="800" height="250"></canvas>

<div class="btn-container">
    <button class="game-btn" id="jumpBtn">NHAY (SPACE)</button>
    <button class="game-btn duck-btn" id="duckBtn">CUI (MUI TEN XUONG)</button>
</div>

<script>
window.onload = function() {
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");
    const bgMusic = document.getElementById("bgMusic");

    let audioCtx = null;
    let isMusicStarted = false;

    function ensureMusic() {
        if (!isMusicStarted) {
            bgMusic.play().then(() => {
                isMusicStarted = true;
            }).catch(() => {});
        }
    }

    function initAudio() {
        ensureMusic();
        if (!audioCtx) {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (AudioContext) {
                audioCtx = new AudioContext();
            }
        }
        if (audioCtx && audioCtx.state === 'suspended') {
            audioCtx.resume();
        }
    }

    function playSound(type) {
        initAudio();
        if (!audioCtx) return;
        try {
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.connect(gain);
            gain.connect(audioCtx.destination);

            if (type === 'jump') {
                osc.type = 'square';
                osc.frequency.setValueAtTime(150, audioCtx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(400, audioCtx.currentTime + 0.1);
                gain.gain.setValueAtTime(0.12, audioCtx.currentTime);
                gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);
                osc.start();
                osc.stop(audioCtx.currentTime + 0.1);
            } else if (type === 'duck') {
                osc.type = 'sine';
                osc.frequency.setValueAtTime(300, audioCtx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(120, audioCtx.currentTime + 0.08);
                gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
                gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.08);
                osc.start();
                osc.stop(audioCtx.currentTime + 0.08);
            } else if (type === 'gameover') {
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(200, audioCtx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(40, audioCtx.currentTime + 0.4);
                gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
                gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.4);
                osc.start();
                osc.stop(audioCtx.currentTime + 0.4);
            }
        } catch(e){}
    }

    let score = 0;
    let highScore = 0;
    let gameSpeed = 5;
    let isGameOver = false;
    let currentSeason = 0;

    const seasons = [
        { name: "MUA XUAN (SPRING)", bg: "#70c5ce", ground: "#27ae60", line: "#1e8449" },
        { name: "MUA HA (SUMMER)", bg: "#f39c12", ground: "#d35400", line: "#ba4a00" },
        { name: "MUA THU (AUTUMN)", bg: "#d35400", ground: "#b9770e", line: "#7e5109" },
        { name: "MUA DONG (WINTER)", bg: "#2c3e50", ground: "#bdc3c7", line: "#7f8c8d" }
    ];

    let clouds = [];
    for(let i = 0; i < 4; i++) {
        clouds.push({
            x: Math.random() * canvas.width,
            y: 20 + Math.random() * 45,
            speed: 0.4 + Math.random() * 0.6,
            width: 45 + Math.random() * 25
        });
    }

    // T-Rex chuẩn xác theo mẫu hình siluet (chân ngắn, tay cực nhỏ, đuôi to)
    let dino = {
        x: 50,
        y: 164,
        width: 34,
        height: 36,
        normalHeight: 36,
        duckHeight: 18,
        vy: 0,
        gravity: 0.75,
        jumpPower: -13.5,
        isJumping: false,
        isDucking: false,
        animFrame: 0,
        draw() {
            const p = 3; // 1 ô pixel = 3px
            const px = this.x;
            const py = this.y;

            ctx.fillStyle = "#2ecc71";

            if (this.isDucking && !this.isJumping) {
                // Trạng thái CÚI: Nén ngắn chiều cao sát mặt đất như lò xò
                ctx.fillRect(px, 200 - 18, 42, 18);
                ctx.fillRect(px + 28, 200 - 24, 14, 10);
                ctx.fillStyle = "#ffffff";
                ctx.fillRect(px + 32, 200 - 21, 3, 3);
            } else {
                // ĐẦU & MÕM VUÔNG
                ctx.fillRect(px + 3*p, py, 6*p, 3*p);
                ctx.fillRect(px + 2*p, py + 1*p, 1*p, 2*p);
                
                // MẮT TRẮNG
                ctx.fillStyle = "#ffffff";
                ctx.fillRect(px + 4*p, py + 1*p, 1*p, 1*p);

                ctx.fillStyle = "#2ecc71";
                // THÂN & CỔ
                ctx.fillRect(px + 4*p, py + 3*p, 4*p, 5*p);

                // TAY NHỎ XÍU ĐẶC TRƯNG T-REX
                ctx.fillStyle = "#1e8449";
                ctx.fillRect(px + 2*p, py + 4*p, 2*p, 1*p);

                ctx.fillStyle = "#2ecc71";
                // ĐUÔI TO VỂNH PHÍA SAU
                ctx.fillRect(px, py + 3*p, 3*p, 2*p);
                ctx.fillRect(px - 1*p, py + 2*p, 1*p, 2*p);
                ctx.fillRect(px + 1*p, py + 5*p, 3*p, 2*p);
                ctx.fillRect(px + 2*p, py + 7*p, 2*p, 2*p);

                // CHÂN NGẮN VỪA VĂN
                ctx.fillStyle = "#1e8449";
                if (this.isJumping) {
                    ctx.fillRect(px + 3*p, py + 8*p, 2*p, 2*p);
                    ctx.fillRect(px + 6*p, py + 8*p, 2*p, 2*p);
                } else {
                    if (Math.floor(this.animFrame / 6) % 2 === 0) {
                        ctx.fillRect(px + 3*p, py + 8*p, 2*p, 3*p); // Chân trước
                        ctx.fillRect(px + 6*p, py + 8*p, 2*p, 1*p); // Chân sau co
                    } else {
                        ctx.fillRect(px + 3*p, py + 8*p, 2*p, 1*p);
                        ctx.fillRect(px + 6*p, py + 8*p, 2*p, 3*p);
                    }
                }
            }
            this.animFrame++;
        },
        jump() {
            if (!this.isJumping) {
                playSound('jump');
                this.vy = this.jumpPower;
                this.isJumping = true;
                this.isDucking = false;
                this.height = this.normalHeight;
            }
        },
        duck(active) {
            if (!this.isJumping) {
                if (active && !this.isDucking) {
                    playSound('duck');
                }
                this.isDucking = active;
                if (active) {
                    this.height = this.duckHeight;
                    this.y = 200 - this.duckHeight;
                } else {
                    this.height = this.normalHeight;
                    this.y = 164;
                }
            }
        },
        update() {
            this.vy += this.gravity;
            this.y += this.vy;
            let groundLevel = this.isDucking ? (200 - this.duckHeight) : 164;
            if (this.y > groundLevel) {
                this.y = groundLevel;
                this.vy = 0;
                this.isJumping = false;
            }
        }
    };

    let obstacles = [];

    class Cactus {
        constructor() {
            this.width = 22;
            this.height = 36;
            this.x = canvas.width;
            this.y = 200 - this.height;
            this.type = 'cactus';
        }
        draw() {
            ctx.fillStyle = "#1e8449";
            ctx.fillRect(this.x, this.y, this.width, this.height);
            ctx.fillStyle = "#2ecc71";
            ctx.fillRect(this.x - 4, this.y + 8, 4, 6);
            ctx.fillRect(this.x + this.width, this.y + 14, 4, 6);
        }
        update() {
            this.x -= gameSpeed;
        }
    }

    class LowBird {
        constructor() {
            this.width = 34;
            this.height = 20;
            this.x = canvas.width;
            this.y = 158;
            this.type = 'bird';
            this.animFrame = 0;
        }
        draw() {
            ctx.fillStyle = "#e74c3c";
            ctx.fillRect(this.x, this.y + 6, 34, 10);
            ctx.fillRect(this.x + 8, this.y, 10, 8);
            
            ctx.fillStyle = "#c0392b";
            if (Math.floor(this.animFrame / 8) % 2 === 0) {
                ctx.fillRect(this.x + 12, this.y - 6, 8, 8);
            } else {
                ctx.fillRect(this.x + 12, this.y + 14, 8, 8);
            }
            this.animFrame++;
        }
        update() {
            this.x -= gameSpeed;
        }
    }

    function resetGame() {
        score = 0;
        gameSpeed = 5;
        obstacles = [];
        isGameOver = false;
        currentSeason = 0;
        dino.y = 164;
        dino.height = dino.normalHeight;
        dino.isDucking = false;
        ensureMusic();
    }

    window.addEventListener("keydown", e => {
        initAudio();
        if (e.code === "Space" || e.code === "ArrowUp") {
            if (isGameOver) resetGame();
            else dino.jump();
            e.preventDefault();
        }
        if (e.code === "ArrowDown") {
            if (!isGameOver) dino.duck(true);
            e.preventDefault();
        }
    });

    window.addEventListener("keyup", e => {
        if (e.code === "ArrowDown") {
            if (!isGameOver) dino.duck(false);
        }
    });

    document.getElementById("jumpBtn").addEventListener("click", () => {
        initAudio();
        if (isGameOver) resetGame();
        else dino.jump();
    });

    const duckBtn = document.getElementById("duckBtn");
    duckBtn.addEventListener("mousedown", () => { initAudio(); if(!isGameOver) dino.duck(true); });
    duckBtn.addEventListener("mouseup", () => { if(!isGameOver) dino.duck(false); });
    duckBtn.addEventListener("touchstart", (e) => { initAudio(); if(!isGameOver) dino.duck(true); e.preventDefault(); });
    duckBtn.addEventListener("touchend", (e) => { if(!isGameOver) dino.duck(false); e.preventDefault(); });

    let obstacleTimer = 0;

    function gameLoop() {
        ensureMusic();
        let currentScore = Math.floor(score);
        currentSeason = Math.floor(currentScore / 50) % seasons.length;
        let season = seasons[currentSeason];

        ctx.fillStyle = season.bg;
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = "rgba(255, 255, 255, 0.75)";
        clouds.forEach(cloud => {
            cloud.x -= cloud.speed;
            if (cloud.x < -60) cloud.x = canvas.width + 50;
            ctx.fillRect(cloud.x, cloud.y, cloud.width, 10);
            ctx.fillRect(cloud.x + 8, cloud.y - 6, cloud.width - 16, 6);
        });

        ctx.fillStyle = season.ground;
        ctx.fillRect(0, 200, canvas.width, 50);
        ctx.fillStyle = season.line;
        ctx.fillRect(0, 200, canvas.width, 4);

        if (!isGameOver) {
            dino.update();
            score += 0.15;
            gameSpeed = 5 + (score / 60);

            obstacleTimer++;
            if (obstacleTimer > Math.max(35, 80 - (gameSpeed * 2.5)) + Math.random() * 30) {
                if (score > 40 && Math.random() > 0.45) {
                    obstacles.push(new LowBird());
                } else {
                    obstacles.push(new Cactus());
                }
                obstacleTimer = 0;
            }
        }

        for (let i = obstacles.length - 1; i >= 0; i--) {
            obstacles[i].update();
            obstacles[i].draw();

            if (
                dino.x + 2 < obstacles[i].x + obstacles[i].width - 2 &&
                dino.x + dino.width - 2 > obstacles[i].x + 2 &&
                dino.y + 2 < obstacles[i].y + obstacles[i].height &&
                dino.y + dino.height > obstacles[i].y
            ) {
                if (!isGameOver) {
                    playSound('gameover');
                }
                isGameOver = true;
                if (score > highScore) highScore = Math.floor(score);
            }

            if (obstacles[i].x < -40) {
                obstacles.splice(i, 1);
            }
        }

        dino.draw();

        ctx.fillStyle = "#fff";
        ctx.font = "bold 15px 'Courier New'";
        ctx.fillText("DIEM: " + currentScore, 580, 30);
        ctx.fillText("KY LUC: " + highScore, 580, 52);
        ctx.fillText(season.name, 20, 30);

        if (isGameOver) {
            ctx.fillStyle = "rgba(0, 0, 0, 0.8)";
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            ctx.fillStyle = "#e74c3c";
            ctx.font = "bold 24px 'Courier New'";
            ctx.fillText("GAME OVER - VAP NGA ROI!", 210, 100);
            
            ctx.fillStyle = "#fff";
            ctx.font = "15px 'Courier New'";
            ctx.fillText("Bam [SPACEBAR] hoac nut [NHAY] de choi lai", 205, 145);
        }

        requestAnimationFrame(gameLoop);
    }

    gameLoop();
};
</script>

</body>
</html>
"""

components.html(game_html, height=380)

st.sidebar.title("4 SEASONS GAME")
st.sidebar.markdown("""
- **Nhạc nền**: TheFatRat - Unity (Tự động phát khi khởi chạy).
- **Nút điều khiển**: Phím Spacebar / Mũi tên lên để Nhảy | Phím Mũi tên xuống để Cúi / Nén chiều cao.
- **Mùa Xuân (SPRING)**: Khung cảnh xanh tươi.
- **Mùa Hạ (SUMMER)**: Nắng vàng rực rỡ.
- **Mùa Thu (AUTUMN)**: Bầu trời cam đỏ ấm áp.
- **Mùa Đông (WINTER)**: Bầu trời đêm lạnh giá.
""")
