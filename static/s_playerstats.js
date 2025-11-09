document.addEventListener("DOMContentLoaded", async () => {
    console.log("hi");
    const stats_div = document.getElementById("stats");

    // Show loading text immediately
    stats_div.innerText = "Loading stats...";

    try {
        const response = await fetch("http://127.0.0.1:5000/api/player/stats", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            credentials: "include",
        });

        const data = await response.json();

        if (data) {
            // If data is an object, convert to string for display
            stats_div.innerText = typeof data === "object" ? JSON.stringify(data, null, 2) : data;
        } else {
            stats_div.innerText = "No stats available";
        }
    } catch (error) {
        console.error("Error during fetch:", error);
        stats_div.innerText = "Failed to load stats";
    }
});
