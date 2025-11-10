document.addEventListener("DOMContentLoaded", () => {
  const mySwitch = document.getElementById("mySwitch");
  const status = document.getElementById("status");

  mySwitch.addEventListener("change", () => {
    if (mySwitch.checked) {
      status.innerText = "Roast Switch is ON";
    } else {
      status.innerText = "Roast Switch is OFF";
    }
  });

  const review_btn = document.getElementsByClassName("review");
  for(const btn of review_btn) {
    console.log(btn.dataset.matchid)
    btn.addEventListener("click", async () => {
      try {
        for (const b of review_btn) {
          b.disabled = true;
        }
        btn.innerText = "Loading...";
        btn.classList.remove("hover:bg-blue-600");

        fetch("http://127.0.0.1:5000/api/player/update_stats", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({
            "matchid": btn.dataset.matchid,
          }),
        }).catch(err => console.warn("Stats update failed:", err));

        // Send the fetch request to Flask server to let ai coach review
        const response = await fetch("http://127.0.0.1:5000/aws/ai_coach", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          credentials: "include",
          body: JSON.stringify({
            "matchid": btn.dataset.matchid,
            "roast": mySwitch.checked,
          })
        });

        if (response.redirected) {
          window.location.href = response.url;
          return;
        } else {
          // Parse the response from Flask
          const data = await response.json();
          console.log("Server Response:", data);
        }

      } catch (error) {
        for (const b of review_btn) {
          b.disabled = false;
          b.innerText = "Review";
          b.classList.add("hover:bg-blue-600");
        }
        console.error("Error during fetch:", error);
      }
    });
  }
});