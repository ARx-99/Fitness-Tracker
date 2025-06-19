import sqlite3

DATABASE_NAME = "fitness_tracker.db"

def connect_db():
    """Connects to the SQLite database."""
    return sqlite3.connect(DATABASE_NAME)

def init_db():
    """Initializes the database schema."""
    conn = connect_db()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Exercises table (Pre-defined exercises)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            image_path TEXT,
            gif_path TEXT
        )
    """)

    # Workouts table (Custom workout routines)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Workout_Exercises table (Many-to-many relationship for workouts and exercises)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workout_exercises (
            workout_id INTEGER NOT NULL,
            exercise_id INTEGER NOT NULL,
            sequence INTEGER NOT NULL, -- Order of exercises in a workout
            PRIMARY KEY (workout_id, exercise_id),
            FOREIGN KEY (workout_id) REFERENCES workouts(id),
            FOREIGN KEY (exercise_id) REFERENCES exercises(id)
        )
    """)

    # Exercise_Logs table (User's logged exercise data)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exercise_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            exercise_id INTEGER NOT NULL,
            log_date TEXT NOT NULL,
            sets INTEGER,
            reps INTEGER,
            weight REAL,
            duration_minutes REAL,
            calories_burned REAL,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (exercise_id) REFERENCES exercises(id)
        )
    """)

    conn.commit()
    conn.close()

def add_user(username, password):
    """Adds a new user to the database."""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        print(f"User '{username}' already exists.")
        return False
    finally:
        conn.close()

def get_user(username, password):
    """Retrieves a user by username and password."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

def add_exercise(name, description, image_path, gif_path):
    """Adds a new exercise to the database."""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO exercises (name, description, image_path, gif_path) VALUES (?, ?, ?, ?)",
            (name, description, image_path, gif_path)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        print(f"Exercise '{name}' already exists.")
        return False
    finally:
        conn.close()

def get_all_exercises():
    """Retrieves all exercises from the database."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description, image_path, gif_path FROM exercises ORDER BY name")
    exercises = cursor.fetchall()
    conn.close()
    return exercises

def get_exercise_by_id(exercise_id):
    """Retrieves an exercise by its ID."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description, image_path, gif_path FROM exercises WHERE id = ?", (exercise_id,))
    exercise = cursor.fetchone()
    conn.close()
    return exercise

def create_workout(user_id, workout_name, exercise_ids):
    """Creates a new workout routine for a user."""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO workouts (user_id, name) VALUES (?, ?)", (user_id, workout_name))
        workout_id = cursor.lastrowid

        for i, exercise_id in enumerate(exercise_ids):
            cursor.execute(
                "INSERT INTO workout_exercises (workout_id, exercise_id, sequence) VALUES (?, ?, ?)",
                (workout_id, exercise_id, i)
            )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error creating workout: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def get_user_workouts(user_id):
    """Retrieves all workouts for a given user."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM workouts WHERE user_id = ?", (user_id,))
    workouts = cursor.fetchall()
    conn.close()
    return workouts

def get_workout_details(workout_id):
    """Retrieves exercises within a specific workout."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.id, e.name, e.description, e.image_path, e.gif_path
        FROM workout_exercises we
        JOIN exercises e ON we.exercise_id = e.id
        WHERE we.workout_id = ?
        ORDER BY we.sequence
    """, (workout_id,))
    exercises = cursor.fetchall()
    conn.close()
    return exercises

def log_exercise(user_id, exercise_id, sets, reps, weight, duration_minutes, calories_burned, notes, log_date):
    """Logs a performed exercise."""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO exercise_logs
               (user_id, exercise_id, sets, reps, weight, duration_minutes, calories_burned, notes, log_date)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, exercise_id, sets, reps, weight, duration_minutes, calories_burned, notes, log_date)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error logging exercise: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def get_user_exercise_logs(user_id):
    """Retrieves all exercise logs for a given user, with exercise names."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT el.log_date, e.name, el.sets, el.reps, el.weight, el.duration_minutes, el.calories_burned, el.notes
        FROM exercise_logs el
        JOIN exercises e ON el.exercise_id = e.id
        WHERE el.user_id = ?
        ORDER BY el.log_date DESC
    """, (user_id,))
    logs = cursor.fetchall()
    conn.close()
    return logs

if __name__ == '__main__':
    # This block runs when database.py is executed directly for setup/testing
    init_db()
    print("Database initialized.")

    # Add some dummy exercises if they don't exist
    if not get_all_exercises():
        add_exercise("Push-ups", "A common calisthenics exercise performed in a prone position by raising and lowering the body using the arms.", "images/pushup.png", "gifs/pushup.gif")
        add_exercise("Squats", "A strength exercise in which the trainee lowers their hips from a standing position and then stands back up.", "images/squat.png", "gifs/squat.gif")
        add_exercise("Plank", "An isometric core strength exercise that involves maintaining a position similar to a push-up for the maximum possible time.", "images/plank.png", "gifs/plank.gif")
        add_exercise("Lunges", "A strength training exercise that works the quads, glutes, hamstrings, and calves.", "images/lunge.png", "gifs/lunge.gif")
        print("Dummy exercises added.")