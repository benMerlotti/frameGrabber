import os
import sys
from moviepy.editor import VideoFileClip
import argparse
import traceback

def extract_frames(video_path, output_folder, num_frames=3):
    print(f"Number of frames to extract: {num_frames}")
    """Extract frames from a video file and save them as JPGs.
    
    Args:
        video_path: Path to the video file
        output_folder: Folder to save the extracted frames
        num_frames: Number of frames to extract (default: 3)
    """
    try:
        # Get video filename without extension
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        
        # Create output directory for this video if needed
        video_output_dir = os.path.join(output_folder, video_name)
        os.makedirs(video_output_dir, exist_ok=True)
        
        print(f"Processing {video_path}...")
        
        # Load the video
        clip = VideoFileClip(video_path)
        
        # Check if the video loaded correctly
        if clip is None:
            print(f"Failed to load video: {video_path}")
            return
            
        duration = clip.duration
        
        # Calculate timestamps for frame extraction
        timestamps = []
        for i in range(num_frames):
            timestamp = i * duration / num_frames  # Evenly distribute the frames
            timestamps.append(timestamp)
        
        print(f"Video duration: {duration:.2f}s, extracting frames at timestamps: {[f'{t:.2f}s' for t in timestamps]}")
        
        # Extract frames at specified timestamps
        for i, timestamp in enumerate(timestamps):
            if timestamp > duration:
                timestamp = duration - 0.1  # Adjust if timestamp exceeds duration
                
            # Save the frame as JPG
            output_path = os.path.join(video_output_dir, f"{video_name}_{timestamp}.jpg")
            print(f"Attempting to save frame at {timestamp:.2f}s to {output_path}")
            
            clip.save_frame(output_path, t=timestamp)
            print(f"Successfully saved frame to {output_path}")
        
        # Close the clip to release resources
        clip.close()
        
    except Exception as e:
        print(f"Error processing {video_path}:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        traceback.print_exc()


def process_directory(input_dir, output_dir, num_frames=3):
    """Process all video files in a directory.
    
    Args:
        input_dir: Directory containing video files
        output_dir: Directory to save extracted frames
        num_frames: Number of frames to extract per video
    """
    # Check if input directory exists
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist.")
        return
    
    if not os.path.isdir(input_dir):
        print(f"Error: '{input_dir}' is not a directory.")
        return
    
    # Create output directory if needed
    os.makedirs(output_dir, exist_ok=True)
    
    # List of common video file extensions
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
    
    # Get list of files in the directory
    try:
        files = os.listdir(input_dir)
        print(f"Found {len(files)} files in directory {input_dir}")
    except Exception as e:
        print(f"Error reading directory {input_dir}: {e}")
        return
    
    # Keep track of videos processed
    videos_processed = 0
    
    # Process each video file
    for filename in files:
        filepath = os.path.join(input_dir, filename)
        print(f"Checking file: {filepath}")
        
        if os.path.isfile(filepath) and any(filename.lower().endswith(ext) for ext in video_extensions):
            print(f"Found video file: {filename}")
            videos_processed += 1
            try:
                extract_frames(filepath, output_dir, num_frames)
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                traceback.print_exc()
    
    if videos_processed == 0:
        print(f"No video files found in {input_dir}. Supported formats: {', '.join(video_extensions)}")
    else:
        print(f"Processed {videos_processed} video files.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract frames from video files")
    parser.add_argument("input", help="Input directory containing video files")
    parser.add_argument("output", help="Output directory for extracted frames")
    parser.add_argument("--frames", type=int, default=3, help="Number of frames to extract (default: 3)")
    
    args = parser.parse_args()
    
    print(f"Starting frame extraction...")
    print(f"Input directory: {args.input}")
    print(f"Output directory: {args.output}")
    print(f"Frames per video: {args.frames}")
    
    process_directory(args.input, args.output, args.frames)
    print(f"Finished extracting frames from videos in {args.input}")