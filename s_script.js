document.addEventListener("DOMContentLoaded", () => {
  const button = document.getElementById("setUserBtn");
  const status = document.getElementById("status");
  const home = document.getElementById('home');


  button.addEventListener("click", async () => {
    const sname = document.getElementById("sname").value.trim();
    const tag = document.getElementById("tag").value.trim();

    try {
      // Send the fetch request to Flask server to set up user
      const response = await fetch("http://127.0.0.1:5000/api/set_user", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        credentials: "include",
        body: JSON.stringify({
          "sname": sname,
          "tag": tag
        })
      });

      if (response.redirected) {
        window.location.href = response.url;
        return;
      }

      // Parse the response from Flask
      const data = await response.json();

      // console.log(data)
      // console.log("Server Response:", data);

      if (data.error) {
        status.innerText = data.error;
      }

    } catch (error) {
      console.error("Error during fetch:", error);
      status.innerText = "Network error, please try again.";
    }
  });

  if (homeButton) {
    home.addEventListener("click", async () => {
      window.location.href = 'index.html';
      });
  }
});
