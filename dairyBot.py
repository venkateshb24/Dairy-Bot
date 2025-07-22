import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import bcrypt
from datetime import datetime
import speech_recognition as sr
from textblob import TextBlob
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import shutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class DiaryBot:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DiaryBot - Personal Diary")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        self.colors = {
            'primary': '#4A90E2',
            'secondary': '#7ED321',
            'background': '#f0f0f0',
            'white': '#ffffff',
            'text': '#333333',
            'light_gray': '#e0e0e0'
        }
        self.create_folders()
        self.current_user = None
        self.attached_files = []
        self.show_login()
    
    def create_folders(self):
        for folder in ['users', 'entries', 'attachments']:
            os.makedirs(folder, exist_ok=True)
    
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    def check_password(self, password, hashed):
        return bcrypt.checkpw(password.encode('utf-8'), hashed)
    
    def register(self):
        username, password = self.username_entry.get().strip(), self.password_entry.get().strip()
        if not username or not password:
            return messagebox.showerror("Error", "Please fill in all fields.")
        user_file = f"users/{username}.json"
        if os.path.exists(user_file):
            return messagebox.showerror("Error", "Username already exists.")
        user_data = {
            'username': username,
            'password': self.hash_password(password).decode('utf-8'),
            'created_date': datetime.now().isoformat()
        }
        with open(user_file, 'w') as f:
            json.dump(user_data, f)
        messagebox.showinfo("Success", "Account created successfully!")
    
    def login(self):
        username, password = self.username_entry.get().strip(), self.password_entry.get().strip()
        if not username or not password:
            return messagebox.showerror("Error", "Please fill in all fields.")
        user_file = f"users/{username}.json"
        if not os.path.exists(user_file):
            return messagebox.showerror("Error", "User not found.")
        with open(user_file, 'r') as f:
            user_data = json.load(f)
        if self.check_password(password, user_data['password'].encode('utf-8')):
            self.current_user = username
            self.show_main_app()
        else:
            messagebox.showerror("Error", "Wrong password.")
    
    def logout(self):
        self.current_user = None
        self.show_login()

    def show_login(self):
        self.clear_window()
        main_frame = tk.Frame(self.root, bg=self.colors['primary'])
        main_frame.pack(fill='both', expand=True)
        center_frame = tk.Frame(main_frame, bg=self.colors['primary'])
        center_frame.pack(expand=True)
        tk.Label(center_frame, text="DiaryBot", font=('Arial', 32, 'bold'), fg='white', bg=self.colors['primary']).pack(pady=(50, 30))
        login_card = tk.Frame(center_frame, bg=self.colors['white'], relief='flat', bd=0, padx=40, pady=40)
        login_card.pack(padx=50, pady=20)
        tk.Label(login_card, text="Username:", font=('Arial', 14), bg=self.colors['white']).pack(anchor='w', pady=(0, 5))
        self.username_entry = tk.Entry(login_card, font=('Arial', 12), relief='solid', bd=1, width=30)
        self.username_entry.pack(pady=(0, 20), ipady=8)
        tk.Label(login_card, text="Password:", font=('Arial', 14), bg=self.colors['white']).pack(anchor='w', pady=(0, 5))
        self.password_entry = tk.Entry(login_card, font=('Arial', 12), show='*', relief='solid', bd=1, width=30)
        self.password_entry.pack(pady=(0, 30), ipady=8)
        btn_frame = tk.Frame(login_card, bg=self.colors['white'])
        btn_frame.pack()
        tk.Button(btn_frame, text="Login", command=self.login,bg=self.colors['secondary'], fg='white', font=('Arial', 12, 'bold'), relief='flat',padx=20, pady=8, cursor='hand2').pack(side='left', padx=(0, 10))
        tk.Button(btn_frame, text="Register", command=self.register,bg=self.colors['primary'], fg='white', font=('Arial', 12, 'bold'), relief='flat',padx=20, pady=8, cursor='hand2').pack(side='left')
        self.root.bind('<Return>', lambda e: self.login())
    
    def show_main_app(self):
        self.clear_window()
        header = tk.Frame(self.root, bg=self.colors['primary'], height=60)
        header.pack(fill='x')
        header.pack_propagate(False)
        header_content = tk.Frame(header, bg=self.colors['primary'])
        header_content.pack(fill='both', expand=True, padx=20, pady=10)
        tk.Label(header_content, text=f"Welcome, {self.current_user}!", font=('Arial', 16, 'bold'), fg='white', bg=self.colors['primary']).pack(side='left')
        tk.Button(header_content, text="Logout", command=self.logout,bg='#d9534f', fg='white', font=('Arial', 10),relief='flat', padx=15, pady=5, cursor='hand2').pack(side='right')
        style = ttk.Style()
        style.configure('Custom.TNotebook', background=self.colors['background'])
        style.configure('Custom.TNotebook.Tab', padding=[20, 10])
        self.notebook = ttk.Notebook(self.root, style='Custom.TNotebook')
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        self.create_add_entry_tab()
        self.create_view_entries_tab()
        self.create_search_tab()
        self.create_analytics_tab()
        self.create_settings_tab()
    
    def create_add_entry_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Add Entry")
        main_container = tk.Frame(frame, bg=self.colors['white'], padx=30, pady=30)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        tk.Label(main_container, text="Add New Diary Entry", font=('Arial', 20, 'bold'), bg=self.colors['white']).pack(anchor='w', pady=(0, 20))
        tk.Label(main_container, text="Title:", font=('Arial', 14), bg=self.colors['white']).pack(anchor='w', pady=(0, 5))
        self.title_entry = tk.Entry(main_container, font=('Arial', 12), relief='solid', bd=1, width=60)
        self.title_entry.pack(anchor='w', pady=(0, 20), ipady=8)
        tk.Label(main_container, text="Content:", font=('Arial', 14), bg=self.colors['white']).pack(anchor='w', pady=(0, 5))
        self.content_text = tk.Text(main_container, height=12, font=('Arial', 11),relief='solid', bd=1, wrap='word')
        self.content_text.pack(fill='both', expand=True, pady=(0, 20))
        btn_frame = tk.Frame(main_container, bg=self.colors['white'])
        btn_frame.pack(fill='x', pady=(10, 0))
        left_frame = tk.Frame(btn_frame, bg=self.colors['white'])
        left_frame.pack(side='left')
        tk.Button(left_frame, text="🎤 Voice Input", command=self.voice_input,bg='#ff9500', fg='white', font=('Arial', 10),relief='flat', padx=15, pady=8, cursor='hand2').pack(side='left', padx=(0, 10))
        tk.Button(left_frame, text="📎 Attach File", command=self.attach_file,bg='#9013fe', fg='white', font=('Arial', 10),relief='flat', padx=15, pady=8, cursor='hand2').pack(side='left')
        tk.Button(btn_frame, text="💾 Save Entry", command=self.save_entry,bg=self.colors['secondary'], fg='white', font=('Arial', 12, 'bold'),relief='flat', padx=20, pady=10, cursor='hand2').pack(side='right')
    
    def create_view_entries_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="View Entries")
        container = tk.Frame(frame, bg=self.colors['white'], padx=20, pady=20)
        container.pack(fill='both', expand=True, padx=20, pady=20)
        header_frame = tk.Frame(container, bg=self.colors['white'])
        header_frame.pack(fill='x', pady=(0, 20))
        tk.Label(header_frame, text="Your Diary Entries", font=('Arial', 18, 'bold'), bg=self.colors['white']).pack(side='left')
        tk.Button(header_frame, text="🔄 Refresh", command=self.load_entries,bg=self.colors['primary'], fg='white', font=('Arial', 10),relief='flat', padx=15, pady=5, cursor='hand2').pack(side='right')
        list_frame = tk.Frame(container, bg=self.colors['white'])
        list_frame.pack(fill='both', expand=True)
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        self.entries_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,font=('Arial', 11), relief='solid', bd=1)
        self.entries_listbox.pack(fill='both', expand=True)
        scrollbar.config(command=self.entries_listbox.yview)
        tk.Button(container, text="👁️ View Selected Entry", command=self.view_entry,bg=self.colors['secondary'], fg='white', font=('Arial', 12),relief='flat', padx=20, pady=10, cursor='hand2').pack(pady=15)
        self.load_entries()
    
    def create_search_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Search")
        container = tk.Frame(frame, bg=self.colors['white'], padx=30, pady=30)
        container.pack(fill='both', expand=True, padx=20, pady=20)
        tk.Label(container, text="Search Your Entries", font=('Arial', 18, 'bold'), bg=self.colors['white']).pack(pady=(0, 20))
        search_frame = tk.Frame(container, bg=self.colors['white'])
        search_frame.pack(fill='x', pady=(0, 20))
        self.search_entry = tk.Entry(search_frame, font=('Arial', 12), relief='solid', bd=1)
        self.search_entry.pack(side='left', fill='x', expand=True, ipady=8)
        tk.Button(search_frame, text="🔍 Search", command=self.search_entries,bg=self.colors['primary'], fg='white', font=('Arial', 12),relief='flat', padx=20, pady=8, cursor='hand2').pack(side='right', padx=(10, 0))
        self.search_results = tk.Listbox(container, font=('Arial', 11), relief='solid', bd=1)
        self.search_results.pack(fill='both', expand=True)
    
    def create_analytics_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Analytics")
        container = tk.Frame(frame, bg=self.colors['white'], padx=30, pady=30)
        container.pack(fill='both', expand=True, padx=20, pady=20)
        tk.Label(container, text="Your Diary Analytics", font=('Arial', 18, 'bold'), bg=self.colors['white']).pack(pady=(0, 20))
        tk.Button(container, text="📊 Generate Analytics", command=self.generate_analytics,bg='#9013fe', fg='white', font=('Arial', 12),relief='flat', padx=20, pady=10, cursor='hand2').pack(pady=(0, 20))
        self.analytics_plot_frame = tk.Frame(container, bg=self.colors['white'])
        self.analytics_plot_frame.pack(fill='both', expand=True)

    def create_settings_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Settings")
        container = tk.Frame(frame, bg=self.colors['white'], padx=30, pady=30)
        container.pack(fill='both', expand=True, padx=20, pady=20)
        tk.Label(container, text="Settings & Export", font=('Arial', 18, 'bold'), bg=self.colors['white']).pack(pady=(0, 30))
        tk.Button(container, text="📄 Export to PDF", command=self.export_to_pdf,bg='#d9534f', fg='white', font=('Arial', 12),relief='flat', padx=20, pady=10, cursor='hand2').pack(pady=5)
        stats_text = tk.Text(container, height=8, font=('Arial', 11), relief='solid', bd=1, state='disabled')
        stats_text.pack(fill='x', pady=(20, 0))
        user_entries = [f for f in os.listdir('entries') if f.startswith(f"{self.current_user}_")]
        stats = f"""USER STATISTICS:
• Total entries: {len(user_entries)}
• Account: {self.current_user}
• Data location: Local files
"""
        stats_text.config(state='normal')
        stats_text.insert(1.0, stats)
        stats_text.config(state='disabled')
    
    def voice_input(self):
        r = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                messagebox.showinfo("Voice Input", "Speak now... (Click OK and start speaking)")
                self.root.update_idletasks()  # Ensure messagebox appears before listening
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source, timeout=10)
            text = r.recognize_google(audio)
            self.content_text.insert(tk.END, f"\n{text}")
            messagebox.showinfo("Success", "Voice input captured!")
        except sr.WaitTimeoutError:
            messagebox.showwarning("Timeout", "No speech detected.")
        except sr.UnknownValueError:
            messagebox.showerror("Error", "Could not understand audio.")
        except sr.RequestError as e:
            messagebox.showerror("Error", f"Could not request results; check your internet connection: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
    
    def attach_file(self):
        file_path = filedialog.askopenfilename(
            title="Select file to attach",
            filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.gif"), ("All files", "*.*")]
        )
        if file_path:
            filename = os.path.basename(file_path)
            new_path = f"attachments/{self.current_user}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            try:
                shutil.copy2(file_path, new_path)
                self.attached_files.append(new_path)
                messagebox.showinfo("Success", f"File attached: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to attach file: {e}")
    
    def save_entry(self):
        title, content = self.title_entry.get().strip(), self.content_text.get(1.0, tk.END).strip()
        if not title or not content:
            return messagebox.showerror("Error", "Please fill in title and content.")
        blob = TextBlob(content)
        polarity = blob.sentiment.polarity
        emotion = "positive" if polarity > 0.1 else "negative" if polarity < -0.1 else "neutral"
        entry = {
            'id': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'title': title,
            'content': content,
            'date': datetime.now().isoformat(),
            'emotion': emotion,
            'sentiment_score': polarity,
            'attachments': self.attached_files.copy()  # Keep paths of attached files
        }
        try:
            with open(f"entries/{self.current_user}_{entry['id']}.json", 'w') as f:
                json.dump(entry, f, indent=2)
            messagebox.showinfo("Success", f"Entry saved! Emotion detected: {emotion}")
            self.title_entry.delete(0, tk.END)
            self.content_text.delete(1.0, tk.END)
            self.attached_files = []
            self.load_entries()  # Refresh entries list after saving
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save entry: {e}")
    
    def load_entries(self):
        self.entries_listbox.delete(0, tk.END)
        entries = []
        for filename in os.listdir('entries'):
            if filename.startswith(f"{self.current_user}_") and filename.endswith('.json'):
                try:
                    with open(f"entries/{filename}", 'r') as f:
                        entries.append(json.load(f))
                except json.JSONDecodeError:
                    print(f"Skipping malformed JSON file: {filename}")
        entries.sort(key=lambda x: x['date'], reverse=True)
        for entry in entries:
            date_str = datetime.fromisoformat(entry['date']).strftime('%Y-%m-%d %H:%M')
            emotion_emoji = {'positive': '😊', 'negative': '😢', 'neutral': '😐'}
            display_text = f"{date_str} - {entry['title']} {emotion_emoji.get(entry['emotion'], '😐')}"
            self.entries_listbox.insert(tk.END, display_text)
        self.entries_data = entries
    
    def view_entry(self):
        selection = self.entries_listbox.curselection()
        if not selection:
            return messagebox.showwarning("Warning", "Please select an entry to view.")
        entry = self.entries_data[selection[0]]
        view_window = tk.Toplevel(self.root)
        view_window.title(f"Entry: {entry['title']}")
        view_window.geometry("700x500")
        view_window.configure(bg=self.colors['white'])
        container = tk.Frame(view_window, bg=self.colors['white'], padx=30, pady=30)
        container.pack(fill='both', expand=True)
        tk.Label(container, text=entry['title'], font=('Arial', 16, 'bold'), bg=self.colors['white']).pack(pady=(0, 10))
        date_str = datetime.fromisoformat(entry['date']).strftime('%Y-%m-%d %H:%M:%S')
        info_text = f"Date: {date_str} | Emotion: {entry['emotion']} | Score: {entry['sentiment_score']:.2f}"
        tk.Label(container, text=info_text, font=('Arial', 10), bg=self.colors['white'], fg='gray').pack(pady=(0, 20))
        content_text = tk.Text(container, font=('Arial', 11), relief='solid', bd=1)
        content_text.pack(fill='both', expand=True)
        content_text.insert(1.0, entry['content'])
        content_text.config(state='disabled')
        if entry.get('attachments'):
            tk.Label(container, text=f"Attachments: {len(entry['attachments'])} files", font=('Arial', 10), bg=self.colors['white']).pack(pady=(10, 0))
            for attachment in entry['attachments']:
                filename = os.path.basename(attachment)
                attachment_button = tk.Button(container, text=filename, command=lambda path=attachment: self.open_attachment(path),bg=self.colors['primary'], fg='white', font=('Arial', 10),relief='flat', padx=15, pady=5, cursor='hand2')
                attachment_button.pack(pady=(5, 0))

    def open_attachment(self, filepath):
        """Open the attached file."""
        try:
            os.startfile(filepath)  # Opens the file in the associated program
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {str(e)}")
    
    def search_entries(self):
        query = self.search_entry.get().strip().lower()
        if not query:
            self.search_results.delete(0, tk.END)
            return messagebox.showwarning("Warning", "Please enter a search term.")
        self.search_results.delete(0, tk.END)
        found_entries = []
        for entry in self.entries_data:  # Search in loaded entries
            if query in entry['title'].lower() or query in entry['content'].lower():
                found_entries.append(entry)
        if not found_entries:
            self.search_results.insert(tk.END, "No matching entries found.")
            return
        for entry in found_entries:
            date_str = datetime.fromisoformat(entry['date']).strftime('%Y-%m-%d')
            self.search_results.insert(tk.END, f"{date_str} - {entry['title']}")
    
    def generate_analytics(self):
        for widget in self.analytics_plot_frame.winfo_children():
            widget.destroy()
        entries = []
        for filename in os.listdir('entries'):
            if filename.startswith(f"{self.current_user}_") and filename.endswith('.json'):
                try:
                    with open(f"entries/{filename}", 'r') as f:
                        entries.append(json.load(f))
                except json.JSONDecodeError:
                    continue  # Skip malformed files
        if not entries:
            tk.Label(self.analytics_plot_frame, text="No entries found to analyze.", 
                     font=('Arial', 14), bg=self.colors['white']).pack(pady=50)
            return
        positive_count = sum(1 for e in entries if e['emotion'] == 'positive')
        negative_count = sum(1 for e in entries if e['emotion'] == 'negative')
        neutral_count = sum(1 for e in entries if e['emotion'] == 'neutral')
        sentiments_summary = (
            f"Sentiment Summary:\n"
            f"Total Entries: {len(entries)}\n"
            f"Positive Entries: {positive_count}\n"
            f"Negative Entries: {negative_count}\n"
            f"Neutral Entries: {neutral_count}\n"
        )
        sentiment_text = tk.Text(self.analytics_plot_frame, height=10, font=('Arial', 11), wrap='word')
        sentiment_text.pack(fill='both', expand=True)
        sentiment_text.insert(tk.END, sentiments_summary)
        sentiment_text.config(state='disabled')  # Make it read-only
        emotions = [e['emotion'] for e in entries]
        emotion_counts = {
            'positive': emotions.count('positive'),
            'negative': emotions.count('negative'),
            'neutral': emotions.count('neutral')
        }
        fig1, ax1 = plt.subplots(figsize=(5, 4))
        labels = [f'{k} ({v})' for k, v in emotion_counts.items() if v > 0]
        sizes = [v for v in emotion_counts.values() if v > 0]
        colors = ['#7ED321', '#d9534f', '#4A90E2']  # Positive, Negative, Neutral
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors[:len(sizes)])
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        ax1.set_title('Emotion Distribution')
        canvas1 = FigureCanvasTkAgg(fig1, master=self.analytics_plot_frame)
        canvas_widget1 = canvas1.get_tk_widget()
        canvas_widget1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        canvas1.draw()
        sentiment_scores = [e['sentiment_score'] for e in entries]
        fig2, ax2 = plt.subplots(figsize=(5, 4))
        ax2.hist(sentiment_scores, bins=10, color=self.colors['primary'], edgecolor='black')
        ax2.set_title('Sentiment Score Distribution')
        ax2.set_xlabel('Sentiment Score')
        ax2.set_ylabel('Number of Entries')
        ax2.grid(True, linestyle='--', alpha=0.7)
        canvas2 = FigureCanvasTkAgg(fig2, master=self.analytics_plot_frame)
        canvas_widget2 = canvas2.get_tk_widget()
        canvas_widget2.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        canvas2.draw()

    def export_to_pdf(self):
        try:
            filename = f"DiaryExport_{self.current_user}_{datetime.now().strftime('%Y%m%d')}.pdf"
            c = canvas.Canvas(filename, pagesize=letter)
            width, height = letter
            c.setFont("Helvetica-Bold", 16)
            c.drawString(100, height - 50, f"Diary Export - {self.current_user}")
            y_position = height - 100
            entries = []
            for file in os.listdir('entries'):
                if file.startswith(f"{self.current_user}_") and file.endswith('.json'):
                    try:
                        with open(f"entries/{file}", 'r') as f:
                            entries.append(json.load(f))
                    except (json.JSONDecodeError, FileNotFoundError):
                        continue  # Skip problematic files
            entries.sort(key=lambda x: x['date'])
            for entry in entries:
                if y_position < 150:
                    c.showPage()
                    y_position = height - 50
                c.setFont("Helvetica-Bold", 12)
                date_str = datetime.fromisoformat(entry['date']).strftime('%Y-%m-%d %H:%M')
                title_text = f"{entry['title']} ({date_str})"
                c.drawString(100, y_position, title_text)
                y_position -= 25
                c.setFont("Helvetica", 9)
                emotion_text = f"Emotion: {entry.get('emotion', 'N/A')} | Score: {entry.get('sentiment_score', 0):.2f}"
                c.drawString(100, y_position, emotion_text)
                y_position -= 20
                c.setFont("Helvetica", 10)
                content = entry['content']
                max_width = 400  # Maximum width in points
                words = content.split()
                lines = []
                current_line = ""
                for word in words:
                    test_line = current_line + " " + word if current_line else word
                    text_width = c.stringWidth(test_line, "Helvetica", 10)
                    if text_width <= max_width:
                        current_line = test_line
                    else:
                        if current_line:
                            lines.append(current_line)
                            current_line = word
                        else:
                            # Single word is too long, break it
                            lines.append(word)         
                if current_line:
                    lines.append(current_line)
                for line in lines:
                    if y_position < 50:  # Check for page overflow
                        c.showPage()
                        y_position = height - 50
                    c.drawString(100, y_position, line)
                    y_position -= 15
                if entry.get('attachments'):
                    y_position -= 10
                    c.setFont("Helvetica-Oblique", 9)
                    attachment_text = f"Attachments: {len(entry['attachments'])} file(s)"
                    c.drawString(100, y_position, attachment_text)
                    y_position -= 15
                y_position -= 10
                if y_position > 50:
                    c.line(100, y_position, 500, y_position)
                    y_position -= 20
            c.save()
            messagebox.showinfo("Success", f"PDF exported successfully as {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export PDF: {str(e)}")
            print(f"PDF Export Error Details: {e}")  # For debugging
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = DiaryBot()
    app.run()