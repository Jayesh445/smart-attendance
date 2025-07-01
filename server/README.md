# Face Recognition Attendance System

A complete face recognition-based attendance system built with Python, OpenCV, and FastAPI.

## Features

- **Student Registration**: Register new students and capture their face images for training
- **Face Training**: Train the face recognition model using captured images
- **Automatic Attendance**: Mark attendance automatically using face recognition
- **Data Storage**: Store student details and attendance records in CSV files
- **Multiple Recognition Methods**: Support for both traditional CV2 and advanced face_recognition library
- **REST API**: FastAPI-based REST API for integration with other applications
- **Real-time Processing**: Live camera feed for face recognition

## System Requirements

- Python 3.8 or higher
- Webcam/Camera
- Windows/Linux/MacOS

## Installation

1. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Install additional system dependencies (if needed):**

   For Windows:

   - Visual Studio Build Tools (for dlib compilation)

   For Linux:

   ```bash
   sudo apt-get update
   sudo apt-get install python3-opencv
   sudo apt-get install cmake
   sudo apt-get install libopenblas-dev liblapack-dev
   sudo apt-get install libx11-dev libgtk-3-dev
   ```

## Quick Start

### Method 1: Simple Command Line Interface

```bash
python simple_attendance.py
```

This provides an easy-to-use menu-driven interface with emojis and clear instructions.

### Method 2: Advanced Face Recognition

```bash
python advanced_face_recognition.py
```

Uses the `face_recognition` library for more accurate results.

### Method 3: Traditional OpenCV Approach

```bash
python face_recognition_system.py
```

Uses OpenCV's LBPH (Local Binary Pattern Histogram) face recognizer.

### Method 4: REST API Server

```bash
python api.py
```

Starts a FastAPI server at `http://localhost:8000` with the following endpoints:

- `POST /register-student` - Register a new student
- `POST /train-model` - Train the face recognition model
- `POST /mark-attendance` - Mark attendance using face recognition
- `GET /attendance-report` - Get attendance report
- `GET /students` - Get list of registered students
- `GET /attendance-stats` - Get attendance statistics

## Usage Flow

### 1. Register Students

- Run the system and select "Register New Student"
- Enter student details (ID, name, email)
- Position face in front of camera and capture 20-30 images
- Images are automatically saved in `training_images/[student_id]/` folder
- Student details are saved in `data/students.csv`

### 2. Train the Model

- Select "Train Face Recognition Model"
- System processes all captured images and creates a recognition model
- Model is saved for future use

### 3. Mark Attendance

- Select "Mark Attendance"
- Students position their faces in front of the camera
- System automatically recognizes faces and marks attendance
- Attendance records are saved in `data/attendance.csv`
- Prevents duplicate entries for the same day

### 4. View Reports

- View attendance reports by date
- View list of registered students
- Export data from CSV files

## File Structure

```
server/
├── requirements.txt                 # Python dependencies
├── simple_attendance.py            # Easy-to-use CLI interface
├── advanced_face_recognition.py    # Advanced face recognition
├── face_recognition_system.py      # Traditional OpenCV approach
├── api.py                          # REST API server
├── data/
│   ├── students.csv                # Student information
│   └── attendance.csv              # Attendance records
├── training_images/
│   └── [student_id]/               # Face images for each student
└── models/
    ├── trained_model.yml           # Trained OpenCV model
    └── face_encodings.pkl          # Face encodings (advanced method)
```

## API Documentation

Once the API server is running, visit `http://localhost:8000/docs` for interactive API documentation.

## Configuration

### Face Recognition Sensitivity

You can adjust the recognition sensitivity by modifying the confidence threshold:

```python
# In the recognition code, look for:
if confidence < 70:  # Lower values = more strict
```

### Minimum Training Images

Adjust the minimum number of training images required:

```python
target_images = 20  # Increase for better accuracy
```

## Troubleshooting

### Common Issues

1. **Camera not accessible:**

   - Check if camera is being used by another application
   - Try changing camera index: `cv2.VideoCapture(1)` instead of `cv2.VideoCapture(0)`

2. **No face detected during registration:**

   - Ensure good lighting
   - Position face clearly in front of camera
   - Check if camera is working properly

3. **Poor recognition accuracy:**

   - Capture more training images (30-50 per student)
   - Ensure consistent lighting during training and recognition
   - Adjust confidence threshold
   - Re-train the model with better quality images

4. **Installation issues:**
   - For dlib compilation issues on Windows, install Visual Studio Build Tools
   - For Linux, ensure all system dependencies are installed
   - Try using conda instead of pip for problematic packages

### Performance Tips

1. **Better Accuracy:**

   - Capture images in various lighting conditions
   - Include slight variations in face angles
   - Ensure high-quality camera
   - Regular model retraining with new images

2. **Faster Processing:**
   - Reduce image resolution for processing
   - Use GPU acceleration if available
   - Optimize confidence thresholds

## Security Considerations

- Store face images securely
- Implement proper authentication for API access
- Regular backup of attendance data
- Consider privacy regulations in your region

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review the code comments
3. Test with different lighting conditions
4. Ensure all dependencies are properly installed
