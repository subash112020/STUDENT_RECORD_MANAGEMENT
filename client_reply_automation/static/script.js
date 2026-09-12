let monitoring = false;
let intervalId = null;
let timerId = null;
let monitoringStartedAt = null;
let audioContext = null;

const status = document.getElementById("status");
const replyBox = document.getElementById("replyBox");
const monitoringTimer = document.getElementById("monitoringTimer");

document.getElementById("startMonitoring").addEventListener("click", startMonitoring);
document.getElementById("stopMonitoring").addEventListener("click", stopMonitoring);

function startMonitoring() {

    if (monitoring) {
        return;
    }

    monitoring = true;

    document.getElementById(
        "monitoringStatus"
    ).textContent = "● Active";
    updateCurrentTime();
    timerId = setInterval(updateCurrentTime, 1000);
    prepareAudio();

    status.textContent = "Checking...";
    checkReplies();

    intervalId = setInterval(
        checkReplies,
        10000
    );
}


function stopMonitoring() {

    monitoring = false;

    clearInterval(intervalId);
    clearInterval(timerId);
    intervalId = null;
    timerId = null;
    updateCurrentTime();

    document.getElementById(
        "monitoringStatus"
    ).textContent = "● Stopped";

    status.textContent = "Monitoring stopped.";
}


function checkReplies() {

    fetch("/check-replies")

        .then(response => {
            if (!response.ok) {
                throw new Error(`Request failed: ${response.status}`);
            }

            return response.json();
        })

        .then(data => {

            status.textContent = data.message;

            if (data.new_reply) {

                showReply(data);
                playReplyBeep();

            }

        })

        .catch(error => {

            console.error(
                "Error:",
                error
            );

        });
}


function showReply(data) {

    replyBox.innerHTML = `

        <h2>🔔 New Client Reply</h2>

        <p>
            ${data.message}
        </p>

        <a class="open-email" href="https://mail.google.com/mail/u/0/#all/${encodeURIComponent(data.message_id)}" target="_blank" rel="noopener">
            Open email in Gmail
        </a>

    `;

    replyBox.hidden = false;


    if (
        "Notification" in window &&
        Notification.permission === "granted"
    ) {

        new Notification(
            "New Client Reply",
            {
                body:
                    "A client has replied to your email."
            }
        );

    }

}


function updateCurrentTime() {

    const currentTime = new Date();
    const hours = String(currentTime.getHours()).padStart(2, "0");
    const minutes = String(currentTime.getMinutes()).padStart(2, "0");
    const seconds = String(currentTime.getSeconds()).padStart(2, "0");

    monitoringTimer.textContent = `Current time: ${hours}:${minutes}:${seconds}`;
}


function prepareAudio() {

    const AudioContext = window.AudioContext || window.webkitAudioContext;

    if (!AudioContext) {
        return;
    }

    if (!audioContext) {
        audioContext = new AudioContext();
    }

    if (audioContext.state === "suspended") {
        audioContext.resume();
    }
}


function playReplyBeep() {

    if (!audioContext) {
        return;
    }

    const frequencies = [600, 800, 1000, 1200];
    const toneDuration = 0.5;
    const startTime = audioContext.currentTime;

    frequencies.forEach((frequency, index) => {
        const oscillator = audioContext.createOscillator();
        const gain = audioContext.createGain();
        const toneStart = startTime + index * toneDuration;
        const toneEnd = toneStart + toneDuration;

        oscillator.frequency.value = frequency;
        gain.gain.setValueAtTime(0.15, toneStart);
        gain.gain.exponentialRampToValueAtTime(0.001, toneEnd);
        oscillator.connect(gain);
        gain.connect(audioContext.destination);
        oscillator.start(toneStart);
        oscillator.stop(toneEnd);
    });
}