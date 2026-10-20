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
        body { margin: 0; padding: 0; background: #0f0f0f; display: flex; flex-direction: column; align-items: center; font-family: Courier, monospace; }
        canvas { border: 4px solid #fff; image-rendering: pixelated; box-shadow: 0 0 25px rgba(46,204,113,0.4); background: #f9d5e5; display: block; }
        .btn-container { margin-top: 12px; display: flex; gap: 15px; }
        .game-btn { background-color: #2ecc71; color: white; border: 3px solid #fff; padding: 10px 25px; font-size: 18px; font-weight: bold; font-family: Courier, monospace; cursor: pointer; border-radius: 6px; }
        .game-btn:active { transform: translateY(4px); }
        .duck-btn { background-color: #e67e22; }
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
    let audioCtx = null, isMusicStarted = false;
    function ensureMusic() { if (!isMusicStarted) { bgMusic.play().then(()=>isMusicStarted=true).catch(()=>{}); } }
    function initAudio() { ensureMusic(); if (!audioCtx) { const AC = window.AudioContext || window.webkitAudioContext; if (AC) audioCtx = new AC(); } }
    function playSound(type) { initAudio(); if(!audioCtx) return; const osc = audioCtx.createOscillator(), gain = audioCtx.createGain(); osc.connect(gain); gain.connect(audioCtx.destination); if (type === 'jump') { osc.frequency.setValueAtTime(150, audioCtx.currentTime); gain.gain.setValueAtTime(0.12, audioCtx.currentTime); osc.start(); osc.stop(audioCtx.currentTime+0.1); } else if (type === 'duck') { osc.type = 'sine'; osc.frequency.setValueAtTime(300, audioCtx.currentTime); gain.gain.setValueAtTime(0.1, audioCtx.currentTime); osc.start(); osc.stop(audioCtx.currentTime+0.08); } else if (type === 'gameover') { osc.type = 'sawtooth'; osc.frequency.setValueAtTime(200, audioCtx.currentTime); gain.gain.setValueAtTime(0.2, audioCtx.currentTime); osc.start(); osc.stop(audioCtx.currentTime+0.4); } }
    let score = 0, highScore = 0, gameSpeed = 5, isGameOver = false, currentSeason = 0;
    
    // Mùa Đông giờ có bầu trời màu cam ấm áp và không gian đặc trưng
    const seasons = [
        { name: "MUA XUAN (SPRING)", bg: "#f9d5e5", ground: "#27ae60", cactusColor: "#1e8449" },
        { name: "MUA HA (SUMMER)", bg: "#f39c12", ground: "#d35400", cactusColor: "#27ae60" },
        { name: "MUA THU (AUTUMN)", bg: "#d35400", ground: "#b9770e", cactusColor: "#1e8449" },
        { name: "MUA DONG (WINTER)", bg: "#e67e22", ground: "#bdc3c7", cactusColor: "#16a085" }
    ];

    let springFlowers = [], fallingLeaves = [], snowFlakes = [], sunAngle = 0, clouds = [];
    for(let i=0; i<8; i++) springFlowers.push({ x: Math.random()*canvas.width, y: 192+Math.random()*6, color: Math.random()>0.5?"#e74c3c":"#ffffff" });
    for(let i=0; i<12; i++) fallingLeaves.push({ x: Math.random()*canvas.width, y: Math.random()*180, speedY: 0.8+Math.random()*1.2, speedX: -0.5-Math.random()*0.8, size: 4+Math.random()*4 });
    for(let i=0; i<25; i++) snowFlakes.push({ x: Math.random()*canvas.width, y: Math.random()*200, speedY: 1+Math.random()*1.5, size: 2+Math.random()*3 });
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

    // Vẽ cây thông pixel đặc trưng mùa đông
    function drawPixelPineTree(x, y) {
        ctx.fillStyle = "#1e3d2f";
        ctx.fillRect(x + 8, y + 24, 4, 16); // Thân cây
        ctx.fillStyle = "#27ae60";
        ctx.fillRect(x + 4, y + 16, 12, 8);
        ctx.fillRect(x + 2, y + 10, 16, 6);
        ctx.fillRect(x, y + 4, 20, 6);
        ctx.fillRect(x + 6, y, 8, 4);
        // Bông tuyết bám trên cây thông
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(x + 4, y + 6, 3, 2);
        ctx.fillRect(x + 12, y + 12, 3, 2);
    }

    let dino = { x: 50, y: 156, width: 32, height: 44, vy: 0, gravity: 0.75, jumpPower: -13.5, isJumping: false, isDucking: false, animFrame: 0, draw() { const p = 2.5, px = this.x; ctx.save(); if (this.isDucking && !this.isJumping) { ctx.translate(px, 200); ctx.scale(1.1, 0.5); ctx.translate(0, -17.5*p); } else ctx.translate(px, this.y); ctx.fillStyle = "#2ecc71"; ctx.fillRect(7*p, 0, 7*p, 2*p); ctx.fillRect(7*p, 2*p, 8*p, 2*p); ctx.fillRect(7*p, 4*p, 6*p, 1*p); ctx.fillStyle="#ffffff"; ctx.fillRect(8*p, 1*p, 1.5*p, 1.5*p); ctx.fillStyle = "#2ecc71"; ctx.fillRect(7*p, 5*p, 4*p, 4*p); ctx.fillRect(5*p, 7*p, 5*p, 5*p); ctx.fillRect(3*p, 9*p, 6*p, 4*p); ctx.fillRect(11*p, 6*p, 3*p, 1*p); ctx.fillRect(11*p, 7*p, 1*p, 1.5*p); ctx.fillRect(0, 4*p, 1*p, 4*p); ctx.fillRect(1*p, 6*p, 1*p, 4*p); ctx.fillRect(2*p, 8*p, 1*p, 3*p); ctx.fillStyle = "#1e8449"; if (this.isJumping) { ctx.fillRect(4*p, 13*p, 2*p, 2*p); ctx.fillRect(7*p, 13*p, 2*p, 2*p); } else { if (Math.floor(this.animFrame/6)%2===0) { ctx.fillRect(4*p, 13*p, 2*p, 4.5*p); ctx.fillRect(7*p, 13*p, 2*p, 2*p); } else { ctx.fillRect(4*p, 13*p, 2*p, 2*p); ctx.fillRect(7*p, 13*p, 2*p, 4.5*p); } } ctx.restore(); this.animFrame++; }, jump() { if (!this.isJumping) { playSound('jump'); this.vy=this.jumpPower; this.isJumping=true; } }, duck(active) { if (!this.isJumping) { if (active && !this.isDucking) playSound('duck'); this.isDucking=active; this.y=active?178:156; } }, update() { this.vy += this.gravity; this.y += this.vy; let ground=this.isDucking?178:156; if (this.y>ground) { this.y=ground; this.vy=0; this.isJumping=false; } } };
    
    let obstacles = [];
    class Cactus { constructor() { this.cluster=Math.floor(Math.random()*3); this.width=[24,44,62][this.cluster]; this.height=[42,45,48][this.cluster]; this.x=canvas.width; this.y=200-this.height; this.type='cactus'; } drawSingle(ox, oy, h, color) { const p=2; ctx.fillStyle=color; ctx.fillRect(ox+4*p,oy,4*p,h); ctx.fillRect(ox,oy+h*0.3,2*p,h*0.35); ctx.fillRect(ox,oy+h*0.65,5*p,2*p); ctx.fillRect(ox+10*p,oy+h*0.25,2*p,h*0.35); ctx.fillRect(ox+7*p,oy+h*0.55,5*p,2*p); } draw() { let color=seasons[currentSeason].cactusColor; if (this.cluster===0) this.drawSingle(this.x, this.y, this.height, color); else if (this.cluster===1) { this.drawSingle(this.x, this.y, this.height, color); this.drawSingle(this.x+22, this.y+10, this.height-10, color); } else { this.drawSingle(this.x, this.y, this.height, color); this.drawSingle(this.x+20, this.y+16, this.height-16, color); this.drawSingle(this.x+38, this.y+4, this.height-4, color); } } update() { this.x -= gameSpeed; } }
    
    class LowBird { constructor() { this.width=34; this.height=20; this.x=canvas.width; this.y=158; this.type='bird'; this.animFrame=0; } draw() { ctx.fillStyle="#e74c3c"; ctx.fillRect(this.x, this.y+6, 34, 10); ctx.fillRect(this.x+8, this.y, 10, 8); if (Math.floor(this.animFrame/8)%2===0) ctx.fillRect(this.x+12, this.y-6, 8, 8); else ctx.fillRect(this.x+12, this.y+14, 8, 8); this.animFrame++; } update() { this.x -= gameSpeed; } }

    function resetGame() { score=0; gameSpeed=5; obstacles=[]; isGameOver=false; currentSeason=0; dino.y=156; dino.isDucking=false; ensureMusic(); }
    window.addEventListener("keydown", e => { initAudio(); if (e.code==="Space") { if(isGameOver) resetGame(); else dino.jump(); e.preventDefault(); } if (e.code==="ArrowDown") { if(!isGameOver) dino.duck(true); e.preventDefault(); } });
    window.addEventListener("keyup", e => { if (e.code==="ArrowDown") if(!isGameOver) dino.duck(false); });
    document.getElementById("jumpBtn").addEventListener("click", () => { initAudio(); if(isGameOver) resetGame(); else dino.jump(); });
    const duckBtn = document.getElementById("duckBtn");
    duckBtn.addEventListener("mousedown", () => { initAudio(); if(!isGameOver) dino.duck(true); });
    duckBtn.addEventListener("mouseup", () => { if(!isGameOver) dino.duck(false); });

    let obstacleTimer=0;
    function gameLoop() { 
        ensureMusic(); 
        score+=0.15; 
        currentSeason=Math.floor(Math.floor(score)/50)%4; 
        let season=seasons[currentSeason]; 
        
        ctx.fillStyle=season.bg; 
        ctx.fillRect(0,0,canvas.width,canvas.height); 

        if (currentSeason===0) { 
            springFlowers.forEach(f => { f.x-=gameSpeed*0.5; if(f.x<0)f.x=canvas.width; ctx.fillStyle=f.color; ctx.fillRect(f.x,f.y,4,4); }); 
        } else if (currentSeason===1) { 
            sunAngle+=0.01; 
            ctx.fillStyle="#f1c40f"; 
            ctx.beginPath(); ctx.arc(700,50,36,0,Math.PI*2); ctx.fill(); 
        } else if (currentSeason===2) { 
            ctx.fillStyle="#e67e22"; 
            fallingLeaves.forEach(leaf => { leaf.x+=leaf.speedX; leaf.y+=leaf.speedY; if(leaf.y>200){leaf.y=0;leaf.x=Math.random()*canvas.width;} ctx.fillRect(leaf.x,leaf.y,leaf.size,leaf.size); }); 
        } else if (currentSeason===3) { 
            // MÙA ĐÔNG: Có mặt trăng lưỡi liềm và cây thông phía xa
            ctx.fillStyle = "#f1c40f";
            ctx.beginPath();
            ctx.arc(700, 55, 22, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = "#e67e22";
            ctx.beginPath();
            ctx.arc(708, 50, 18, 0, Math.PI * 2);
            ctx.fill(); // Hiệu ứng trăng lưỡi liềm

            // Vẽ vài cây thông mờ phía sau nền mùa đông
            drawPixelPineTree(150, 160);
            drawPixelPineTree(450, 160);

            ctx.fillStyle="#ffffff"; 
            snowFlakes.forEach(flake => { flake.y+=flake.speedY; if(flake.y>200){flake.y=0;flake.x=Math.random()*canvas.width;} ctx.fillRect(flake.x,flake.y,flake.size,flake.size); }); 
        } 

        clouds.forEach(cloud => {
            cloud.x -= cloud.speed;
            if(cloud.x < -60) cloud.x = canvas.width + 50;
            drawPixelCloud(cloud.x, cloud.y);
        });

        ctx.fillStyle=season.ground; 
        ctx.fillRect(0,200,canvas.width,50); 

        if (!isGameOver) { 
            dino.update(); 
            gameSpeed=5+score/60; 
            obstacleTimer++; 
            if (obstacleTimer>80+Math.random()*35) { 
                if (score>40&&Math.random()>0.45) obstacles.push(new LowBird()); 
                else obstacles.push(new Cactus()); 
                obstacleTimer=0; 
            } 
        } 

        for (let i=obstacles.length-1; i>=0; i--) { 
            obstacles[i].update(); 
            obstacles[i].draw(); 
            if (dino.x+2<obstacles[i].x+obstacles[i].width-2 && dino.x+30>obstacles[i].x+2 && dino.y+2<obstacles[i].y+obstacles[i].height && dino.y+42>obstacles[i].y) { 
                playSound('gameover'); 
                isGameOver=true; 
                if(score>highScore)highScore=Math.floor(score); 
            } 
            if (obstacles[i].x<-70) obstacles.splice(i,1); 
        } 

        dino.draw(); 
        ctx.fillStyle="#fff"; 
        ctx.font="bold 15px Courier"; 
        ctx.fillText("DIEM: "+Math.floor(score),580,30); 
        ctx.fillText("KY LUC: "+highScore,580,52); 
        ctx.fillText(season.name,20,30); 

        if (isGameOver) { 
            ctx.fillStyle="rgba(0,0,0,0.8)"; 
            ctx.fillRect(0,0,canvas.width,canvas.height); 
            ctx.fillStyle="#e74c3c"; 
            ctx.font="bold 24px Courier"; 
            ctx.fillText("GAME OVER - VAP NGA ROI!",210,100); 
            ctx.fillStyle="#fff"; 
            ctx.font="15px Courier"; 
            ctx.fillText("Bam [SPACEBAR] hoac nut [NHAY] de choi lai",205,145); 
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
- **Nhạc nền**: TheFatRat - Unity (Tự động phát)[cite: 10].
- **Điều khiển**: [Spacebar] / [Jump] để Nhảy | Phím [Mũi tên xuống] để Cúi / Thu nhỏ[cite: 10].
- **Mùa Xuân**: Bầu trời hồng nhạt, hoa & chim[cite: 10].
- **Mùa Hạ**: Bầu trời cam, ông mặt trời to[cite: 10].
- **Mùa Thu**: Bầu trời đỏ thẫm, lá thu rơi[cite: 10].
- **Mùa Đông**: Bầu trời cam ấm áp, mặt trăng & cây thông pixel[cite: 14].
""")
