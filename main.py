import speech_recognition as sr
import webbrowser
import os
from PIL import ImageGrab
import numpy as np
import cv2
import spacy
import threading
import queue
import subprocess
import datetime
import tkinter as tk
from tkinter import messagebox

nlp = spacy.load('en_core_web_sm')
command_queue = queue.Queue()


class VoiceAssistantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Assistant")
        self.root.geometry("600x200")

        self.label = tk.Label(root, text="Voice Assistant", font=("Times New Roman", 16))
        self.label.pack(pady=10)

        self.status_label = tk.Label(root, text="Status: Idle", font=("Nunito", 12))
        self.status_label.pack(pady=10)

        self.command_listbox = tk.Listbox(root, width=50, height=10)
        self.command_listbox.pack(pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Start the command worker thread
        threading.Thread(target=self.command_worker, daemon=True).start()
        # Start listening for the wake word
        threading.Thread(target=self.listen_loop, daemon=True).start()

    def listen_for_wake_word(self, wake_word="jarvis"):
        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        with mic as source:
            self.update_status("Listening for wake word")
            audio = recognizer.listen(source)
            try:
                transcript = recognizer.recognize_google(audio).lower()
                if wake_word in transcript:
                    self.update_status("Wake word detected!")
                    return True
            except sr.UnknownValueError:
                pass
        return False

    def listen_for_command(self):
        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        with mic as source:
            self.update_status("Listening for command")
            audio = recognizer.listen(source)
            try:
                query_text = recognizer.recognize_google(audio).lower()
                return query_text
            except sr.UnknownValueError:
                pass
        return None

    def capture_screen(self):
        try:
            screen = ImageGrab.grab(bbox=None)
            screen_np = np.array(screen)
            screen_cv = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
            file_path = f'C:/screencapture/screencapture_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            cv2.imwrite(file_path, screen_cv)
            self.update_status(f"Screenshot saved as {file_path}")
        except Exception as e:
            self.update_status(f"Error capturing screen: {e}")

    def open_app(self, app_path):
        try:
            subprocess.Popen(app_path)
            self.update_status(f"Opened application: {app_path}")
        except Exception as e:
            self.update_status(f"An error occurred while trying to open {app_path}")

    def process_command(self, command):
        doc = nlp(command)
        for token in doc:
            print(token.text, token.lemma_, token.pos_, token.dep_)
        if "capture" in command and "screen" in command:
            self.capture_screen()
        elif "screenshot" in command:
            self.capture_screen()
        elif "open" in command and "browser" in command:
            webbrowser.open("https://www.google.com")
        elif "open" in command and "youtube" in command:
            webbrowser.open("https://www.youtube.com")
        elif "shutdown" in command:
            os.system("shutdown /s /t 1")
        elif "open" in command:
            if """App Name""" in command:
                self.open_app("""Path to your desired app""")
            # Continue adding apps as desired with this elif statement
            elif """App Name""" in command:
                self.open_app("""Path to desired app""")


    def command_worker(self):
        while True:
            command_text = command_queue.get()
            if command_text is None:
                break
            self.command_listbox.insert(tk.END, command_text)
            self.process_command(command_text)
            command_queue.task_done()

    def listen_loop(self):
        while True:
            if self.listen_for_wake_word():
                command_text = self.listen_for_command()
                if command_text:
                    self.update_status(f"Command received: {command_text}")
                    command_queue.put(command_text)
            self.update_status("Idle")

    def update_status(self, status):
        self.status_label.config(text=f"Status: {status}")
        self.root.update()

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
            command_queue.put(None)


if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceAssistantApp(root)
    root.mainloop()
