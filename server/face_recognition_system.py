import cv2
import os
import pandas as pd
import numpy as np
from datetime import datetime
import pickle
from PIL import Image

class FaceRecognitionSystem:
    def __init__(self):
        self.students_csv = "data/students.csv"
        self.attendance_csv = "data/attendance.csv"
        self.training_folder = "training_images"
        self.model_file = "models/face_model.yml"
        self.encodings_file = "models/face_encodings.pkl"
        
        # Create necessary directories
        os.makedirs("data", exist_ok=True)
        os.makedirs("training_images", exist_ok=True)
        os.makedirs("models", exist_ok=True)
        os.makedirs("temp_captures", exist_ok=True)
        
        # Initialize face recognizer
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        # Initialize CSV files if they don't exist
        self.init_csv_files()
        
    def init_csv_files(self):
        """Initialize CSV files with headers if they don't exist"""
        if not os.path.exists(self.students_csv):
            df = pd.DataFrame(columns=['student_id', 'name', 'email', 'registration_date'])
            df.to_csv(self.students_csv, index=False)
            
        if not os.path.exists(self.attendance_csv):
            df = pd.DataFrame(columns=['student_id', 'name', 'date', 'time', 'status'])
            df.to_csv(self.attendance_csv, index=False)
    
    def register_student(self, student_id, name, email):
        """Register a new student and capture their face images"""
        try:
            # Check if student already exists
            students_df = pd.read_csv(self.students_csv)
            if student_id in students_df['student_id'].values:
                return {"success": False, "message": "Student ID already exists"}
            
            # Create student folder
            student_folder = os.path.join(self.training_folder, str(student_id))
            os.makedirs(student_folder, exist_ok=True)
            
            # Capture face images
            captured = self.capture_face_images(student_id, student_folder)
            if not captured:
                return {"success": False, "message": "Failed to capture face images"}
            
            # Add student to CSV
            new_student = {
                'student_id': student_id,
                'name': name,
                'email': email,
                'registration_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            students_df = pd.concat([students_df, pd.DataFrame([new_student])], ignore_index=True)
            students_df.to_csv(self.students_csv, index=False)
            
            print(f"Student {name} registered successfully!")
            return {"success": True, "message": f"Student {name} registered successfully!"}
            
        except Exception as e:
            return {"success": False, "message": f"Error registering student: {str(e)}"}
    
    def capture_face_images(self, student_id, folder_path, num_images=30):
        """Capture face images for training"""
        cap = cv2.VideoCapture(0)
        count = 0
        
        print(f"Capturing images for Student ID: {student_id}")
        print("Look at the camera and press SPACE to capture images, ESC to cancel")
        
        while count < num_images:
            ret, frame = cap.read()
            if not ret:
                break
                
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                face_region = gray[y:y+h, x:x+w]
                
            cv2.putText(frame, f'Images captured: {count}/{num_images}', (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, 'Press SPACE to capture, ESC to cancel', (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow('Face Capture', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord(' '):  # Space key
                if len(faces) > 0:
                    face_img = gray[faces[0][1]:faces[0][1]+faces[0][3], 
                                  faces[0][0]:faces[0][0]+faces[0][2]]
                    img_name = f"{student_id}_{count}.jpg"
                    cv2.imwrite(os.path.join(folder_path, img_name), face_img)
                    count += 1
                    print(f"Image {count} captured")
                else:
                    print("No face detected, try again")
            elif key == 27:  # ESC key
                break
                
        cap.release()
        cv2.destroyAllWindows()
        
        return count >= 10  # Minimum 10 images required
    
    def train_model(self):
        """Train the face recognition model"""
        try:
            faces = []
            labels = []
            
            # Read all training images
            for student_folder in os.listdir(self.training_folder):
                student_id = int(student_folder)
                folder_path = os.path.join(self.training_folder, student_folder)
                
                for image_name in os.listdir(folder_path):
                    if image_name.endswith(('.jpg', '.jpeg', '.png')):
                        image_path = os.path.join(folder_path, image_name)
                        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                        
                        if image is not None:
                            faces.append(image)
                            labels.append(student_id)
            
            if len(faces) > 0:
                # Train the recognizer
                self.recognizer.train(faces, np.array(labels))
                self.recognizer.save(self.model_file)
                print(f"Model trained with {len(faces)} images")
                return {"success": True, "message": f"Model trained successfully with {len(faces)} images"}
            else:
                return {"success": False, "message": "No training images found"}
                
        except Exception as e:
            return {"success": False, "message": f"Error training model: {str(e)}"}
    
    def mark_attendance(self):
        """Mark attendance using face recognition"""
        try:
            # Load the trained model
            if not os.path.exists(self.model_file):
                return {"success": False, "message": "Model not trained yet. Please train the model first."}
            
            self.recognizer.read(self.model_file)
            
            # Load students data
            students_df = pd.read_csv(self.students_csv)
            
            cap = cv2.VideoCapture(0)
            attendance_marked = False
            recognized_student = None
            
            print("Face Recognition for Attendance")
            print("Position your face in front of the camera, press 'q' to quit")
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    face_region = gray[y:y+h, x:x+w]
                    
                    # Recognize face
                    student_id, confidence = self.recognizer.predict(face_region)
                    
                    # Check confidence (lower is better)
                    if confidence < 50:  # Adjust threshold as needed
                        student_info = students_df[students_df['student_id'] == student_id]
                        if not student_info.empty:
                            name = student_info.iloc[0]['name']
                            cv2.putText(frame, f'{name} (ID: {student_id})', (x, y-10), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                            cv2.putText(frame, f'Confidence: {round(100-confidence, 1)}%', (x, y+h+30), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                            
                            recognized_student = (student_id, name)
                        else:
                            cv2.putText(frame, 'Unknown', (x, y-10), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                    else:
                        cv2.putText(frame, 'Unknown', (x, y-10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                
                cv2.putText(frame, 'Press SPACE to mark attendance, Q to quit', (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.imshow('Face Recognition Attendance', frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord(' ') and recognized_student:  # Space to mark attendance
                    student_id, name = recognized_student
                    result = self.save_attendance(student_id, name)
                    print(result["message"])
                    attendance_marked = True
                    break
                elif key == ord('q'):
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            
            if attendance_marked:
                return {"success": True, "message": "Attendance marked successfully"}
            else:
                return {"success": False, "message": "No attendance marked"}
                
        except Exception as e:
            return {"success": False, "message": f"Error marking attendance: {str(e)}"}
    
    def save_attendance(self, student_id, name):
        """Save attendance record"""
        try:
            current_date = datetime.now().strftime('%Y-%m-%d')
            current_time = datetime.now().strftime('%H:%M:%S')
            
            # Check if attendance already marked today
            attendance_df = pd.read_csv(self.attendance_csv)
            today_attendance = attendance_df[
                (attendance_df['student_id'] == student_id) & 
                (attendance_df['date'] == current_date)
            ]
            
            if not today_attendance.empty:
                return {"success": False, "message": f"Attendance already marked for {name} today"}
            
            # Add new attendance record
            new_record = {
                'student_id': student_id,
                'name': name,
                'date': current_date,
                'time': current_time,
                'status': 'Present'
            }
            
            attendance_df = pd.concat([attendance_df, pd.DataFrame([new_record])], ignore_index=True)
            attendance_df.to_csv(self.attendance_csv, index=False)
            
            return {"success": True, "message": f"Attendance marked for {name} at {current_time}"}
            
        except Exception as e:
            return {"success": False, "message": f"Error saving attendance: {str(e)}"}
    
    def get_attendance_report(self, date=None):
        """Get attendance report for a specific date or all dates"""
        try:
            attendance_df = pd.read_csv(self.attendance_csv)
            
            if date:
                attendance_df = attendance_df[attendance_df['date'] == date]
            
            return attendance_df.to_dict('records')
            
        except Exception as e:
            print(f"Error getting attendance report: {str(e)}")
            return []
    
    def get_students_list(self):
        """Get list of all registered students"""
        try:
            students_df = pd.read_csv(self.students_csv)
            return students_df.to_dict('records')
        except Exception as e:
            print(f"Error getting students list: {str(e)}")
            return []


if __name__ == "__main__":
    system = FaceRecognitionSystem()
    
    while True:
        print("\n=== Face Recognition Attendance System ===")
        print("1. Register New Student")
        print("2. Train Model")
        print("3. Mark Attendance")
        print("4. View Attendance Report")
        print("5. View Students List")
        print("6. Exit")
        
        choice = input("Enter your choice (1-6): ")
        
        if choice == '1':
            student_id = input("Enter Student ID: ")
            name = input("Enter Student Name: ")
            email = input("Enter Student Email: ")
            
            try:
                student_id = int(student_id)
                result = system.register_student(student_id, name, email)
                print(result["message"])
            except ValueError:
                print("Please enter a valid numeric Student ID")
        
        elif choice == '2':
            print("Training model...")
            result = system.train_model()
            print(result["message"])
        
        elif choice == '3':
            result = system.mark_attendance()
            print(result["message"])
        
        elif choice == '4':
            date = input("Enter date (YYYY-MM-DD) or press Enter for all dates: ")
            if not date:
                date = None
            
            records = system.get_attendance_report(date)
            if records:
                print(f"\n{'Student ID':<12} {'Name':<20} {'Date':<12} {'Time':<10} {'Status':<10}")
                print("-" * 70)
                for record in records:
                    print(f"{record['student_id']:<12} {record['name']:<20} {record['date']:<12} {record['time']:<10} {record['status']:<10}")
            else:
                print("No attendance records found")
        
        elif choice == '5':
            students = system.get_students_list()
            if students:
                print(f"\n{'Student ID':<12} {'Name':<20} {'Email':<30} {'Registration Date':<20}")
                print("-" * 85)
                for student in students:
                    print(f"{student['student_id']:<12} {student['name']:<20} {student['email']:<30} {student['registration_date']:<20}")
            else:
                print("No students registered")
        
        elif choice == '6':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")
