import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import random
import os
import glob
import threading
import wave
import pyaudio
from pathlib import Path

class Database:
    def __init__(self, db_path="sessions.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS sessions 
                               (name TEXT PRIMARY KEY, words TEXT, memo_time REAL)''')
                               
        try:
            self.cursor.execute("ALTER TABLE sessions ADD COLUMN memo_time REAL DEFAULT 1.0")
        except sqlite3.OperationalError:
            pass 
            
        self.conn.commit()

    def save_session(self, name, words, memo_time):
        self.cursor.execute("REPLACE INTO sessions (name, words, memo_time) VALUES (?, ?, ?)", 
                            (name, words, memo_time))
        self.conn.commit()

    def get_session_data(self, name):
        self.cursor.execute("SELECT words, memo_time FROM sessions WHERE name=?", (name,))
        row = self.cursor.fetchone()
        if row:
            return row[0].split(','), float(row[1])
        return[], 1.0

    def get_all_sessions(self):
        self.cursor.execute("SELECT name FROM sessions")
        return [row[0] for row in self.cursor.fetchall()]


class AudioRecorder:
    def __init__(self):
        self.is_recording = False
        self.frames =[]
        self.audio = pyaudio.PyAudio()
        self.stream = None

    def start(self, filepath):
        self.is_recording = True
        self.filepath = filepath
        threading.Thread(target=self._record_thread, daemon=True).start()

    def _record_thread(self):
        self.frames =[]
        self.stream = self.audio.open(format=pyaudio.paInt16, channels=1, rate=44100, 
                                      input=True, frames_per_buffer=1024)
        while self.is_recording:
            try:
                data = self.stream.read(1024, exception_on_overflow=False)
                self.frames.append(data)
            except Exception:
                pass

        self.stream.stop_stream()
        self.stream.close()

        with wave.open(self.filepath, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(self.frames))

    def stop(self):
        self.is_recording = False


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ShuffleSpeak - Memory Training Recorder")
        self.geometry("600x600") 
        
        self.workspace_dir = os.path.join(str(Path.home()), "Documents", "Voice Recorder Sessions")
        os.makedirs(self.workspace_dir, exist_ok=True)
        
        self.db = Database(os.path.join(self.workspace_dir, "sessions.db"))
        self.recorder = AudioRecorder()
        
        self.current_session = None
        self.current_words =[]
        self.current_display_text = ""
        self.current_memo_time = 1.0  # Now represents time PER word
        self.current_record_id = None
        self.current_word_index = 0
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.setup_management_tab()
        self.setup_recording_tab()

    def setup_management_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="1. Manage Sessions")
        
        ws_frame = ttk.LabelFrame(frame, text="Save Location (Where your files go)")
        ws_frame.pack(fill="x", padx=10, pady=(10, 10))
        
        self.lbl_workspace = ttk.Label(ws_frame, text=self.workspace_dir, foreground="blue")
        self.lbl_workspace.pack(side="left", padx=10, pady=10)
        
        btn_change_ws = ttk.Button(ws_frame, text="Change Folder", command=self.change_workspace)
        btn_change_ws.pack(side="right", padx=10, pady=10)
        
        ttk.Label(frame, text="Session Name:").pack(pady=(5, 0))
        self.entry_session_name = ttk.Entry(frame, width=40)
        self.entry_session_name.pack(pady=5)
        
        ttk.Label(frame, text="Enter words (comma separated):").pack(pady=(5, 0))
        self.text_words = tk.Text(frame, height=4, width=50)
        self.text_words.pack(pady=5)
        
        # --- UPDATED: Time per word ---
        ttk.Label(frame, text="Time per word (Seconds, e.g., 1.0):").pack(pady=(5, 0))
        self.entry_memo_time = ttk.Entry(frame, width=15, justify="center")
        self.entry_memo_time.insert(0, "1.0")
        self.entry_memo_time.pack(pady=5)
        
        ttk.Button(frame, text="Save Session", command=self.save_session).pack(pady=10)
        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=5)
        
        ttk.Label(frame, text="Load Existing Session:").pack()
        self.combo_sessions = ttk.Combobox(frame, values=self.db.get_all_sessions(), state="readonly")
        self.combo_sessions.pack(pady=5)
        
        ttk.Button(frame, text="Load & Go to Recorder", command=self.load_session).pack(pady=10)

    def change_workspace(self):
        new_dir = filedialog.askdirectory(initialdir=self.workspace_dir, title="Select Save Folder")
        if new_dir:
            self.workspace_dir = new_dir
            self.lbl_workspace.config(text=self.workspace_dir)
            self.db = Database(os.path.join(self.workspace_dir, "sessions.db"))
            self.combo_sessions['values'] = self.db.get_all_sessions()
            self.combo_sessions.set('')
            messagebox.showinfo("Folder Updated", f"Save location changed to:\n{self.workspace_dir}")

    def setup_recording_tab(self):
        self.record_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.record_frame, text="2. Recorder", state="disabled")
        
        self.lbl_session_title = ttk.Label(self.record_frame, text="No Session Loaded", font=("Helvetica", 16, "bold"))
        self.lbl_session_title.pack(pady=10)
        
        self.lbl_words = ttk.Label(self.record_frame, text="", font=("Helvetica", 16, "bold"), wraplength=500, justify="center")
        self.lbl_words.pack(pady=30)
        
        self.lbl_status = ttk.Label(self.record_frame, text="Press 'Start Recording' to reveal words.", font=("Helvetica", 12), foreground="gray")
        self.lbl_status.pack(pady=10)
        
        button_frame = ttk.Frame(self.record_frame)
        button_frame.pack(pady=10)
        
        self.btn_record = ttk.Button(button_frame, text="Start Recording", command=self.start_memorization)
        self.btn_record.grid(row=0, column=0, padx=5)
        
        self.btn_stop = ttk.Button(button_frame, text="Stop Recording", command=self.stop_recording, state="disabled")
        self.btn_stop.grid(row=0, column=1, padx=5)
        
        self.btn_shuffle = ttk.Button(button_frame, text="Shuffle & Next", command=self.prepare_recording_view)
        self.btn_shuffle.grid(row=0, column=2, padx=5)

    def save_session(self):
        name = self.entry_session_name.get().strip()
        words = self.text_words.get("1.0", tk.END).strip()
        memo_str = self.entry_memo_time.get().strip()
        
        if not name or not words:
            messagebox.showwarning("Input Error", "Please provide both session name and words.")
            return
            
        try:
            memo_time = float(memo_str)
            if memo_time <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Input Error", "Time per word must be a positive decimal number (e.g., 1.0).")
            return
            
        self.db.save_session(name, words, memo_time)
        self.combo_sessions['values'] = self.db.get_all_sessions()
        messagebox.showinfo("Success", f"Session '{name}' saved successfully!")

    def load_session(self):
        session = self.combo_sessions.get()
        if not session:
            messagebox.showwarning("Select Session", "Please select a session from the list.")
            return
            
        self.current_session = session
        self.current_words, self.current_memo_time = self.db.get_session_data(session)
        
        # Clean up empty spaces in the word list immediately upon loading
        self.current_words = [w.strip() for w in self.current_words if w.strip()]
        
        session_path = os.path.join(self.workspace_dir, self.current_session)
        os.makedirs(os.path.join(session_path, "audio"), exist_ok=True)
        os.makedirs(os.path.join(session_path, "text"), exist_ok=True)
            
        self.notebook.tab(self.record_frame, state="normal")
        self.notebook.select(self.record_frame)
        self.lbl_session_title.config(text=f"Session: {session}  ({self.current_memo_time}s per word)")
        
        self.prepare_recording_view()

    def _get_next_record_id(self):
        text_dir = os.path.join(self.workspace_dir, self.current_session, "text")
        existing_files = glob.glob(os.path.join(text_dir, "record_*.txt"))
        
        max_num = 0
        for f in existing_files:
            filename = os.path.basename(f)
            try:
                num = int(filename.split('_')[1].split('.')[0])
                if num > max_num:
                    max_num = num
            except (IndexError, ValueError):
                continue
        return f"record_{max_num + 1}"

    def prepare_recording_view(self):
        random.shuffle(self.current_words)
        # Store the combined string for the final review phase
        self.current_display_text = " • ".join(self.current_words)
        
        self.lbl_words.config(text="[ Words Hidden - Press Start to Reveal ]", foreground="black", font=("Helvetica", 16, "bold"))
        self.lbl_status.config(text="Ready. Press Start to begin memorization.", foreground="gray")
        
        self.btn_record.config(state="normal")
        self.btn_stop.config(state="disabled")
        self.btn_shuffle.config(state="normal")

    def start_memorization(self):
        self.btn_record.config(state="disabled")
        self.btn_shuffle.config(state="disabled")
        
        # Reset word index
        self.current_word_index = 0
        self.show_next_word()

    def show_next_word(self):
        if self.current_word_index < len(self.current_words):
            word = self.current_words[self.current_word_index]
            
            # Show single word, scale up font to massive size for focus
            self.lbl_words.config(text=word, foreground="blue", font=("Helvetica", 36, "bold"))
            self.lbl_status.config(
                text=f"Memorize! Word {self.current_word_index + 1} of {len(self.current_words)}", 
                foreground="orange"
            )
            
            self.current_word_index += 1
            
            # Wait for user's configured time (converted to milliseconds)
            delay_ms = int(self.current_memo_time * 1000)
            self.after(delay_ms, self.show_next_word)
        else:
            # All words have been shown, start recording!
            self.start_recording()

    def start_recording(self):
        # 1. Hide words and reset font size
        self.lbl_words.config(text="[ * * * HIDDEN * * * ]", foreground="black", font=("Helvetica", 16, "bold"))
        
        # 2. Get ID and save text file
        self.current_record_id = self._get_next_record_id()
        txt_path = os.path.join(self.workspace_dir, self.current_session, "text", f"{self.current_record_id}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(" ".join(self.current_words))
            
        # 3. Start Audio Recording
        wav_path = os.path.join(self.workspace_dir, self.current_session, "audio", f"{self.current_record_id}.wav")
        self.recorder.start(wav_path)
        
        self.lbl_status.config(text=f"🔴 Recording {self.current_record_id}... Speak from memory!", foreground="red")
        self.btn_stop.config(state="normal")

    def stop_recording(self):
        self.recorder.stop()
        
        # Reveal all words together in normal font so the user can verify their accuracy
        self.lbl_words.config(text=self.current_display_text, foreground="green", font=("Helvetica", 16, "bold"))
        
        self.lbl_status.config(text=f"Saved {self.current_record_id} successfully! Check your accuracy above.", foreground="green")
        self.btn_stop.config(state="disabled")
        self.btn_shuffle.config(state="normal")


if __name__ == "__main__":
    app = App()
    app.mainloop()