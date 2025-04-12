import tkinter as tk
from tkinter import filedialog, messagebox
import os
from frame_grabber import process_directory

import tkinter as tk
from tkinter import filedialog, messagebox
import os
from frame_grabber import process_directory

class VideoScriptApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Script App")
        
        # Set window size
        self.root.geometry("400x350")
        
        # Add labels and buttons
        self.label = tk.Label(root, text="Select a Folder with Video Files")
        self.label.pack(pady=10)

        # Folder selection button
        self.select_folder_button = tk.Button(root, text="Browse Input Folder", command=self.select_folder)
        self.select_folder_button.pack(pady=10)

        # Output folder label and button
        self.output_label = tk.Label(root, text="Select Output Folder")
        self.output_label.pack(pady=10)
        self.select_output_button = tk.Button(root, text="Browse Output Folder", command=self.select_output_folder)
        self.select_output_button.pack(pady=10)

        # Dropdown for selecting number of frames
        self.frames_label = tk.Label(root, text="Select Number of Frames to Extract")
        self.frames_label.pack(pady=10)
        
        # Dropdown options for number of frames
        self.frames_options = [1, 3, 5, 10, 20]
        self.selected_frames = tk.IntVar()
        self.selected_frames.set(self.frames_options[1])  # Default to 3 frames

        self.frames_dropdown = tk.OptionMenu(root, self.selected_frames, *self.frames_options)
        self.frames_dropdown.pack(pady=10)

        # Run Script Button
        self.run_button = tk.Button(root, text="Run Script", command=self.run_script, state=tk.DISABLED)
        self.run_button.pack(pady=10)

        # Folder path variables
        self.folder_path = ""
        self.output_folder_path = ""

    def select_folder(self):
        # Open folder dialog to select input folder
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path = folder
            self.label.config(text=f"Selected Input Folder: {folder}")
            self.run_button.config(state=tk.NORMAL)  # Enable the run button once a folder is selected

    def select_output_folder(self):
        # Open folder dialog to select output folder
        output_folder = filedialog.askdirectory()
        if output_folder:
            self.output_folder_path = output_folder
            self.output_label.config(text=f"Selected Output Folder: {output_folder}")
    
    def run_script(self):
        if not self.folder_path:
            messagebox.showerror("Error", "Please select an input folder first!")
            return
        
        if not self.output_folder_path:
            messagebox.showerror("Error", "Please select an output folder!")
            return
        
        # Get the number of frames selected from the dropdown
        num_frames = self.selected_frames.get()
        
        try:
            process_directory(self.folder_path, self.output_folder_path, num_frames)
            messagebox.showinfo("Success", "Script ran successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoScriptApp(root)
    root.mainloop()

