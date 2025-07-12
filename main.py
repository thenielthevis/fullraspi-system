import tkinter as tk
from screens.welcome import WelcomeScreen
from screens.add_credit import AddCreditScreen
from screens.instructions import InstructionScreen
from screens.game_intro import GameIntroScreen
from screens.gameplay import GameplayScreen
from screens.final_screen import FinalScreen
from screens.end_screen import EndScreen
from screens.rewards import RewardsScreen

class ArcadeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Arcade Game")
        self.geometry("800x600")
        self.resizable(False, False)

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for ScreenClass in (WelcomeScreen, AddCreditScreen, InstructionScreen, GameIntroScreen,
                            GameplayScreen, FinalScreen, EndScreen, RewardsScreen):
            frame = ScreenClass(container, self)
            self.frames[ScreenClass.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("WelcomeScreen")

    def show_frame(self, screen_name):
        frame = self.frames[screen_name]
        frame.tkraise()

if __name__ == "__main__":
    app = ArcadeApp()
    app.mainloop()