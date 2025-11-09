window.onload = () => {
  const review_btn = document.getElementsByClassName("review");
  for(const btn of review_btn) {
    btn.addEventListener("click", async () => {
      try {
        // Send the fetch request to Flask server to let ai coach review
        console.log(btn.dataset.info)

        const response = await fetch("http://127.0.0.1:5000/aws/ai_coach", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          credentials: "include",
          body: JSON.stringify({
            "matchid": btn.dataset.info,
          })
        });

        // Parse the response from Flask
        const data = await response.json();

        console.log("Server Response:", data);

      } catch (error) {
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