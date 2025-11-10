document.addEventListener("DOMContentLoaded", () => {
  const home = document.getElementById('home');
  if (home){
    home.addEventListener("click", () => {
      window.location.href = "https://lol-ai-coach.onrender.com/";
    });
  }
  
  const dashboard = document.getElementById('dashboard');
  if (dashboard){
    dashboard.addEventListener("click", () => {
      window.location.href = "https://lol-ai-coach.onrender.com/dashboard";
    });
  }
});