window.onload = () => {
  const review_btn = document.getElementsByClassName("review");
  for(const btn of review_btn) {
    btn.addEventListener("click", async () => {
      try {
        for (const b of review_btn) {
          b.disabled = true;
        }
        btn.innerText = "Loading...";
        btn.classList.remove("hover:bg-blue-600");

        // Send the fetch request to Flask server to let ai coach review
        const response = await fetch("http://127.0.0.1:5000/aws/ai_coach", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          credentials: "include",
          body: JSON.stringify({
            "matchid": btn.dataset.matchid,
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
      }
    });
  }

  const test_btn = document.getElementById("test");
  test_btn.addEventListener("click", async () => {
    try {
      // Send the fetch request to Flask server to get traits
      const response = await fetch("http://127.0.0.1:5000/aws/ai_traits", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        credentials: "include"
      });

      // Parse the response from Flask
      const data = await response.json();

      console.log("Server Response:", data);

    } catch (error) {
      console.error("Error during fetch:", error);
    }
  });
};