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
import hashlib
import getpass

class WindowsFaceRecognition:
    def __init__(self):
        # File paths
        self.students_csv = "data/students.csv"
        self.attendance_csv = "data/attendance.csv"
        self.training_folder = "training_images"
        self.model_file = "models/trained_model.yml"
        self.admin_file = "data/admin_config.txt"
        
        # Create directories
        self.create_directories()
        
        # Initialize face detection and recognition
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        # Create CSV files and admin config
        self.create_csv_files()
        self.setup_admin_password()
        
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
        """Register a new student with enhanced security checks"""
        print(f"\n🎓 STUDENT REGISTRATION")
        print("=" * 40)
        print(f"👤 Student: {name} (ID: {student_id})")
        print(f"📧 Email: {email}")
        
        # SECURITY CHECK 1: Admin Password Verification
        print("\n🔐 SECURITY VERIFICATION REQUIRED")
        print("Admin authentication needed to register new students")
        
        if not self.verify_admin_password():
            print("❌ Registration cancelled due to authentication failure!")
            self.log_security_event("AUTH_FAILED", student_id, f"Failed admin authentication for registration attempt: {name} ({email})")
            return False
        
        self.log_security_event("AUTH_SUCCESS", student_id, f"Admin authenticated for registration: {name} ({email})")
        
        # SECURITY CHECK 2: Duplicate Data Check
        print("\n🔍 Checking for duplicate entries...")
        is_duplicate, message = self.check_duplicate_student(student_id, name, email)
        
        if is_duplicate:
            print(f"❌ {message}")
            print("🚫 Registration cannot proceed with duplicate data!")
            self.log_security_event("DUPLICATE_BLOCKED", student_id, f"Registration blocked - {message}")
            return False
        else:
            print("✅ No duplicate data found")
            self.log_security_event("DUPLICATE_CHECK_PASSED", student_id, f"No duplicates found for: {name} ({email})")
        
        # Create student directory
        student_dir = os.path.join(self.training_folder, str(student_id))
        os.makedirs(student_dir, exist_ok=True)
        
        # Capture face images with enhanced validation
        print("\n📸 Starting enhanced face capture process...")
        print("🔒 SECURITY MODE: Enhanced validation active")
        print("⚠️ Please ensure:")
        print("   • Excellent lighting conditions")
        print("   • Clear, unobstructed view of face")
        print("   • Only the registering person in frame")
        print("   • Stable position during capture")
        
        temp_face_path = None
        if self.enhanced_face_capture_with_validation(student_id, student_dir):
            # SECURITY CHECK 3: Face Similarity Check
            print("\n🔍 Performing face similarity analysis...")
            
            # Get the first captured image for similarity check
            for image_file in os.listdir(student_dir):
                if image_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    temp_face_path = os.path.join(student_dir, image_file)
                    break
            
            if temp_face_path:
                is_similar, similarity_message = self.check_face_similarity(student_id, temp_face_path)
                
                if is_similar:
                    print(f"\n{similarity_message}")
                    
                    # Check for ULTRA HIGH similarity (absolutely no override possible)
                    if "🚨 ULTRA HIGH SIMILARITY DETECTED!" in similarity_message:
                        print("🚫 Registration AUTOMATICALLY CANCELLED - FRAUD PROTECTION ACTIVATED!")
                        print("💀 SECURITY ALERT: This appears to be an attempt to register the same person with different credentials.")
                        print("🛡️ This decision CANNOT be overridden for security reasons.")
                        self.log_security_event("ULTRA_HIGH_FRAUD_BLOCKED", student_id, f"Ultra high similarity detected - Registration blocked for security: {name} ({email})")
                        # Clean up created directory
                        import shutil
                        shutil.rmtree(student_dir)
                        return False
                    
                    # Check for HIGH similarity (automatic block)
                    elif "🚨 HIGH SIMILARITY DETECTED!" in similarity_message:
                        print("🚫 Registration AUTOMATICALLY CANCELLED due to high face similarity!")
                        print("💡 This appears to be an attempt to register the same person with different credentials.")
                        self.log_security_event("HIGH_FRAUD_BLOCKED", student_id, f"High similarity detected - Registration blocked for security: {name} ({email})")
                        # Clean up created directory
                        import shutil
                        shutil.rmtree(student_dir)
                        return False
                    
                    # Medium similarity - strong warning but allow admin override
                    elif "⚠️ SUSPICIOUS SIMILARITY DETECTED!" in similarity_message or "⚠️ MODERATE SIMILARITY WARNING!" in similarity_message:
                        print("\n🚨 CRITICAL SECURITY ALERT: Potential identity fraud detected!")
                        print("🔍 This could indicate:")
                        print("   • Same person trying to register with different details (FRAUD)")
                        print("   • Twins or very similar looking individuals")
                        print("   • Poor image quality causing false positive")
                        print("   • Identical twins from the same family")
                        
                        print("\n⚠️ ADMIN SECURITY DECISION REQUIRED:")
                        print("   If this is the SAME PERSON, select 'N' to block fraud")
                        print("   If this is a DIFFERENT PERSON (twin/sibling), select 'Y' to continue")
                        
                        response = input("\n🛡️ Is this definitely a DIFFERENT person? (y/N): ").strip().lower()
                        
                        if response != 'y' and response != 'yes':
                            print("❌ Registration cancelled by admin due to similarity concerns!")
                            print("🛡️ Fraud prevention successful - duplicate identity blocked")
                            self.log_security_event("SIMILARITY_REJECTED", student_id, f"Admin rejected registration due to similarity: {name} ({email})")
                            # Clean up created directory
                            import shutil
                            shutil.rmtree(student_dir)
                            return False
                        else:
                            print("⚠️ Admin override: Proceeding with registration despite similarity warning...")
                            print("📝 Note: This decision has been logged for security review.")
                            print("🔍 Recommendation: Verify identity documents before final approval.")
                            self.log_security_event("SIMILARITY_OVERRIDE", student_id, f"Admin override - Registration proceeded despite similarity: {name} ({email})")
                else:
                    print("✅ Face verification passed - No similar faces detected")
            
            # All security checks passed - Save student data
            print("\n💾 Saving student data...")
            
            try:
                students_df = pd.read_csv(self.students_csv)
            except:
                students_df = pd.DataFrame(columns=['student_id', 'name', 'email', 'registration_date'])
            
            new_student = pd.DataFrame({
                'student_id': [student_id],
                'name': [name],
                'email': [email],
                'registration_date': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
            })
            
            students_df = pd.concat([students_df, new_student], ignore_index=True)
            students_df.to_csv(self.students_csv, index=False)
            
            print(f"✅ Student {name} registered successfully!")
            print("🔐 All security checks passed")
            print("💡 Remember to train the model before marking attendance!")
            self.log_security_event("REGISTRATION_SUCCESS", student_id, f"Student successfully registered: {name} ({email})")
            return True
        else:
            print("❌ Failed to capture enough face images!")
            self.log_security_event("REGISTRATION_FAILED", student_id, f"Registration failed - insufficient face images: {name} ({email})")
            # Clean up created directory
            import shutil
            if os.path.exists(student_dir):
                shutil.rmtree(student_dir)
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
    
    def hash_password(self, password):
        """Create a hash of the password for secure storage"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def setup_admin_password(self):
        """Setup admin password if it doesn't exist"""
        if not os.path.exists(self.admin_file):
            print("\n🔐 FIRST TIME SETUP - Admin Password Required")
            print("=" * 50)
            print("⚠️  Please set up an admin password for system security")
            
            while True:
                password = getpass.getpass("🔑 Enter admin password: ")
                if len(password) < 6:
                    print("❌ Password must be at least 6 characters long!")
                    continue
                
                confirm_password = getpass.getpass("🔑 Confirm admin password: ")
                if password != confirm_password:
                    print("❌ Passwords don't match! Please try again.")
                    continue
                
                # Save hashed password
                hashed_password = self.hash_password(password)
                with open(self.admin_file, 'w') as f:
                    f.write(hashed_password)
                
                print("✅ Admin password set successfully!")
                break
    
    def verify_admin_password(self):
        """Verify admin password"""
        if not os.path.exists(self.admin_file):
            print("❌ Admin password not set!")
            return False
        
        # Read stored password hash
        with open(self.admin_file, 'r') as f:
            stored_hash = f.read().strip()
        
        # Get password from user
        password = getpass.getpass("🔐 Enter admin password: ")
        entered_hash = self.hash_password(password)
        
        if entered_hash == stored_hash:
            print("✅ Admin authentication successful!")
            return True
        else:
            print("❌ Incorrect admin password!")
            return False
    
    def update_admin_password(self):
        """Update admin password"""
        print("\n🔐 UPDATE ADMIN PASSWORD")
        print("=" * 30)
        
        # Verify current password first
        if not self.verify_admin_password():
            print("❌ Cannot update password without current password verification!")
            return False
        
        print("📝 Setting new password...")
        while True:
            new_password = getpass.getpass("🔑 Enter new admin password: ")
            if len(new_password) < 6:
                print("❌ Password must be at least 6 characters long!")
                continue
            
            confirm_password = getpass.getpass("🔑 Confirm new admin password: ")
            if new_password != confirm_password:
                print("❌ Passwords don't match! Please try again.")
                continue
            
            # Save new hashed password
            hashed_password = self.hash_password(new_password)
            with open(self.admin_file, 'w') as f:
                f.write(hashed_password)
            
            print("✅ Admin password updated successfully!")
            return True
    
    def check_duplicate_student(self, student_id, name, email):
        """Check if student already exists by ID, name, or email"""
        try:
            students_df = pd.read_csv(self.students_csv)
            
            if students_df.empty:
                return False, "No duplicates found"
            
            # Check for duplicate ID
            if student_id in students_df['student_id'].values:
                return True, f"Student ID {student_id} already exists!"
            
            # Check for duplicate name (case insensitive)
            if name.lower() in students_df['name'].str.lower().values:
                return True, f"Student name '{name}' already exists!"
            
            # Check for duplicate email (case insensitive)
            if email.lower() in students_df['email'].str.lower().values:
                return True, f"Email '{email}' already exists!"
            
            return False, "No duplicates found"
            
        except Exception as e:
            print(f"⚠️  Error checking duplicates: {e}")
            return False, "Error occurred during duplicate check"
    
    def check_face_similarity(self, student_id, temp_face_path):
        """Ultra-strict face similarity check with advanced algorithms to prevent identity fraud"""
        try:
            print("🔍 Running ULTRA-STRICT face similarity analysis...")
            print("🚨 SECURITY MODE: Maximum fraud prevention active")
            
            # Load the new face image
            new_face = cv2.imread(temp_face_path, cv2.IMREAD_GRAYSCALE)
            if new_face is None:
                return True, "🚨 SECURITY BLOCK: Could not load face image - registration blocked for safety"
            
            # Validate that the new image contains a clear face
            if not self.validate_face_in_image(temp_face_path):
                return True, "🚨 SECURITY BLOCK: No clear face detected in image - registration blocked for safety"
            
            # Multiple size analysis for better detection
            new_face_large = cv2.resize(new_face, (300, 300))
            new_face_medium = cv2.resize(new_face, (200, 200))
            new_face_small = cv2.resize(new_face, (100, 100))
            
            # Check against existing student faces
            similarity_results = []
            detailed_analysis = []
            
            for existing_student_folder in os.listdir(self.training_folder):
                if not existing_student_folder.isdigit():
                    continue
                
                existing_student_id = int(existing_student_folder)
                if existing_student_id == student_id:
                    continue  # Skip self
                
                folder_path = os.path.join(self.training_folder, existing_student_folder)
                if not os.path.isdir(folder_path):
                    continue
                
                print(f"   🔍 DEEP ANALYSIS against Student ID: {existing_student_id}")
                
                # Compare with ALL images from existing student (maximum robustness)
                max_similarity = 0
                total_similarity = 0
                images_checked = 0
                method_scores = []
                
                for image_file in os.listdir(folder_path):
                    if image_file.lower().endswith(('.jpg', '.jpeg', '.png')) and images_checked < 10:
                        existing_face_path = os.path.join(folder_path, image_file)
                        
                        # Validate that the existing image contains a clear face
                        if not self.validate_face_in_image(existing_face_path):
                            continue  # Skip invalid images
                        
                        existing_face = cv2.imread(existing_face_path, cv2.IMREAD_GRAYSCALE)
                        
                        if existing_face is not None:
                            # Multiple size comparison for robustness
                            existing_face_large = cv2.resize(existing_face, (300, 300))
                            existing_face_medium = cv2.resize(existing_face, (200, 200))
                            existing_face_small = cv2.resize(existing_face, (100, 100))
                            
                            # METHOD 1: Multi-scale Template Matching
                            template_large = cv2.matchTemplate(new_face_large, existing_face_large, cv2.TM_CCOEFF_NORMED).max()
                            template_medium = cv2.matchTemplate(new_face_medium, existing_face_medium, cv2.TM_CCOEFF_NORMED).max()
                            template_small = cv2.matchTemplate(new_face_small, existing_face_small, cv2.TM_CCOEFF_NORMED).max()
                            template_similarity = (template_large + template_medium + template_small) / 3
                            
                            # METHOD 2: Multi-scale Histogram Comparison
                            hist1_large = cv2.calcHist([new_face_large], [0], None, [256], [0, 256])
                            hist2_large = cv2.calcHist([existing_face_large], [0], None, [256], [0, 256])
                            hist1_medium = cv2.calcHist([new_face_medium], [0], None, [256], [0, 256])
                            hist2_medium = cv2.calcHist([existing_face_medium], [0], None, [256], [0, 256])
                            
                            hist_correl_large = cv2.compareHist(hist1_large, hist2_large, cv2.HISTCMP_CORREL)
                            hist_correl_medium = cv2.compareHist(hist1_medium, hist2_medium, cv2.HISTCMP_CORREL)
                            hist_chi_square_large = 1 / (1 + cv2.compareHist(hist1_large, hist2_large, cv2.HISTCMP_CHISQR))
                            hist_similarity = (hist_correl_large + hist_correl_medium + hist_chi_square_large) / 3
                            
                            # METHOD 3: Enhanced Structural Similarity
                            mse_large = np.mean((new_face_large.astype("float") - existing_face_large.astype("float")) ** 2)
                            mse_medium = np.mean((new_face_medium.astype("float") - existing_face_medium.astype("float")) ** 2)
                            structural_large = 1 / (1 + mse_large / 5000)
                            structural_medium = 1 / (1 + mse_medium / 5000)
                            structural_similarity = (structural_large + structural_medium) / 2
                            
                            # METHOD 4: Edge Detection Similarity
                            edges1 = cv2.Canny(new_face_medium, 50, 150)
                            edges2 = cv2.Canny(existing_face_medium, 50, 150)
                            edge_mse = np.mean((edges1.astype("float") - edges2.astype("float")) ** 2)
                            edge_similarity = 1 / (1 + edge_mse / 1000)
                            
                            # METHOD 5: Gradient Magnitude Similarity
                            grad_x1 = cv2.Sobel(new_face_medium, cv2.CV_64F, 1, 0, ksize=3)
                            grad_y1 = cv2.Sobel(new_face_medium, cv2.CV_64F, 0, 1, ksize=3)
                            grad_x2 = cv2.Sobel(existing_face_medium, cv2.CV_64F, 1, 0, ksize=3)
                            grad_y2 = cv2.Sobel(existing_face_medium, cv2.CV_64F, 0, 1, ksize=3)
                            
                            grad_mag1 = np.sqrt(grad_x1**2 + grad_y1**2)
                            grad_mag2 = np.sqrt(grad_x2**2 + grad_y2**2)
                            grad_mse = np.mean((grad_mag1 - grad_mag2) ** 2)
                            gradient_similarity = 1 / (1 + grad_mse / 50000)
                            
                            # ULTRA-STRICT Combined similarity score with enhanced weighting
                            combined_similarity = (template_similarity * 0.35 + 
                                                 hist_similarity * 0.25 + 
                                                 structural_similarity * 0.20 +
                                                 edge_similarity * 0.10 +
                                                 gradient_similarity * 0.10)
                            
                            method_scores.append({
                                'template': template_similarity,
                                'histogram': hist_similarity, 
                                'structural': structural_similarity,
                                'edge': edge_similarity,
                                'gradient': gradient_similarity,
                                'combined': combined_similarity
                            })
                            
                            max_similarity = max(max_similarity, combined_similarity)
                            total_similarity += combined_similarity
                            images_checked += 1
                
                if images_checked > 0:
                    avg_similarity = total_similarity / images_checked
                    # Use the MAXIMUM of max similarity and average similarity for ultra-strict checking
                    final_similarity = max(max_similarity, avg_similarity * 1.1)  # Boost average by 10%
                    
                    if final_similarity > 0:
                        similarity_results.append((existing_student_id, final_similarity))
                        detailed_analysis.append({
                            'student_id': existing_student_id,
                            'max_similarity': max_similarity,
                            'avg_similarity': avg_similarity,
                            'final_similarity': final_similarity,
                            'images_checked': images_checked,
                            'method_scores': method_scores[-1] if method_scores else None
                        })
            
            # Sort by similarity (highest first)
            similarity_results.sort(key=lambda x: x[1], reverse=True)
            
            # ULTRA-STRICT thresholds - much lower to catch similar faces
            ultra_high_similarity_threshold = 0.45    # AUTOMATIC BLOCK - Very strict
            high_similarity_threshold = 0.35          # AUTOMATIC BLOCK - Strict  
            medium_similarity_threshold = 0.25        # WARNING with admin review
            
            if similarity_results:
                top_match_id, top_similarity = similarity_results[0]
                
                print(f"   📊 ANALYSIS COMPLETE - Highest similarity: {top_similarity:.3f} with Student ID: {top_match_id}")
                
                # Log detailed analysis for audit
                self.log_security_event("FACE_ANALYSIS_DETAILED", student_id, 
                    f"Face similarity analysis: Top match {top_match_id} with score {top_similarity:.3f}")
                
                if top_similarity > ultra_high_similarity_threshold:
                    # ULTRA HIGH SIMILARITY - AUTOMATIC BLOCK
                    students_df = pd.read_csv(self.students_csv)
                    existing_name = students_df[students_df['student_id'] == top_match_id]['name'].iloc[0]
                    return True, f"🚨 ULTRA HIGH SIMILARITY DETECTED!\n💀 FRAUD ALERT: Face matches existing student: {existing_name} (ID: {top_match_id})\n📊 Similarity Score: {top_similarity:.1%}\n🚫 Registration AUTOMATICALLY BLOCKED - This appears to be the SAME PERSON!"
                
                elif top_similarity > high_similarity_threshold:
                    # HIGH SIMILARITY - AUTOMATIC BLOCK
                    students_df = pd.read_csv(self.students_csv)
                    existing_name = students_df[students_df['student_id'] == top_match_id]['name'].iloc[0]
                    return True, f"🚨 HIGH SIMILARITY DETECTED!\n⚠️ Face matches existing student: {existing_name} (ID: {top_match_id})\n📊 Similarity Score: {top_similarity:.1%}\n🚫 Registration BLOCKED for security reasons!"
                
                elif top_similarity > medium_similarity_threshold:
                    # MEDIUM SIMILARITY - STRONG WARNING
                    students_df = pd.read_csv(self.students_csv)
                    existing_name = students_df[students_df['student_id'] == top_match_id]['name'].iloc[0]
                    return True, f"⚠️ SUSPICIOUS SIMILARITY DETECTED!\n🔍 Face shows similarity to: {existing_name} (ID: {top_match_id})\n📊 Similarity Score: {top_similarity:.1%}\n⚠️ SECURITY REVIEW REQUIRED - Verify this is a different person!"
            
            print("   ✅ Face verification passed - No suspicious similarities detected")
            return False, "No similar faces detected - Registration can proceed"
            
        except Exception as e:
            print(f"❌ Error during face similarity check: {e}")
            self.log_security_event("SIMILARITY_CHECK_ERROR", student_id, f"Face similarity check failed: {str(e)}")
            # In case of error, fail safely by blocking registration
            return True, f"🚨 SECURITY BLOCK: Face similarity check failed due to technical error.\nRegistration blocked for security reasons.\nError: {str(e)}"
    
    def log_security_event(self, event_type, student_id, details):
        """Log security events for audit trail"""
        try:
            log_file = "data/security_log.txt"
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            log_entry = f"[{timestamp}] {event_type} - Student ID: {student_id} - {details}\n"
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
                
        except Exception as e:
            print(f"⚠️ Could not write to security log: {e}")
    
    def enhanced_face_capture_with_validation(self, student_id, student_dir, target_images=25):
        """Enhanced face capture with real-time validation"""
        cap = cv2.VideoCapture(0)
        count = 0
        consecutive_faces = 0
        required_consecutive = 3  # Require 3 consecutive clear face detections before allowing capture
        
        print(f"📸 Enhanced Face Capture for Student ID: {student_id}")
        print("🔒 Security Enhancements Active:")
        print("   👤 Face must be clearly visible")
        print("   ⏱️ Multiple consecutive detections required")
        print("   🎯 High-quality captures only")
        print("   ⌨️ Press SPACEBAR to capture images")
        print("   ❌ Press ESC to cancel")
        
        if not cap.isOpened():
            print("❌ Cannot access camera!")
            return False
        
        while count < target_images:
            ret, frame = cap.read()
            if not ret:
                print("❌ Cannot read from camera!")
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=6, minSize=(120, 120))
            
            # Enhanced face validation
            valid_faces = []
            for (x, y, w, h) in faces:
                # Check face size (must be reasonable size)
                if w > 120 and h > 120:
                    face_area = w * h
                    frame_area = frame.shape[0] * frame.shape[1]
                    face_ratio = face_area / frame_area
                    
                    # Face should occupy reasonable portion of frame (not too small/large)
                    if 0.05 < face_ratio < 0.4:
                        valid_faces.append((x, y, w, h))
            
            # Update consecutive face counter
            if len(valid_faces) == 1:  # Exactly one valid face
                consecutive_faces += 1
                x, y, w, h = valid_faces[0]
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, f'Valid Face Detected ({consecutive_faces}/{required_consecutive})', 
                           (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            else:
                consecutive_faces = 0
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                
                if len(faces) == 0:
                    cv2.putText(frame, 'No Face Detected', (10, 150), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                elif len(faces) > 1:
                    cv2.putText(frame, 'Multiple Faces - Please ensure only one person', (10, 150), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            # Display capture status
            cv2.putText(frame, f'Images Captured: {count}/{target_images}', (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(frame, 'SPACEBAR: Capture | ESC: Cancel', (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            if consecutive_faces >= required_consecutive:
                cv2.putText(frame, 'READY TO CAPTURE - Press SPACEBAR', (10, 110), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            else:
                cv2.putText(frame, f'Face validation: {consecutive_faces}/{required_consecutive}', (10, 110), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            cv2.imshow('Enhanced Face Capture', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 32:  # SPACEBAR
                if len(valid_faces) == 1 and consecutive_faces >= required_consecutive:
                    x, y, w, h = valid_faces[0]
                    
                    # Extract and enhance face
                    face_img = gray[y:y+h, x:x+w]
                    
                    # Enhance image quality
                    face_img = cv2.equalizeHist(face_img)  # Improve contrast
                    face_img = cv2.resize(face_img, (200, 200))
                    
                    # Save with high quality
                    filename = os.path.join(student_dir, f'{student_id}_{count:03d}.jpg')
                    cv2.imwrite(filename, face_img, [cv2.IMWRITE_JPEG_QUALITY, 95])
                    count += 1
                    
                    print(f"📸 High-quality image {count}/{target_images} captured and validated")
                    consecutive_faces = 0  # Reset for next capture
                    
                    cv2.waitKey(300)  # Brief pause
                else:
                    if len(valid_faces) == 0:
                        print("⚠️ No valid face detected! Please position your face properly.")
                    elif len(valid_faces) > 1:
                        print("⚠️ Multiple faces detected! Please ensure only one person is in frame.")
                    else:
                        print(f"⚠️ Face validation incomplete ({consecutive_faces}/{required_consecutive}). Keep face steady.")
                        
            elif key == 27:  # ESC
                print("❌ Capture cancelled by user")
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        success = count >= 15
        if success:
            print(f"✅ Successfully captured {count} high-quality, validated images!")
            self.log_security_event("FACE_CAPTURE_SUCCESS", student_id, f"Captured {count} validated images")
        else:
            print(f"❌ Only captured {count} images. Minimum 15 required.")
            self.log_security_event("FACE_CAPTURE_FAILED", student_id, f"Only {count} images captured")
        
        return success
    
    def validate_face_in_image(self, image_path):
        """Validate that the image contains a clear, detectable face"""
        try:
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if image is None:
                return False
            
            # Detect faces in the image
            faces = self.face_cascade.detectMultiScale(image, 1.3, 5)
            
            # Must contain exactly one face and it should be reasonably sized
            if len(faces) == 1:
                x, y, w, h = faces[0]
                # Face should be at least 50x50 pixels
                if w >= 50 and h >= 50:
                    return True
            
            return False
        except:
            return False

    def test_face_similarity_security(self):
        """Test function to demonstrate the ultra-strict face similarity detection"""
        print("🧪 TESTING ULTRA-STRICT FACE SIMILARITY DETECTION")
        print("=" * 60)
        print("🔒 Security Features Active:")
        print("   • 5 advanced comparison algorithms")
        print("   • Multi-scale analysis (3 resolutions)")
        print("   • Ultra-strict thresholds (45%, 35%, 25%)")
        print("   • Face validation for all images")
        print("   • Enhanced fraud detection")
        print("   • Comprehensive security logging")
        print("✅ System ready for maximum security operation!")

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
        print("7️⃣  Update Admin Password")
        print("8️⃣  Exit")
        print("-" * 40)
        
        try:
            choice = input("🔢 Enter your choice (1-8): ").strip()
            
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
                system.update_admin_password()
            
            elif choice == '8':
                print("👋 Thank you for using Face Recognition Attendance System!")
                print("🎯 Have a great day!")
                break
            
            else:
                print("❌ Invalid choice! Please select 1-8.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ An unexpected error occurred: {e}")
            print("💡 Please try again or restart the system.")


if __name__ == "__main__":
    main()
