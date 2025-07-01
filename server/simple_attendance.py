#!/usr/bin/env python3
"""
Simple Face Recognition Attendance System
This script provides a streamlined approach to face recognition attendance
"""

import cv2
import os
import pandas as pd
import numpy as np
from datetime import datetime

class SimpleFaceAttendance:
    def __init__(self):
        # File paths
        self.students_csv = "data/students.csv"
        self.attendance_csv = "data/attendance.csv"
        self.training_folder = "training_images"
        
        # Create directories
        os.makedirs("data", exist_ok=True)
        os.makedirs(self.training_folder, exist_ok=True)
        
        # Initialize face detection
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        # Create CSV files if they don't exist
        self.create_csv_files()
    
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
        print(f"\n--- Registering Student: {name} (ID: {student_id}) ---")
        
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
            return True
        else:
            print("❌ Failed to capture face images!")
            return False
    
    def capture_faces(self, student_id, save_dir, target_images=20):
        """Capture face images for training"""
        cap = cv2.VideoCapture(0)
        count = 0
        
        print(f"📸 Capturing face images for Student ID: {student_id}")
        print("👤 Look at the camera and press SPACE to capture images")
        print("❌ Press ESC to cancel")
        
        while count < target_images:
            ret, frame = cap.read()
            if not ret:
                print("❌ Cannot access camera!")
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            # Draw rectangles around faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Display progress
            cv2.putText(frame, f'Images: {count}/{target_images}', (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, 'SPACE: Capture | ESC: Cancel', (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow('Face Capture', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 32:  # SPACE key
                if len(faces) > 0:
                    # Save the largest face
                    largest_face = max(faces, key=lambda face: face[2] * face[3])
                    x, y, w, h = largest_face
                    face_img = gray[y:y+h, x:x+w]
                    
                    filename = os.path.join(save_dir, f'{student_id}_{count:03d}.jpg')
                    cv2.imwrite(filename, face_img)
                    count += 1
                    print(f"📸 Captured image {count}/{target_images}")
                else:
                    print("⚠️  No face detected! Please position your face properly.")
            elif key == 27:  # ESC key
                print("❌ Capture cancelled by user")
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        return count >= 10  # Minimum 10 images required
    
    def train_model(self):
        """Train the face recognition model"""
        print("\n🔄 Training face recognition model...")
        
        faces = []
        labels = []
        
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
                    
                    # Load image
                    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                    if img is not None:
                        faces.append(img)
                        labels.append(student_id)
                        image_count += 1
            
            print(f"📁 Loaded {image_count} images for Student ID: {student_id}")
        
        if len(faces) == 0:
            print("❌ No training images found!")
            return False
        
        # Train the model
        print(f"🎯 Training model with {len(faces)} images...")
        self.recognizer.train(faces, np.array(labels))
        
        # Save the model
        model_path = "models/trained_model.yml"
        os.makedirs("models", exist_ok=True)
        self.recognizer.save(model_path)
        
        print("✅ Model trained and saved successfully!")
        return True
    
    def mark_attendance(self):
        """Mark attendance using face recognition"""
        model_path = "models/trained_model.yml"
        
        if not os.path.exists(model_path):
            print("❌ No trained model found! Please train the model first.")
            return
        
        # Load the trained model
        self.recognizer.read(model_path)
        
        # Load student data
        try:
            students_df = pd.read_csv(self.students_csv)
        except:
            print("❌ No students registered!")
            return
        
        cap = cv2.VideoCapture(0)
        print("\n👁️  Face Recognition Attendance System")
        print("📷 Position your face in front of the camera")
        print("✅ Press SPACE to mark attendance | ❌ Press Q to quit")
        
        marked_today = set()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                
                face_region = gray[y:y+h, x:x+w]
                student_id, confidence = self.recognizer.predict(face_region)
                
                # Check if recognition is confident enough
                if confidence < 70:  # Adjust threshold as needed
                    student_info = students_df[students_df['student_id'] == student_id]
                    if not student_info.empty:
                        name = student_info.iloc[0]['name']
                        accuracy = round(100 - confidence, 1)
                        
                        # Display student info
                        cv2.putText(frame, f'{name}', (x, y-10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                        cv2.putText(frame, f'Accuracy: {accuracy}%', (x, y+h+25), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        
                        # Auto-mark attendance for high accuracy
                        if accuracy > 80 and student_id not in marked_today:
                            if self.save_attendance_record(student_id, name):
                                marked_today.add(student_id)
                                print(f"✅ Attendance marked for {name}")
                    else:
                        cv2.putText(frame, 'Unknown Student', (x, y-10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                else:
                    cv2.putText(frame, 'Unknown', (x, y-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            # Display instructions
            cv2.putText(frame, f'Marked today: {len(marked_today)}', (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, 'Press Q to quit', (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow('Attendance System', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        print(f"\n📊 Attendance session completed! {len(marked_today)} students marked present.")
    
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
                print(f"⚠️  {name} already marked present today!")
                return False
            
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
            
            if date:
                attendance_df = attendance_df[attendance_df['date'] == date]
                print(f"\n📊 Attendance Report for {date}")
            else:
                print("\n📊 Complete Attendance Report")
            
            if attendance_df.empty:
                print("📭 No attendance records found!")
                return
            
            print("=" * 80)
            print(f"{'ID':<8} {'Name':<20} {'Date':<12} {'Time':<10} {'Status':<10}")
            print("=" * 80)
            
            for _, record in attendance_df.iterrows():
                print(f"{record['student_id']:<8} {record['name']:<20} {record['date']:<12} {record['time']:<10} {record['status']:<10}")
            
            print("=" * 80)
            print(f"📈 Total Records: {len(attendance_df)}")
            
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
            print("=" * 85)
            print(f"{'ID':<8} {'Name':<20} {'Email':<30} {'Registration Date':<20}")
            print("=" * 85)
            
            for _, student in students_df.iterrows():
                print(f"{student['student_id']:<8} {student['name']:<20} {student['email']:<30} {student['registration_date']:<20}")
            
            print("=" * 85)
            print(f"📈 Total Students: {len(students_df)}")
            
        except Exception as e:
            print(f"❌ Error reading students: {e}")


def main():
    """Main function to run the attendance system"""
    system = SimpleFaceAttendance()
    
    print("🎓 Welcome to Face Recognition Attendance System")
    print("=" * 60)
    
    while True:
        print("\n📋 MENU OPTIONS:")
        print("1️⃣  Register New Student")
        print("2️⃣  Train Face Recognition Model")
        print("3️⃣  Mark Attendance")
        print("4️⃣  View Attendance Report")
        print("5️⃣  View Students List")
        print("6️⃣  Exit")
        print("-" * 40)
        
        try:
            choice = input("🔢 Enter your choice (1-6): ").strip()
            
            if choice == '1':
                print("\n📝 STUDENT REGISTRATION")
                student_id = int(input("👤 Student ID: "))
                name = input("📛 Student Name: ").strip()
                email = input("📧 Student Email: ").strip()
                
                if name and email:
                    system.register_student(student_id, name, email)
                else:
                    print("❌ Name and email cannot be empty!")
            
            elif choice == '2':
                system.train_model()
            
            elif choice == '3':
                system.mark_attendance()
            
            elif choice == '4':
                date_input = input("📅 Enter date (YYYY-MM-DD) or press Enter for all dates: ").strip()
                date = date_input if date_input else None
                system.show_attendance_report(date)
            
            elif choice == '5':
                system.show_students_list()
            
            elif choice == '6':
                print("👋 Thank you for using Face Recognition Attendance System!")
                break
            
            else:
                print("❌ Invalid choice! Please select 1-6.")
                
        except ValueError:
            print("❌ Please enter a valid number!")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ An error occurred: {e}")


if __name__ == "__main__":
    main()
