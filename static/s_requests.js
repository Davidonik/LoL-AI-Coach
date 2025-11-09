window.onload = () => {
  const review_btn = document.getElementsByClassName("review");
  for(const btn of review_btn) {
    btn.addEventListener("click", async () => {
      try {
        button.disabled = true;
        button.innerText = "Loading...";
        button.classList.remove("hover:bg-blue-600");
        // Send the fetch request to Flask server to let ai coach review
        console.log(btn.dataset.matchid)

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

        // Parse the response from Flask
        const data = await response.json();

        console.log("Server Response:", data);

      } catch (error) {
        button.disabled = false;
        button.innerText = "Review";
        button.classList.add("hover:bg-blue-600");
        console.error("Error during fetch:", error);
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