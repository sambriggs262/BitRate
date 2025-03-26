"""Entry point for the BitRate voice assistant application.

Author: Sam Briggs
"""

from BitRate import VoiceAssistantApp
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceAssistantApp(root)
    root.mainloop()
