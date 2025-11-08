window.onload = () => {
    const test_btn = document.getElementById("test");

    test_btn.addEventListener("click", async () => {
    try {
      // Send the fetch request to Flask server to set up user
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