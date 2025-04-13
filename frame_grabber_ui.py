import sys
import os
import threading
import time
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QProgressBar, QComboBox, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from frame_grabber import extract_frames

# Create a signals class to communicate between threads
class WorkerSignals(QObject):
    progress = pyqtSignal(int, int, float)
    finished = pyqtSignal(str, str)
    error = pyqtSignal(str)

class VideoScriptApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Video Frame Grabber")
        self.setGeometry(100, 100, 500, 450)  # Window size
        
        # Initialize folder paths
        self.folder_path = ""
        self.output_folder_path = ""
        
        # Cancel flag
        self.cancel_flag = False
        
        # Processing thread
        self.processing_thread = None
        
        # Create signals for thread communication
        self.signals = WorkerSignals()
        self.signals.progress.connect(self.update_progress)
        self.signals.finished.connect(self.show_completion_message)
        self.signals.error.connect(self.show_error)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()

        # Label for folder selection
        self.label = QLabel("Select a Folder with Video Files")
        layout.addWidget(self.label)

        # Browse button for input folder
        self.select_folder_button = QPushButton("Browse Input Folder")
        self.select_folder_button.clicked.connect(self.select_folder)
        layout.addWidget(self.select_folder_button)

        # Label for selected folder
        self.selected_folder_label = QLabel("No folder selected")
        layout.addWidget(self.selected_folder_label)

        # Label and button for output folder
        self.output_label = QLabel("Select Output Folder")
        layout.addWidget(self.output_label)
        
        self.select_output_button = QPushButton("Browse Output Folder")
        self.select_output_button.clicked.connect(self.select_output_folder)
        layout.addWidget(self.select_output_button)

        # Label for selected output folder
        self.selected_output_folder_label = QLabel("No output folder selected")
        layout.addWidget(self.selected_output_folder_label)

        # Dropdown for selecting number of frames
        self.frames_label = QLabel("Select Number of Frames to Extract")
        layout.addWidget(self.frames_label)

        self.frames_options = [1, 3, 5, 10, 20]
        self.selected_frames = QComboBox()
        self.selected_frames.addItems([str(option) for option in self.frames_options])
        self.selected_frames.setCurrentIndex(1)  # Default to 3 frames
        layout.addWidget(self.selected_frames)

        # Run Script Button
        self.run_button = QPushButton("Run Script")
        self.run_button.clicked.connect(self.run_script)
        self.run_button.setEnabled(False)  # Initially disabled
        layout.addWidget(self.run_button)

        # Cancel Button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_process)
        self.cancel_button.setEnabled(False)  # Initially disabled
        layout.addWidget(self.cancel_button)

        # Status label
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        # Loading bar
        self.loading_bar = QProgressBar()
        layout.addWidget(self.loading_bar)

        # Percentage label
        self.percentage_label = QLabel("0%")
        layout.addWidget(self.percentage_label)

        # Estimated time label
        self.estimated_time_label = QLabel("Estimated Time Remaining: N/A")
        layout.addWidget(self.estimated_time_label)

        self.setLayout(layout)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder_path = folder
            self.selected_folder_label.setText(f"Folder: {os.path.basename(folder)}")
            self.update_run_button_state()

    def select_output_folder(self):
        output_folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if output_folder:
            self.output_folder_path = output_folder
            self.selected_output_folder_label.setText(f"Folder: {os.path.basename(output_folder)}")
            self.update_run_button_state()

    def update_run_button_state(self):
        # Enable run button only if both input and output folders are selected
        if self.folder_path and self.output_folder_path:
            self.run_button.setEnabled(True)
        else:
            self.run_button.setEnabled(False)

    def run_script(self):
        if not self.folder_path:
            self.show_error("Please select an input folder first!")
            return
        if not self.output_folder_path:
            self.show_error("Please select an output folder!")
            return

        self.cancel_flag = False
        self.run_button.setEnabled(False)
        self.cancel_button.setEnabled(True)

        num_frames = int(self.selected_frames.currentText())
        
        # Start processing in a separate thread to keep UI responsive
        self.processing_thread = threading.Thread(target=self.process_videos, args=(num_frames,))
        self.processing_thread.daemon = True
        self.processing_thread.start()

    def process_videos(self, num_frames):
        try:
            # Get the list of videos in the folder
            video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
            video_files = [f for f in os.listdir(self.folder_path)
                          if os.path.isfile(os.path.join(self.folder_path, f)) and 
                          any(f.lower().endswith(ext) for ext in video_extensions)]
            
            total_videos = len(video_files)
            
            if total_videos == 0:
                self.status_label.setText("No video files found in the selected folder")
                self.signals.finished.emit("Warning", "No video files found in the selected folder")
                return

            processed_videos = 0
            start_time = time.time()

            # Process each video file
            for filename in video_files:
                if self.cancel_flag:
                    break

                # Use signals to update the status label from the main thread
                # This will be done in the update_progress slot
                
                filepath = os.path.join(self.folder_path, filename)

                # Call the extract_frames function from frame_grabber.py
                extract_frames(filepath, self.output_folder_path, num_frames)

                processed_videos += 1

                # Emit the progress signal to update UI in the main thread
                self.signals.progress.emit(processed_videos, total_videos, start_time)

            if not self.cancel_flag:
                self.signals.finished.emit("Success", "All videos processed successfully!")
            else:
                self.signals.finished.emit("Cancelled", "Process was cancelled.")
        
        except Exception as e:
            self.signals.error.emit(f"An error occurred: {str(e)}")

    def update_progress(self, processed_videos, total_videos, start_time):
        # Update UI components with progress information
        self.status_label.setText(f"Processing: {processed_videos} of {total_videos} videos")
        self.loading_bar.setMaximum(total_videos)
        self.loading_bar.setValue(processed_videos)
        
        # Calculate the percentage of completion
        percentage = (processed_videos / total_videos) * 100
        self.percentage_label.setText(f"{percentage:.1f}%")
        
        # Estimate remaining time
        if processed_videos > 0:
            elapsed_time = time.time() - start_time
            avg_time_per_video = elapsed_time / processed_videos
            remaining_time = avg_time_per_video * (total_videos - processed_videos)
            remaining_minutes, remaining_seconds = divmod(remaining_time, 60)
            self.estimated_time_label.setText(f"Est. Time Remaining: {int(remaining_minutes)}m {int(remaining_seconds)}s")

    def show_completion_message(self, title, message):
        QMessageBox.information(self, title, message)
        self.status_label.setText("")
        self.run_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.loading_bar.setValue(0)
        self.percentage_label.setText("0%")
        self.estimated_time_label.setText("Estimated Time Remaining: N/A")

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)
        self.run_button.setEnabled(True)
        self.cancel_button.setEnabled(False)

    def cancel_process(self):
        self.cancel_flag = True
        self.status_label.setText("Cancelling... Please wait")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = VideoScriptApp()
    ex.show()
    sys.exit(app.exec_())