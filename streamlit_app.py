import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from dotenv import load_dotenv
import openai
import PyPDF2
import requests
from bs4 import BeautifulSoup

# טען מפתח API
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# חילוץ טקסט מ־PDF
def extract_text_from_pdf(file_path):
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            return "\n".join(page.extract_text() for page in reader.pages)
    except Exception as e:
        return f"שגיאה בקריאת קובץ PDF: {e}"

# חילוץ טקסט מ־URL
def extract_text_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        return "\n".join([p.get_text() for p in soup.find_all('p')])
    except Exception as e:
        return f"שגיאה בשליפת טקסט: {e}"

# סיכום טקסט ע\"י OpenAI
def summarize_text(text, style):
    prompt = f"תמצת את הטקסט הבא בצורה {style}:\n{text}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "אתה עוזר שמסכם טקסטים."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"שגיאה בסיכום: {e}"

# מענה לשאלה על טקסט
def answer_question(text, question):
    prompt = f"טקסט:\n{text}\n\nשאלה: {question}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "ענה על שאלות בהתבסס על טקסט."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"שגיאה במענה לשאלה: {e}"

# ממשק גרפי
def create_app():
    def load_file():
        file_path = filedialog.askopenfilename(filetypes=[("PDF or TXT", "*.pdf *.txt")])
        if file_path.endswith(".pdf"):
            text = extract_text_from_pdf(file_path)
        elif file_path.endswith(".txt"):
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            messagebox.showerror("שגיאה", "סוג קובץ לא נתמך.")
            return
        text_box.delete("1.0", tk.END)
        text_box.insert(tk.END, text)

    def load_url():
        url = simpledialog.askstring("הכנס URL", "הזן קישור לדף אינטרנט:")
        if url:
            text = extract_text_from_url(url)
            text_box.delete("1.0", tk.END)
            text_box.insert(tk.END, text)

    def summarize():
        text = text_box.get("1.0", tk.END)
        style = simpledialog.askstring("סגנון סיכום", "קצר / בינוני / מפורט:")
        if text.strip() and style:
            result = summarize_text(text, style)
            result_box.delete("1.0", tk.END)
            result_box.insert(tk.END, result)

    def ask_question():
        text = text_box.get("1.0", tk.END)
        question = simpledialog.askstring("שאלה", "הזן שאלה לגבי הטקסט:")
        if question:
            answer = answer_question(text, question)
            result_box.delete("1.0", tk.END)
            result_box.insert(tk.END, answer)

    window = tk.Tk()
    window.title("סיכום מסמכים ושאלות")
    window.geometry("800x600")

    tk.Button(window, text="טען קובץ", command=load_file).pack(pady=5)
    tk.Button(window, text="טען URL", command=load_url).pack(pady=5)
    tk.Button(window, text="סכם טקסט", command=summarize).pack(pady=5)
    tk.Button(window, text="שאל שאלה", command=ask_question).pack(pady=5)

    tk.Label(window, text="טקסט מקור:").pack()
    text_box = tk.Text(window, height=15)
    text_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    tk.Label(window, text="תוצאה:").pack()
    result_box = tk.Text(window, height=10, bg="#f0f0f0")
    result_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    window.mainloop()

create_app()
