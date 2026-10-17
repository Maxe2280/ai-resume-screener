import colorsys
import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

import google.generativeai as genai
from dotenv import load_dotenv

from screener.cache import EvaluationCache
from screener.evaluator import MODEL_NAME, ResumeEvaluator
from screener.extract import extract_resume_text


class ResumeScreenerApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("AI Resume Screener")
        self.window.geometry("820x740")
        self.window.configure(bg="#1e1e2f")

        # --- Animated gradient background ---
        self.bg_canvas = tk.Canvas(self.window, width=820, height=740, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0)
        self.animate_bg(self.bg_canvas, 820, 740)

        self.resume_path_var = tk.StringVar()
        self.cache = EvaluationCache()
        self.evaluator = ResumeEvaluator(self.setup_api(), self.cache)
        self.create_widgets()
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.window.mainloop()

    def setup_api(self):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file.")
        genai.configure(api_key=api_key)
        return genai.GenerativeModel(MODEL_NAME)

    def create_widgets(self):
        label_style = {"font": ("Consolas", 11, "bold"), "bg": "#1e1e2f", "fg": "#00ffcc"}
        button_style = {"font": ("Consolas", 12, "bold"), "bg": "#00bfff", "fg": "white"}

        # Job Description (centered)
        tk.Label(self.window, text="📋 Job Description:", **label_style).pack(padx=10, pady=(10, 0))
        self.job_entry = scrolledtext.ScrolledText(
            self.window, wrap=tk.WORD, width=95, height=10,
            bg="#121219", fg="#ffffff", insertbackground="white"
        )
        self.job_entry.pack(padx=10)

        # Resume File section (centered)
        tk.Label(self.window, text="📄 Resume File (PDF or DOCX):", **label_style).pack(padx=10, pady=(10, 0))
        path_frame = tk.Frame(self.window, bg="#1e1e2f")
        path_frame.pack(pady=(0, 10))
        tk.Entry(
            path_frame, textvariable=self.resume_path_var, width=60,
            bg="#252533", fg="white", insertbackground="white"
        ).pack(side="left", padx=(0, 5))
        tk.Button(path_frame, text="Browse", command=self.choose_file, **button_style).pack(side="left")

        # Gemini Evaluation (centered)
        tk.Label(self.window, text="🔍 Gemini Evaluation:", **label_style).pack(padx=10, pady=(10, 0))
        self.result_display = scrolledtext.ScrolledText(
            self.window, wrap=tk.WORD, width=95, height=15,
            bg="#121219", fg="#00ffcc", insertbackground="white", font=("Consolas", 10)
        )
        self.result_display.pack(padx=10)
        self.result_display.config(state="disabled")

        # Color‑cycling “Evaluate Resume” button
        self.eval_btn = tk.Button(
            self.window, text="Evaluate Resume", command=self.on_evaluate, **button_style
        )
        self.eval_btn.pack(pady=15)
        self.animate_button_color(self.eval_btn, hue=200)

    def choose_file(self):
        path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf"), ("Word files", "*.docx")])
        self.resume_path_var.set(path)

    def holographic_typing(self, text):
        """
        Moderate-pace typing: ~5ms per character.
        """
        self.result_display.config(state="normal")
        self.result_display.delete("1.0", tk.END)
        for char in text:
            self.result_display.insert(tk.END, char)
            self.result_display.see(tk.END)
            self.result_display.update()
            time.sleep(0.005)  # moderate speed
        self.result_display.config(state="disabled")

    def on_evaluate(self):
        job_desc = self.job_entry.get("1.0", tk.END).strip()
        file_path = self.resume_path_var.get()
        if not job_desc or not file_path:
            messagebox.showerror("Missing Info", "Please provide both a job description and resume file.")
            return

        try:
            resume_text = extract_resume_text(file_path)
        except ValueError as e:
            messagebox.showerror("Invalid File", str(e))
            return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read resume file:\n{e}")
            return

        self.result_display.config(state="normal")
        self.result_display.delete("1.0", tk.END)
        self.result_display.insert(tk.END, "🧠 Gemini is thinking...\n")
        self.result_display.update()

        try:
            result, from_cache = self.evaluator.evaluate(job_desc, resume_text)
            if from_cache:
                result = "⚡ Cached result (this resume and job were evaluated before)\n\n" + result
            self.holographic_typing(result)
        except Exception as e:
            self.result_display.insert(tk.END, f"❌ Error querying Gemini: {e}")
            self.result_display.config(state="disabled")

    def on_close(self):
        self.cache.close()
        self.window.destroy()

    # --- Animation methods below ---

    def animate_button_color(self, btn, hue=0):
        r, g, b = colorsys.hsv_to_rgb(hue/360, 0.6, 0.9)
        hex_color = f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'
        btn.config(bg=hex_color)
        next_hue = (hue + 1) % 360
        self.window.after(100, lambda: self.animate_button_color(btn, next_hue))

    def animate_bg(self, canvas, width, height, hue=0):
        c1 = colorsys.hsv_to_rgb(hue/360, 0.6, 0.2)
        c2 = colorsys.hsv_to_rgb(((hue+60)%360)/360, 0.6, 0.2)
        def to_hex(c):
            return f'#{int(c[0]*255):02x}{int(c[1]*255):02x}{int(c[2]*255):02x}'
        hex1, hex2 = to_hex(c1), to_hex(c2)

        canvas.delete("grad")
        for i in range(height):
            t = i / height
            r1, g1, b1 = canvas.winfo_rgb(hex1)
            r2, g2, b2 = canvas.winfo_rgb(hex2)
            nr = int(r1 + (r2-r1)*t) >> 8
            ng = int(g1 + (g2-g1)*t) >> 8
            nb = int(b1 + (b2-b1)*t) >> 8
            canvas.create_line(0, i, width, i, fill=f'#{nr:02x}{ng:02x}{nb:02x}', tags="grad")

        next_hue = (hue + 2) % 360
        self.window.after(50, lambda: self.animate_bg(canvas, width, height, next_hue))


# --- Run the App ---
if __name__ == "__main__":
    ResumeScreenerApp()
