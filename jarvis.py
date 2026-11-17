import os
import sys
import time
import math
import threading
import urllib.parse
import webbrowser
import tkinter as tk
import pyautogui
import pyperclip
import speech_recognition as sr
import pyttsx3
from google import genai

sys.stdout.reconfigure(encoding='utf-8')

# Replace with your actual Google AI Studio API Key
client = genai.Client(api_key="YOUR_GEMINI_API_KEY")

engine = pyttsx3.init()
engine.setProperty('rate', 175)

current_status = "INITIALIZING..."
is_active = False

class JarvisUI:
    def __init__(self, root):
        self.root = root
        self.root.title("J.A.R.V.I.S. - MARK LXXXV")
        self.root.geometry("500x550")
        self.root.configure(bg="#050A14")
        self.root.resizable(False, False)

        self.title_label = tk.Label(
            root, text="J.A.R.V.I.S.", font=("Consolas", 24, "bold"),
            fg="#00F0FF", bg="#050A14"
        )
        self.title_label.pack(pady=(15, 5))

        self.canvas = tk.Canvas(root, width=320, height=320, bg="#050A14", highlightthickness=0)
        self.canvas.pack()

        self.status_label = tk.Label(
            root, text="BOOTING SYSTEMS...", font=("Consolas", 13, "bold"),
            fg="#00FFAA", bg="#050A14"
        )
        self.status_label.pack(pady=5)

        self.chat_label = tk.Label(
            root, text="Waiting for command...", font=("Consolas", 10),
            fg="#B0E0E6", bg="#0A192F", wraplength=440, justify="center",
            width=52, height=4, relief="flat"
        )
        self.chat_label.pack(pady=10, padx=20)

        self.angle = 0
        self.pulse = 0
        self.animate()

    def animate(self):
        self.canvas.delete("all")
        cx, cy = 160, 160

        pulse_offset = math.sin(self.pulse) * (10 if is_active else 3)
        self.pulse += 0.15
        self.angle = (self.angle + (4 if is_active else 1.5)) % 360

        r1 = 120 + pulse_offset
        self.canvas.create_oval(cx - r1, cy - r1, cx + r1, cy + r1, outline="#005577", width=2)

        self.canvas.create_arc(cx - 105, cy - 105, cx + 105, cy + 105, start=self.angle, extent=110, outline="#00F0FF", width=5, style=tk.ARC)
        self.canvas.create_arc(cx - 105, cy - 105, cx + 105, cy + 105, start=self.angle + 180, extent=110, outline="#00F0FF", width=5, style=tk.ARC)

        self.canvas.create_arc(cx - 80, cy - 80, cx + 80, cy + 80, start=-self.angle * 1.5, extent=140, outline="#0088FF", width=4, style=tk.ARC)
        self.canvas.create_arc(cx - 80, cy - 80, cx + 80, cy + 80, start=-self.angle * 1.5 + 180, extent=140, outline="#0088FF", width=4, style=tk.ARC)

        core_r = 42 + (pulse_offset * 0.6)
        core_color = "#00FFFF" if is_active else "#007799"
        self.canvas.create_oval(cx - core_r, cy - core_r, cx + core_r, cy + core_r, fill="#082032", outline=core_color, width=3)
        self.canvas.create_text(cx, cy, text="AI CORE", font=("Consolas", 10, "bold"), fill="#FFFFFF")

        self.status_label.config(text=current_status)
        self.root.after(30, self.animate)

    def update_chat(self, text):
        self.chat_label.config(text=text)

ui_app = None

def speak(text):
    global current_status, is_active
    current_status = "JARVIS SPEAKING..."
    is_active = True
    if ui_app:
        ui_app.update_chat(f"Jarvis: {text}")
    print(f"Jarvis: {text}")
    engine.say(text)
    engine.runAndWait()
    is_active = False

def listen():
    global current_status, is_active
    r = sr.Recognizer()
    with sr.Microphone() as source:
        current_status = "LISTENING..."
        is_active = True
        print("Listening...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    is_active = False
    current_status = "PROCESSING..."
    try:
        query = r.recognize_google(audio, language='en-IN')
        if ui_app:
            ui_app.update_chat(f"You: {query}")
        print(f"You said: {query}")
        return query
    except Exception:
        return ""

def ask_ai(prompt_text):
    models_to_try = ['gemini-3.8-flash', 'gemini-3.8-flash-lite', 'gemini-2.5-flash-lite']
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt_text
            )
            return response.text.replace("*", "").strip()
        except Exception:
            continue
    return "Sir, server load is high right now. Please try again."

def find_file(filename):
    speak(f"Sir, searching for {filename} on your laptop...")
    user_folder = os.path.expanduser("~")
    search_folders = [
        os.path.join(user_folder, "Desktop"),
        os.path.join(user_folder, "Documents"),
        os.path.join(user_folder, "Downloads")
    ]
    found_paths = []
    for folder in search_folders:
        for root, dirs, files in os.walk(folder):
            for file in files:
                if filename.lower() in file.lower():
                    found_paths.append(os.path.join(root, file))
    if found_paths:
        first_file = found_paths[0]
        folder_name = os.path.basename(os.path.dirname(first_file))
        speak(f"Sir, file found in {folder_name} folder. File name is {os.path.basename(first_file)}.")
    else:
        speak(f"Sorry Sir, I could not find any file named {filename}.")

def read_whatsapp(contact_name):
    speak(f"Sir, checking WhatsApp messages from {contact_name}.")
    pyautogui.press('win')
    time.sleep(1)
    pyautogui.write('WhatsApp')
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(4)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(1)
    pyperclip.copy(contact_name)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(2)
    pyautogui.press('enter')
    time.sleep(1)
    screen_width, screen_height = pyautogui.size()
    pyautogui.click(screen_width * 0.65, screen_height * 0.5)
    time.sleep(0.5)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.5)
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.5)
    copied_text = pyperclip.paste()
    if copied_text:
        reply = ask_ai(f"This is copied WhatsApp chat text. Tell me only the last message in short Hinglish: {copied_text[-1000:]}")
        speak(reply)
    else:
        speak("Sir, could not copy the message.")

def send_whatsapp(contact_name, message_text):
    speak(f"Sir, sending WhatsApp message to {contact_name}.")
    pyautogui.press('win')
    time.sleep(1)
    pyautogui.write('WhatsApp')
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(4)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(1)
    pyperclip.copy(contact_name)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(2)
    pyautogui.press('enter')
    time.sleep(1)
    pyperclip.copy(message_text)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    pyautogui.press('enter')
    speak("Message sent Sir.")

def jarvis_brain():
    time.sleep(1)
    speak("Hello Sir, Jarvis visual interface is online!")
    while True:
        command = listen().lower()
        if not command:
            continue
        if any(w in command for w in ["band ho jao", "stop", "exit", "ruk jao"]):
            speak("Okay Sir, shutting down systems. Goodbye!")
            os._exit(0)
        elif "find file" in command or ("file" in command and ("kahan" in command or "dhoondh" in command or "search" in command)):
            words = command.replace("find file", "").replace("file", "").replace("kahan hai", "").replace("dhoondho", "").strip()
            if words:
                find_file(words)
            else:
                speak("Sir, which file should I search for?")
        elif "whatsapp" in command and ("bhej" in command or "send" in command):
            details = ask_ai(f"Extract friend name and message from this sentence. Reply strictly in format: NAME | MESSAGE. Sentence: {command}")
            if "|" in details:
                parts = details.split("|")
                send_whatsapp(parts[0].strip(), parts[1].strip())
            else:
                speak("Sir, I did not catch the name and message.")
        elif "whatsapp" in command and ("message" in command or "msg" in command or "padh" in command or "read" in command):
            friend_name = ask_ai(f"Which friend's name is mentioned in this sentence? Reply with only the name: {command}")
            read_whatsapp(friend_name)
        elif "youtube" in command and ("chalao" in command or "play" in command or "song" in command or "gana" in command):
            song_name = command
            for word in ["youtube par", "youtube", "chalao", "play", "koi", "sab"]:
                song_name = song_name.replace(word, "")
            song_name = song_name.strip()
            if not song_name or song_name in ["song", "gana"]:
                song_name = "trending hindi songs"
            speak(f"Playing {song_name} on YouTube Sir.")
            query = urllib.parse.quote(song_name)
            webbrowser.open(f"https://youtube.com{query}")
        elif "open youtube" in command or "youtube kholo" in command:
            speak("Opening YouTube Sir")
            webbrowser.open("https://youtube.com")
        elif "open google" in command or "google kholo" in command:
            speak("Opening Google Sir")
            webbrowser.open("https://google.com")
        elif "open notepad" in command or "notepad kholo" in command:
            speak("Opening Notepad Sir")
            os.system("notepad")
        elif "open whatsapp" in command or "whatsapp kholo" in command:
            speak("Opening WhatsApp Sir")
            pyautogui.press('win')
            time.sleep(1)
            pyautogui.write('WhatsApp')
            time.sleep(1)
            pyautogui.press('enter')
        else:
            reply = ask_ai(f"You are Iron Man's Jarvis. Give a very short and smart reply in Hinglish: {command}")
            speak(reply)

root = tk.Tk()
ui_app = JarvisUI(root)
threading.Thread(target=jarvis_brain, daemon=True).start()
root.mainloop()
