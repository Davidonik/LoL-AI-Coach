document.addEventListener("DOMContentLoaded", async () => {
 const home = document.getElementById('home');
 const leaderboard = document.getElementById('leaderboard');

  if (home){
    home.addEventListener("click", () => {
      window.location.href = "http://127.0.0.1:5000/home";
    });
  }
  if (leaderboard){
    home.addEventListener("click", () => {
      window.location.href = "http://127.0.0.1:5000/leaderboard";
    });
  }
})