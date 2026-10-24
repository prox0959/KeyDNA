
# KeyDNA 🧬

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Status](https://img.shields.io/badge/status-active-success.svg)

**KeyDNA** is a modern Keystroke Dynamics Biometric Authentication System. It doesn't just look at *what* you type (your password/phrase), but *how* you type it. It analyzes your unique typing rhythm to detect imposters, even if they know your exact passphrase!

## 🧠 What is Keystroke Dynamics?
Keystroke dynamics is a behavioral biometric. Just like your fingerprint or DNA, the way you type on a keyboard is unique to you. Key factors include:
- **Dwell Time:** How long you hold down a specific key.
- **Flight Time:** The time it takes for your finger to travel from releasing one key to pressing the next.

This system captures these micro-second timings and creates a "Typing Profile" for your user account.

## ✨ Features
- 💻 **Beautiful Hacker Aesthetic UI** (Dark mode, neon green accents, monospace fonts)
- 📊 **Real-time Rhythm Visualization** using Chart.js
- 🔐 **Dual Modes**: 
  - **Enroll:** Type the phrase 5 times to build your typing DNA profile.
  - **Verify:** Type it once to authenticate.
- 🐍 **Lightweight Python Backend** using Flask.
- 🤖 **Custom ML Distance Algorithm** to calculate similarity scores and confidence percentages.

## 🛠️ How It Works

1. **Capture:** The JavaScript frontend (`app.js`) listens for `keydown` and `keyup` events, recording the precise timestamp (in milliseconds) for each keystroke.
2. **Feature Extraction:** The Python backend (`model.py`) calculates arrays of *Dwell Times* and *Flight Times*.
3. **Training:** By typing the phrase 5 times, the system calculates the mathematical *mean* (average) of your timings to create a stable profile.
4. **Verification:** When you attempt to log in, your new timings are compared against your saved profile using **Manhattan Distance**. If the distance is below a certain threshold, you are authenticated!

## 🚀 Installation and Usage

1. **Clone the repository (or navigate to the folder):**
   ```bash
   cd KeyDNA
   ```

2. **Install the requirements:**
   Make sure you have Python installed, then run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Flask application:**
   ```bash
   python app.py
   ```

4. **Open in Browser:**
   Navigate to `http://127.0.0.1:5000` in your web browser.

## 🔬 The Science Behind It
In `model.py`, we use simple but effective statistical methods.
- We calculate absolute differences between your current attempt and your baseline profile.
- Total Distance = Sum of Dwell Differences + Sum of Flight Differences.
- Confidence Score drops as the Total Distance increases.
- *Turkish Note:* Sistem basit bir uzaklık metriği (Manhattan distance) kullanarak yeni yazılan verinin orijinal profile ne kadar benzediğini matematiksel olarak hesaplar.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
