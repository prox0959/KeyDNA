// App State
// TR: Uygulama Durumu
let currentMode = 'enroll'; // Can be 'enroll' or 'verify'
const TARGET_PHRASE = "the quick brown fox";
const ENROLL_COUNT = 5;

// Variables to store current typing session data
// TR: Mevcut yazma oturumu verilerini saklamak için değişkenler
let currentTimings = [];
let enrollAttempts = [];

// DOM Elements
const btnEnroll = document.getElementById('btn-enroll');
const btnVerify = document.getElementById('btn-verify');
const usernameInput = document.getElementById('username');
const phraseInput = document.getElementById('phrase-input');
const instructionText = document.getElementById('instruction-text');
const counterEl = document.getElementById('counter');
const feedbackEl = document.getElementById('feedback');
const feedbackMessage = document.getElementById('feedback-message');
const confidenceScore = document.getElementById('confidence-score');

// Chart instance
let typingChart = null;

// Initialize the Chart.js visualization
// TR: Chart.js görselleştirmesini başlatıyoruz
function initChart() {
    const ctx = document.getElementById('typingChart').getContext('2d');
    
    // Set default color for Chart.js to match our theme
    Chart.defaults.color = '#8b949e';
    Chart.defaults.borderColor = '#30363d';

    typingChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Dwell Time (ms)',
                    data: [],
                    backgroundColor: 'rgba(0, 255, 65, 0.5)',
                    borderColor: '#00FF41',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Milliseconds (ms)'
                    }
                }
            }
        }
    });
}

// Update the chart with new timings data
// TR: Grafiği yeni zamanlama verileriyle günceller
function updateChart() {
    // Extract dwell times to visualize
    // We match the keyup events with keydown events to find how long a key was pressed
    let dwells = [];
    let labels = [];
    let presses = {};

    currentTimings.forEach(event => {
        if (event.type === 'keydown') {
            presses[event.key] = event.time;
        } else if (event.type === 'keyup' && presses[event.key]) {
            let dwellTime = event.time - presses[event.key];
            dwells.push(dwellTime);
            labels.push(event.key === ' ' ? 'SPACE' : event.key.toUpperCase());
            delete presses[event.key];
        }
    });

    typingChart.data.labels = labels;
    typingChart.data.datasets[0].data = dwells;
    typingChart.update();
}

// Reset the input field and current session data
// TR: Girdi alanını ve mevcut oturum verilerini sıfırlar
function resetInput() {
    phraseInput.value = '';
    currentTimings = [];
}

// Switch between Enroll and Verify modes
// TR: Kayıt (Enroll) ve Doğrulama (Verify) modları arasında geçiş yapar
function setMode(mode) {
    currentMode = mode;
    resetInput();
    enrollAttempts = [];
    feedbackEl.className = 'feedback hidden';
    
    if (mode === 'enroll') {
        btnEnroll.classList.add('active');
        btnVerify.classList.remove('active');
        instructionText.innerHTML = `Type the phrase below <strong>5 times</strong> to create your typing DNA.`;
        counterEl.style.display = 'block';
        counterEl.innerText = `Attempts: 0/${ENROLL_COUNT}`;
    } else {
        btnVerify.classList.add('active');
        btnEnroll.classList.remove('active');
        instructionText.innerHTML = `Type the phrase below <strong>once</strong> to verify your identity.`;
        counterEl.style.display = 'none';
    }
}

// Event Listeners for mode buttons
btnEnroll.addEventListener('click', () => setMode('enroll'));
btnVerify.addEventListener('click', () => setMode('verify'));

// Event Listener for KeyDown: Capture the exact timestamp when a key is pressed
// TR: Tuşa basıldığında tam zaman damgasını yakalar
phraseInput.addEventListener('keydown', (e) => {
    // Ignore special keys for the phrase typing
    if (e.key === 'Shift' || e.key === 'CapsLock' || e.key === 'Backspace') return;
    
    currentTimings.push({
        key: e.key,
        type: 'keydown',
        time: Date.now()
    });
});

// Event Listener for KeyUp: Capture the exact timestamp when a key is released
// TR: Tuş bırakıldığında tam zaman damgasını yakalar
phraseInput.addEventListener('keyup', (e) => {
    if (e.key === 'Shift' || e.key === 'CapsLock' || e.key === 'Backspace') return;
    
    currentTimings.push({
        key: e.key,
        type: 'keyup',
        time: Date.now()
    });
    
    updateChart();

    // Check if user has finished typing the target phrase
    if (phraseInput.value.toLowerCase() === TARGET_PHRASE) {
        phraseInput.disabled = true; // Disable temporarily while processing
        handlePhraseCompletion();
    }
});

// Process the completed phrase
// TR: Tamamlanan cümleyi işler
async function handlePhraseCompletion() {
    const username = usernameInput.value.trim();
    
    if (!username) {
        alert("Please enter a username first!");
        resetInput();
        phraseInput.disabled = false;
        return;
    }

    if (currentMode === 'enroll') {
        // Add current timings to our list of attempts
        enrollAttempts.push([...currentTimings]);
        counterEl.innerText = `Attempts: ${enrollAttempts.length}/${ENROLL_COUNT}`;
        
        if (enrollAttempts.length < ENROLL_COUNT) {
            // Wait a moment, then let user type again
            setTimeout(() => {
                resetInput();
                phraseInput.disabled = false;
                phraseInput.focus();
            }, 1000);
        } else {
            // We have all 5 attempts, send to backend
            await sendEnrollData(username);
        }
    } else if (currentMode === 'verify') {
        // Send single attempt to backend for verification
        await sendVerifyData(username);
    }
}

// Send enrollment data to Flask backend
// TR: Kayıt verilerini Flask arka ucuna gönderir
async function sendEnrollData(username) {
    try {
        const response = await fetch('/enroll', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: username,
                timings_list: enrollAttempts
            })
        });
        
        const result = await response.json();
        
        // Show success message
        feedbackEl.className = 'feedback success';
        feedbackMessage.innerText = "Profile created successfully!";
        confidenceScore.parentElement.style.display = 'none';
        
        setTimeout(() => {
            setMode('verify');
            phraseInput.disabled = false;
        }, 2000);
        
    } catch (error) {
        console.error("Error during enrollment:", error);
        alert("Failed to enroll. See console for details.");
        phraseInput.disabled = false;
    }
}

// Send verification data to Flask backend
// TR: Doğrulama verilerini Flask arka ucuna gönderir
async function sendVerifyData(username) {
    try {
        const response = await fetch('/verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: username,
                timings: currentTimings
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // Show result based on match status
            // TR: Eşleşme durumuna göre sonucu gösterir
            feedbackEl.className = `feedback ${result.match ? 'success' : 'error'}`;
            feedbackMessage.innerText = result.message;
            confidenceScore.parentElement.style.display = 'block';
            confidenceScore.innerText = result.confidence;
        } else {
            feedbackEl.className = 'feedback error';
            feedbackMessage.innerText = result.error || "Verification failed.";
            confidenceScore.parentElement.style.display = 'none';
        }
        
        setTimeout(() => {
            resetInput();
            phraseInput.disabled = false;
            phraseInput.focus();
        }, 3000);
        
    } catch (error) {
        console.error("Error during verification:", error);
        alert("Failed to verify. See console for details.");
        phraseInput.disabled = false;
    }
}

// Initialize on page load
window.onload = () => {
    initChart();
};
