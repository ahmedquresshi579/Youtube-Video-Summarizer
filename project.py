import sys
import os
import warnings
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QMessageBox
)
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp
import whisper
from transformers import pipeline
from urllib.parse import urlparse, parse_qs
import re

warnings.filterwarnings("ignore")  # Optional: hide FP16 warning

# ======================
# Helper Functions
# ======================

def get_video_id(url):
    parsed = urlparse(url)
    if 'youtu.be' in parsed.netloc:
        return parsed.path[1:]
    elif 'youtube.com' in parsed.netloc:
        return parse_qs(parsed.query).get("v", [None])[0]
    return None

def get_transcript_youtube(url):
    video_id = get_video_id(url)
    if not video_id:
        raise ValueError("Invalid YouTube URL")
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([x["text"] for x in transcript])
    except Exception as e:
        print(f"[YouTube Transcript Error] {e}")
        return None

def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return "audio.mp3"

def get_transcript_whisper(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"]

def get_transcript(url, update_status):
    transcript = get_transcript_youtube(url)
    if transcript:
        update_status("✔️ Transcript from YouTube API.")
        return transcript

    update_status("⚠️ YouTube transcript unavailable. Using Whisper...")
    audio_path = download_audio(url)
    transcript = get_transcript_whisper(audio_path)
    os.remove(audio_path)
    update_status("✔️ Transcript generated using Whisper.")
    return transcript

def summarize_text(text, update_status, max_chunk=1000):
    update_status("🧠 Summarizing with Hugging Face model...")
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    chunks = [text[i:i+max_chunk] for i in range(0, len(text), max_chunk)]
    summaries = summarizer(chunks, max_length=130, min_length=30, do_sample=False)
    full_summary = " ".join([s["summary_text"] for s in summaries])

    update_status("📚 Formatting summary...")

    sections = re.split(r'\. (?=[A-Z])', full_summary)
    bullet_summary = ""
    current_heading = "🔹 Key Points"

    bullet_summary += f"{current_heading}:\n"

    for line in sections:
        line = line.strip()
        if not line:
            continue
        if len(line.split()) > 7:
            bullet_summary += f"• {line.strip('.')}.\n"

    update_status("✔️ Summary complete.")
    return bullet_summary

# ======================
# GUI App
# ======================
class YouTubeSummarizerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📺 YouTube Video Summarizer")
        self.setGeometry(300, 150, 900, 750)
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
                background-color: #0d1b2a;
                color: #e0e1dd;
            }
            QLineEdit, QTextEdit {
                padding: 10px;
                border: 1px solid #415a77;
                border-radius: 8px;
                background-color: #1b263b;
                color: #e0e1dd;
            }
            QTextEdit {
                font-family: Consolas, monospace;
            }
            QPushButton {
                padding: 12px;
                font-weight: bold;
                background-color: #778da9;
                color: #0d1b2a;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #a9bcd0;
            }
            QLabel {
                font-size: 16px;
                color: #e0e1dd;
                font-weight: 600;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("🔗 Enter YouTube Video URL here...")
        layout.addWidget(self.url_input)

        self.status_label = QLabel("🔷 Status: Waiting for input...")
        self.status_label.setStyleSheet("color: #89c2d9; font-weight: bold; font-size: 15px;")
        layout.addWidget(self.status_label)

        label_transcript = QLabel("📝 Transcript:")
        layout.addWidget(label_transcript)

        self.transcript_output = QTextEdit()
        self.transcript_output.setPlaceholderText("Transcript will appear here...")
        self.transcript_output.setFixedHeight(220)
        layout.addWidget(self.transcript_output)

        label_summary = QLabel("📑 Summary:")
        layout.addWidget(label_summary)

        self.summary_output = QTextEdit()
        self.summary_output.setPlaceholderText("Summary will appear here...")
        self.summary_output.setFixedHeight(220)
        layout.addWidget(self.summary_output)

        self.start_button = QPushButton("▶️ Start Summarization")
        self.start_button.clicked.connect(self.run_summary)
        layout.addWidget(self.start_button)

        self.setLayout(layout)

    def update_status(self, msg):
        self.status_label.setText(f"🔷 Status: {msg}")
        QApplication.processEvents()

    def run_summary(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Input Error", "Please enter a valid YouTube URL.")
            return

        try:
            self.update_status("⏳ Fetching transcript...")
            transcript = get_transcript(url, self.update_status)
            self.transcript_output.setText(transcript)

            self.update_status("⏳ Summarizing...")
            summary = summarize_text(transcript, self.update_status)
            self.summary_output.setText(summary)

            self.update_status("✅ Done.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            self.update_status("❌ Failed.")

# ======================
# Run App
# ======================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YouTubeSummarizerApp()
    window.show()
    sys.exit(app.exec_())
