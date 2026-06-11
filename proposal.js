/* ── Proposal page logic ──────────────────────────────────────────────────── */
(function () {
  "use strict";

  /* ── Typing effect ──────────────────────────────────────────────────────── */
  function typeText(el, text, speed, onDone) {
    let i = 0;
    el.textContent = "";
    function tick() {
      if (i < text.length) {
        el.textContent += text[i++];
        setTimeout(tick, speed + Math.random() * 30);
      } else if (onDone) {
        onDone();
      }
    }
    tick();
  }

  /* ── "No" button escape logic ────────────────────────────────────────────── */
  const btnNo = document.getElementById("btnNo");
  let noClickCount = 0;
  const noLabels = [
    "💔 No", "😅 Nope!", "🏃 Catch me!", "😂 Never!", "🙈 Try again!", "💨 Too slow!", "😜 Hehe!"
  ];

  function moveNoButton(e) {
    if (e) e.preventDefault();
    noClickCount++;
    btnNo.textContent = noLabels[Math.min(noClickCount, noLabels.length - 1)];
    const margin = 10;
    const bw = btnNo.offsetWidth + margin;
    const bh = btnNo.offsetHeight + margin;
    const maxX = window.innerWidth - bw;
    const maxY = window.innerHeight - bh;
    const newX = Math.max(margin, Math.random() * maxX);
    const newY = Math.max(margin, Math.random() * maxY);
    btnNo.style.left = newX + "px";
    btnNo.style.top  = newY + "px";
    btnNo.style.right  = "auto";
    btnNo.style.bottom = "auto";
  }

  // Initial position
  btnNo.style.position = "fixed";
  btnNo.style.left = "auto";
  btnNo.style.bottom = "40px";
  btnNo.style.right  = "30%";

  btnNo.addEventListener("mouseover",   moveNoButton);
  btnNo.addEventListener("touchstart",  moveNoButton, { passive: false });
  btnNo.addEventListener("click",       moveNoButton);

  /* ── Confetti ──────────────────────────────────────────────────────────── */
  const canvas = document.getElementById("confettiCanvas");
  const ctx    = canvas.getContext("2d");
  let confettiParts = [];
  let animFrame;

  function resizeCanvas() {
    canvas.width  = window.innerWidth;
    canvas.height = window.innerHeight;
  }
  resizeCanvas();
  window.addEventListener("resize", resizeCanvas);

  const confettiColors = ["#e0607e","#f7b8c8","#c040a0","#ffd700","#ff85a1","#f9429e","#ff6699"];

  function createConfetti() {
    confettiParts = [];
    for (let i = 0; i < 200; i++) {
      confettiParts.push({
        x:  Math.random() * canvas.width,
        y:  Math.random() * canvas.height - canvas.height,
        r:  Math.random() * 6 + 3,
        d:  Math.random() * 200,
        color: confettiColors[Math.floor(Math.random() * confettiColors.length)],
        tilt:  Math.random() * 10 - 10,
        tiltAngle: 0,
        tiltAngleInc: (Math.random() * 0.07) + 0.05,
        shape: Math.random() > 0.5 ? "circle" : "rect",
      });
    }
  }

  function drawConfetti() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    confettiParts.forEach(p => {
      ctx.beginPath();
      ctx.fillStyle = p.color;
      if (p.shape === "circle") {
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      } else {
        ctx.save();
        ctx.translate(p.x, p.y);
        ctx.rotate(p.tiltAngle);
        ctx.fillRect(-p.r, -p.r / 2, p.r * 2, p.r);
        ctx.restore();
      }
      ctx.fill();
    });
  }

  let confettiDone = false;
  function updateConfetti() {
    confettiParts.forEach(p => {
      p.tiltAngle += p.tiltAngleInc;
      p.y += (Math.cos(p.d) + 2 + p.r / 2) * 1.2;
      p.x += Math.sin(p.d) * 1.5;
      p.tilt = Math.sin(p.tiltAngle) * 12;
    });
    confettiParts = confettiParts.filter(p => p.y < canvas.height + 20);
    if (confettiParts.length === 0) {
      confettiDone = true;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      return;
    }
    drawConfetti();
  }

  function startConfetti() {
    createConfetti();
    confettiDone = false;
    function loop() {
      if (!confettiDone) {
        updateConfetti();
        animFrame = requestAnimationFrame(loop);
      }
    }
    loop();
    // Refill after 1.5s for burst effect
    setTimeout(() => {
      if (!confettiDone) createConfetti();
    }, 1500);
  }

  /* ── Celebration audio ─────────────────────────────────────────────────── */
  function playCelebration() {
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!AudioCtx) return;
    const ctx2 = new AudioCtx();
    const notes = [523, 659, 784, 1047, 1319, 1568];
    notes.forEach((freq, i) => {
      const osc = ctx2.createOscillator();
      const gain = ctx2.createGain();
      osc.connect(gain);
      gain.connect(ctx2.destination);
      osc.frequency.value = freq;
      osc.type = "sine";
      const t = ctx2.currentTime + i * 0.12;
      gain.gain.setValueAtTime(0, t);
      gain.gain.linearRampToValueAtTime(0.3, t + 0.05);
      gain.gain.linearRampToValueAtTime(0, t + 0.4);
      osc.start(t);
      osc.stop(t + 0.4);
    });
  }

  /* ── Yes handler ─────────────────────────────────────────────────────────── */
  window.handleYes = function () {
    const btnYes = document.getElementById("btnYes");
    btnYes.disabled = true;
    btnYes.textContent = "💕 Sending love…";

    // Stop no-button nonsense
    btnNo.style.display = "none";

    fetch(`/api/yes/${LINK_ID}`, { method: "POST" })
      .then(r => r.json())
      .then(data => {
        startConfetti();
        playCelebration();

        // Show overlay
        const overlay = document.getElementById("yesOverlay");
        overlay.style.display = "flex";

        // Detail text
        document.getElementById("yesDetail").textContent =
          `📅 ${data.date}  ⏰ ${data.time}`;

        // Image
        if (data.image_url) {
          const img = document.getElementById("yesImage");
          img.src = data.image_url;
          img.style.display = "block";
        }

        // Burst extra emojis
        const emojisContainer = document.getElementById("floatingEmojis");
        if (emojisContainer) {
          for (let i = 0; i < 20; i++) {
            setTimeout(() => {
              const el = document.createElement("span");
              el.className = "emoji-particle";
              el.textContent = ["🎉","❤️","💕","🥰","💖","✨","🌸"][Math.floor(Math.random() * 7)];
              el.style.fontSize = (20 + Math.random() * 24) + "px";
              el.style.left = Math.random() * 100 + "vw";
              el.style.animationDuration = (4 + Math.random() * 4) + "s";
              emojisContainer.appendChild(el);
              setTimeout(() => el.remove(), 8000);
            }, i * 150);
          }
        }
      })
      .catch(() => {
        btnYes.disabled = false;
        btnYes.textContent = "❤️ Yes";
        alert("Something went wrong. Please try again! 💕");
      });
  };

  /* ── Background music toggle ─────────────────────────────────────────────── */
  const musicToggle = document.getElementById("musicToggle");
  const bgMusic     = document.getElementById("bgMusic");
  let   musicPlaying = false;

  if (musicToggle && bgMusic) {
    musicToggle.addEventListener("click", () => {
      if (musicPlaying) {
        bgMusic.pause();
        musicToggle.classList.add("muted");
        musicToggle.textContent = "🔇";
        musicPlaying = false;
      } else {
        bgMusic.play().then(() => {
          musicToggle.classList.remove("muted");
          musicToggle.textContent = "🎵";
          musicPlaying = true;
        }).catch(() => {});
      }
    });

    // Auto-play on first interaction
    document.addEventListener("click", function tryPlay() {
      if (!musicPlaying) {
        bgMusic.play().then(() => {
          musicPlaying = true;
          musicToggle.textContent = "🎵";
        }).catch(() => {});
        document.removeEventListener("click", tryPlay);
      }
    }, { once: true });
  }

  /* ── Typing on load ────────────────────────────────────────────────────── */
  document.addEventListener("DOMContentLoaded", () => {
    const crushNameEl = document.getElementById("crushNameTyped");
    const messageEl   = document.getElementById("messageTyped");

    if (crushNameEl) {
      typeText(crushNameEl, CRUSH_NAME, 80, () => {
        if (messageEl) {
          setTimeout(() => typeText(messageEl, CUSTOM_MESSAGE, 30), 300);
        }
      });
    } else if (messageEl) {
      typeText(messageEl, CUSTOM_MESSAGE, 30);
    }
  });
})();
