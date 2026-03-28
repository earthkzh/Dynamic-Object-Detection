import tkinter as tk
import subprocess

# -------------------- FUNCTIONS FOR BUTTONS --------------------
def open_rectangle():
    subprocess.Popen(["python", "similarity.py"])

def open_grayscale():
    subprocess.Popen(["python", "object.py"])

# -------------------- MAIN WINDOW --------------------
root = tk.Tk()
root.title("Main Page")
root.geometry("850x550")
root.resizable(False, False)
root.configure(bg="#ADD8E6")

# -------------------- TITLE --------------------
title_label = tk.Label(
    root,
    text="Welcome to our page",
    font=("Helvetica", 20, "bold"),
    bg="#ADD8E6",
    fg="#ffffff"
)
title_label.pack(pady=(30, 100))

# -------------------- DESCRIPTION --------------------

# -------------------- BUTTONS --------------------
btn_rectangle = tk.Button(
    root,
    text="Find Similarity",
    font=("Helvetica", 14, "bold"),
    bg="#D8BFD8", fg="black",
    activebackground="#c0392b",
    width=20, height=2,
    command=open_rectangle
)
btn_rectangle.pack(pady=40)

btn_obj = tk.Button(
    root,
    text="Object Detection",
    font=("Helvetica", 14, "bold"),
    bg="#FFFFE0", fg="black",
    activebackground="#2980b9",
    width=20, height=2,
    command=open_grayscale
)
btn_obj.pack(pady=40)

# -------------------- RUN GUI --------------------
root.mainloop()