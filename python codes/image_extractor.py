import cv2
import os

# Function to extract frames from a video file
frame_count = 0
def extract_frames(video_path, output_folder, interval_seconds):
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    global frame_count
    
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return
    
    # Get the frames per second (fps) of the video
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Calculate the number of frames to skip based on the interval_seconds
    frames_to_skip = fps * interval_seconds
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        # Save the frame every 'frames_to_skip' frames
        if frame_count % frames_to_skip == 0:
            frame_filename = os.path.join(output_folder, f"frame_{frame_count // frames_to_skip:04d}.jpg")
            cv2.imwrite(frame_filename, frame)
        
        frame_count += 1
    
    # Release the video capture object
    cap.release()
    print(f"Frames extracted and saved from {video_path} to {output_folder}")

if __name__ == "__main__":
    video_folder = "C:/Users/sjose/Downloads/videos"  # Replace with the folder containing your video files
    output_folder = "C:/Users/sjose/Downloads/videos/output"  # Replace with your desired output folder
    interval_seconds = 5
    
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Iterate through all video files in the input folder
    for video_filename in os.listdir(video_folder):
        print("HI")
        if video_filename.endswith(".ts"):
            
            video_path = os.path.join(video_folder, video_filename)
            extract_frames(video_path, output_folder, interval_seconds)
