import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from googletrans import Translator, LANGUAGES
import threading

class LanguageTranslator:
    def __init__(self, root):
        self.root = root
        self.root.title("Language Translator")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        self.translator = Translator()
        self.languages = {lang.capitalize(): code for code, lang in LANGUAGES.items()}
        self.lang_names = sorted(self.languages.keys())
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title = ttk.Label(main_frame, text="Language Translator", 
                         font=("Arial", 18, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Language selection frame
        lang_frame = ttk.Frame(main_frame)
        lang_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        lang_frame.columnconfigure(0, weight=1)
        lang_frame.columnconfigure(1, weight=1)
        
        # Source language
        source_frame = ttk.Frame(lang_frame)
        source_frame.grid(row=0, column=0, padx=5, sticky=(tk.W, tk.E))
        
        ttk.Label(source_frame, text="From:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.source_lang = ttk.Combobox(source_frame, values=["Auto-detect"] + self.lang_names, 
                                        state="readonly", width=25)
        self.source_lang.set("Auto-detect")
        self.source_lang.pack(fill=tk.X, pady=5)
        
        # Target language
        target_frame = ttk.Frame(lang_frame)
        target_frame.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        
        ttk.Label(target_frame, text="To:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.target_lang = ttk.Combobox(target_frame, values=self.lang_names, 
                                        state="readonly", width=25)
        self.target_lang.set("English")
        self.target_lang.pack(fill=tk.X, pady=5)
        
        # Text areas frame
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.columnconfigure(1, weight=1)
        text_frame.rowconfigure(1, weight=1)
        
        # Source text
        ttk.Label(text_frame, text="Source Text:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, padx=5)
        self.source_text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, 
                                                      width=40, height=15, font=("Arial", 10))
        self.source_text.grid(row=1, column=0, padx=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Target text
        ttk.Label(text_frame, text="Translated Text:", font=("Arial", 10, "bold")).grid(
            row=0, column=1, sticky=tk.W, padx=5)
        self.target_text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, 
                                                      width=40, height=15, font=("Arial", 10))
        self.target_text.grid(row=1, column=1, padx=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.target_text.config(state=tk.DISABLED)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Translate button
        self.translate_btn = ttk.Button(button_frame, text="Translate", 
                                        command=self.translate_text)
        self.translate_btn.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        clear_btn = ttk.Button(button_frame, text="Clear", command=self.clear_text)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Swap button
        swap_btn = ttk.Button(button_frame, text="Swap Languages", command=self.swap_languages)
        swap_btn.pack(side=tk.LEFT, padx=5)
        
        # Copy button
        copy_btn = ttk.Button(button_frame, text="Copy Translation", 
                             command=self.copy_translation)
        copy_btn.pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_label = ttk.Label(main_frame, text="Ready", relief=tk.SUNKEN)
        self.status_label.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
    def translate_text(self):
        source = self.source_text.get("1.0", tk.END).strip()
        
        if not source:
            messagebox.showwarning("Empty Text", "Please enter text to translate.")
            return
        
        self.translate_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Translating...")
        
        # Run translation in a separate thread
        thread = threading.Thread(target=self._perform_translation, args=(source,))
        thread.start()
        
    def _perform_translation(self, source):
        try:
            src_lang = None if self.source_lang.get() == "Auto-detect" else \
                       self.languages.get(self.source_lang.get())
            dest_lang = self.languages.get(self.target_lang.get())
            
            result = self.translator.translate(source, src=src_lang, dest=dest_lang)
            
            # Update UI in main thread
            self.root.after(0, self._update_translation, result)
            
        except Exception as e:
            self.root.after(0, self._show_error, str(e))
    
    def _update_translation(self, result):
        self.target_text.config(state=tk.NORMAL)
        self.target_text.delete("1.0", tk.END)
        self.target_text.insert("1.0", result.text)
        self.target_text.config(state=tk.DISABLED)
        
        detected = result.src.upper() if result.src else "Unknown"
        self.status_label.config(text=f"Translation complete (Detected: {detected})")
        self.translate_btn.config(state=tk.NORMAL)
    
    def _show_error(self, error_msg):
        messagebox.showerror("Translation Error", f"An error occurred: {error_msg}")
        self.status_label.config(text="Translation failed")
        self.translate_btn.config(state=tk.NORMAL)
    
    def clear_text(self):
        self.source_text.delete("1.0", tk.END)
        self.target_text.config(state=tk.NORMAL)
        self.target_text.delete("1.0", tk.END)
        self.target_text.config(state=tk.DISABLED)
        self.status_label.config(text="Ready")
    
    def swap_languages(self):
        if self.source_lang.get() == "Auto-detect":
            messagebox.showinfo("Cannot Swap", 
                              "Cannot swap when source is set to Auto-detect.")
            return
        
        source = self.source_lang.get()
        target = self.target_lang.get()
        
        self.source_lang.set(target)
        self.target_lang.set(source)
        
        # Swap text content
        source_content = self.source_text.get("1.0", tk.END).strip()
        target_content = self.target_text.get("1.0", tk.END).strip()
        
        self.source_text.delete("1.0", tk.END)
        self.source_text.insert("1.0", target_content)
        
        self.target_text.config(state=tk.NORMAL)
        self.target_text.delete("1.0", tk.END)
        self.target_text.insert("1.0", source_content)
        self.target_text.config(state=tk.DISABLED)
    
    def copy_translation(self):
        translation = self.target_text.get("1.0", tk.END).strip()
        if translation:
            self.root.clipboard_clear()
            self.root.clipboard_append(translation)
            self.status_label.config(text="Translation copied to clipboard")
        else:
            messagebox.showwarning("No Translation", "No translation to copy.")

if __name__ == "__main__":
    root = tk.Tk()
    app = LanguageTranslator(root)
    root.mainloop()