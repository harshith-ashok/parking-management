from flask import Flask, render_template, Response, jsonify
import cv2
import numpy as np
import json
import os

app = Flask(__name__)

# Load parking slots from JSON


def load_slots():
    try:
        with open('slots.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"slots": []}


# Global variables
slots_data = load_slots()
slot_status = {}
IMAGE_PATH = "parking.jpg"  # Changed from video.mp4 to parking.jpg


def inside_polygon(point, polygon):
    """Check if a point is inside a polygon using cv2.pointPolygonTest"""
    polygon_array = np.array(polygon, dtype=np.int32)
    result = cv2.pointPolygonTest(polygon_array, point, False)
    return result >= 0


def detect_occupancy(frame):
    """Detect occupancy for each parking slot using edge detection and contour analysis"""
    global slot_status

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 25, 16)

    # Apply morphological operations
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    morphed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Edge detection
    edges = cv2.Canny(blurred, 50, 150)

    # Process each parking slot
    for slot in slots_data.get("slots", []):
        slot_id = slot.get("id")
        polygon = slot.get("polygon")

        if not polygon or not slot_id:
            continue

        # Create mask for this parking slot
        mask = np.zeros(morphed.shape, dtype=np.uint8)
        polygon_array = np.array(polygon, dtype=np.int32)
        cv2.fillPoly(mask, [polygon_array], 255)

        # Apply mask to processed image
        slot_region = cv2.bitwise_and(morphed, mask)
        slot_edges = cv2.bitwise_and(edges, mask)

        # Count white pixels (potential car indicators)
        white_pixel_count = cv2.countNonZero(slot_region)
        edge_count = cv2.countNonZero(slot_edges)

        # Calculate the area of the parking slot
        slot_area = cv2.countNonZero(mask)

        # Calculate occupancy ratio
        occupancy_ratio = white_pixel_count / slot_area if slot_area > 0 else 0
        edge_ratio = edge_count / slot_area if slot_area > 0 else 0

        # Determine if slot is occupied based on thresholds
        # A slot is considered occupied if it has sufficient texture/edges
        is_occupied = occupancy_ratio > 0.15 or edge_ratio > 0.05

        slot_status[slot_id] = {
            "occupied": is_occupied,
            "count": int(white_pixel_count),
            "occupancy_ratio": float(occupancy_ratio)
        }

        # Draw polygon on frame
        color = (0, 0, 255) if is_occupied else (
            0, 255, 0)  # Red if occupied, Green if free
        cv2.polylines(frame, [polygon_array], True, color, 3)

        # Add label with background for better visibility
        centroid_x = int(np.mean([p[0] for p in polygon]))
        centroid_y = int(np.mean([p[1] for p in polygon]))
        status_text = "Occupied" if is_occupied else "Free"

        # Draw text background
        text = f"{slot_id}: {status_text}"
        (text_width, text_height), _ = cv2.getTextSize(
            text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(frame,
                      (centroid_x - text_width//2 - 5,
                       centroid_y - text_height - 5),
                      (centroid_x + text_width//2 + 5, centroid_y + 5),
                      (0, 0, 0), -1)

        # Draw text
        cv2.putText(frame, text,
                    (centroid_x - text_width//2, centroid_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    return frame


def generate_frames():
    """Generate frames for image streaming (continuously serve the same processed image)"""

    if not os.path.exists(IMAGE_PATH):
        # Create a dummy frame if image doesn't exist
        dummy_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        cv2.putText(dummy_frame, f"Image file '{IMAGE_PATH}' not found",
                    (300, 360), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        ret, buffer = cv2.imencode('.jpg', dummy_frame)
        frame_bytes = buffer.tobytes()
        while True:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    else:
        # Read the image once
        frame = cv2.imread(IMAGE_PATH)

        if frame is None:
            dummy_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
            cv2.putText(dummy_frame, f"Failed to load '{IMAGE_PATH}'",
                        (300, 360), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            ret, buffer = cv2.imencode('.jpg', dummy_frame)
            frame_bytes = buffer.tobytes()
            while True:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        else:
            # Process the image once
            processed_frame = frame.copy()
            processed_frame = detect_occupancy(processed_frame)

            # Encode frame to JPEG
            ret, buffer = cv2.imencode('.jpg', processed_frame, [
                                       cv2.IMWRITE_JPEG_QUALITY, 90])
            frame_bytes = buffer.tobytes()

            # Continuously serve the same processed image
            while True:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    """Image streaming route (renamed for compatibility with frontend)"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/slots')
def get_slots():
    """API endpoint to get slot status"""
    total_slots = len(slots_data.get("slots", []))
    occupied_count = sum(1 for status in slot_status.values()
                         if status.get("occupied", False))
    free_count = total_slots - occupied_count

    return jsonify({
        "total": total_slots,
        "occupied": occupied_count,
        "free": free_count,
        "slots": slot_status
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9000)
