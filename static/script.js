let chart;
let sniffing = false;

function startSniffing() {
  fetch('/start');
  sniffing = true;
  updateData();
}

function stopSniffing() {
  fetch('/stop');
  sniffing = false;
}

function exportData() {
  window.location.href = '/export';
}

function updateData() {
  if (!sniffing) return;

  fetch('/packets')
    .then(response => response.json())
    .then(data => {
      const tbody = document.querySelector("#packetTable tbody");
      tbody.innerHTML = "";

      data.slice().reverse().forEach(pkt => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${pkt.time}</td>
          <td>${pkt.source}</td>
          <td>${pkt.destination}</td>
          <td>${pkt.protocol}</td>
          <td>${pkt.length}</td>
        `;
        tbody.appendChild(row);
      });
    });

  fetch('/graph')
    .then(response => response.json())
    .then(data => {
      if (!chart) {
        const ctx = document.getElementById("packetChart").getContext("2d");
        chart = new Chart(ctx, {
          type: "line",
          data: {
            labels: data.timestamps,
            datasets: [{
              label: "Packets per second",
              data: data.packet_counts,
              borderColor: "#1100ffff",
              backgroundColor: "rgba(0, 225, 255, 0.57)",
              tension: 0.3,
              fill: true,
            }]
          },
          options: {
            responsive: true,
            scales: {
              x: {
                title: {
                  display: true,
                  text: "Time",
                  color: "#00bcd4"
                },
                ticks: { color: "#aaa" }
              },
              y: {
                title: {
                  display: true,
                  text: "Packet Count",
                  color: "#00bcd4"
                },
                ticks: { color: "#aaa" }
              }
            },
            plugins: {
              legend: { labels: { color: "#0066ffff" } }
            }
          }
        });
      } else {
        chart.data.labels = data.timestamps;
        chart.data.datasets[0].data = data.packet_counts;
        chart.update();
      }
    });

  setTimeout(updateData, 1000);
}
