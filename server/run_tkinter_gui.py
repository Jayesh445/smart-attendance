#!/usr/bin/env python3
"""
Launcher for the Tkinter GUI Face Recognition Attendance System
Simple launcher that handles initialization and error checking
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

def check_requirements():
    """Check if all required packages are available"""
    required_packages = [
        'cv2', 'numpy', 'pandas', 'PIL'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        error_msg = f"Missing required packages: {', '.join(missing_packages)}\n\n"
        error_msg += "Please install them using:\n"
        error_msg += "pip install opencv-python numpy pandas pillow"
        
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        messagebox.showerror("Missing Dependencies", error_msg)
        root.destroy()
        return False
    
    return True

def check_directories():
    """Create necessary directories if they don't exist"""
    directories = ['data', 'images', 'models']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

def main():
    """Main launcher function"""
    print("🎓 Face Recognition Attendance System - Tkinter GUI")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required")
        print(f"   Current version: {sys.version}")
        input("Press Enter to exit...")
        sys.exit(1)
    
    print("✅ Python version check passed")
    
    # Check required packages
    print("🔍 Checking required packages...")
    if not check_requirements():
        input("Press Enter to exit...")
        sys.exit(1)
    
    print("✅ All required packages are available")
    
    # Create necessary directories
    print("📁 Setting up directories...")
    check_directories()
    print("✅ Directory setup complete")
    
    # Import and run the GUI
    try:
        print("🚀 Starting GUI...")
        from tkinter_gui import run_gui
        run_gui()
    except ImportError as e:
        print(f"❌ Error importing GUI module: {e}")
        input("Press Enter to exit...")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting GUI: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
