import tkinter as tk
from tkinter import messagebox, scrolledtext, StringVar, Toplevel
from PIL import Image, ImageTk, ImageSequence
import os
import datetime

import database
from user_manager import UserManager
from UI_elements import ScrollFrame, NotificationManager

class BaseScreen(tk.Frame):
    """Base class for all application screens."""
    def __init__(self, master, app_instance):
        super().__init__(master)
        self.app = app_instance
        self.config(bg="#f0f0f0") # Default background

    def show(self):
        """Packs the screen frame."""
        self.pack(fill="both", expand=True)

    def hide(self):
        """Unpacks the screen frame."""
        self.pack_forget()

    def refresh(self):
        """Method to refresh screen content when it becomes active. Override in subclasses."""
        pass

class LoginScreen(BaseScreen):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        tk.Label(self, text="Fitness Tracker", font=("Arial", 24, "bold"), bg="#f0f0f0").grid(row=0, column=0, columnspan=2, pady=30)

        tk.Label(self, text="Username:", font=("Arial", 14), bg="#f0f0f0").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.username_entry = tk.Entry(self, font=("Arial", 14))
        self.username_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        tk.Label(self, text="Password:", font=("Arial", 14), bg="#f0f0f0").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.password_entry = tk.Entry(self, show="*", font=("Arial", 14))
        self.password_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        tk.Button(self, text="Login", command=self.login, font=("Arial", 12), bg="#4CAF50", fg="white").grid(row=3, column=0, columnspan=2, pady=10)
        tk.Button(self, text="Register", command=self.register, font=("Arial", 12), bg="#2196F3", fg="white").grid(row=4, column=0, columnspan=2, pady=5)

        self.notification_label = tk.Label(self, text="", fg="red", bg="#f0f0f0", font=("Arial", 10))
        self.notification_label.grid(row=5, column=0, columnspan=2, pady=10)
        NotificationManager.init(master, self.notification_label) # Initialize notification manager

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if UserManager.login_user(username, password):
            NotificationManager.show_notification(f"Welcome, {username}!", fg="green")
            self.app.show_screen("home")
        else:
            NotificationManager.show_notification("Invalid username or password.", fg="red")

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if not username or not password:
            NotificationManager.show_notification("Username and password cannot be empty.", fg="red")
            return
        if UserManager.register_user(username, password):
            NotificationManager.show_notification("Registration successful! Please login.", fg="green")
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
        else:
            NotificationManager.show_notification("Registration failed. Username might exist.", fg="red")

class HomeScreen(BaseScreen):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance)
        self.user_var = StringVar()
        tk.Label(self, textvariable=self.user_var, font=("Arial", 18, "bold"), bg="#f0f0f0").pack(pady=20)

        buttons_frame = tk.Frame(self, bg="#f0f0f0")
        buttons_frame.pack(pady=20)

        # Define button_style WITHOUT 'bg' here
        button_style = {"font": ("Arial", 14), "width": 20, "height": 2, "fg": "white", "padx": 10, "pady": 5}

        tk.Button(buttons_frame, text="Browse Exercises", command=lambda: self.app.show_screen("exercise_browser"), **button_style, bg="#007BFF").pack(pady=10)
        tk.Button(buttons_frame, text="Create Workout", command=lambda: self.app.show_screen("workout_creator"), **button_style, bg="#007BFF").pack(pady=10)
        tk.Button(buttons_frame, text="Log Workout", command=lambda: self.app.show_screen("log_workout"), **button_style, bg="#007BFF").pack(pady=10)
        tk.Button(buttons_frame, text="Track Progress", command=lambda: self.app.show_screen("progress_tracking"), **button_style, bg="#007BFF").pack(pady=10)
        tk.Button(buttons_frame, text="Logout", command=self.logout, **button_style, bg="#DC3545").pack(pady=10)
        
    def refresh(self):
        current_user = UserManager.get_current_user()
        if current_user:
            self.user_var.set(f"Welcome, {current_user['username']}!")
        else:
            self.user_var.set("Welcome!")

    def logout(self):
        UserManager.logout_user()
        NotificationManager.show_notification("Logged out successfully.", fg="blue")
        self.app.show_screen("login")

class ExerciseBrowserScreen(BaseScreen):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance)

        self.exercises = []
        self.current_exercise_index = 0
        self.gif_frames = []
        self._after_id = None # To manage GIF animation loop

        tk.Label(self, text="Exercise Browser", font=("Arial", 20, "bold"), bg="#f0f0f0").pack(pady=15)

        self.image_label = tk.Label(self, bg="#f0f0f0")
        self.image_label.pack(pady=5)

        self.gif_label = tk.Label(self, bg="#f0f0f0")
        self.gif_label.pack(pady=5)

        self.exercise_name_label = tk.Label(self, text="", font=("Arial", 16, "bold"), bg="#f0f0f0")
        self.exercise_name_label.pack(pady=5)

        self.description_label = tk.Label(self, text="", wraplength=500, font=("Arial", 12), justify="center", bg="#f0f0f0")
        self.description_label.pack(pady=5)

        nav_frame = tk.Frame(self, bg="#f0f0f0")
        nav_frame.pack(pady=10)

        tk.Button(nav_frame, text="Previous", command=self.prev_exercise, font=("Arial", 12), bg="#FFC107", fg="black").pack(side="left", padx=20)
        tk.Button(nav_frame, text="Next", command=self.next_exercise, font=("Arial", 12), bg="#28A745", fg="white").pack(side="right", padx=20)

        tk.Button(self, text="Back to Home", command=lambda: self.app.show_screen("home"), font=("Arial", 12), bg="#6C757D", fg="white").pack(pady=10)

    def refresh(self):
        self.exercises = database.get_all_exercises()
        if self.exercises:
            self.current_exercise_index = 0
            self.load_exercise()
        else:
            self.clear_display()
            self.exercise_name_label.config(text="No exercises found.")

    def clear_display(self):
        self.image_label.config(image='')
        self.image_label.image = None
        self.gif_label.config(image='')
        self.gif_label.image = None
        self.exercise_name_label.config(text="")
        self.description_label.config(text="")
        if hasattr(self, '_after_id') and self._after_id:
            self.master.after_cancel(self._after_id)
            self._after_id = None

    def load_exercise(self):
        self.clear_display() # Clear previous content and stop GIF

        if not self.exercises:
            return

        exercise_data = self.exercises[self.current_exercise_index]
        _id, name, description, image_path, gif_path = exercise_data

        self.exercise_name_label.config(text=name)
        self.description_label.config(text=description)

        # Load and display static image
        if image_path and os.path.exists(image_path):
            try:
                img = Image.open(image_path)
                img = img.resize((100, 100), Image.LANCZOS)
                self.photo_image = ImageTk.PhotoImage(img)
                self.image_label.config(image=self.photo_image)
            except Exception as e:
                self.image_label.config(text=f"Error loading image: {e}")
                self.image_label.image = None
        else:
            self.image_label.config(text=f"Image not found: {image_path}")
            self.image_label.image = None

        # Load and display GIF
        if gif_path and os.path.exists(gif_path):
            try:
                self.gif_frames = []
                gif_obj = Image.open(gif_path)
                for frame in ImageSequence.Iterator(gif_obj):
                    frame = frame.resize((300, 300), Image.LANCZOS)
                    self.gif_frames.append(ImageTk.PhotoImage(frame))
                self.animate_gif(0)
            except Exception as e:
                self.gif_label.config(text=f"Error loading GIF: {e}")
                self.gif_label.image = None
        else:
            self.gif_label.config(text=f"GIF not found: {gif_path}")
            self.gif_label.image = None


    def animate_gif(self, frame_index):
        if not self.gif_frames:
            return

        frame = self.gif_frames[frame_index]
        self.gif_label.config(image=frame)
        self.gif_label.image = frame

        next_frame_index = (frame_index + 1) % len(self.gif_frames)
        # You can try to get duration from GIF info if available, otherwise use a default
        # For simplicity, using a fixed duration. A real GIF might have frame durations.
        duration = 100 # milliseconds
        try:
            # Attempt to get duration from the first frame, if not, default
            duration = Image.open(self.exercises[self.current_exercise_index][4]).info.get('duration', 100)
        except:
            pass # Fallback to default
        self._after_id = self.master.after(duration, self.animate_gif, next_frame_index)

    def next_exercise(self):
        if self.exercises:
            if hasattr(self, '_after_id') and self._after_id:
                self.master.after_cancel(self._after_id)
            self.current_exercise_index = (self.current_exercise_index + 1) % len(self.exercises)
            self.load_exercise()

    def prev_exercise(self):
        if self.exercises:
            if hasattr(self, '_after_id') and self._after_id:
                self.master.after_cancel(self._after_id)
            self.current_exercise_index = (self.current_exercise_index - 1 + len(self.exercises)) % len(self.exercises)
            self.load_exercise()

class WorkoutCreatorScreen(BaseScreen):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance)
        self.available_exercises = []
        self.selected_exercises = []

        tk.Label(self, text="Create New Workout", font=("Arial", 20, "bold"), bg="#f0f0f0").pack(pady=15)

        tk.Label(self, text="Workout Name:", font=("Arial", 14), bg="#f0f0f0").pack(pady=5)
        self.workout_name_entry = tk.Entry(self, font=("Arial", 14), width=40)
        self.workout_name_entry.pack(pady=5)

        selection_frame = tk.Frame(self, bg="#f0f0f0")
        selection_frame.pack(fill="x", expand=True, padx=20, pady=10)

        # Available Exercises Listbox
        tk.Label(selection_frame, text="Available Exercises:", font=("Arial", 12, "bold"), bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.available_listbox = tk.Listbox(selection_frame, selectmode="single", height=10, font=("Arial", 12))
        self.available_listbox.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.available_listbox.bind("<Double-Button-1>", self.add_to_workout)
        selection_frame.grid_columnconfigure(0, weight=1)

        # Buttons in the middle
        button_col_frame = tk.Frame(selection_frame, bg="#f0f0f0")
        button_col_frame.grid(row=1, column=1, padx=10)
        tk.Button(button_col_frame, text="Add >", command=self.add_to_workout, font=("Arial", 10), bg="#28A745", fg="white").pack(pady=5)
        tk.Button(button_col_frame, text="< Remove", command=self.remove_from_workout, font=("Arial", 10), bg="#DC3545", fg="white").pack(pady=5)

        # Selected Exercises Listbox
        tk.Label(selection_frame, text="Workout Exercises:", font=("Arial", 12, "bold"), bg="#f0f0f0").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.selected_listbox = tk.Listbox(selection_frame, selectmode="single", height=10, font=("Arial", 12))
        self.selected_listbox.grid(row=1, column=2, padx=5, pady=5, sticky="nsew")
        self.selected_listbox.bind("<Double-Button-1>", self.remove_from_workout)
        selection_frame.grid_columnconfigure(2, weight=1)

        tk.Button(self, text="Save Workout", command=self.save_workout, font=("Arial", 14), bg="#007BFF", fg="white").pack(pady=20)
        tk.Button(self, text="Back to Home", command=lambda: self.app.show_screen("home"), font=("Arial", 12), bg="#6C757D", fg="white").pack(pady=10)

    def refresh(self):
        self.workout_name_entry.delete(0, tk.END)
        self.selected_exercises = []
        self.update_listboxes()
        self.load_available_exercises()

    def load_available_exercises(self):
        self.available_exercises = database.get_all_exercises()
        self.update_listboxes()

    def update_listboxes(self):
        self.available_listbox.delete(0, tk.END)
        for ex in self.available_exercises:
            if ex not in self.selected_exercises:
                self.available_listbox.insert(tk.END, ex[1]) # ex[1] is the name

        self.selected_listbox.delete(0, tk.END)
        for ex in self.selected_exercises:
            self.selected_listbox.insert(tk.END, ex[1])

    def add_to_workout(self, event=None):
        selection_index = self.available_listbox.curselection()
        if selection_index:
            exercise = self.available_exercises[selection_index[0]]
            if exercise not in self.selected_exercises:
                self.selected_exercises.append(exercise)
                self.update_listboxes()

    def remove_from_workout(self, event=None):
        selection_index = self.selected_listbox.curselection()
        if selection_index:
            del self.selected_exercises[selection_index[0]]
            self.update_listboxes()

    def save_workout(self):
        workout_name = self.workout_name_entry.get().strip()
        user = UserManager.get_current_user()

        if not user:
            NotificationManager.show_notification("Please log in to save a workout.", fg="red")
            return

        if not workout_name:
            NotificationManager.show_notification("Workout name cannot be empty.", fg="red")
            return

        if not self.selected_exercises:
            NotificationManager.show_notification("Please add exercises to your workout.", fg="red")
            return

        exercise_ids = [ex[0] for ex in self.selected_exercises] # ex[0] is the ID

        if database.create_workout(user["id"], workout_name, exercise_ids):
            NotificationManager.show_notification(f"Workout '{workout_name}' saved successfully!", fg="green")
            self.app.show_screen("home") # Or stay on screen and clear form
        else:
            NotificationManager.show_notification("Failed to save workout.", fg="red")


class LogWorkoutScreen(BaseScreen):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance)
        self.workouts = []
        self.selected_workout_exercises = []

        tk.Label(self, text="Log Your Workout", font=("Arial", 20, "bold"), bg="#f0f0f0").pack(pady=15)

        # Select Workout
        tk.Label(self, text="Select a Workout:", font=("Arial", 14), bg="#f0f0f0").pack(pady=5)
        self.workout_listbox = tk.Listbox(self, selectmode="single", height=5, font=("Arial", 12))
        self.workout_listbox.pack(pady=5, padx=20, fill="x")
        self.workout_listbox.bind("<<ListboxSelect>>", self.on_workout_select)

        # Exercise Logging Area (Scrollable)
        self.log_frame = ScrollFrame(self, bg="#e0e0e0")
        self.log_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.exercise_entries = {} # Store Entry widgets for each exercise

        tk.Button(self, text="Submit Log", command=self.submit_log, font=("Arial", 14), bg="#007BFF", fg="white").pack(pady=20)
        tk.Button(self, text="Back to Home", command=lambda: self.app.show_screen("home"), font=("Arial", 12), bg="#6C757D", fg="white").pack(pady=10)

    def refresh(self):
        self.workouts = []
        user = UserManager.get_current_user()
        if user:
            self.workouts = database.get_user_workouts(user["id"])
            self.workout_listbox.delete(0, tk.END)
            if self.workouts:
                for wid, wname in self.workouts:
                    self.workout_listbox.insert(tk.END, wname)
            else:
                self.workout_listbox.insert(tk.END, "No workouts created yet.")
                self.workout_listbox.config(state="disabled") # Disable if no workouts
        self.clear_exercise_entries()

    def clear_exercise_entries(self):
        for widget in self.log_frame.frame.winfo_children():
            widget.destroy()
        self.exercise_entries = {}
        self.selected_workout_exercises = []

    def on_workout_select(self, event):
        selection_index = self.workout_listbox.curselection()
        if selection_index:
            workout_id = self.workouts[selection_index[0]][0] # Get workout ID
            self.selected_workout_exercises = database.get_workout_details(workout_id)
            self.display_exercise_logging_form()

    def display_exercise_logging_form(self):
        self.clear_exercise_entries()

        if not self.selected_workout_exercises:
            tk.Label(self.log_frame.frame, text="Select a workout to log exercises.", font=("Arial", 12), bg="#e0e0e0").pack(pady=10)
            return

        for i, exercise in enumerate(self.selected_workout_exercises):
            ex_id, ex_name, _, _, _ = exercise
            frame = tk.LabelFrame(self.log_frame.frame, text=ex_name, font=("Arial", 12, "bold"), bg="#f0f0f0", bd=2, relief="groove")
            frame.pack(fill="x", padx=10, pady=5)

            # Use a dictionary to store entry widgets for easy retrieval
            self.exercise_entries[ex_id] = {}

            fields = ["Sets", "Reps", "Weight (kg)", "Duration (min)", "Calories Burned", "Notes"]
            keys = ["sets", "reps", "weight", "duration", "calories", "notes"]

            for j, (field, key) in enumerate(zip(fields, keys)):
                row_frame = tk.Frame(frame, bg="#f0f0f0")
                row_frame.pack(fill="x", padx=5, pady=2)
                tk.Label(row_frame, text=f"{field}:", font=("Arial", 10), bg="#f0f0f0", width=15, anchor="w").pack(side="left")
                if key == "notes":
                    entry = scrolledtext.ScrolledText(row_frame, height=2, width=30, font=("Arial", 10))
                else:
                    entry = tk.Entry(row_frame, width=20, font=("Arial", 10))
                entry.pack(side="left", expand=True, fill="x")
                self.exercise_entries[ex_id][key] = entry


    def submit_log(self):
        user = UserManager.get_current_user()
        if not user:
            NotificationManager.show_notification("Please log in to submit a workout.", fg="red")
            return

        log_date = datetime.date.today().isoformat() # YYYY-MM-DD

        for exercise_id, entries in self.exercise_entries.items():
            sets = entries["sets"].get()
            reps = entries["reps"].get()
            weight = entries["weight"].get()
            duration = entries["duration"].get()
            calories = entries["calories"].get()
            notes = entries["notes"].get("1.0", tk.END).strip() # For ScrolledText

            try:
                sets = int(sets) if sets else None
                reps = int(reps) if reps else None
                weight = float(weight) if weight else None
                duration = float(duration) if duration else None
                calories = float(calories) if calories else None
            except ValueError:
                NotificationManager.show_notification(f"Invalid numeric input for {database.get_exercise_by_id(exercise_id)[1]}. Please use numbers.", fg="red")
                return

            if not database.log_exercise(user["id"], exercise_id, sets, reps, weight, duration, calories, notes, log_date):
                NotificationManager.show_notification(f"Failed to log exercise: {database.get_exercise_by_id(exercise_id)[1]}", fg="red")
                return

        NotificationManager.show_notification("Workout logged successfully!", fg="green")
        self.app.show_screen("home")


class ProgressTrackingScreen(BaseScreen):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance)
        self.logs = []

        tk.Label(self, text="Your Progress", font=("Arial", 20, "bold"), bg="#f0f0f0").pack(pady=15)

        self.log_display_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=80, height=20, font=("Arial", 10))
        self.log_display_area.pack(pady=10, padx=20, fill="both", expand=True)
        self.log_display_area.config(state="disabled") # Make it read-only

        tk.Button(self, text="Back to Home", command=lambda: self.app.show_screen("home"), font=("Arial", 12), bg="#6C757D", fg="white").pack(pady=10)

    def refresh(self):
        user = UserManager.get_current_user()
        self.log_display_area.config(state="normal")
        self.log_display_area.delete("1.0", tk.END)
        if user:
            self.logs = database.get_user_exercise_logs(user["id"])
            if self.logs:
                self.log_display_area.insert(tk.END, "--- Your Exercise Log ---\n\n")
                for log in self.logs:
                    log_date, ex_name, sets, reps, weight, duration, calories, notes = log
                    self.log_display_area.insert(tk.END, f"Date: {log_date}\n")
                    self.log_display_area.insert(tk.END, f"  Exercise: {ex_name}\n")
                    if sets is not None: self.log_display_area.insert(tk.END, f"  Sets: {sets}\n")
                    if reps is not None: self.log_display_area.insert(tk.END, f"  Reps: {reps}\n")
                    if weight is not None: self.log_display_area.insert(tk.END, f"  Weight: {weight:.1f} kg\n")
                    if duration is not None: self.log_display_area.insert(tk.END, f"  Duration: {duration:.1f} min\n")
                    if calories is not None: self.log_display_area.insert(tk.END, f"  Calories: {calories:.1f} kcal\n")
                    if notes: self.log_display_area.insert(tk.END, f"  Notes: {notes}\n")
                    self.log_display_area.insert(tk.END, "------------------------\n\n")
            else:
                self.log_display_area.insert(tk.END, "No exercise logs found yet. Start logging your workouts!")
        else:
            self.log_display_area.insert(tk.END, "Please log in to view your progress.")
        self.log_display_area.config(state="disabled")