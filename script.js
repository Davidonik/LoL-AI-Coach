document.addEventListener("DOMContentLoaded", () => {
  const button = document.getElementById("setUserBtn");
  const status = document.getElementById("status");

  button.addEventListener("click", async () => {
    const sname = document.getElementById("sname").value.trim();
    const tag = document.getElementById("tag").value.trim();

    try {
      // Send the data to Flask as JSON
      const response = await fetch("http://127.0.0.1:5000/set_user", {
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

      // Parse the response from Flask
      const data = await response.json();

      console.log(data)

      if (response.ok && data.message) {
        status.innerText = `User saved: ${data.user}`;
      } else {
        status.innerText = data.error;
      }

      console.log("Server Response:", data);

    } catch (error) {
      console.error("Error during fetch:", error);
      status.innerText = "Network error, please try again.";
    }
  });
});
