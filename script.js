document.addEventListener("DOMContentLoaded", () => {
  const button = document.getElementById("setUserBtn");
  const status = document.getElementById("status");

  button.addEventListener("click", async () => {
    const sname = document.getElementById("sname").value.trim();
    const tag = document.getElementById("tag").value.trim();

    if (!sname || !tag) {
      status.innerText = "⚠️ Please enter both summoner name and tag.";
      return;
    }

    status.innerText = "Sending data...";

    try {
      // Send the data to Flask as JSON
      const response = await fetch("/set_user", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ sname, tag })
      });

      // Parse the response from Flask
      const data = await response.get_json();

      if (response.ok && data.message) {
        status.innerText = `User saved: ${data.user}`;
      } else {
        status.innerText = "Failed to save user.";
      }

      console.log("Server Response:", data);

    } catch (error) {
      console.error("Error during fetch:", error);
      status.innerText = "Network error, please try again.";
    }
  });
});
