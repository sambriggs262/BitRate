"""Main application class for BitRate voice assistant.

Handles GUI, voice recognition, multithreaded command listening and processing.

Author: Sam Briggs
"""

import speech_recognition as sr
import spacy
import threading
import queue
import tkinter as tk
from tkinter import messagebox
from commands import capture_screen, open_app, handle_web_command, shutdown

nlp = spacy.load('en_core_web_sm')
command_queue = queue.Queue()


class VoiceAssistantApp:
    """A voice-controlled assistant with GUI and multithreaded command handling."""

    def __init__(self, root):
        """Initialize GUI and start background threads.

        Args:
            root (tk.Tk): Root window for the Tkinter application.
        """
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

        threading.Thread(target=self.command_worker, daemon=True).start()
        threading.Thread(target=self.listen_loop, daemon=True).start()

    def listen_for_wake_word(self, wake_word="jarvis"):
        """Listen for a wake word using the microphone.

        Args:
            wake_word (str): Keyword to trigger command listening.

        Returns:
            bool: True if wake word detected, else False.
        """
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
        """Listen for and transcribe a voice command.

        Returns:
            str | None: The command string or None if not understood.
        """
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

    def process_command(self, command):
        """Process a spoken command and route to appropriate function.

        Args:
            command (str): Transcribed user command.
        """
        doc = nlp(command)
        for token in doc:
            print(token.text, token.lemma_, token.pos_, token.dep_)

        if "capture" in command and "screen" in command or "screenshot" in command:
            status = capture_screen()
            self.update_status(status)
        elif "open" in command:
            status = handle_web_command(command)
            if status:
                self.update_status(status)
            elif "App Name" in command:
                self.update_status(open_app("Path to your desired app"))
        elif "shutdown" in command:
            status = shutdown()
            self.update_status(status)

    def command_worker(self):
        """Threaded worker to process voice command queue."""
        while True:
            command_text = command_queue.get()
            if command_text is None:
                break
            self.command_listbox.insert(tk.END, command_text)
            self.process_command(command_text)
            command_queue.task_done()

    def listen_loop(self):
        """Continuously listen for wake word and queue voice commands."""
        while True:
            if self.listen_for_wake_word():
                command_text = self.listen_for_command()
                if command_text:
                    self.update_status(f"Command received: {command_text}")
                    command_queue.put(command_text)
            self.update_status("Idle")

    def update_status(self, status):
        """Update the GUI status label.

        Args:
            status (str): Status message to display.
        """
        self.status_label.config(text=f"Status: {status}")
        self.root.update()

    def on_closing(self):
        """Handle app closure and thread cleanup."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
            command_queue.put(None)
