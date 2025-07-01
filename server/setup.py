"""
Setup script for Face Recognition Attendance System
Run this script to set up the system and install dependencies
"""

import os
import sys
import subprocess
import platform

def install_requirements():
    """Install Python requirements"""
    print("📦 Installing Python packages...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Python packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        "data",
        "training_images", 
        "models",
        "temp_captures"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def create_initial_csv_files():
    """Create initial CSV files"""
    print("📊 Creating initial CSV files...")
    
    import pandas as pd
    
    # Students CSV
    students_df = pd.DataFrame(columns=['student_id', 'name', 'email', 'registration_date'])
    students_df.to_csv('data/students.csv', index=False)
    print("✅ Created students.csv")
    
    # Attendance CSV  
    attendance_df = pd.DataFrame(columns=['student_id', 'name', 'date', 'time', 'status'])
    attendance_df.to_csv('data/attendance.csv', index=False)
    print("✅ Created attendance.csv")

def test_camera():
    """Test camera functionality"""
    print("📷 Testing camera...")
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        
        if cap.isOpened():
            print("✅ Camera is working!")
            cap.release()
            return True
        else:
            print("❌ Camera not accessible!")
            return False
    except Exception as e:
        print(f"❌ Camera test failed: {e}")
        return False

def check_system_requirements():
    """Check system requirements"""
    print("🔍 Checking system requirements...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 8:
        print(f"✅ Python {python_version.major}.{python_version.minor} is supported")
    else:
        print(f"❌ Python {python_version.major}.{python_version.minor} is not supported. Please use Python 3.8 or higher")
        return False
    
    # Check OS
    os_name = platform.system()
    print(f"✅ Operating System: {os_name}")
    
    return True

def install_system_dependencies():
    """Install system-specific dependencies"""
    os_name = platform.system()
    
    if os_name == "Linux":
        print("🐧 Detected Linux - Installing system dependencies...")
        
        try:
            # Common Ubuntu/Debian commands
            commands = [
                "sudo apt-get update",
                "sudo apt-get install -y python3-opencv",
                "sudo apt-get install -y cmake",
                "sudo apt-get install -y libopenblas-dev liblapack-dev", 
                "sudo apt-get install -y libx11-dev libgtk-3-dev"
            ]
            
            for cmd in commands:
                print(f"Running: {cmd}")
                # Note: In production, you might want to handle this differently
                print("⚠️  Please run these commands manually if needed:")
                print(cmd)
                
        except Exception as e:
            print(f"⚠️  Please install system dependencies manually: {e}")
    
    elif os_name == "Windows":
        print("🪟 Detected Windows - Additional setup may be needed")
        print("ℹ️  If you encounter dlib installation issues:")
        print("   1. Install Visual Studio Build Tools")
        print("   2. Or use conda: conda install -c conda-forge dlib")
    
    elif os_name == "Darwin":  # macOS
        print("🍎 Detected macOS - Additional setup may be needed")
        print("ℹ️  If you encounter issues, try:")
        print("   brew install cmake")

def main():
    """Main setup function"""
    print("🎓 Face Recognition Attendance System Setup")
    print("=" * 50)
    
    # Check system requirements
    if not check_system_requirements():
        return
    
    # Install system dependencies info
    install_system_dependencies()
    
    # Create directories
    create_directories()
    
    # Install Python requirements
    if not install_requirements():
        print("⚠️  Please install requirements manually: pip install -r requirements.txt")
    
    # Create CSV files
    try:
        create_initial_csv_files()
    except ImportError:
        print("⚠️  Pandas not installed. Please install requirements first.")
    
    # Test camera
    try:
        test_camera()
    except ImportError:
        print("⚠️  OpenCV not installed. Please install requirements first.")
    
    print("\n🎉 Setup completed!")
    print("\n📋 Next steps:")
    print("1️⃣  Run: python simple_attendance.py (for easy interface)")
    print("2️⃣  Or run: python face_recognition_system.py (for traditional CV)")
    print("3️⃣  Or run: python advanced_face_recognition.py (for advanced recognition)")
    print("4️⃣  Or run: python api.py (for REST API server)")
    print("5️⃣  Or run: python utils.py (for system utilities)")
    
    print("\n📖 Read README.md for detailed usage instructions")

if __name__ == "__main__":
    main()
