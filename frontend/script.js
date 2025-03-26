async function fetchRooms() {
    let response = await fetch("http://127.0.0.1:5000/rooms");
    let rooms = await response.json();
    document.getElementById("rooms").innerHTML = rooms.map(room => `
        <li>Room ID: ${room[0]}, Type: ${room[2]}, Price: $${room[3]}</li>
    `).join("");
}

document.getElementById("bookingForm").addEventListener("submit", async function(event) {
    event.preventDefault();
    let data = {
        customer_id: document.getElementById("customer_id").value,
        room_id: document.getElementById("room_id").value,
        checkin_date: document.getElementById("checkin_date").value,
        checkout_date: document.getElementById("checkout_date").value,
        total_cost: document.getElementById("total_cost").value
    };

    let response = await fetch("http://127.0.0.1:5000/book", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    let result = await response.json();
    alert(result.message);
    fetchRooms();
});
