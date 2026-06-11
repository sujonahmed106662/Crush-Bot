/* Floating hearts & emoji particles */
(function () {
  function randomBetween(a, b) { return a + Math.random() * (b - a); }

  function spawnParticle(container, content, sizeMin, sizeMax) {
    const el = document.createElement("span");
    el.classList.add(container.id === "floatingHearts" ? "heart-particle" : "emoji-particle");
    el.textContent = content;
    const size = randomBetween(sizeMin, sizeMax);
    el.style.fontSize = size + "px";
    el.style.left = randomBetween(0, 100) + "vw";
    el.style.animationDuration = randomBetween(6, 14) + "s";
    el.style.animationDelay = randomBetween(0, 3) + "s";
    el.style.opacity = randomBetween(0.4, 0.9);
    container.appendChild(el);
    const dur = parseFloat(el.style.animationDuration) * 1000 + parseFloat(el.style.animationDelay) * 1000;
    setTimeout(() => { if (el.parentNode) el.parentNode.removeChild(el); }, dur + 500);
  }

  const HEARTS = ["❤️","💕","💗","💖","💝","🌸","✨"];

  function startHearts() {
    const c = document.getElementById("floatingHearts");
    if (!c) return;
    function loop() {
      spawnParticle(c, HEARTS[Math.floor(Math.random() * HEARTS.length)], 12, 28);
      setTimeout(loop, randomBetween(600, 1400));
    }
    // Initial burst
    for (let i = 0; i < 8; i++) {
      setTimeout(() => spawnParticle(c, HEARTS[Math.floor(Math.random() * HEARTS.length)], 14, 26), i * 200);
    }
    loop();
  }

  function startEmojis() {
    const c = document.getElementById("floatingEmojis");
    if (!c) return;
    const raw = c.dataset.emoji || "❤️";
    const emojis = raw.split(/\s+/).filter(Boolean);
    if (!emojis.length) return;
    function loop() {
      spawnParticle(c, emojis[Math.floor(Math.random() * emojis.length)], 18, 36);
      setTimeout(loop, randomBetween(800, 2000));
    }
    for (let i = 0; i < 5; i++) {
      setTimeout(() => spawnParticle(c, emojis[Math.floor(Math.random() * emojis.length)], 20, 34), i * 300);
    }
    loop();
  }

  document.addEventListener("DOMContentLoaded", () => {
    startHearts();
    startEmojis();
  });
})();
