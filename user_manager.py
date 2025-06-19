import database

class UserManager:
    _current_user = None # Stores (id, username) of the logged-in user

    @staticmethod
    def register_user(username, password):
        """Registers a new user."""
        if database.add_user(username, password):
            return True
        return False

    @staticmethod
    def login_user(username, password):
        """Logs in a user and sets the current user."""
        user = database.get_user(username, password)
        if user:
            UserManager._current_user = {"id": user[0], "username": user[1]}
            return True
        return False

    @staticmethod
    def logout_user():
        """Logs out the current user."""
        UserManager._current_user = None

    @staticmethod
    def get_current_user():
        """Returns the currently logged-in user's ID and username."""
        return UserManager._current_user

    @staticmethod
    def is_logged_in():
        """Checks if a user is currently logged in."""
        return UserManager._current_user is not None