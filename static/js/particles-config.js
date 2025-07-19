// static/js/particles-config.js
particlesJS('particles-container', {
  "particles": {
    "number": {
      "value": 30, // عدد قليل
      "density": { "enable": true, "value_area": 800 }
    },
    "color": { "value": "#ffffff" },
    "shape": { "type": "circle" },
    "opacity": {
      "value": 0.2, // شبه شفاف
      "random": true,
      "anim": { "enable": true, "speed": 0.5, "opacity_min": 0.05, "sync": false }
    },
    "size": {
      "value": 3,
      "random": true,
      "anim": { "enable": false }
    },
    "line_linked": { "enable": false }, // لا نريد خطوطًا
    "move": {
      "enable": true,
      "speed": 0.6, // حركة بطيئة جدًا
      "direction": "none",
      "random": true,
      "straight": false,
      "out_mode": "out",
      "bounce": false
    }
  },
  "interactivity": { "detect_on": "canvas", "events": { "onhover": { "enable": false }, "onclick": { "enable": false } } },
  "retina_detect": true
});