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
body { margin: 0; padding: 0; background: #0f0f0f; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; overflow: hidden; font-family: Courier, monospace; }
canvas { border: 4px solid #fff; image-rendering: pixelated; box-shadow: 0 0 25px rgba(46,204,113,0.4); background: #f9d5e5; display: block; }
</style>
</head>
<body>
<audio id="bgMusic" loop src="https://archive.org/download/gdps-2.2-song-621134/621134.mp3" preload="auto"></audio>
<canvas id="gameCanvas" width="800" height="250"></canvas>
<script>
window.onload = function() {
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");
    const bgMusic = document.getElementById("bgMusic");
    let audioCtx = null, isMusicStarted = false;
    function ensureMusic() { if (!isMusicStarted) { bgMusic.play().then(()=>isMusicStarted=true).catch(()=>{}); } }
    function initAudio() { ensureMusic(); if (!audioCtx) { const AC = window.AudioContext || window.webkitAudioContext; if (AC) audioCtx = new AC(); } }
    function playSound(type) { initAudio(); if(!audioCtx) return; const osc = audioCtx.createOscillator(), gain = audioCtx.createGain(); osc.connect(gain); gain.connect(audioCtx.destination); if (type === 'jump') { osc.frequency.setValueAtTime(150, audioCtx.currentTime); gain.gain.setValueAtTime(0.12, audioCtx.currentTime); osc.start(); osc.stop(audioCtx.currentTime+0.1); } else if (type === 'duck') { osc.type = 'sine'; osc.frequency.setValueAtTime(300, audioCtx.currentTime); gain.gain.setValueAtTime(0.1, audioCtx.currentTime); osc.start(); osc.stop(audioCtx.currentTime+0.08); } else if (type === 'gameover') { osc.type = 'sawtooth'; osc.frequency.setValueAtTime(200, audioCtx.currentTime); gain.gain.setValueAtTime(0.2, audioCtx.currentTime); osc.start(); osc.stop(audioCtx.currentTime+0.4); } }
    let score = 0, highScore = 0, gameSpeed = 5, isGameOver = false, currentSeason = 0;
    
    const seasons = [
        { name: "MUA XUAN (SPRING)", bg: "#f9d5e5", ground: "#27ae60", cactusColor: "#1e8449" },
        { name: "MUA HA (SUMMER)", bg: "#f39c12", ground: "#d35400", cactusColor: "#27ae60" },
        { name: "MUA THU (AUTUMN)", bg: "#d35400", ground: "#b9770e", cactusColor: "#1e8449" },
        { name: "MUA DONG (WINTER)", bg: "#111e38", ground: "#2c3e50", cactusColor: "#16a085" }
    ];

    let springFlowers = [], fallingLeaves = [], snowFlakes = [], sunAngle = 0, clouds = [];
    for(let i=0; i<8; i++) springFlowers.push({ x: Math.random()*canvas.width, y: 192+Math.random()*6, color: Math.random()>0.5?"#e74c3c":"#ffffff" });
    
    for(let i=0; i<10; i++) {
        fallingLeaves.push({
            x: Math.random() * canvas.width,
            y: Math.random() * 180,
            speedY: 0.6 + Math.random() * 1.0,
            speedX: -0.4 - Math.random() * 0.6,
            type: Math.floor(Math.random() * 3)
        });
    }

    for(let i=0; i<30; i++) snowFlakes.push({ x: Math.random()*canvas.width, y: Math.random()*200, speedY: 0.8+Math.random()*1.4, size: 2+Math.random()*3.5 });
    for(let i=0; i<4; i++) clouds.push({ x: Math.random()*canvas.width, y: 20+Math.random()*50, speed: 0.3+Math.random()*0.5 });

    function drawPixelCloud(x, y) {
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(x + 8, y + 8, 32, 12);
        ctx.fillRect(x + 4, y + 12, 40, 8);
        ctx.fillRect(x + 12, y + 4, 16, 8);
        ctx.fillRect(x + 24, y, 12, 6);
        ctx.fillStyle = "#d4f0f0";
        ctx.fillRect(x + 4, y + 20, 40, 2);
    }

    // Cây thông mùa đông thiết kế to cao hơn khủng long, dáng tháp chuẩn đẹp
    function drawPixelPineTree(x, y) {
        ctx.fillStyle = "#0e2318";
        ctx.fillRect(x + 12, y + 36, 6, 18); // Thân cây cao
        
        ctx.fillStyle = "#1e6b45";
        ctx.fillRect(x + 6, y + 24, 18, 14);
        ctx.fillRect(x + 3, y + 14, 24, 12);
        ctx.fillRect(x, y + 4, 30, 12);
        ctx.fillRect(x + 10, y, 10, 6);

        // Tuyết đọng phủ trắng trên các tầng lá thông
        ctx.fillStyle = "#e2f1f8";
        ctx.fillRect(x + 3, y + 14, 24, 3);
        ctx.fillRect(x, y + 4, 30, 3);
        ctx.fillRect(x + 10, y, 10, 2);
    }

    // Cây mùa thu to cao hơn khủng long đúng chuẩn
    function drawPixelAutumnTree(x, y) {
        ctx.fillStyle = "#5c3a21";
        ctx.fillRect(x + 18, y + 24, 8, 30);
        ctx.fillRect(x + 10, y + 38, 14, 12);
        
        ctx.fillStyle = "#f39c12";
        ctx.fillRect(x + 4, y + 4, 36, 22);
        ctx.fillStyle = "#e67e22";
        ctx.fillRect(x, y + 10, 44, 14);
        ctx.fillStyle = "#f1c40f";
        ctx.fillRect(x + 10, y, 24, 10);

        // Đống lá rụng dưới gốc cây
        ctx.fillStyle = "#f39c12";
        ctx.fillRect(x - 4, y + 44, 44, 6);
    }

    function drawDetailedLeaf(x, y, type) {
        if (type === 0) {
            ctx.fillStyle = "#e67e22";
            ctx.fillRect(x+4, y, 4, 12);
            ctx.fillRect(x, y+4, 12, 4);
            ctx.fillStyle = "#d35400";
            ctx.fillRect(x+2, y+10, 2, 4);
        } else if (type === 1) {
            ctx.fillStyle = "#f39c12";
            ctx.fillRect(x+2, y, 6, 14);
            ctx.fillStyle = "#c0392b";
            ctx.fillRect(x+4, y+2, 2, 10);
            ctx.fillStyle = "#e67e22";
            ctx.fillRect(x, y+4, 10, 2);
            ctx.fillRect(x, y+8, 10, 2);
        } else {
            ctx.fillStyle = "#d35400";
            ctx.fillRect(x+2, y, 6, 12);
            ctx.fillStyle = "#f1c40f";
            ctx.fillRect(x+4, y+2, 2, 8);
            ctx.fillStyle = "#7e5109";
            ctx.fillRect(x+4, y+12, 2, 3);
        }
    }

    let dino = {
        x: 50, y: 156, width: 32, height: 44, vy: 0, gravity: 0.75, jumpPower: -13.5, isJumping: false, isDucking: false, animFrame: 0,
        draw() {
            const p = 2.5, px = this.x;
            ctx.save();
            if (this.isDucking && !this.isJumping) {
                ctx.translate(px, 200);
                ctx.scale(1.1, 0.5);
                ctx.translate(
