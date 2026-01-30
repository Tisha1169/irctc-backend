const API_BASE = "http://127.0.0.1:8000/api";
const token = localStorage.getItem("accessToken");

if (!token) {
  alert("Login required");
  window.location.href = "../index.html";
}

// ---------------- STATS ----------------

fetch(`${API_BASE}/admin/stats/`, {
  headers: {
    "Authorization": `Bearer ${token}`
  }
})
.then(res => res.json())
.then(data => {

  document.getElementById("totalBookings").innerText = data.total_bookings;
  document.getElementById("confirmed").innerText = data.confirmed;
  document.getElementById("waitlisted").innerText = data.waitlisted;
  document.getElementById("cancelled").innerText = data.cancelled;
  document.getElementById("trains").innerText = data.total_trains;

  loadChart(data.confirmed, data.waitlisted, data.cancelled);
});


// ---------------- BOOKING TABLE ----------------

fetch(`${API_BASE}/history/`, {
  headers: {
    "Authorization": `Bearer ${token}`
  }
})
.then(res => res.json())
.then(bookings => {

  const table = document.getElementById("bookingTable");

  bookings.forEach(b => {

    const row = `
      <tr class="border">
        <td class="p-2">${b.booking_id}</td>
        <td>${b.user || "User"}</td>
        <td>${b.train}</td>
        <td>${b.date}</td>
        <td>${b.seats}</td>
        <td>${b.status}</td>
      </tr>
    `;

    table.innerHTML += row;
  });

});


// ---------------- CHART ----------------

function loadChart(confirmed, waitlisted, cancelled) {

  const ctx = document.getElementById("bookingChart");

  new Chart(ctx, {
    type: "line",
    data: {
      labels: ["Confirmed", "Waitlisted", "Cancelled"],
      datasets: [{
        label: "Tickets",
        data: [confirmed, waitlisted, cancelled],
        borderWidth: 2,
        fill: false
      }]
    }
  });
}


// ---------------- LOGOUT ----------------

function logout() {
  localStorage.clear();
  window.location.href = "../index.html";
}
