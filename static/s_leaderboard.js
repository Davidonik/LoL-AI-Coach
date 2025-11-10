document.addEventListener("DOMContentLoaded", () => {
  const home = document.getElementById('home');
  if (home){
    home.addEventListener("click", () => {
      window.location.href = "http://127.0.0.1:5000/";
    });
  }
  
  const dashboard = document.getElementById('dashboard');
  if (dashboard){
    dashboard.addEventListener("click", () => {
      window.location.href = "http://127.0.0.1:5000/dashboard";
    });
  }
});