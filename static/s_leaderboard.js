document.addEventListener("DOMContentLoaded", () => {
  const home = document.getElementById('home');
  if (home){
    home.addEventListener("click", () => {
      window.location.href = "/";
    });
  }
  
  const dashboard = document.getElementById('dashboard');
  if (dashboard){
    dashboard.addEventListener("click", () => {
      window.location.href = "/dashboard";
    });
  }
});