document.addEventListener("DOMContentLoaded", async () => {
  let lastScrollY = window.scrollY;
  const navbar = document.getElementById("navbar");
  const sw = document.getElementById('mySwitch');
  const bubble = document.getElementById('speech');
  window.addEventListener("scroll", () => {
      const currentScroll = window.scrollY;
  // hide nav bar when scrolling down, show when scrolling up
  if (currentScroll > lastScrollY && currentScroll > 50) {
      navbar.style.transform = "translateY(-100%)";
  } else {
      navbar.style.transform = "translateY(0)";
  }
  if (currentScroll > 0) {
  navbar.classList.add("shadow-lg");
  } else {
  navbar.classList.remove("shadow-lg");
  }
  lastScrollY = currentScroll;
  });
  
  function updateBubble(){
    const on = sw.checked;
    bubble.textContent = on ? "🔥 Roast is ON" : "Roast is OFF";
    bubble.classList.toggle('bubble-on', on);
    bubble.classList.toggle('bubble-off', !on);
  }

  sw.addEventListener('change', updateBubble);
  // init on load (in case switch is pre-checked from saved state)
  updateBubble();
});