# Parking Occupancy Detection System

A Flask-based web application for real-time parking lot occupancy detection using computer vision techniques. The system analyzes parking lot images to identify occupied and available parking spaces through adaptive thresholding, edge detection, and polygon-based region analysis.

## Overview

This application provides an automated solution for monitoring parking lot occupancy. It processes static parking lot images and uses computer vision algorithms to determine whether individual parking spaces are occupied or available. The system displays results through an interactive web interface with real-time status updates.

## Features

- **Automated Occupancy Detection**: Utilizes adaptive thresholding and edge detection to analyze parking spaces
- **Polygon-Based Region Definition**: Flexible parking space definition using customizable polygon coordinates
- **Real-Time Web Interface**: Live streaming display with status indicators
- **RESTful API**: JSON endpoint for integration with external systems
- **Visual Feedback**: Color-coded overlay showing occupied (red) and free (green) parking spaces
- **Statistics Dashboard**: Real-time counters for total, occupied, and available spaces
- **Responsive Design**: Mobile-friendly interface that adapts to different screen sizes

## Requirements

- Python 3.7 or higher
- Flask 2.0+
- OpenCV (cv2) 4.5+
- NumPy 1.19+

## Installation

Install the required dependencies using pip:

```bash
pip install flask opencv-python numpy
```

## Configuration

### Parking Space Definition

Parking spaces are defined in `slots.json` using polygon coordinates. Each parking space requires four corner points specified in clockwise order starting from the top-left corner.

Example structure:

```json
{
  "slots": [
    {
      "id": "L1",
      "polygon": [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    }
  ]
}
```

### Coordinate Helper Tool

A coordinate helper utility is provided to assist in determining the correct polygon coordinates for your parking lot image:

```bash
python coordinate_helper.py
```

Instructions for use:

1. Click on the four corners of each parking space in order
2. Press 's' to save the current slot
3. Press 'u' to undo the last point
4. Press 'r' to reset the current slot
5. Press 'q' to finish and save to `slots.json`

### Detection Threshold Adjustment

The occupancy detection algorithm can be fine-tuned by adjusting threshold values in `app.py`:

```python
is_occupied = occupancy_ratio > 0.15 or edge_ratio > 0.05
```

- **occupancy_ratio**: Proportion of detected pixels within the parking space (range: 0.0 to 1.0)
- **edge_ratio**: Proportion of edge pixels detected within the parking space (range: 0.0 to 1.0)

Increase values for stricter detection (fewer false positives), decrease for more sensitive detection.

## Usage

### Starting the Application

Run the Flask application:

```bash
python app.py
```

The server will start on `http://localhost:5000` by default.

### Accessing the Interface

Open a web browser and navigate to:

```
http://localhost:5000
```

The interface displays:

- Live parking lot image with annotated parking spaces
- Real-time occupancy statistics
- Detailed list of individual slot statuses

### API Endpoints

#### GET /

Returns the main web interface.

#### GET /video_feed

Streams the processed parking lot image with occupancy annotations in MJPEG format.

#### GET /slots

Returns current occupancy data in JSON format.

Response structure:

```json
{
  "total": 10,
  "occupied": 3,
  "free": 7,
  "slots": {
    "L1": {
      "occupied": false,
      "count": 120,
      "occupancy_ratio": 0.08
    }
  }
}
```

## Technical Details

### Detection Algorithm

The system employs multiple computer vision techniques:

1. **Grayscale Conversion**: Reduces computational complexity
2. **Gaussian Blur**: Removes noise while preserving edges
3. **Adaptive Thresholding**: Handles varying lighting conditions
4. **Morphological Operations**: Enhances object boundaries
5. **Canny Edge Detection**: Identifies object contours
6. **Region Analysis**: Calculates occupancy metrics per parking space

### Image Processing Pipeline

1. Load parking lot image
2. Convert to grayscale
3. Apply Gaussian blur (5x5 kernel)
4. Perform adaptive thresholding
5. Apply morphological closing
6. Detect edges using Canny algorithm
7. For each defined parking space:
   - Create polygon mask
   - Calculate pixel density within mask
   - Determine occupancy based on thresholds
   - Annotate image with results

## Customization

### Image Source

Modify the `IMAGE_PATH` variable in `app.py`:

```python
IMAGE_PATH = "parking.jpg"
```

### Server Configuration

Adjust Flask server parameters in the main block:

```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

### Visual Styling

Customize the appearance by modifying the CSS in `templates/index.html`. Key elements include color schemes, card layouts, and responsive breakpoints.

## Troubleshooting

### Incorrect Detection Results

- Verify polygon coordinates match actual parking space positions
- Adjust detection thresholds in the `detect_occupancy()` function
- Ensure adequate image quality and resolution
- Check lighting conditions in the image

### Image Not Loading

- Confirm the image file exists at the specified path
- Verify the image format is supported (JPG, PNG)
- Check file permissions

### Performance Issues

- Reduce image resolution if processing is slow
- Optimize polygon complexity
- Consider caching processed results for static images

## Integration Examples

### Fetching Occupancy Data

JavaScript example:

```javascript
fetch("/slots")
  .then((response) => response.json())
  .then((data) => {
    console.log(`Available spaces: ${data.free}`);
  });
```

Python example:

```python
import requests

response = requests.get('http://localhost:5000/slots')
data = response.json()
print(f"Occupancy rate: {data['occupied']}/{data['total']}")
```

## Limitations

- Designed for overhead/aerial parking lot images
- Requires manual polygon definition for each parking space
- Static image analysis (no temporal tracking)
- Performance depends on image quality and lighting conditions
- May require threshold tuning for different environments

## Future Enhancements

Potential improvements for future versions:

- Automatic parking space detection using machine learning
- Support for video streams and real-time processing
- Historical occupancy tracking and analytics
- Multi-camera support
- Deep learning-based vehicle detection
- Mobile application integration
- Cloud deployment configuration
