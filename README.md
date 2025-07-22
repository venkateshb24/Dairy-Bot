![Python](https://img.shields.io/badge/Python-3.10-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

# 📔 DiaryBot – Personal Digital Diary

DiaryBot is a feature-rich desktop diary application built with Python and Tkinter. It allows users to write, analyze, and manage personal diary entries with added functionalities like voice input, emotion analysis, file attachments, search, analytics, and PDF export.

---

## ✨ Features

- 📝 Add, view, and search diary entries
- 🎤 Voice-to-text diary entry input using SpeechRecognition
- 😊 Automatic sentiment & emotion detection with TextBlob
- 📎 Attach files to entries
- 📊 Generate analytics with emotion pie charts and sentiment histograms
- 📄 Export all entries into a single PDF
- 🔐 Secure user registration and login with hashed passwords

---

## 🛠 Technologies Used

- Python 3.x
- Tkinter (GUI)
- bcrypt (password hashing)
- SpeechRecognition
- TextBlob (sentiment analysis)
- ReportLab (PDF generation)
- Matplotlib (data visualization)
- JSON (entry storage)

---

## ▶️ How to Run

1. **Install the required libraries**:
   ```bash
   pip install bcrypt speechrecognition textblob reportlab matplotlib
   python -m textblob.download_corpora

---
   
## 📄 License

This project is licensed under the **MIT License**.  
Feel free to use, modify, and distribute it for personal or educational use.
