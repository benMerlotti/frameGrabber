import tkinter as tk

root = tk.Tk()
root.title("Test Window")
root.geometry("200x100")
tk.Label(root, text="Hello!").pack()
root.mainloop()
