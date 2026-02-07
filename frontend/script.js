let lastPredictedDisease = "";
let chatInitialized = false;

/* ---------- IMAGE PREVIEW ---------- */
document.getElementById("imageInput").addEventListener("change", previewImage);

function previewImage() {
    const input = document.getElementById("imageInput");
    const preview = document.getElementById("imagePreview");

    preview.innerHTML = "";

    if (!input.files || !input.files[0]) return;

    const reader = new FileReader();
    reader.onload = function (e) {
        preview.innerHTML = `<img src="${e.target.result}" alt="Uploaded Image">`;
    };
    reader.readAsDataURL(input.files[0]);
}

/* ---------- UPLOAD & PREDICT ---------- */
async function uploadImage() {
    const input = document.getElementById("imageInput");
    const resultDiv = document.getElementById("result");
    const gradcamDiv = document.getElementById("gradcamPreview");
    const chatBtn = document.getElementById("chatButton");

    if (!input.files || input.files.length === 0) {
        resultDiv.innerHTML = "⚠️ Please select an image.";
        return;
    }

    const formData = new FormData();
    formData.append("file", input.files[0]);

    resultDiv.innerHTML = "🔍 Analyzing image...";
    gradcamDiv.innerHTML = "";
    chatBtn.disabled = true;

    try {
        const response = await fetch("http://127.0.0.1:8000/predict", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!data.top_predictions || data.top_predictions.length === 0) {
            resultDiv.innerHTML = `<div class="note warning">
                ${data.note || "❌ Unable to analyze image"}
            </div>`;
            lastPredictedDisease = "";
            return;
        }

        lastPredictedDisease = data.top_predictions[0].disease;
        chatInitialized = false;
        chatBtn.disabled = false;

        let html = `<div class="result-title">Top Possible Skin Conditions</div>`;

        data.top_predictions.forEach((item, i) => {
            html += `
                <div class="prediction">
                    <strong>${i + 1}. ${item.disease}</strong> – ${item.confidence}%
                    <div class="progress-bar">
                        <div class="progress-fill" style="width:${item.confidence}%"></div>
                    </div>
                </div>`;
        });

        html += `<div class="note">${data.note}</div>`;
        resultDiv.innerHTML = html;

        if (data.gradcam) {
            gradcamDiv.innerHTML = `<img src="data:image/jpeg;base64,${data.gradcam}">`;
        }

    } catch (err) {
        console.error(err);
        resultDiv.innerHTML = "❌ Server error.";
    }
}

/* ---------- CHAT ---------- */
function toggleChat() {
    const popup = document.getElementById("chatPopup");
    popup.classList.toggle("show-chat");

    const chatBox = document.getElementById("chatBox");

    if (!chatInitialized && lastPredictedDisease) {
        chatInitialized = true;

        fetch("http://127.0.0.1:8000/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                disease: lastPredictedDisease,
                message: "start",
                username: localStorage.getItem("username") || "Guest"   // ✅ FIX
            })
        })
        .then(r => r.json())
        .then(d => {
            chatBox.innerHTML =
                `<p><b>Bot:</b> ${d.reply.replace(/\n/g,"<br>")}</p>`;
        })
        .catch(e=>{
            console.error(e);
            chatBox.innerHTML = "Chat server error";
        });
    }
}

/* ---------- SEND MESSAGE ---------- */
async function sendMessage() {
    const input = document.getElementById("chatInput");
    const chatBox = document.getElementById("chatBox");

    const msg = input.value.trim();
    if (!msg) return;

    chatBox.innerHTML += `<p><b>You:</b> ${msg}</p>`;
    input.value = "";

    try {
        const res = await fetch("http://127.0.0.1:8000/chat", {
            method: "POST",
            headers: {"Content-Type":"application/json"},
            body: JSON.stringify({
                disease: lastPredictedDisease,
                message: msg,
                username: localStorage.getItem("username") || "Guest"   // ✅ FIX
            })
        });

        const data = await res.json();

        chatBox.innerHTML +=
            `<p><b>Bot:</b> ${data.reply.replace(/\n/g,"<br>")}</p>`;

        chatBox.scrollTop = chatBox.scrollHeight;

    } catch (e) {
        console.error(e);
        chatBox.innerHTML += `<p>❌ Chat error</p>`;
    }
}
