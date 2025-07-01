"""
Complete Face Recognition Attendance System
Works on Windows without requiring Visual Studio Build Tools
Uses only OpenCV for face detection and recognition
"""

import cv2
import os
import pandas as pd
import numpy as np
from datetime import datetime
import pickle

class WindowsFaceRecognition:
    def __init__(self):
        # File paths
        self.students_csv = "data/students.csv"
        self.attendance_csv = "data/attendance.csv"
        self.training_folder = "training_images"
        self.model_file = "models/trained_model.yml"
        
        # Create directories
        self.create_directories()
        
        # Initialize face detection and recognition
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        # Create CSV files
        self.create_csv_files()
        
        print("✅ Face Recognition System initialized successfully!")
    
    def create_directories(self):
        """Create necessary directories"""
        directories = ["data", "training_images", "models", "temp_captures"]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def create_csv_files(self):
        """Create CSV files with proper headers"""
        if not os.path.exists(self.students_csv):
            df = pd.DataFrame(columns=['student_id', 'name', 'email', 'registration_date'])
            df.to_csv(self.students_csv, index=False)
        
        if not os.path.exists(self.attendance_csv):
            df = pd.DataFrame(columns=['student_id', 'name', 'date', 'time', 'status'])
            df.to_csv(self.attendance_csv, index=False)
    
    def register_student(self, student_id, name, email):
        """Register a new student and capture face images"""
        print(f"\n🎓 Registering Student: {name} (ID: {student_id})")
        
        # Check if student already exists
        try:
            students_df = pd.read_csv(self.students_csv)
            if student_id in students_df['student_id'].values:
                print("❌ Student ID already exists!")
                return False
        except:
            students_df = pd.DataFrame(columns=['student_id', 'name', 'email', 'registration_date'])
        
        # Create student directory
        student_dir = os.path.join(self.training_folder, str(student_id))
        os.makedirs(student_dir, exist_ok=True)
        
        # Capture face images
        print("📸 Starting face capture process...")
        if self.capture_faces(student_id, student_dir):
            # Add student to CSV
            new_student = pd.DataFrame({
                'student_id': [student_id],
                'name': [name],
                'email': [email],
                'registration_date': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
            })
            
            students_df = pd.concat([students_df, new_student], ignore_index=True)
            students_df.to_csv(self.students_csv, index=False)
            
            print(f"✅ Student {name} registered successfully!")
            print("💡 Remember to train the model before marking attendance!")
            return True
        else:
            print("❌ Failed to capture enough face images!")
            return False
    
    def capture_faces(self, student_id, save_dir, target_images=25):
        """Capture face images for training"""
        cap = cv2.VideoCapture(0)
        count = 0
        
        print(f"📸 Capturing face images for Student ID: {student_id}")
        print("📋 Instructions:")
        print("   👀 Look directly at the camera")
        print("   💡 Ensure good lighting")
        print("   ⌨️  Press SPACEBAR to capture images")
        print("   ❌ Press ESC to cancel")
        
        # Check if camera is working
        if not cap.isOpened():
            print("❌ Cannot access camera!")
            return False
        
        while count < target_images:
            ret, frame = cap.read()
            if not ret:
                print("❌ Cannot read from camera!")
                break
            
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(100, 100))
            
            # Draw rectangles around detected faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, f'Face Detected', (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Display progress and instructions
            cv2.putText(frame, f'Images Captured: {count}/{target_images}', (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(frame, 'SPACEBAR: Capture | ESC: Cancel', (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            if len(faces) > 0:
                cv2.putText(frame, 'Face Ready - Press SPACEBAR', (10, 110), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            else:
                cv2.putText(frame, 'No Face Detected', (10, 110), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            cv2.imshow('Face Capture', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 32:  # SPACEBAR
                if len(faces) > 0:
                    # Save the largest detected face
                    largest_face = max(faces, key=lambda face: face[2] * face[3])
                    x, y, w, h = largest_face
                    
                    # Extract face region
                    face_img = gray[y:y+h, x:x+w]
                    
                    # Resize to standard size for better recognition
                    face_img = cv2.resize(face_img, (200, 200))
                    
                    # Save image
                    filename = os.path.join(save_dir, f'{student_id}_{count:03d}.jpg')
                    cv2.imwrite(filename, face_img)
                    count += 1
                    
                    print(f"📸 Captured image {count}/{target_images}")
                    
                    # Brief pause to prevent multiple captures
                    cv2.waitKey(500)
                else:
                    print("⚠️  No face detected! Please position your face properly.")
                    
            elif key == 27:  # ESC key
                print("❌ Capture cancelled by user")
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        success = count >= 15  # Minimum 15 images required
        if success:
            print(f"✅ Successfully captured {count} images!")
        else:
            print(f"❌ Only captured {count} images. Minimum 15 required.")
        
        return success
    
    def train_model(self):
        """Train the face recognition model"""
        print("\n🔄 Training face recognition model...")
        
        faces = []
        labels = []
        student_count = 0
        
        # Check if training folder exists
        if not os.path.exists(self.training_folder):
            print("❌ No training images found!")
            return False
        
        # Load training images
        for student_folder in os.listdir(self.training_folder):
            if not student_folder.isdigit():
                continue
                
            student_id = int(student_folder)
            folder_path = os.path.join(self.training_folder, student_folder)
            
            if not os.path.isdir(folder_path):
                continue
            
            image_count = 0
            for image_file in os.listdir(folder_path):
                if image_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    image_path = os.path.join(folder_path, image_file)
                    
                    # Load image in grayscale
                    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                    if img is not None:
                        faces.append(img)
                        labels.append(student_id)
                        image_count += 1
            
            if image_count > 0:
                student_count += 1
                print(f"📁 Loaded {image_count} images for Student ID: {student_id}")
        
        if len(faces) == 0:
            print("❌ No training images found!")
            return False
        
        # Train the model
        print(f"🎯 Training model with {len(faces)} images from {student_count} students...")
        
        try:
            self.recognizer.train(faces, np.array(labels))
            
            # Save the model
            os.makedirs("models", exist_ok=True)
            self.recognizer.save(self.model_file)
            
            print("✅ Model trained and saved successfully!")
            print(f"📊 Training completed: {len(faces)} images, {student_count} students")
            return True
            
        except Exception as e:
            print(f"❌ Error training model: {str(e)}")
            return False
    
    def mark_attendance(self):
        """Mark attendance using face recognition"""
        print("\n👁️  Starting Face Recognition Attendance System")
        
        # Check if model exists
        if not os.path.exists(self.model_file):
            print("❌ No trained model found!")
            print("💡 Please train the model first using option 2")
            return
        
        # Load the trained model
        try:
            self.recognizer.read(self.model_file)
            print("✅ Model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading model: {str(e)}")
            return
        
        # Load student data
        try:
            students_df = pd.read_csv(self.students_csv)
            if students_df.empty:
                print("❌ No students registered!")
                return
            print(f"📚 Loaded {len(students_df)} registered students")
        except:
            print("❌ No students registered!")
            return
        
        # Start camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Cannot access camera!")
            return
        
        print("📷 Camera started successfully")
        print("📋 Instructions:")
        print("   👤 Position your face clearly in front of the camera")
        print("   ⏰ Attendance will be marked automatically when recognized")
        print("   ❌ Press 'Q' to quit")
        
        marked_today = set()
        recognition_frames = 0
        required_frames = 5  # Number of consecutive frames required for recognition
        last_recognized = None
        confidence_threshold = 70  # Adjust this value for sensitivity (lower = more strict)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Cannot read from camera!")
                break
            
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(100, 100))
            
            current_recognition = None
            
            for (x, y, w, h) in faces:
                # Draw rectangle around face
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                
                # Extract and resize face
                face_region = gray[y:y+h, x:x+w]
                face_region = cv2.resize(face_region, (200, 200))
                
                # Recognize face
                student_id, confidence = self.recognizer.predict(face_region)
                
                # Check if recognition is confident enough
                if confidence <= confidence_threshold:
                    # Find student info
                    student_info = students_df[students_df['student_id'] == student_id]
                    if not student_info.empty:
                        name = student_info.iloc[0]['name']
                        accuracy = round(100 - confidence, 1)
                        
                        # Display recognition info
                        cv2.putText(frame, f'{name}', (x, y-40), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                        cv2.putText(frame, f'ID: {student_id}', (x, y-10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        cv2.putText(frame, f'Confidence: {accuracy}%', (x, y+h+25), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        
                        current_recognition = (student_id, name)
                        
                        # Check if already marked today
                        if student_id in marked_today:
                            cv2.putText(frame, 'Already Marked Today', (x, y+h+50), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                        else:
                            cv2.putText(frame, 'Ready to Mark Attendance', (x, y+h+50), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    else:
                        cv2.putText(frame, 'Unknown Student', (x, y-10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                else:
                    cv2.putText(frame, 'Unknown Person', (x, y-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    cv2.putText(frame, f'Low Confidence: {round(100-confidence, 1)}%', (x, y+h+25), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            # Handle consecutive frame recognition
            if current_recognition and current_recognition == last_recognized:
                recognition_frames += 1
                if recognition_frames >= required_frames:
                    student_id, name = current_recognition
                    if student_id not in marked_today:
                        if self.save_attendance_record(student_id, name):
                            marked_today.add(student_id)
                            print(f"✅ Attendance marked for {name} (ID: {student_id})")
                        recognition_frames = 0
            else:
                recognition_frames = 0
                last_recognized = current_recognition
            
            # Display system info
            cv2.putText(frame, f'Marked Today: {len(marked_today)}', (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, 'Press Q to quit', (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            if current_recognition and current_recognition[0] not in marked_today:
                cv2.putText(frame, f'Recognition Progress: {recognition_frames}/{required_frames}', (10, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            cv2.imshow('Face Recognition Attendance', frame)
            
            # Check for quit key
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        print(f"\n📊 Attendance session completed!")
        print(f"✅ Total students marked present today: {len(marked_today)}")
        
        if len(marked_today) > 0:
            print("👥 Students marked present:")
            for student_id in marked_today:
                student_info = students_df[students_df['student_id'] == student_id]
                if not student_info.empty:
                    name = student_info.iloc[0]['name']
                    print(f"   • {name} (ID: {student_id})")
    
    def save_attendance_record(self, student_id, name):
        """Save attendance record to CSV"""
        try:
            current_date = datetime.now().strftime('%Y-%m-%d')
            current_time = datetime.now().strftime('%H:%M:%S')
            
            # Load existing attendance
            try:
                attendance_df = pd.read_csv(self.attendance_csv)
            except:
                attendance_df = pd.DataFrame(columns=['student_id', 'name', 'date', 'time', 'status'])
            
            # Check if already marked today
            today_records = attendance_df[
                (attendance_df['student_id'] == student_id) & 
                (attendance_df['date'] == current_date)
            ]
            
            if not today_records.empty:
                return False  # Already marked
            
            # Add new record
            new_record = pd.DataFrame({
                'student_id': [student_id],
                'name': [name],
                'date': [current_date],
                'time': [current_time],
                'status': ['Present']
            })
            
            attendance_df = pd.concat([attendance_df, new_record], ignore_index=True)
            attendance_df.to_csv(self.attendance_csv, index=False)
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving attendance: {e}")
            return False
    
    def show_attendance_report(self, date=None):
        """Display attendance report"""
        try:
            attendance_df = pd.read_csv(self.attendance_csv)
            
            if attendance_df.empty:
                print("📭 No attendance records found!")
                return
            
            if date:
                attendance_df = attendance_df[attendance_df['date'] == date]
                print(f"\n📊 Attendance Report for {date}")
            else:
                print("\n📊 Complete Attendance Report")
            
            if attendance_df.empty:
                print("📭 No records found for the specified date!")
                return
            
            print("=" * 80)
            print(f"{'ID':<8} {'Name':<20} {'Date':<12} {'Time':<10} {'Status':<10}")
            print("=" * 80)
            
            for _, record in attendance_df.iterrows():
                print(f"{record['student_id']:<8} {record['name']:<20} {record['date']:<12} {record['time']:<10} {record['status']:<10}")
            
            print("=" * 80)
            print(f"📈 Total Records: {len(attendance_df)}")
            
            # Show statistics if showing all records
            if date is None:
                unique_students = len(attendance_df['student_id'].unique())
                unique_dates = len(attendance_df['date'].unique())
                print(f"👥 Unique Students: {unique_students}")
                print(f"📅 Unique Dates: {unique_dates}")
            
        except Exception as e:
            print(f"❌ Error reading attendance: {e}")
    
    def show_students_list(self):
        """Display registered students"""
        try:
            students_df = pd.read_csv(self.students_csv)
            
            if students_df.empty:
                print("📭 No students registered!")
                return
            
            print("\n👥 Registered Students")
            print("=" * 90)
            print(f"{'ID':<8} {'Name':<20} {'Email':<30} {'Registration Date':<20}")
            print("=" * 90)
            
            for _, student in students_df.iterrows():
                print(f"{student['student_id']:<8} {student['name']:<20} {student['email']:<30} {student['registration_date']:<20}")
            
            print("=" * 90)
            print(f"📈 Total Students: {len(students_df)}")
            
        except Exception as e:
            print(f"❌ Error reading students: {e}")
    
    def test_camera(self):
        """Test camera functionality"""
        print("\n📷 Testing camera...")
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Cannot access camera!")
            print("💡 Troubleshooting tips:")
            print("   • Make sure no other application is using the camera")
            print("   • Try unplugging and reconnecting the camera")
            print("   • Check camera drivers")
            return False
        
        print("✅ Camera is working!")
        print("📋 Press any key to close the test window...")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Cannot read from camera!")
                break
            
            # Add some text to the frame
            cv2.putText(frame, 'Camera Test - Press any key to exit', (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f'Resolution: {frame.shape[1]}x{frame.shape[0]}', (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            cv2.imshow('Camera Test', frame)
            
            if cv2.waitKey(1) & 0xFF != 255:  # Any key pressed
                break
        
        cap.release()
        cv2.destroyAllWindows()
        print("✅ Camera test completed!")
        return True


def main():
    """Main function to run the attendance system"""
    print("🎓 Welcome to Face Recognition Attendance System")
    print("🖥️  Windows Compatible Version")
    print("=" * 60)
    
    try:
        system = WindowsFaceRecognition()
    except Exception as e:
        print(f"❌ Error initializing system: {e}")
        return
    
    while True:
        print("\n📋 MAIN MENU:")
        print("1️⃣  Register New Student")
        print("2️⃣  Train Face Recognition Model")
        print("3️⃣  Mark Attendance")
        print("4️⃣  View Attendance Report")
        print("5️⃣  View Students List")
        print("6️⃣  Test Camera")
        print("7️⃣  Exit")
        print("-" * 40)
        
        try:
            choice = input("🔢 Enter your choice (1-7): ").strip()
            
            if choice == '1':
                print("\n📝 STUDENT REGISTRATION")
                print("-" * 30)
                
                try:
                    student_id = int(input("👤 Student ID (number): "))
                    name = input("📛 Student Name: ").strip()
                    email = input("📧 Student Email: ").strip()
                    
                    if not name or not email:
                        print("❌ Name and email cannot be empty!")
                        continue
                    
                    system.register_student(student_id, name, email)
                    
                except ValueError:
                    print("❌ Please enter a valid numeric Student ID!")
                except Exception as e:
                    print(f"❌ Error during registration: {e}")
            
            elif choice == '2':
                system.train_model()
            
            elif choice == '3':
                system.mark_attendance()
            
            elif choice == '4':
                print("\n📊 ATTENDANCE REPORT")
                print("-" * 30)
                date_input = input("📅 Enter date (YYYY-MM-DD) or press Enter for all dates: ").strip()
                date = date_input if date_input else None
                system.show_attendance_report(date)
            
            elif choice == '5':
                system.show_students_list()
            
            elif choice == '6':
                system.test_camera()
            
            elif choice == '7':
                print("👋 Thank you for using Face Recognition Attendance System!")
                print("🎯 Have a great day!")
                break
            
            else:
                print("❌ Invalid choice! Please select 1-7.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ An unexpected error occurred: {e}")
            print("💡 Please try again or restart the system.")


if __name__ == "__main__":
    main()
