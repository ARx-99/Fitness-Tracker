import tkinter as tk
from tkinter import messagebox

class ScrollFrame(tk.Frame):
    """
    A custom scrollable frame widget.
    Allows content to extend beyond the visible area and be scrolled.
    """
    def __init__(self, parent, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)

        self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff")
        self.frame = tk.Frame(self.canvas, background="#ffffff")
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas_frame_id = self.canvas.create_window((4,4), window=self.frame, anchor="nw",
                                      tags="self.frame")

        self.frame.bind("<Configure>", self.onFrameConfigure)
        self.canvas.bind("<Configure>", self.onCanvasConfigure)

    def onFrameConfigure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def onCanvasConfigure(self, event):
        """Resize the inner frame to fit the canvas width"""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_frame_id, width=canvas_width)

class NotificationManager:
    """Manages simple in-app notifications."""
    _notification_label = None
    _master = None
    _after_id = None

    @staticmethod
    def init(master, label_widget):
        """Initializes the notification manager with the main window and a label."""
        NotificationManager._master = master
        NotificationManager._notification_label = label_widget

    @staticmethod
    def show_notification(message, duration_ms=3000, fg="green"):
        """Displays a notification message."""
        if NotificationManager._notification_label:
            NotificationManager._notification_label.config(text=message, fg=fg)
            if NotificationManager._after_id:
                NotificationManager._master.after_cancel(NotificationManager._after_id)
            NotificationManager._after_id = NotificationManager._master.after(duration_ms, NotificationManager.clear_notification)
        else:
            # Fallback to messagebox if label not initialized (for critical errors)
            messagebox.showinfo("Notification", message)

    @staticmethod
    def clear_notification():
        """Clears the displayed notification."""
        if NotificationManager._notification_label:
            NotificationManager._notification_label.config(text="")
            NotificationManager._after_id = None