import cv2
import numpy as np
import face_recognition
import os
import pandas as pd
from datetime import datetime
import pickle

class AdvancedFaceRecognition:
    def __init__(self):
        self.students_csv = "data/students.csv"
        self.attendance_csv = "data/attendance.csv"
        self.training_folder = "training_images"
        self.encodings_file = "models/face_encodings.pkl"
        
        # Create necessary directories
        os.makedirs("data", exist_ok=True)
        os.makedirs("training_images", exist_ok=True)
        os.makedirs("models", exist_ok=True)
        
        # Initialize known face encodings
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_ids = []
        
        # Initialize CSV files
        self.init_csv_files()
        
        # Load existing encodings if available
        self.load_encodings()
    
    def init_csv_files(self):
        """Initialize CSV files with headers if they don't exist"""
        if not os.path.exists(self.students_csv):
            df = pd.DataFrame(columns=['student_id', 'name', 'email', 'registration_date'])
            df.to_csv(self.students_csv, index=False)
            
        if not os.path.exists(self.attendance_csv):
            df = pd.DataFrame(columns=['student_id', 'name', 'date', 'time', 'status'])
            df.to_csv(self.attendance_csv, index=False)
    
    def register_student_with_image(self, student_id, name, email, image_path):
        """Register a student with a single image"""
        try:
            # Check if student already exists
            students_df = pd.read_csv(self.students_csv)
            if student_id in students_df['student_id'].values:
                return {"success": False, "message": "Student ID already exists"}
            
            # Load and encode the face
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(image)
            
            if len(face_encodings) == 0:
                return {"success": False, "message": "No face found in the image"}
            
            # Use the first face found
            face_encoding = face_encodings[0]
            
            # Create student folder and save encoding
            student_folder = os.path.join(self.training_folder, str(student_id))
            os.makedirs(student_folder, exist_ok=True)
            
            # Save the original image
            import shutil
            shutil.copy2(image_path, os.path.join(student_folder, f"{student_id}_original.jpg"))
            
            # Add to known faces
            self.known_face_encodings.append(face_encoding)
            self.known_face_names.append(name)
            self.known_face_ids.append(student_id)
            
            # Save encodings to file
            self.save_encodings()
            
            # Add student to CSV
            new_student = {
                'student_id': student_id,
                'name': name,
                'email': email,
                'registration_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            students_df = pd.concat([students_df, pd.DataFrame([new_student])], ignore_index=True)
            students_df.to_csv(self.students_csv, index=False)
            
            return {"success": True, "message": f"Student {name} registered successfully!"}
            
        except Exception as e:
            return {"success": False, "message": f"Error registering student: {str(e)}"}
    
    def save_encodings(self):
        """Save face encodings to pickle file"""
        try:
            encodings_data = {
                'encodings': self.known_face_encodings,
                'names': self.known_face_names,
                'ids': self.known_face_ids
            }
            with open(self.encodings_file, 'wb') as f:
                pickle.dump(encodings_data, f)
        except Exception as e:
            print(f"Error saving encodings: {str(e)}")
    
    def load_encodings(self):
        """Load face encodings from pickle file"""
        try:
            if os.path.exists(self.encodings_file):
                with open(self.encodings_file, 'rb') as f:
                    encodings_data = pickle.load(f)
                    self.known_face_encodings = encodings_data['encodings']
                    self.known_face_names = encodings_data['names']
                    self.known_face_ids = encodings_data['ids']
                print(f"Loaded {len(self.known_face_encodings)} face encodings")
        except Exception as e:
            print(f"Error loading encodings: {str(e)}")
    
    def mark_attendance_from_camera(self):
        """Mark attendance using live camera feed"""
        try:
            if len(self.known_face_encodings) == 0:
                return {"success": False, "message": "No registered students found. Please register students first."}
            
            cap = cv2.VideoCapture(0)
            attendance_marked = set()  # To track which students have been marked
            
            print("Face Recognition for Attendance - Press 'q' to quit")
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Resize frame for faster processing
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                
                # Find faces in the frame
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                
                for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                    # Scale back up face locations
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4
                    
                    # Check if face matches any known face
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.6)
                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                    
                    best_match_index = np.argmin(face_distances)
                    
                    if matches[best_match_index] and face_distances[best_match_index] < 0.6:
                        name = self.known_face_names[best_match_index]
                        student_id = self.known_face_ids[best_match_index]
                        confidence = round((1 - face_distances[best_match_index]) * 100, 1)
                        
                        # Draw rectangle and label
                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
                        cv2.putText(frame, f"{name} ({confidence}%)", (left + 6, bottom - 6), 
                                   cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
                        
                        # Auto-mark attendance if confidence is high enough
                        if confidence > 75 and student_id not in attendance_marked:
                            result = self.save_attendance(student_id, name)
                            if result["success"]:
                                attendance_marked.add(student_id)
                                print(f"✓ {result['message']}")
                            else:
                                print(f"✗ {result['message']}")
                    else:
                        # Unknown face
                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                        cv2.putText(frame, "Unknown", (left + 6, bottom - 6), 
                                   cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
                
                # Display instructions
                cv2.putText(frame, f"Attendance marked: {len(attendance_marked)}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, "Press 'q' to quit", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                cv2.imshow('Face Recognition Attendance', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            
            return {"success": True, "message": f"Attendance session completed. {len(attendance_marked)} students marked present."}
            
        except Exception as e:
            return {"success": False, "message": f"Error during attendance marking: {str(e)}"}
    
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
        """Get attendance report"""
        try:
            attendance_df = pd.read_csv(self.attendance_csv)
            if date:
                attendance_df = attendance_df[attendance_df['date'] == date]
            return attendance_df.to_dict('records')
        except Exception as e:
            print(f"Error getting attendance report: {str(e)}")
            return []
    
    def get_students_list(self):
        """Get list of registered students"""
        try:
            students_df = pd.read_csv(self.students_csv)
            return students_df.to_dict('records')
        except Exception as e:
            print(f"Error getting students list: {str(e)}")
            return []


if __name__ == "__main__":
    system = AdvancedFaceRecognition()
    
    while True:
        print("\n=== Advanced Face Recognition Attendance System ===")
        print("1. Register Student with Image")
        print("2. Mark Attendance (Camera)")
        print("3. View Attendance Report")
        print("4. View Students List")
        print("5. Exit")
        
        choice = input("Enter your choice (1-5): ")
        
        if choice == '1':
            student_id = input("Enter Student ID: ")
            name = input("Enter Student Name: ")
            email = input("Enter Student Email: ")
            image_path = input("Enter path to student's image: ")
            
            try:
                student_id = int(student_id)
                if os.path.exists(image_path):
                    result = system.register_student_with_image(student_id, name, email, image_path)
                    print(result["message"])
                else:
                    print("Image file not found!")
            except ValueError:
                print("Please enter a valid numeric Student ID")
        
        elif choice == '2':
            result = system.mark_attendance_from_camera()
            print(result["message"])
        
        elif choice == '3':
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
        
        elif choice == '4':
            students = system.get_students_list()
            if students:
                print(f"\n{'Student ID':<12} {'Name':<20} {'Email':<30} {'Registration Date':<20}")
                print("-" * 85)
                for student in students:
                    print(f"{student['student_id']:<12} {student['name']:<20} {student['email']:<30} {student['registration_date']:<20}")
            else:
                print("No students registered")
        
        elif choice == '5':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")
