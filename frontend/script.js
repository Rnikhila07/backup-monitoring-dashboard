const API_BASE_URL = "http://127.0.0.1:8000";

const token = localStorage.getItem("access_token");

if (!token) {
  window.location.href = "login.html";
}

document.getElementById("logoutLink").addEventListener("click", (e) => {
  e.preventDefault();
  localStorage.removeItem("access_token");
  window.location.href = "login.html";
});

document.querySelectorAll(".upload-card").forEach((card) => {
  const backupType = card.dataset.type;
  const uploadBtn = card.querySelector(".uploadBtn");
  const fileInput = card.querySelector(".fileInput");
  const unitSelect = card.querySelector(".unitSelect");
  const statusMessage = card.querySelector(".statusMessage");

  uploadBtn.addEventListener("click", async () => {
    const file = fileInput.files[0];
    const unitNumber = unitSelect.value;

    if (!file) {
      statusMessage.textContent = "Please select a file first.";
      statusMessage.style.color = "red";
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("backup_type", backupType);
    formData.append("unit_number", unitNumber);

    statusMessage.textContent = "Uploading...";
    statusMessage.style.color = "black";

    try {
      const response = await fetch(`${API_BASE_URL}/upload/csv`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`
        },
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Upload failed");
      }

      statusMessage.textContent = `✅ ${data.records_inserted} records inserted`;
      statusMessage.style.color = "green";

    } catch (error) {
      statusMessage.textContent = `❌ ${error.message}`;
      statusMessage.style.color = "red";
    }
  });
});