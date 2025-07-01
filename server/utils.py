"""
Utility functions for the Face Recognition Attendance System
"""

import cv2
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class AttendanceUtils:
    """Utility class for attendance system operations"""
    
    @staticmethod
    def test_camera():
        """Test if camera is working properly"""
        print("Testing camera...")
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ Cannot access camera!")
            return False
        
        print("✅ Camera is working!")
        print("Press any key to close the test window...")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Cannot read from camera!")
                break
            
            cv2.putText(frame, 'Camera Test - Press any key to exit', (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow('Camera Test', frame)
            
            if cv2.waitKey(1) & 0xFF != 255:  # Any key pressed
                break
        
        cap.release()
        cv2.destroyAllWindows()
        return True
    
    @staticmethod
    def backup_data():
        """Create backup of CSV files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_folder = f"backup_{timestamp}"
        os.makedirs(backup_folder, exist_ok=True)
        
        files_to_backup = ['data/students.csv', 'data/attendance.csv']
        
        for file_path in files_to_backup:
            if os.path.exists(file_path):
                import shutil
                backup_path = os.path.join(backup_folder, os.path.basename(file_path))
                shutil.copy2(file_path, backup_path)
                print(f"✅ Backed up: {file_path}")
        
        print(f"📦 Backup created in folder: {backup_folder}")
    
    @staticmethod
    def generate_attendance_stats():
        """Generate attendance statistics"""
        try:
            students_df = pd.read_csv('data/students.csv')
            attendance_df = pd.read_csv('data/attendance.csv')
            
            if students_df.empty or attendance_df.empty:
                print("❌ No data available for statistics")
                return
            
            print("\n📊 ATTENDANCE STATISTICS")
            print("=" * 50)
            
            # Overall stats
            total_students = len(students_df)
            total_attendance_records = len(attendance_df)
            
            print(f"👥 Total Registered Students: {total_students}")
            print(f"📝 Total Attendance Records: {total_attendance_records}")
            
            # Daily attendance
            attendance_df['date'] = pd.to_datetime(attendance_df['date'])
            daily_attendance = attendance_df.groupby('date').size()
            
            print(f"\n📅 Daily Attendance Summary:")
            for date, count in daily_attendance.items():
                percentage = (count / total_students) * 100
                print(f"   {date.strftime('%Y-%m-%d')}: {count}/{total_students} ({percentage:.1f}%)")
            
            # Student-wise attendance
            student_attendance = attendance_df.groupby('student_id').size().sort_values(ascending=False)
            
            print(f"\n🏆 Top Attendees:")
            for student_id, count in student_attendance.head(5).items():
                student_name = students_df[students_df['student_id'] == student_id]['name'].iloc[0]
                print(f"   {student_name} (ID: {student_id}): {count} days")
            
            # Recent activity
            recent_date = datetime.now() - timedelta(days=7)
            recent_attendance = attendance_df[attendance_df['date'] >= recent_date.strftime('%Y-%m-%d')]
            
            print(f"\n📆 Last 7 Days Activity: {len(recent_attendance)} records")
            
        except Exception as e:
            print(f"❌ Error generating statistics: {e}")
    
    @staticmethod
    def clean_training_data():
        """Clean up training images and remove orphaned data"""
        print("\n🧹 Cleaning training data...")
        
        try:
            students_df = pd.read_csv('data/students.csv')
            training_folder = 'training_images'
            
            if not os.path.exists(training_folder):
                print("❌ Training folder not found!")
                return
            
            # Get registered student IDs
            registered_ids = set(students_df['student_id'].astype(str))
            
            # Check training folders
            removed_folders = 0
            for folder_name in os.listdir(training_folder):
                folder_path = os.path.join(training_folder, folder_name)
                
                if os.path.isdir(folder_path) and folder_name not in registered_ids:
                    import shutil
                    shutil.rmtree(folder_path)
                    print(f"🗑️  Removed orphaned folder: {folder_name}")
                    removed_folders += 1
            
            print(f"✅ Cleanup completed! Removed {removed_folders} orphaned folders.")
            
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
    
    @staticmethod
    def export_attendance_report(output_format='csv'):
        """Export attendance report in different formats"""
        try:
            attendance_df = pd.read_csv('data/attendance.csv')
            students_df = pd.read_csv('data/students.csv')
            
            if attendance_df.empty:
                print("❌ No attendance data to export!")
                return
            
            # Create detailed report
            detailed_report = attendance_df.merge(
                students_df[['student_id', 'email']], 
                on='student_id', 
                how='left'
            )
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if output_format.lower() == 'csv':
                filename = f"attendance_report_{timestamp}.csv"
                detailed_report.to_csv(filename, index=False)
                print(f"✅ CSV report exported: {filename}")
            
            elif output_format.lower() == 'excel':
                filename = f"attendance_report_{timestamp}.xlsx"
                detailed_report.to_excel(filename, index=False)
                print(f"✅ Excel report exported: {filename}")
            
            else:
                print("❌ Unsupported format! Use 'csv' or 'excel'")
            
        except Exception as e:
            print(f"❌ Error exporting report: {e}")
    
    @staticmethod
    def validate_system():
        """Validate system setup and data integrity"""
        print("\n🔍 SYSTEM VALIDATION")
        print("=" * 40)
        
        issues_found = 0
        
        # Check required directories
        required_dirs = ['data', 'training_images', 'models']
        for dir_name in required_dirs:
            if os.path.exists(dir_name):
                print(f"✅ Directory '{dir_name}' exists")
            else:
                print(f"❌ Directory '{dir_name}' missing")
                issues_found += 1
        
        # Check CSV files
        csv_files = ['data/students.csv', 'data/attendance.csv']
        for csv_file in csv_files:
            if os.path.exists(csv_file):
                try:
                    df = pd.read_csv(csv_file)
                    print(f"✅ '{csv_file}' is valid ({len(df)} records)")
                except:
                    print(f"❌ '{csv_file}' is corrupted")
                    issues_found += 1
            else:
                print(f"❌ '{csv_file}' missing")
                issues_found += 1
        
        # Check training images
        if os.path.exists('training_images'):
            student_folders = [f for f in os.listdir('training_images') 
                             if os.path.isdir(os.path.join('training_images', f))]
            print(f"✅ Training images found for {len(student_folders)} students")
            
            for folder in student_folders:
                folder_path = os.path.join('training_images', folder)
                image_count = len([f for f in os.listdir(folder_path) 
                                 if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
                if image_count < 10:
                    print(f"⚠️  Student {folder} has only {image_count} training images (recommended: 20+)")
        
        # Check camera
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✅ Camera is accessible")
            cap.release()
        else:
            print("❌ Camera not accessible")
            issues_found += 1
        
        print(f"\n📋 Validation completed: {issues_found} issues found")
        
        if issues_found == 0:
            print("🎉 System is ready to use!")
        else:
            print("⚠️  Please fix the issues before using the system")


def main():
    """Main utility menu"""
    utils = AttendanceUtils()
    
    while True:
        print("\n🛠️  ATTENDANCE SYSTEM UTILITIES")
        print("=" * 40)
        print("1️⃣  Test Camera")
        print("2️⃣  Backup Data")
        print("3️⃣  Generate Statistics")
        print("4️⃣  Clean Training Data")
        print("5️⃣  Export Report (CSV)")
        print("6️⃣  Export Report (Excel)")
        print("7️⃣  Validate System")
        print("8️⃣  Exit")
        print("-" * 30)
        
        try:
            choice = input("🔢 Enter your choice (1-8): ").strip()
            
            if choice == '1':
                utils.test_camera()
            elif choice == '2':
                utils.backup_data()
            elif choice == '3':
                utils.generate_attendance_stats()
            elif choice == '4':
                utils.clean_training_data()
            elif choice == '5':
                utils.export_attendance_report('csv')
            elif choice == '6':
                utils.export_attendance_report('excel')
            elif choice == '7':
                utils.validate_system()
            elif choice == '8':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice! Please select 1-8.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ An error occurred: {e}")


if __name__ == "__main__":
    main()
