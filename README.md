# 🎙️ ShuffleSpeak (Active Recall Voice Recorder)

**ShuffleSpeak** is a desktop application designed for cognitive training, language learning, and active recall. It allows users to input a set of words, shuffles them, gives the user a customizable timer to memorize the sequence, and then records their voice as they attempt to recite the words from memory.

Perfect for speech therapy, vocabulary practice, or memory testing.

![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Ubuntu-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![License](https://img.shields.io/badge/License-MIT-orange)

## ✨ Capabilities & Features

* **🧠 Active Recall Workflow:** Words are shuffled, shown for a specific timeframe, and then hidden while you record your voice. Once recording stops, words are revealed for accuracy checking.
* **⏱️ Custom Memorization Timer:** Set a highly accurate decimal countdown timer (e.g., 2.5 seconds) for the memorization phase.
* **📂 Smart Data Management:** Automatically saves and organizes your recordings into dedicated `text` and `audio` folders. Generates safe, incremental filenames (e.g., `record_1.wav`, `record_2.wav`) without overwriting previous data.
* **🗂️ Portable Workspace:** Choose exactly where your files are saved. Defaults to `Documents/Voice Recorder Sessions`. The SQLite database dynamically moves with your chosen workspace.
* **🚀 Single-Page UX:** Designed to prevent "click fatigue." You can continuously shuffle, memorize, and record without ever opening or closing multiple windows.
* **💻 Cross-Platform:** Fully compatible with both Windows and Ubuntu Linux.

---

## 🛠️ How to Use the App

1. **Create a Session:** Go to the `1. Manage Sessions` tab. Enter a session name, a comma-separated list of words, and your desired memorization time. Click **Save Session**.
2. **Load Session:** Select your session from the dropdown and click **Load & Go to Recorder**.
3. **Memorize:** Click **Start Recording**. The shuffled words will appear, and the countdown timer will begin.
4. **Record:** When the timer hits zero, the words are hidden. Speak the words from memory into your microphone.
5. **Review:** Click **Stop Recording**. The audio is saved, and the words reappear so you can check your accuracy.
6. **Repeat:** Click **Shuffle & Next** to get a brand-new arrangement and go again!

---

## 🚀 Installation & Running

There are three ways to run this application depending on your technical comfort level.

### Option A: Run from Pre-Built Executables (No Installation Required)
*Best for non-coders and end-users.*

**For Windows:**
1. Download `ShuffleSpeak.exe` from the [Releases](https://github.com/ajayragh97/ShuffleSpeak/releases/tag/v1.0.0-windows) page.
2. Double-click the file to run. 
   *(Note: Windows Defender may show a "SmartScreen" warning because the app is unpublished. Click **More Info** -> **Run Anyway**).*

**For Ubuntu / Linux:**
1. Download the `shufflespeak_ubuntu` binary from the [Releases](https://github.com/ajayragh97/ShuffleSpeak/releases/tag/v1.0.0-ubuntu/) page.
2. Open your terminal and grant execution permissions: `chmod +x shufflespeak_ubuntu`
3. Run the app: `./shufflespeak_ubuntu`

### Option B: Run via Automated Setup Scripts
*Best if you have downloaded the source code but don't want to deal with manual Python environments.*

1. Clone or download this repository.
2. **On Windows:** Double-click `start_windows.bat`. It will automatically create an isolated virtual environment, install dependencies, and launch the app.
3. **On Ubuntu:** Open a terminal in the folder and run:
   ```bash
   chmod +x start_ubuntu.sh
   ./start_ubuntu.sh
   ```
   *(Note: The Ubuntu script may ask for your password to install `portaudio19-dev`, which is required for microphone access on Linux).*

### Option C: Build from Source & Package with PyInstaller
*Best for Developers who want to modify the code and compile their own `.exe` or binary.*

**1. Prerequisites**
* Python 3.8+ installed.
* On Linux, you must install PortAudio first: `sudo apt-get install portaudio19-dev python3-tk python3-dev`

**2. Setup Environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate
# Ubuntu
source venv/bin/activate

pip install -r requirements.txt
pip install pyinstaller
```

**3. Build the Executable**
*Note: PyInstaller cannot cross-compile. You must run this command on a Windows machine to get a `.exe`, and on a Linux machine to get a Linux binary.*
```bash
pyinstaller --noconsole --onefile app.py
```
* Your standalone application will be generated inside the `dist/` folder.

---

## 📁 File Structure Output

By default, all your user data is saved safely in your `Documents` folder under `Voice Recorder Sessions`. The structure looks like this:

```text
📁 Documents
└── 📁 Voice Recorder Sessions
    ├── 🛢️ sessions.db               <-- SQLite Database tracking your setups
    └── 📁 Session_Name              <-- A folder for your specific session
        ├── 📁 audio                 <-- Contains record_1.wav, record_2.wav
        └── 📁 text                  <-- Contains record_1.txt, record_2.txt
```

---

## ⚠️ Troubleshooting

* **Microphone Error on Startup:** Ensure your default microphone is enabled in your system settings. If privacy settings block microphone access to desktop apps, the app will not be able to record.
* **PyAudio fails to install (Linux):** You are missing the C++ headers for audio. Run `sudo apt-get install portaudio19-dev build-essential` before running `pip install pyaudio`.
* **Where did my files go?:** Look at the top of the "Manage Sessions" tab. The app clearly displays the current Save Location directory.

---

