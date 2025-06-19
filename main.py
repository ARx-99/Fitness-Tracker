import tkinter as tk
from tkinter import messagebox
import os

import database
from screens import LoginScreen, HomeScreen, ExerciseBrowserScreen, WorkoutCreatorScreen, LogWorkoutScreen, ProgressTrackingScreen
from user_manager import UserManager # Import UserManager to check login state for screen transitions

class FitnessApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fitness Tracker App")
        self.geometry("900x700")
        self.minsize(700, 600) # Minimum window size

        # Initialize database (create tables and dummy data if needed)
        database.init_db()

        # Ensure image and gif directories exist
        if not os.path.exists('images'):
            os.makedirs('images')
        if not os.path.exists('gifs'):
            os.makedirs('gifs')

        # Add initial exercises if database is empty (for first run)
        if not database.get_all_exercises():
            database.add_exercise("Push-ups", "A common calisthenics exercise performed in a prone position by raising and lowering the body using the arms.", "images/pushup.png", "gifs/pushup.gif")
            database.add_exercise("Squats", "A strength exercise in which the trainee lowers their hips from a standing position and then stands back up.", "images/squat.png", "gifs/squat.gif")
            database.add_exercise("Plank", "An isometric core strength exercise that involves maintaining a position similar to a push-up for the maximum possible time.", "images/plank.png", "gifs/plank.gif")
            database.add_exercise("Lunges", "A strength training exercise that works the quads, glutes, hamstrings, and calves.", "images/lunge.png", "gifs/lunge.gif")
            print("Default exercises populated.")


        self.current_screen = None

        self.screens = {
            "login": LoginScreen(self, self),
            "home": HomeScreen(self, self),
            "exercise_browser": ExerciseBrowserScreen(self, self),
            "workout_creator": WorkoutCreatorScreen(self, self),
            "log_workout": LogWorkoutScreen(self, self),
            "progress_tracking": ProgressTrackingScreen(self, self),
        }

        # Start with the login screen
        self.show_screen("login")

    def show_screen(self, screen_name):
        """Hides the current screen and shows the new one."""
        if self.current_screen:
            self.current_screen.hide()

        screen_to_show = self.screens.get(screen_name)
        if screen_to_show:
            self.current_screen = screen_to_show
            self.current_screen.refresh() # Refresh content when showing
            self.current_screen.show()
        else:
            messagebox.showerror("Error", f"Screen '{screen_name}' not found.")

if __name__ == "__main__":
    app = FitnessApp()
    app.mainloop()