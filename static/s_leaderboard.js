
document.addEventListener("DOMContentLoaded", async () => {
const home = document.getElementById('home');


if (home){
    home.addEventListener("click", () => {
    window.location.href = '../index.html';
    });
  }
})