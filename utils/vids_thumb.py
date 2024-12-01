import cv2
import numpy as np
import os


def capture_frames(vid, num_frames):
    cap = cv2.VideoCapture(vid)

    if not cap.isOpened():
        print("Error: Could not open video.")
        return [], 0, 0

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Get total number of frames in the video
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Calculate interval between frames to capture
    interval = int(0.95 * total_frames) // num_frames

    frames = []
    for i in range(num_frames):
        # Set the position of the next frame to capture
        cap.set(cv2.CAP_PROP_POS_FRAMES, i * interval + 4)

        # Read the frame
        ret, frame = cap.read()
        if not ret:
            print(f"Error: Could not read frame {i * interval}.")
            break

        frames.append(frame)

    cap.release()
    return frames, width, height


def create_thumbnail(frames, thumb_width=100, thumb_height=100, columns=5):
    print(thumb_width, thumb_height)
    # Resize frames to the thumbnail size
    resized_frames = [
        cv2.resize(frame, (thumb_width, thumb_height)) for frame in frames
    ]

    # Determine number of rows based on number of columns
    rows = (len(resized_frames) + columns - 1) // columns

    # Create a blank image to hold the thumbnails
    thumbnail_height = rows * thumb_height
    thumbnail_width = columns * thumb_width
    thumbnail = np.zeros(
        (thumbnail_height, thumbnail_width, 3), dtype=np.uint8)

    # Paste the thumbnails into the blank image
    for i, frame in enumerate(resized_frames):
        row = i // columns
        col = i % columns
        y_start = row * thumb_height
        y_end = y_start + thumb_height
        x_start = col * thumb_width
        x_end = x_start + thumb_width
        thumbnail[y_start:y_end, x_start:x_end] = frame

    return thumbnail


def rename_all(dir):
    i = 0
    for file in os.listdir(dir):
        print(file)
        new_name = str(i) + file[-4:]
        os.rename(dir + file, dir + new_name)
        i += 1
        print(f"Renamed {file} to {new_name}")


def vid_gen_thumb(vid):
    thumb = vid+'.jpg'
    num_frames = 20
    frames, width, height = capture_frames(vid, num_frames)
    if frames:
        thumbnail = create_thumbnail(frames, width, height, columns=5)
        cv2.imwrite(thumb, thumbnail)
        print(f"Thumbnail saved to {thumb}")
    else:
        print("No frames were captured.")


def gen_thumbs_in_dir(dir):
    for root, _, files in os.walk(dir):
        for file in files:
            filepath = os.path.join(root, file)
            vid_gen_thumb(filepath)


if __name__ == "__main__":
    gen_thumbs_in_dir('.')
