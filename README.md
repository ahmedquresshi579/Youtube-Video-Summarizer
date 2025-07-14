# Youtube-Video-Summarizer
A desktop application that extracts and summarizes YouTube video transcripts using Whisper or YouTubeTranscriptAPI, powered by advanced NLP models. Built with PyQt5, it provides an intuitive GUI for loading, transcribing, and summarizing videos in just a few clicks.

#Requirements
  Python Version:
  Python 3.7 or higher
  
  Required Python Packages:
  Install these with pip:
  PyQt5
  youtube-transcript-api
  yt-dlp
  openai-whisper
  transformers
  torch
  write following line in python cmd:
  pip install PyQt5 youtube-transcript-api yt-dlp openai-whisper transformers torch
  
  FFmpeg (must be installed and added to your system PATH)
  Download from: https://ffmpeg.org/download.html
  After installing, make sure you can run ffmpeg from your command line.

#How to run the app:
1- Open a terminal in your project directory.
2- Run:
   project.py
3- Enter a YouTube video URL in the app and click "Start Summarization".
