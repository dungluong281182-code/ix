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
        { name: "MUA XUAN (SPRING)", bg: "#70c5ce", ground: "#27ae60", line: "#1e8449", cactusColor: "#1e8449" },
        { name: "MUA HA (SUMMER)", bg: "#f39c12", ground: "#d35400", line: "#ba4a00", cactusColor: "#27ae60" },
        { name: "MUA THU (AUTUMN)", bg: "#d35400", ground: "#b9770e", line: "#7e5109", cactusColor: "#1e8449" },
        { name: "MUA DONG (WINTER)", bg: "#1a252f", ground: "#7f8c8d", line: "#34495e", cactusColor: "#16a085" }
    ];

    // Các phần tử thời tiết / môi trường riêng biệt cho từng mùa
    let springFlowers = [];
    for(let i=0; i<8; i++) {
        springFlowers.push({ x: Math.random() * canvas.width, y: 192 + Math.random() * 6, color: Math.random() > 0.5 ? "#e74c3c" : "#f1c40f" });
    }

    let fallingLeaves = [];
    for(let i=0; i<12; i++) {
        fallingLeaves.push({
            x: Math.random() * canvas.width,
            y: Math.random() * 180,
            speedY: 0.8 + Math.random() * 1.2,
            speedX: -0.5 - Math.random() * 0.8,
            size: 4 + Math.random() * 4
        });
    }

    let snowFlakes = [];
    for(let i=0; i<25; i++) {
        snowFlakes.push({
            x: Math.random() * canvas.width,
            y: Math.random() * 200,
            speedY: 1 + Math.random() * 1.5,
            size: 2 + Math.random() * 3
        });
    }

    let sunAngle = 0;

    let dino = {
        x: 50,
        y: 156,
        width: 32,
        height: 44,
        normalHeight: 44,
        duckHeight: 22,
        vy: 0,
        gravity: 0.75,
        jumpPower: -13.5,
        isJumping: false,
        isDucking: false,
        animFrame: 0,
        draw() {
            const p = 2.5;
            const px = this.x;

            ctx.save();
            if (this.isDucking && !this.isJumping) {
                ctx.translate(px, 200);
                ctx.scale(1.1, 0.5);
                ctx.translate(0, -17.5 * p);
            } else {
                ctx.translate(px, this.y);
            }

            ctx.fillStyle = "#2ecc71";
            ctx.fillRect(7*p, 0, 7*p, 2*p);
            ctx.fillRect(7*p, 2*p, 8*p, 2*p);
            ctx.fillRect(7*p, 4*p, 6*p, 1*p);
            
            ctx.fillStyle = "#ffffff";
            ctx.fillRect(8*p, 1*p, 1.5*p, 1.5*p);

            ctx.fillStyle = "#2ecc71";
            ctx.fillRect(7*p, 5*p, 4*p, 4*p);
            ctx.fillRect(5*p, 7*p, 5*p, 5*p);
            ctx.fillRect(3*p, 9*p, 6*p, 4*p);

            ctx.fillRect(11*p, 6*p, 3*p, 1*p);
            ctx.fillRect(11*p, 7*p, 1*p, 1.5*p);

            ctx.fillRect(0, 4*p, 1*p, 4*p);
            ctx.fillRect(1*p, 6*p, 1*p, 4*p);
            ctx.fillRect(2*p, 8*p, 1*p, 3*p);

            if (this.isJumping) {
                ctx.fillRect(4*p, 13*p, 2*p, 2*p);
                ctx.fillRect(7*p, 13*p, 2*p, 2*p);
            } else {
                if (Math.floor(this.animFrame / 6) % 2 === 0) {
                    ctx.fillRect(4*p, 13*p, 2*p, 4.5*p);
                    ctx.fillRect(7*p, 13*p, 2*p, 2*p);
                    ctx.fillRect(8*p, 14*p, 2*p, 1*p);
                } else {
                    ctx.fillRect(4*p, 13*p, 2*p, 2*p);
                    ctx.fillRect(3*p, 14*p, 2*p, 1*p);
                    ctx.fillRect(7*p, 13*p, 2*p, 4.5*p);
                }
            }

            ctx.restore();
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
                    this.y = 156;
                }
            }
        },
        update() {
            this.vy += this.gravity;
            this.y += this.vy;
            let groundLevel = this.isDucking ? (200 - this.duckHeight) : 156;
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
            this.clusterType = Math.floor(Math.random() * 3);
            if (this.clusterType === 0) {
                this.width = 24;
                this.height = 42;
            } else if (this.clusterType === 1) {
                this.width = 44;
                this.height = 45;
            } else {
                this.width = 62;
                this.height = 48;
            }
            this.x = canvas.width;
            this.y = 200 - this.height;
            this.type = 'cactus';
        }
        
        drawSingleCactus(ox, oy, h, color) {
            const p = 2;
            ctx.fillStyle = color;
            ctx.fillRect(ox + 4*p, oy, 4*p, h);
            ctx.fillRect(ox, oy + Math.floor(h*0.3), 2*p, Math.floor(h*0.35));
            ctx.fillRect(ox, oy + Math.floor(h*0.65), 5*p, 2*p);
            ctx.fillRect(ox + 10*p, oy + Math.floor(h*0.25), 2*p, Math.floor(h*0.35));
            ctx.fillRect(ox + 7*p, oy + Math.floor(h*0.55), 5*p, 2*p);
        }

        draw() {
            let color = seasons[currentSeason].cactusColor || "#1e8449";
            if (this.clusterType === 0) {
                this.drawSingleCactus(this.x, this.y, this.height, color);
            } else if (this.clusterType === 1) {
                this.drawSingleCactus(this.x, this.y, this.height, color);
                this.drawSingleCactus(this.x + 22, this.y + 10, this.height - 10, color);
            } else {
                this.drawSingleCactus(this.x, this.y, this.height, color);
                this.drawSingleCactus(this.x + 20, this.y + 16, this.height - 16, color);
                this.drawSingleCactus(this.x + 38, this.y + 4, this.height - 4, color);
            }
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
        dino.y = 156;
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

        // Vẽ nền trời từng mùa
        ctx.fillStyle = season.bg;
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // HIỆU ỨNG RIÊNG CHO TỪNG MÙA
        if (currentSeason === 0) {
            // MÙA XUÂN: Hoa nở trên mặt đất & chim nhỏ bay lượn
            springFlowers.forEach(f => {
                f.x -= gameSpeed * 0.5;
                if (f.x < 0) f.x = canvas.width;
