$(function () {
  // === INITIAL SETUP ===
  initializeChat();

  // === CHAT SEND ===
  $("#send-btn").on("click", sendMessage);
  $("#user-input").keypress(function (e) {
    if (e.which === 13) sendMessage();
  });

  // === FILE UPLOAD ===
  $("#upload-form").on("submit", function (e) {
    e.preventDefault();
    const formData = new FormData(this);
    $.ajax({
      url: "/upload",
      type: "POST",
      data: formData,
      processData: false,
      contentType: false,
      success: function (res) {
        appendMessage("ai", `<p>${res.message}</p>`);
        loadFiles();
      },
      error: function () {
        appendMessage("ai", `<p class='text-danger'>Upload failed.</p>`);
      },
    });
  });

  // === LOAD FILES WHEN DOCS TAB OPENED ===
  $('button[data-bs-target="#docs"]').on("shown.bs.tab", loadFiles);
});


// === INITIALIZE CHAT ===
function initializeChat() {
  if (!getCookie("city") || !getCookie("lat") || !getCookie("lon")) {
    showLocationCard();
  } else {
    console.log(
      `📍 Using saved location: ${getCookie("city")} (${getCookie("lat")}, ${getCookie("lon")})`
    );
  }
}


// === SHOW LOCATION CARD ===
function showLocationCard() {
  const cardHTML = `
    <div class="message ai-message card p-3 mb-3 bg-light border">
      <h6 class="fw-bold mb-2">🌍 Location Access</h6>
      <p class="mb-2">I can provide live weather updates for your area. Would you like to enable location access?</p>
      <div>
        <button class="btn btn-primary btn-sm me-2" id="grant-location">Yes, Enable</button>
        <button class="btn btn-outline-secondary btn-sm" id="skip-location">Maybe Later</button>
      </div>
    </div>`;
  $("#chat-box").append(cardHTML);
  scrollChat();

  // Button actions
  $("#grant-location").on("click", function () {
    getLiveLocation();
  });
  $("#skip-location").on("click", function () {
    appendMessage("ai", `<p>No problem! You can enable location anytime using the "Change My Location" button below.</p>`);
    showChangeLocationCard();
    $(".card:has(#grant-location)").remove();
  });
}


// === GET LIVE LOCATION ===
function getLiveLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      function (position) {
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;
        console.log(`🌍 Coordinates: ${lat}, ${lon}`);

        // ✅ Step 1: Get real city name from backend
        $.ajax({
          url: "/get_city",
          type: "POST",
          contentType: "application/json",
          data: JSON.stringify({ lat, lon }),
          success: function (res) {
            const city = res.city || "Unknown";
            console.log(`🏙️ City resolved: ${city}`);

            // ✅ Step 2: Save to cookies
            setCookie("lat", lat, 7);
            setCookie("lon", lon, 7);
            setCookie("city", city, 7);

            // ✅ Step 3: UI update
            appendMessage(
              "ai",
              `<p>✅ Location access granted! You're currently near <b>${city}</b>. You can now ask for the weather here or anywhere.</p>`
            );
            showChangeLocationCard();
            $(".card:has(#grant-location)").remove();
          },
          error: function () {
            appendMessage("ai", `<p class='text-danger'>⚠️ Unable to determine your city name. Please try again.</p>`);
          },
        });
      },
      function (err) {
        appendMessage("ai", `<p class='text-danger'>⚠️ Unable to access location: ${err.message}</p>`);
      }
    );
  } else {
    appendMessage("ai", `<p class='text-danger'>Geolocation is not supported by your browser.</p>`);
  }
}


// === SHOW CHANGE LOCATION CARD ===
function showChangeLocationCard() {
  const cardHTML = `
    <div class="message ai-message card p-3 mb-3 bg-white border mt-3">
      <h6 class="fw-bold mb-2">📍 Location Settings</h6>
      <p class="mb-2">Would you like to update your location?</p>
      <button class="btn btn-outline-primary btn-sm" id="change-location">Change My Location</button>
    </div>`;
  $("#chat-box").append(cardHTML);
  scrollChat();

  $("#change-location").on("click", function () {
    getLiveLocation();
  });
}


// === SEND MESSAGE ===
function sendMessage() {
  const userText = $("#user-input").val();
  if (!userText.trim()) return;

  appendMessage("user", userText);
  $("#user-input").val("");

  $.ajax({
    url: "/chat",
    type: "POST",
    contentType: "application/json",
    data: JSON.stringify({ message: userText }),
    success: function (res) {
      appendMessage("ai", res.response);
    },
    error: function () {
      appendMessage("ai", `<p class='text-danger'>Server error. Please try again later.</p>`);
    },
  });
}


// === APPEND MESSAGE ===
function appendMessage(sender, html) {
  const msgClass = sender === "user" ? "user-message bg-primary text-white" : "ai-message bg-light";
  $("#chat-box").append(`<div class="message ${msgClass} p-2 rounded mb-2">${html}</div>`);
  scrollChat();
}


// === SCROLL CHAT ===
function scrollChat() {
  $("#chat-box").scrollTop($("#chat-box")[0].scrollHeight);
}


// === COOKIE HELPERS ===
function setCookie(name, value, days) {
  const d = new Date();
  d.setTime(d.getTime() + days * 24 * 60 * 60 * 1000);
  document.cookie = `${name}=${value}; expires=${d.toUTCString()}; path=/`;
}

function getCookie(name) {
  const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
  return match ? match[2] : null;
}


// === LOAD FILES ===
function loadFiles() {
  $.get("/files", function (files) {
    if (!files.length) {
      $("#file-list").html("<p class='text-muted'>No files uploaded yet.</p>");
      return;
    }
    let html = "<ul>";
    $.each(files, function (_, f) {
      html += `
        <li>
          <a href="/uploads/${f}" target="_blank">${f}</a>
          <button class="btn btn-sm btn-danger ms-2" onclick="deleteFile('${f}')">Delete</button>
        </li>`;
    });
    html += "</ul>";
    $("#file-list").html(html);
  });
}


// === DELETE FILE ===
function deleteFile(filename) {
  if (!confirm(`Delete ${filename}?`)) return;
  $.ajax({
    url: `/delete/${filename}`,
    type: "DELETE",
    success: function (res) {
      appendMessage("ai", `<p>${res.message}</p>`);
      loadFiles();
    },
    error: function () {
      appendMessage("ai", `<p class='text-danger'>Error deleting file.</p>`);
    },
  });
}
