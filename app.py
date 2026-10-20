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

<!-- Nhạc nền chuẩn TheFatRat - Unity -->
<audio id="bgMusic" loop src="https://archive.org/download/gdps-2.2-song-621134/621134.mp3" preload="auto"></audio>

<canvas id="gameCanvas" width="800" height="250"></canvas>

<div class="btn-container">
    <button class="game-btn" id="jumpBtn">NHẢY (SPACE)</button>
    <button class="game-btn duck-btn" id="duckBtn">CÚI (MŨI TÊN XUỐNG)</button>
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
        { name: "MÙA XUÂN (SPRING)", bg: "#70c5ce", ground: "#27ae60", line: "#1e8449" },
        { name: "MÙA HẠ (SUMMER)", bg: "#f39c12", ground: "#d35400", line: "#ba4a00" },
        { name: "MÙA THU (AUTUMN)", bg: "#d35400", ground: "#b9770e", line: "#7e5109" },
        { name: "MÙA ĐÔNG (WINTER)", bg: "#2c3e50", ground: "#bdc3c7", line: "#7f8c8d" }
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

    // Khủng Long T-Rex Pixel (khi cúi chiều cao nén lại cực ngắn như lò xò)
    let dino = {
        x: 50,
        y: 164,
        width: 30,
        height: 36,
        normalHeight: 36,
        duckHeight: 18, // Chiều cao nén lại ngắn một nửa khi cúi xuống
        vy: 0,
        gravity: 0.75,
        jumpPower: -13.5,
        isJumping: false,
        isDucking: false,
        animFrame: 0,
        draw() {
            ctx.fillStyle = "#2ecc71";
            if (this.isDucking && !this.isJumping) {
                // T-Rex cúi xuống: Chiều cao bị nén cực ngắn sát mặt đất
                ctx.fillRect(this.x, 200 - this.duckHeight, 38, this.duckHeight);
                ctx.fillRect(this.x + 24, 200 - this.duckHeight - 4, 14, 8); // Đầu cúi thấp
                ctx.fillStyle = "#fff";
                ctx.fillRect(this.x + 32, 200 - this.duckHeight - 2, 3, 3); // Mắt
            } else {
                // T-Rex đứng thẳng bình thường
                ctx.fillRect(this.x + 6, this.y + 12, 18, 16);
                ctx.fillRect(this.x + 14, this.y, 16, 14);
                ctx.fillStyle = "#fff";
                ctx.fillRect(this.x + 24, this.y + 3, 3, 3);
                ctx.fillStyle = "#2ecc71";
                ctx.fillRect(this.x + 20, this.y + 14, 4, 3);
                
                if (this.isJumping) {
                    ctx.fillRect(this.x + 8, this.y + 28, 4, 8);
                    ctx.fillRect(this.x + 16, this.y + 28, 4, 8);
                } else {
                    if (Math.floor(this.animFrame / 8) % 2 === 0) {
                        ctx.fillRect(this.x + 8, this.y + 28, 4, 8);
                        ctx.fillRect(this.x + 16, this.y + 28, 3, 6);
                    } else {
                        ctx.fillRect(this.x + 8, this.y + 28, 3, 6);
                        ctx.fillRect(this.x + 16, this.y + 28, 4, 8);
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
                    this.height =
