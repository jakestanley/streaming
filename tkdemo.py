#!/usr/bin/env python
import tkinter as tk
from tkinter import messagebox

def handle_selection():
    selected_option = var.get()
    messagebox.showinfo("Selection", f"You selected: {selected_option}")

root = tk.Tk()
root.title("Option Selection")

options = ["Option 1", "Option 2", "Option 3"]

listbox = tk.Listbox(root, selectmode=tk.MULTIPLE)
listbox.pack()

for option in options:
    listbox.insert(tk.END, option)

select_button = tk.Button(root, text="Select", command=handle_selection)
select_button.pack()

root.mainloop()