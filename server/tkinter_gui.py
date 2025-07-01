"""
Professional Tkinter GUI for Face Recognition Attendance System
Beautiful modern interface with professional white theme
No external GUI dependencies required - uses built-in tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from tkinter import font as tkFont
import threading
import os
import pandas as pd
from datetime import datetime
import cv2
import numpy as np
from PIL import Image, ImageTk
from main_system import WindowsFaceRecognition

class ModernStyle:
    """Modern styling constants for the GUI"""
    
    # Colors
    PRIMARY_COLOR = "#2196F3"
    PRIMARY_DARK = "#1976D2"
    PRIMARY_LIGHT = "#E3F2FD"
    
    SUCCESS_COLOR = "#4CAF50"
    SUCCESS_LIGHT = "#E8F5E8"
    
    WARNING_COLOR = "#FF9800"
    WARNING_LIGHT = "#FFF8E1"
    
    ERROR_COLOR = "#F44336"
    ERROR_LIGHT = "#FFEBEE"
    
    BACKGROUND_COLOR = "#F8F9FA"
    CARD_COLOR = "#FFFFFF"
    BORDER_COLOR = "#E0E0E0"
    TEXT_COLOR = "#333333"
    TEXT_SECONDARY = "#666666"
    
    # Fonts
    FONT_FAMILY = "Segoe UI"
    FONT_SIZE_LARGE = 24
    FONT_SIZE_MEDIUM = 14
    FONT_SIZE_SMALL = 12
    
    # Dimensions
    BUTTON_HEIGHT = 40
    CARD_PADDING = 20
    BORDER_RADIUS = 8

class ModernFrame(tk.Frame):
    """Custom frame with modern styling"""
    
    def __init__(self, parent, title="", **kwargs):
        super().__init__(parent, bg=ModernStyle.CARD_COLOR, relief="flat", bd=1, **kwargs)
        
        if title:
            title_label = tk.Label(
                self,
                text=title,
                font=(ModernStyle.FONT_FAMILY, 16, "bold"),
                bg=ModernStyle.CARD_COLOR,
                fg=ModernStyle.TEXT_COLOR,
                anchor="w"
            )
            title_label.pack(fill="x", padx=ModernStyle.CARD_PADDING, pady=(ModernStyle.CARD_PADDING, 10))

class ModernButton(tk.Button):
    """Custom button with modern styling"""
    
    def __init__(self, parent, text="", command=None, style="primary", **kwargs):
        
        if style == "primary":
            bg_color = ModernStyle.PRIMARY_COLOR
            fg_color = "white"
            active_bg = ModernStyle.PRIMARY_DARK
        elif style == "success":
            bg_color = ModernStyle.SUCCESS_COLOR
            fg_color = "white"
            active_bg = "#388E3C"
        elif style == "warning":
            bg_color = ModernStyle.WARNING_COLOR
            fg_color = "white"
            active_bg = "#F57C00"
        elif style == "danger":
            bg_color = ModernStyle.ERROR_COLOR
            fg_color = "white"
            active_bg = "#D32F2F"
        else:  # secondary
            bg_color = ModernStyle.CARD_COLOR
            fg_color = ModernStyle.TEXT_COLOR
            active_bg = ModernStyle.BACKGROUND_COLOR
        
        super().__init__(
            parent,
            text=text,
            command=command,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MEDIUM, "bold"),
            bg=bg_color,
            fg=fg_color,
            activebackground=active_bg,
            activeforeground=fg_color,
            relief="flat",
            bd=0,
            cursor="hand2",
            height=2,
            **kwargs
        )

class StatusLabel(tk.Label):
    """Status label with color coding"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL),
            relief="flat",
            bd=1,
            **kwargs
        )
    
    def set_status(self, message, status_type="info"):
        self.config(text=message)
        
        if status_type == "success":
            self.config(bg=ModernStyle.SUCCESS_LIGHT, fg=ModernStyle.SUCCESS_COLOR)
        elif status_type == "error":
            self.config(bg=ModernStyle.ERROR_LIGHT, fg=ModernStyle.ERROR_COLOR)
        elif status_type == "warning":
            self.config(bg=ModernStyle.WARNING_LIGHT, fg=ModernStyle.WARNING_COLOR)
        else:  # info
            self.config(bg=ModernStyle.PRIMARY_LIGHT, fg=ModernStyle.PRIMARY_COLOR)

class FaceRecognitionGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.face_system = None
        self.camera_active = False
        self.cap = None
        self.camera_label = None
        
        self.setup_window()
        self.create_widgets()
        self.init_face_system()
    
    def setup_window(self):
        """Setup main window properties"""
        self.root.title("🎓 Face Recognition Attendance System")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        self.root.configure(bg=ModernStyle.BACKGROUND_COLOR)
        
        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"1200x800+{x}+{y}")
        
        # Set window icon (if available)
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
    
    def create_widgets(self):
        """Create main interface widgets"""
        # Main container
        main_container = tk.Frame(self.root, bg=ModernStyle.BACKGROUND_COLOR)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create sidebar
        self.create_sidebar(main_container)
        
        # Create main content area
        self.create_main_content(main_container)
        
        # Create status bar
        self.create_status_bar()
        
        # Show dashboard by default
        self.show_dashboard()
    
    def create_sidebar(self, parent):
        """Create navigation sidebar"""
        sidebar = tk.Frame(parent, bg=ModernStyle.CARD_COLOR, width=280, relief="flat", bd=1)
        sidebar.pack(side="left", fill="y", padx=(0, 10))
        sidebar.pack_propagate(False)
        
        # Header
        header_frame = tk.Frame(sidebar, bg=ModernStyle.PRIMARY_COLOR, height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🎓 Face Recognition",
            font=(ModernStyle.FONT_FAMILY, 18, "bold"),
            bg=ModernStyle.PRIMARY_COLOR,
            fg="white"
        )
        title_label.pack(pady=(15, 5))
        
        subtitle_label = tk.Label(
            header_frame,
            text="Attendance System",
            font=(ModernStyle.FONT_FAMILY, 12),
            bg=ModernStyle.PRIMARY_COLOR,
            fg="white"
        )
        subtitle_label.pack()
        
        # Menu buttons
        menu_frame = tk.Frame(sidebar, bg=ModernStyle.CARD_COLOR)
        menu_frame.pack(fill="both", expand=True, pady=20)
        
        self.menu_buttons = []
        menu_items = [
            ("📊 Dashboard", self.show_dashboard),
            ("👤 Register Student", self.show_register),
            ("🎯 Train Model", self.show_train),
            ("✅ Mark Attendance", self.show_attendance),
            ("📈 View Reports", self.show_reports),
            ("👥 Students List", self.show_students),
            ("📷 Test Camera", self.show_camera_test),
            ("🔐 Admin Settings", self.show_admin)
        ]
        
        for text, command in menu_items:
            btn = tk.Button(
                menu_frame,
                text=text,
                command=lambda cmd=command: self.set_active_page(cmd),
                font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MEDIUM),
                bg=ModernStyle.CARD_COLOR,
                fg=ModernStyle.TEXT_COLOR,
                relief="flat",
                bd=0,
                anchor="w",
                padx=20,
                pady=15,
                cursor="hand2"
            )
            btn.pack(fill="x")
            self.menu_buttons.append(btn)
            
            # Hover effects
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=ModernStyle.BACKGROUND_COLOR))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=ModernStyle.CARD_COLOR) if b != self.active_button else None)
        
        # Set first button as active
        self.active_button = self.menu_buttons[0]
        self.set_active_button(self.active_button)
    
    def set_active_button(self, button):
        """Set active navigation button"""
        # Reset all buttons
        for btn in self.menu_buttons:
            btn.config(bg=ModernStyle.CARD_COLOR)
        
        # Set active button
        button.config(bg=ModernStyle.PRIMARY_LIGHT)
        self.active_button = button
    
    def set_active_page(self, command):
        """Set active page and button"""
        # Find the button for this command
        for i, (_, cmd) in enumerate([
            ("📊 Dashboard", self.show_dashboard),
            ("👤 Register Student", self.show_register),
            ("🎯 Train Model", self.show_train),
            ("✅ Mark Attendance", self.show_attendance),
            ("📈 View Reports", self.show_reports),
            ("👥 Students List", self.show_students),
            ("📷 Test Camera", self.show_camera_test),
            ("🔐 Admin Settings", self.show_admin)
        ]):
            if cmd == command:
                self.set_active_button(self.menu_buttons[i])
                break
        
        command()
    
    def create_main_content(self, parent):
        """Create main content area"""
        self.content_frame = tk.Frame(parent, bg=ModernStyle.BACKGROUND_COLOR)
        self.content_frame.pack(side="right", fill="both", expand=True)
    
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = tk.Label(
            self.root,
            text="Ready",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL),
            bg=ModernStyle.CARD_COLOR,
            fg=ModernStyle.TEXT_SECONDARY,
            relief="sunken",
            bd=1,
            anchor="w",
            padx=10
        )
        self.status_bar.pack(side="bottom", fill="x")
    
    def clear_content(self):
        """Clear current content"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def init_face_system(self):
        """Initialize face recognition system"""
        def init_system():
            try:
                self.update_status("Initializing Face Recognition System...")
                self.face_system = WindowsFaceRecognition()
                self.update_status("Face Recognition System initialized successfully")
            except Exception as e:
                self.update_status(f"Error initializing system: {str(e)}")
                messagebox.showerror("Initialization Error", f"Failed to initialize face recognition system:\n{str(e)}")
        
        # Run in separate thread to avoid blocking UI
        threading.Thread(target=init_system, daemon=True).start()
    
    def update_status(self, message):
        """Update status bar"""
        self.status_bar.config(text=message)
        self.root.update_idletasks()

    def show_dashboard(self):
        """Show dashboard page"""
        self.clear_content()
        
        # Page title
        title_frame = tk.Frame(self.content_frame, bg=ModernStyle.BACKGROUND_COLOR)
        title_frame.pack(fill="x", pady=(0, 20))
        
        title_label = tk.Label(
            title_frame,
            text="📊 Dashboard",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_LARGE, "bold"),
            bg=ModernStyle.BACKGROUND_COLOR,
            fg=ModernStyle.TEXT_COLOR
        )
        title_label.pack(anchor="w")
        
        # Statistics cards
        stats_frame = tk.Frame(self.content_frame, bg=ModernStyle.BACKGROUND_COLOR)
        stats_frame.pack(fill="x", pady=(0, 20))
        
        # Get statistics
        total_students, present_today, absent_today = self.get_dashboard_stats()
        
        # Create stat cards
        self.create_stat_card(stats_frame, "👥 Total Students", str(total_students), ModernStyle.SUCCESS_COLOR, 0)
        self.create_stat_card(stats_frame, "✅ Present Today", str(present_today), ModernStyle.PRIMARY_COLOR, 1)
        self.create_stat_card(stats_frame, "❌ Absent Today", str(absent_today), ModernStyle.WARNING_COLOR, 2)
        
        # Recent activity
        activity_frame = ModernFrame(self.content_frame, "Recent Activity")
        activity_frame.pack(fill="both", expand=True)
        
        # Activity listbox
        activity_listbox = tk.Listbox(
            activity_frame,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL),
            bg=ModernStyle.CARD_COLOR,
            fg=ModernStyle.TEXT_COLOR,
            selectbackground=ModernStyle.PRIMARY_LIGHT,
            relief="flat",
            bd=0
        )
        activity_listbox.pack(fill="both", expand=True, padx=ModernStyle.CARD_PADDING, pady=(0, ModernStyle.CARD_PADDING))
        
        # Load recent activity
        self.load_recent_activity(activity_listbox)
    
    def create_stat_card(self, parent, title, value, color, column):
        """Create a statistics card"""
        card_frame = tk.Frame(parent, bg=ModernStyle.CARD_COLOR, relief="flat", bd=1)
        card_frame.grid(row=0, column=column, padx=10, pady=10, sticky="ew")
        parent.grid_columnconfigure(column, weight=1)
        
        # Color bar
        color_bar = tk.Frame(card_frame, bg=color, height=4)
        color_bar.pack(fill="x")
        
        # Content
        content_frame = tk.Frame(card_frame, bg=ModernStyle.CARD_COLOR)
        content_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        title_label = tk.Label(
            content_frame,
            text=title,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL),
            bg=ModernStyle.CARD_COLOR,
            fg=ModernStyle.TEXT_SECONDARY
        )
        title_label.pack(anchor="w")
        
        value_label = tk.Label(
            content_frame,
            text=value,
            font=(ModernStyle.FONT_FAMILY, 28, "bold"),
            bg=ModernStyle.CARD_COLOR,
            fg=color
        )
        value_label.pack(anchor="w")
    
    def get_dashboard_stats(self):
        """Get dashboard statistics using main system files"""
        try:
            # Get student count from main system
            if os.path.exists(self.face_system.students_csv):
                students_df = pd.read_csv(self.face_system.students_csv)
                total_students = len(students_df)
            else:
                total_students = 0
            
            # Get today's attendance from main system
            present_today = 0
            if os.path.exists(self.face_system.attendance_csv):
                attendance_df = pd.read_csv(self.face_system.attendance_csv)
                today = datetime.now().strftime('%Y-%m-%d')
                present_today = len(attendance_df[attendance_df['date'] == today])
            
            absent_today = max(0, total_students - present_today)
            
            return total_students, present_today, absent_today
        except:
            return 0, 0, 0
    
    def load_recent_activity(self, listbox):
        """Load recent activity into listbox using main system format"""
        try:
            attendance_file = self.face_system.attendance_csv
            if os.path.exists(attendance_file):
                attendance_df = pd.read_csv(attendance_file)
                if not attendance_df.empty:
                    recent_records = attendance_df.tail(10)
                    for _, record in recent_records.iterrows():
                        # Use main system CSV format: student_id, name, date, time, status
                        student_name = record.get('name', 'Unknown')
                        date = record.get('date', 'Unknown')
                        time = record.get('time', 'Unknown')
                        item_text = f"✅ {student_name} marked present at {time} on {date}"
                        listbox.insert(0, item_text)
            
            if listbox.size() == 0:
                listbox.insert(0, "No recent activity")
                
        except Exception as e:
            listbox.insert(0, f"Error loading activity: {str(e)}")
    
    def show_register(self):
        """Show student registration page"""
        self.clear_content()
        
        # Page title
        title_frame = tk.Frame(self.content_frame, bg=ModernStyle.BACKGROUND_COLOR)
        title_frame.pack(fill="x", pady=(0, 20))
        
        title_label = tk.Label(
            title_frame,
            text="👤 Register New Student",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_LARGE, "bold"),
            bg=ModernStyle.BACKGROUND_COLOR,
            fg=ModernStyle.TEXT_COLOR
        )
        title_label.pack(anchor="w")
        
        # Registration form
        form_frame = ModernFrame(self.content_frame, "Student Information")
        form_frame.pack(fill="x", pady=(0, 20))
        
        # Form fields
        fields_frame = tk.Frame(form_frame, bg=ModernStyle.CARD_COLOR)
        fields_frame.pack(fill="x", padx=ModernStyle.CARD_PADDING, pady=(0, ModernStyle.CARD_PADDING))
        
        # Student ID
        tk.Label(fields_frame, text="Student ID:", font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MEDIUM), 
                bg=ModernStyle.CARD_COLOR, fg=ModernStyle.TEXT_COLOR).grid(row=0, column=0, sticky="w", pady=5)
        self.student_id_entry = tk.Entry(fields_frame, font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MEDIUM), width=30)
        self.student_id_entry.grid(row=0, column=1, pady=5, padx=(10, 0), sticky="ew")
        
        # Name
        tk.Label(fields_frame, text="Full Name:", font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MEDIUM), 
                bg=ModernStyle.CARD_COLOR, fg=ModernStyle.TEXT_COLOR).grid(row=1, column=0, sticky="w", pady=5)
        self.student_name_entry = tk.Entry(fields_frame, font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MEDIUM), width=30)
        self.student_name_entry.grid(row=1, column=1, pady=5, padx=(10, 0), sticky="ew")
        
        # Email
        tk.Label(fields_frame, text="Email:", font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MEDIUM), 
                bg=ModernStyle.CARD_COLOR, fg=ModernStyle.TEXT_COLOR).grid(row=2, column=0, sticky="w", pady=5)
        self.student_email_entry = tk.Entry(fields_frame, font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MEDIUM), width=30)
        self.student_email_entry.grid(row=2, column=1, pady=5, padx=(10, 0), sticky="ew")
        
        fields_frame.grid_columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = tk.Frame(form_frame, bg=ModernStyle.CARD_COLOR)
        button_frame.pack(fill="x", padx=ModernStyle.CARD_PADDING, pady=(10, ModernStyle.CARD_PADDING))
        
        self.start_registration_btn = ModernButton(button_frame, "📸 Start Registration", self.start_registration, "primary")
        self.start_registration_btn.pack(side="left", padx=(0, 10))
        
        self.clear_form_btn = ModernButton(button_frame, "🔄 Clear Form", self.clear_registration_form, "secondary")
        self.clear_form_btn.pack(side="left")
        
        # Status
        self.register_status = StatusLabel(form_frame, text="", bg=ModernStyle.CARD_COLOR)
        self.register_status.pack(fill="x", padx=ModernStyle.CARD_PADDING, pady=(0, ModernStyle.CARD_PADDING))
        
        # Instructions
        instructions_frame = ModernFrame(self.content_frame, "📋 Registration Instructions")
        instructions_frame.pack(fill="both", expand=True)
        
        instructions_text = tk.Text(
            instructions_frame,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL),
            bg=ModernStyle.CARD_COLOR,
            fg=ModernStyle.TEXT_COLOR,
            relief="flat",
            bd=0,
            wrap="word",
            height=8
        )
        instructions_text.pack(fill="both", expand=True, padx=ModernStyle.CARD_PADDING, pady=(0, ModernStyle.CARD_PADDING))
        
        instructions_content = """📋 FACE CAPTURE INSTRUCTIONS:

1. SETUP:
   • Ensure good lighting (natural light preferred)  
   • Position yourself 2-3 feet from camera
   • Remove glasses, hats, or face coverings
   • Make sure only ONE person is in camera view

2. CAPTURE PROCESS:
   • Camera window will open after entering admin password
   • Green rectangle will appear around your face
   • Press SPACEBAR when ready to capture (5 photos needed)
   • Stay still and look directly at camera for each capture
   • Press 'Q' to cancel if needed

3. SECURITY FEATURES:
   • Admin password required for registration
   • Duplicate prevention (ID, name, email)
   • Multiple face images captured for accuracy
   • Automatic quality verification

4. TIPS FOR SUCCESS:
   • Good lighting is crucial for accurate recognition
   • Maintain same head position during capture
   • Avoid shadows on face
   • Clean camera lens if image is blurry"""
        
        instructions_text.insert("1.0", instructions_content)
        instructions_text.config(state="disabled")
    
    def show_train(self):
        """Show model training page"""
        self.clear_content()
        
        # Page title
        title_frame = tk.Frame(self.content_frame, bg=ModernStyle.BACKGROUND_COLOR)
        title_frame.pack(fill="x", pady=(0, 20))
        
        title_label = tk.Label(
            title_frame,
            text="🎯 Train Recognition Model",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_LARGE, "bold"),
            bg=ModernStyle.BACKGROUND_COLOR,
            fg=ModernStyle.TEXT_COLOR
        )
        title_label.pack(anchor="w")
        
        # Training card
        train_frame = ModernFrame(self.content_frame, "Model Training")
        train_frame.pack(fill="both", expand=True)
        
        # Info text
        info_text = tk.Text(
            train_frame,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MEDIUM),
            bg=ModernStyle.CARD_COLOR,
            fg=ModernStyle.TEXT_COLOR,
            relief="flat",
            bd=0,
            wrap="word",
            height=4
        )
        info_text.pack(fill="x", padx=ModernStyle.CARD_PADDING, pady=(0, 20))
        
        info_content = """Train the face recognition model with registered student images.
This process analyzes all captured face images and creates a model
for accurate student identification during attendance marking.

Make sure you have registered students before training the model."""
        
        info_text.insert("1.0", info_content)
        info_text.config(state="disabled")
        
        # Training button
        train_btn = ModernButton(train_frame, "🚀 Start Training", self.start_training, "primary")
        train_btn.pack(padx=ModernStyle.CARD_PADDING, pady=10)
        
        # Progress bar
        self.train_progress = ttk.Progressbar(
            train_frame,
            mode='determinate',
            length=400
        )
        self.train_progress.pack(padx=ModernStyle.CARD_PADDING, pady=10)
        
        # Status
        self.train_status = StatusLabel(train_frame, text="", bg=ModernStyle.CARD_COLOR)
        self.train_status.pack(fill="x", padx=ModernStyle.CARD_PADDING, pady=(0, ModernStyle.CARD_PADDING))
    
    def show_attendance(self):
        """Show attendance marking page"""
        self.clear_content()
        
        # Page title
        title_frame = tk.Frame(self.content_frame, bg=ModernStyle.BACKGROUND_COLOR)
        title_frame.pack(fill="x", pady=(0, 20))
        
        title_label = tk.Label(
            title_frame,
            text="✅ Mark Attendance",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_LARGE, "bold"),
            bg=ModernStyle.BACKGROUND_COLOR,
            fg=ModernStyle.TEXT_COLOR
        )
        title_label.pack(anchor="w")
        
        # Camera frame
        camera_frame = ModernFrame(self.content_frame, "Live Camera Feed")
        camera_frame.pack(fill="both", expand=True)
        
        # Camera display
        self.camera_label = tk.Label(
            camera_frame,
            text="📷 Camera will appear here",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MEDIUM),
            bg=ModernStyle.BACKGROUND_COLOR,
            fg=ModernStyle.TEXT_SECONDARY,
            width=80,
            height=20
        )
        self.camera_label.pack(padx=ModernStyle.CARD_PADDING, pady=10)
        
        # Camera controls
        controls_frame = tk.Frame(camera_frame, bg=ModernStyle.CARD_COLOR)
        controls_frame.pack(fill="x", padx=ModernStyle.CARD_PADDING, pady=10)
        
        self.start_camera_btn = ModernButton(controls_frame, "📹 Start Camera", self.start_camera, "primary")
        self.start_camera_btn.pack(side="left", padx=(0, 10))
        
        self.stop_camera_btn = ModernButton(controls_frame, "⏹️ Stop Camera", self.stop_camera, "danger")
        self.stop_camera_btn.pack(side="left")
        self.stop_camera_btn.config(state="disabled")
        
        # Status
        self.attendance_status = StatusLabel(camera_frame, text="", bg=ModernStyle.CARD_COLOR)
        self.attendance_status.pack(fill="x", padx=ModernStyle.CARD_PADDING, pady=10)
        
        # Today's attendance
        today_frame = tk.Frame(camera_frame, bg=ModernStyle.CARD_COLOR)
        today_frame.pack(fill="x", padx=ModernStyle.CARD_PADDING, pady=(0, ModernStyle.CARD_PADDING))
        
        tk.Label(today_frame, text="Today's Attendance:", 
                font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MEDIUM, "bold"),
                bg=ModernStyle.CARD_COLOR, fg=ModernStyle.TEXT_COLOR).pack(anchor="w")
        
        self.today_listbox = tk.Listbox(
            today_frame,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL),
            bg=ModernStyle.CARD_COLOR,
            fg=ModernStyle.TEXT_COLOR,
            height=6
        )
        self.today_listbox.pack(fill="x", pady=5)
        
        # Initial update of today's attendance
        self.update_today_attendance()

    def show_reports(self):
        """Show reports page"""
        self.clear_content()
        
        # Page title
        title_frame = tk.Frame(self.content_frame, bg=ModernStyle.BACKGROUND_COLOR)
        title_frame.pack(fill="x", pady=(0, 20))
        
        title_label = tk.Label(
            title_frame,
            text="📈 Attendance Reports",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_LARGE, "bold"),
            bg=ModernStyle.BACKGROUND_COLOR,
            fg=ModernStyle.TEXT_COLOR
        )
        title_label.pack(anchor="w")
        
        # Filter frame
        filter_frame = ModernFrame(self.content_frame, "Filter Options")
        filter_frame.pack(fill="x", pady=(0, 20))
        
        controls_frame = tk.Frame(filter_frame, bg=ModernStyle.CARD_COLOR)
        controls_frame.pack(fill="x", padx=ModernStyle.CARD_PADDING, pady=(0, ModernStyle.CARD_PADDING))
        
        tk.Label(controls_frame, text="Date:", font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MEDIUM),
                bg=ModernStyle.CARD_COLOR, fg=ModernStyle.TEXT_COLOR).pack(side="left")
        
        self.date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        date_entry = tk.Entry(controls_frame, textvariable=self.date_var, 
                             font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MEDIUM), width=15)
        date_entry.pack(side="left", padx=10)
        
        load_btn = ModernButton(controls_frame, "📊 Load Report", self.load_report, "primary")
        load_btn.pack(side="left", padx=10)
        
        export_btn = ModernButton(controls_frame, "💾 Export CSV", self.export_report, "secondary")
        export_btn.pack(side="left", padx=10)
        
        # Reports table
        reports_frame = ModernFrame(self.content_frame, "Attendance Records")
        reports_frame.pack(fill="both", expand=True)
        
        # Create treeview for table
        columns = ("ID", "Name", "Date", "Time", "Status")
        self.reports_tree = ttk.Treeview(reports_frame, columns=columns, show="headings", height=15)
        
        # Configure column headings
        for col in columns:
            self.reports_tree.heading(col, text=col)
            self.reports_tree.column(col, width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(reports_frame, orient="vertical", command=self.reports_tree.yview)
        self.reports_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack table and scrollbar
        table_frame = tk.Frame(reports_frame, bg=ModernStyle.CARD_COLOR)
        table_frame.pack(fill="both", expand=True, padx=ModernStyle.CARD_PADDING, pady=(0, ModernStyle.CARD_PADDING))
        
        self.reports_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def show_students(self):
        """Show students list page"""
        self.clear_content()
        
        # Page title
        title_frame = tk.Frame(self.content_frame, bg=ModernStyle.BACKGROUND_COLOR)
        title_frame.pack(fill="x", pady=(0, 20))
        
        title_label = tk.Label(
            title_frame,
            text="👥 Students List",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_LARGE, "bold"),
            bg=ModernStyle.BACKGROUND_COLOR,
            fg=ModernStyle.TEXT_COLOR
        )
        title_label.pack(anchor="w")
        
        # Students table
        students_frame = ModernFrame(self.content_frame, "Registered Students")
        students_frame.pack(fill="both", expand=True)
        
        # Refresh button
        refresh_frame = tk.Frame(students_frame, bg=ModernStyle.CARD_COLOR)
        refresh_frame.pack(fill="x", padx=ModernStyle.CARD_PADDING, pady=(0, 10))
        
        refresh_btn = ModernButton(refresh_frame, "🔄 Refresh List", self.update_students_list, "primary")
        refresh_btn.pack(side="left")
        
        # Create treeview for students
        columns = ("ID", "Name", "Email", "Registration Date")
        self.students_tree = ttk.Treeview(students_frame, columns=columns, show="headings", height=15)
        
        # Configure column headings
        for col in columns:
            self.students_tree.heading(col, text=col)
            self.students_tree.column(col, width=150)
        
        # Scrollbar
        students_scrollbar = ttk.Scrollbar(students_frame, orient="vertical", command=self.students_tree.yview)
        self.students_tree.configure(yscrollcommand=students_scrollbar.set)
        
        # Pack table and scrollbar
        students_table_frame = tk.Frame(students_frame, bg=ModernStyle.CARD_COLOR)
        students_table_frame.pack(fill="both", expand=True, padx=ModernStyle.CARD_PADDING, pady=(0, ModernStyle.CARD_PADDING))
        
        self.students_tree.pack(side="left", fill="both", expand=True)
        students_scrollbar.pack(side="right", fill="y")
        
        # Load students data
        self.update_students_list()
    
    def show_camera_test(self):
        """Show camera test page"""
        self.clear_content()
        
        # Page title
        title_frame = tk.Frame(self.content_frame, bg=ModernStyle.BACKGROUND_COLOR)
        title_frame.pack(fill="x", pady=(0, 20))
        
        title_label = tk.Label(
            title_frame,
            text="📷 Camera Test",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_LARGE, "bold"),
            bg=ModernStyle.BACKGROUND_COLOR,
            fg=ModernStyle.TEXT_COLOR
        )
        title_label.pack(anchor="w")
        
        # Camera test frame
        test_frame = ModernFrame(self.content_frame, "Camera Testing")
        test_frame.pack(fill="both", expand=True)
        
        # Test camera display
        self.test_camera_label = tk.Label(
            test_frame,
            text="📷 Camera test will appear here",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MEDIUM),
            bg=ModernStyle.BACKGROUND_COLOR,
            fg=ModernStyle.TEXT_SECONDARY,
            width=80,
            height=20
        )
        self.test_camera_label.pack(padx=ModernStyle.CARD_PADDING, pady=10)
        
        # Test button
        test_btn = ModernButton(test_frame, "🧪 Test Camera", self.test_camera, "primary")
        test_btn.pack(padx=ModernStyle.CARD_PADDING, pady=10)
        
        # Status
        self.camera_test_status = StatusLabel(test_frame, text="", bg=ModernStyle.CARD_COLOR)
        self.camera_test_status.pack(fill="x", padx=ModernStyle.CARD_PADDING, pady=(0, ModernStyle.CARD_PADDING))
    
    def show_admin(self):
        """Show admin settings page"""
        self.clear_content()
        
        # Page title
        title_frame = tk.Frame(self.content_frame, bg=ModernStyle.BACKGROUND_COLOR)
        title_frame.pack(fill="x", pady=(0, 20))
        
        title_label = tk.Label(
            title_frame,
            text="🔐 Admin Settings",
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_LARGE, "bold"),
            bg=ModernStyle.BACKGROUND_COLOR,
            fg=ModernStyle.TEXT_COLOR
        )
        title_label.pack(anchor="w")
        
        # Password change frame
        password_frame = ModernFrame(self.content_frame, "Change Admin Password")
        password_frame.pack(fill="x", pady=(0, 20))
        
        # Password form
        form_frame = tk.Frame(password_frame, bg=ModernStyle.CARD_COLOR)
        form_frame.pack(fill="x", padx=ModernStyle.CARD_PADDING, pady=(0, ModernStyle.CARD_PADDING))
        
        # Current password
        tk.Label(form_frame, text="Current Password:", font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MEDIUM),
                bg=ModernStyle.CARD_COLOR, fg=ModernStyle.TEXT_COLOR).grid(row=0, column=0, sticky="w", pady=5)
        self.current_password_entry = tk.Entry(form_frame, show="*", font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MEDIUM), width=30)
        self.current_password_entry.grid(row=0, column=1, pady=5, padx=(10, 0), sticky="ew")
        
        # New password
        tk.Label(form_frame, text="New Password:", font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MEDIUM),
                bg=ModernStyle.CARD_COLOR, fg=ModernStyle.TEXT_COLOR).grid(row=1, column=0, sticky="w", pady=5)
        self.new_password_entry = tk.Entry(form_frame, show="*", font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MEDIUM), width=30)
        self.new_password_entry.grid(row=1, column=1, pady=5, padx=(10, 0), sticky="ew")
        
        # Confirm password
        tk.Label(form_frame, text="Confirm Password:", font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MEDIUM),
                bg=ModernStyle.CARD_COLOR, fg=ModernStyle.TEXT_COLOR).grid(row=2, column=0, sticky="w", pady=5)
        self.confirm_password_entry = tk.Entry(form_frame, show="*", font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_MEDIUM), width=30)
        self.confirm_password_entry.grid(row=2, column=1, pady=5, padx=(10, 0), sticky="ew")
        
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Change password button
        change_btn = ModernButton(password_frame, "🔑 Change Password", self.change_admin_password, "primary")
        change_btn.pack(padx=ModernStyle.CARD_PADDING, pady=10)
        
        # Status
        self.admin_status = StatusLabel(password_frame, text="", bg=ModernStyle.CARD_COLOR)
        self.admin_status.pack(fill="x", padx=ModernStyle.CARD_PADDING, pady=(0, ModernStyle.CARD_PADDING))
        
        # System info frame
        info_frame = ModernFrame(self.content_frame, "System Information")
        info_frame.pack(fill="both", expand=True)
        
        info_text = tk.Text(
            info_frame,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL),
            bg=ModernStyle.CARD_COLOR,
            fg=ModernStyle.TEXT_COLOR,
            relief="flat",
            bd=0,
            wrap="word"
        )
        info_text.pack(fill="both", expand=True, padx=ModernStyle.CARD_PADDING, pady=(0, ModernStyle.CARD_PADDING))
        
        info_content = """Face Recognition Attendance System v2.0

Security Features:
• Ultra-strict face similarity detection
• Multi-algorithm fraud prevention
• Admin password protection
• Comprehensive duplicate checking
• Security event logging

Security Thresholds:
• Ultra High Similarity (45%+): Auto-block
• High Similarity (35%+): Auto-block
• Suspicious Similarity (25%+): Admin review

Technical Details:
• Framework: Tkinter (Built-in Python GUI)
• Face Detection: OpenCV Haar Cascades
• Recognition: LBPH (Local Binary Pattern Histograms)
• Security: SHA-256 password hashing
• Data Storage: CSV files with UTF-8 encoding"""
        
        info_text.insert("1.0", info_content)
        info_text.config(state="disabled")

    def start_registration(self):
        """Start the student registration process using main_system"""
        student_id = self.student_id_entry.get().strip()
        name = self.student_name_entry.get().strip()
        email = self.student_email_entry.get().strip()
        
        if not student_id or not name or not email:
            messagebox.showwarning("Input Error", "Please fill in all fields")
            return
        
        if not self.face_system:
            messagebox.showerror("System Error", "Face recognition system not initialized")
            return
        
        # Validate student ID is numeric
        try:
            student_id_int = int(student_id)
        except ValueError:
            messagebox.showerror("Input Error", "Student ID must be a number")
            return
        
        # Admin password check using GUI dialog
        admin_password = simpledialog.askstring("Admin Authentication", "Enter admin password:", show='*')
        if not admin_password:
            return
        
        # Disable inputs and buttons during registration
        self.set_registration_form_state(tk.DISABLED)
        self.register_status.set_status("Verifying admin password...", "info")
        
        def register():
            try:
                # Verify admin password using main system
                import sys
                from io import StringIO
                import getpass
                
                # Backup original getpass function
                original_getpass = getpass.getpass
                
                # Create a mock getpass function that returns our password
                def mock_getpass(prompt="Password: "):
                    return admin_password
                
                # Temporarily replace getpass
                getpass.getpass = mock_getpass
                
                try:
                    # Use main system's verification
                    if not self.face_system.verify_admin_password():
                        self.register_status.set_status("Authentication failed!", "error")
                        messagebox.showerror("Authentication Failed", "Incorrect admin password")
                        return
                    
                    self.register_status.set_status("Admin authenticated. Starting registration...", "success")
                    
                    # Use main system's register_student method
                    result = self.face_system.register_student(student_id_int, name, email)
                    
                    if result:
                        self.register_status.set_status("Student registered successfully!", "success")
                        messagebox.showinfo("Registration Complete", f"Student {name} registered successfully!")
                        # Clear form after delay
                        self.root.after(2000, self.clear_registration_form)
                    else:
                        self.register_status.set_status("Registration failed!", "error")
                        messagebox.showerror("Registration Failed", "Registration process failed. Check console for details.")
                        
                finally:
                    # Restore original getpass
                    getpass.getpass = original_getpass
            
            except Exception as e:
                error_msg = f"Registration error: {str(e)}"
                self.register_status.set_status(error_msg, "error")
                messagebox.showerror("Registration Error", error_msg)
            
            finally:
                # Re-enable inputs and buttons
                self.root.after(100, lambda: self.set_registration_form_state(tk.NORMAL))
        
        # Run registration in a separate thread
        threading.Thread(target=register, daemon=True).start()
    
    def set_registration_form_state(self, state):
        """Enable or disable the registration form inputs and buttons"""
        self.student_id_entry.config(state=state)
        self.student_name_entry.config(state=state)
        self.student_email_entry.config(state=state)
        self.register_status.config(state=state)
        
        if state == tk.DISABLED:
            self.start_registration_btn.config(state=tk.DISABLED)
            self.clear_form_btn.config(state=tk.DISABLED)
        else:
            self.start_registration_btn.config(state=tk.NORMAL)
            self.clear_form_btn.config(state=tk.NORMAL)
    
    def clear_registration_form(self):
        """Clear the registration form fields"""
        self.student_id_entry.delete(0, tk.END)
        self.student_name_entry.delete(0, tk.END)
        self.student_email_entry.delete(0, tk.END)
        self.register_status.set_status("", "info")
    
    def start_training(self):
        """Start the model training process using main_system"""
        if not self.face_system:
            messagebox.showerror("System Error", "Face recognition system not initialized")
            return
        
        self.train_status.set_status("Starting model training...", "info")
        self.train_progress.config(value=0)
        
        def train_model():
            try:
                self.train_progress.config(value=20)
                self.train_status.set_status("Training model using main system...", "info")
                
                # Use main system's train_model method
                result = self.face_system.train_model()
                
                self.train_progress.config(value=100)
                
                if result:
                    self.train_status.set_status("Model training completed successfully!", "success")
                    messagebox.showinfo("Training Complete", "Face recognition model trained successfully!")
                else:
                    self.train_status.set_status("Training failed!", "error")
                    messagebox.showerror("Training Failed", "Model training failed. Check console for details.")
                    self.train_progress.config(value=0)
            
            except Exception as e:
                error_msg = f"Training error: {str(e)}"
                self.train_status.set_status(error_msg, "error")
                self.train_progress.config(value=0)
                messagebox.showerror("Training Error", error_msg)
        
        # Run training in a separate thread
        threading.Thread(target=train_model, daemon=True).start()
    
    def start_attendance(self):
        """Start the attendance marking process using main_system"""
        if not self.face_system:
            messagebox.showerror("System Error", "Face recognition system not initialized")
            return
        
        # Check if model exists by trying to load it in main system
        try:
            # Test if model exists and can be loaded
            if not os.path.exists(self.face_system.model_file):
                messagebox.showerror("Model Error", "No trained model found. Please train the model first.")
                return
        except Exception as e:
            messagebox.showerror("Model Error", f"Model check failed: {str(e)}")
            return
        
        self.attendance_status.set_status("Starting attendance system...", "info")
        
        def mark_attendance():
            try:
                # Use main system's mark_attendance method
                self.attendance_status.set_status("Attendance system running. Press ESC in camera window to exit.", "success")
                
                # Call main system's mark attendance method
                self.face_system.mark_attendance()
                
                self.attendance_status.set_status("Attendance system stopped", "info")
                # Update today's attendance display
                self.update_today_attendance()
                
            except Exception as e:
                error_msg = f"Attendance error: {str(e)}"
                self.attendance_status.set_status(error_msg, "error")
                messagebox.showerror("Attendance Error", error_msg)
        
        # Run attendance in a separate thread
        threading.Thread(target=mark_attendance, daemon=True).start()
    
    def start_camera(self):
        """Start the camera for attendance marking using main system"""
        try:
            # Check if attendance system is ready using main system
            ready, message = self.face_system.check_attendance_ready()
            if not ready:
                self.attendance_status.set_status(f"Error: {message}", "error")
                messagebox.showerror("System Not Ready", message)
                return
            
            # Initialize attendance system
            if not self.face_system.mark_attendance_gui(self.gui_status_callback):
                return  # Error already reported via callback
            
            self.camera_active = True
            self.start_camera_btn.config(state="disabled")
            self.stop_camera_btn.config(state="normal")
            
            # Start camera in a separate thread to avoid blocking GUI
            import threading
            camera_thread = threading.Thread(target=self.run_attendance_camera, daemon=True)
            camera_thread.start()
            
        except Exception as e:
            self.attendance_status.set_status(f"Error starting camera: {str(e)}", "error")
            messagebox.showerror("Camera Error", f"Failed to start camera:\n{str(e)}")
            self.camera_active = False
    
    def gui_status_callback(self, message, status_type):
        """Callback function to update GUI status from main system"""
        self.root.after(0, lambda: self.attendance_status.set_status(message, status_type))
    
    def run_attendance_camera(self):
        """Run the attendance camera using main system logic"""
        try:
            # Load students data using main system
            students_df = pd.read_csv(self.face_system.students_csv)
            
            # Initialize camera
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                self.root.after(0, lambda: self.attendance_status.set_status("❌ Cannot access camera!", "error"))
                return
            
            self.root.after(0, lambda: self.attendance_status.set_status("📷 Camera started! Position face clearly. Attendance marked automatically.", "success"))
            
            marked_today = set()
            recognition_frames = 0
            required_frames = 5  # Consecutive frames for recognition
            last_recognized = None
            confidence_threshold = 70
            
            while self.camera_active:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Convert to grayscale for face detection
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_system.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(100, 100))
                
                current_recognition = None
                
                for (x, y, w, h) in faces:
                    # Draw rectangle around face
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    
                    # Extract and resize face
                    face_region = gray[y:y+h, x:x+w]
                    face_region = cv2.resize(face_region, (200, 200))
                    
                    # Recognize face using main system's recognizer
                    student_id, confidence = self.face_system.recognizer.predict(face_region)
                    
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
                            # Use main system's save_attendance_record method
                            if self.face_system.save_attendance_record(student_id, name):
                                marked_today.add(student_id)
                                # Update GUI status
                                self.root.after(0, lambda n=name, sid=student_id: 
                                    self.attendance_status.set_status(f"✅ Attendance marked for {n} (ID: {sid})", "success"))
                                # Update today's attendance list
                                self.root.after(0, self.update_today_attendance)
                            else:
                                # Student already marked today
                                self.root.after(0, lambda n=name: 
                                    self.attendance_status.set_status(f"ℹ️ {n} already marked today", "warning"))
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
                if key == ord('q') or key == ord('Q') or not self.camera_active:
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            
            # Update final status
            if len(marked_today) > 0:
                self.root.after(0, lambda: self.attendance_status.set_status(
                    f"📊 Session completed! {len(marked_today)} students marked present today.", "success"))
            else:
                self.root.after(0, lambda: self.attendance_status.set_status(
                    "📊 Session completed. No new attendance marked.", "info"))
            
        except Exception as e:
            error_msg = f"❌ Camera error: {str(e)}"
            self.root.after(0, lambda: self.attendance_status.set_status(error_msg, "error"))
            self.root.after(0, lambda: messagebox.showerror("Camera Error", error_msg))
        finally:
            self.camera_active = False
            self.root.after(0, lambda: self.start_camera_btn.config(state="normal"))
            self.root.after(0, lambda: self.stop_camera_btn.config(state="disabled"))
    
    def stop_camera(self):
        """Stop the camera"""
        self.camera_active = False
        self.start_camera_btn.config(state="normal")
        self.stop_camera_btn.config(state="disabled")
        self.attendance_status.set_status("⏹️ Stopping camera...", "info")
        
        # Close all OpenCV windows
        cv2.destroyAllWindows()
        
        self.attendance_status.set_status("📷 Camera stopped", "info")
    
    def update_today_attendance(self):
        """Update the today's attendance list using main system"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Use main system's attendance file
            if os.path.exists(self.face_system.attendance_csv):
                attendance_df = pd.read_csv(self.face_system.attendance_csv)
                today_attendance = attendance_df[attendance_df['date'] == today]
                
                # Clear existing entries
                self.today_listbox.delete(0, tk.END)
                
                # Add today's attendance records
                for _, record in today_attendance.iterrows():
                    name = record.get('name', 'Unknown')
                    time = record.get('time', 'Unknown')
                    self.today_listbox.insert(tk.END, f"✅ {name} - {time}")
                    
                # Update status with count
                count = len(today_attendance)
                if hasattr(self, 'camera_active') and self.camera_active:
                    # Schedule next update only if camera is active
                    self.root.after(5000, self.update_today_attendance)  # Update every 5 seconds
                    
        except Exception as e:
            print(f"Error updating today's attendance: {e}")  # Log error but don't show to user
    
    def load_report(self):
        """Load the attendance report for the selected date using main system format"""
        date = self.date_var.get().strip()
        
        if not date:
            messagebox.showwarning("Input Error", "Please enter a date")
            return
        
        try:
            # Check if attendance file exists
            if not os.path.exists(self.face_system.attendance_csv):
                messagebox.showinfo("No Data", "No attendance records found")
                return
            
            # Load attendance data from main system
            attendance_df = pd.read_csv(self.face_system.attendance_csv)
            
            # Filter by date
            report_df = attendance_df[attendance_df['date'] == date]
            
            if report_df.empty:
                messagebox.showinfo("No Data", f"No attendance records found for {date}")
                return
            
            # Clear existing data
            for i in self.reports_tree.get_children():
                self.reports_tree.delete(i)
            
            # Insert new data using main system format
            for _, row in report_df.iterrows():
                student_id = row.get('student_id', 'N/A')
                name = row.get('name', 'N/A')
                date_val = row.get('date', 'N/A')
                time_val = row.get('time', 'N/A')
                status = row.get('status', 'Present')
                
                self.reports_tree.insert("", "end", values=(
                    student_id, name, date_val, time_val, status
                ))
            
            self.update_status(f"Loaded {len(report_df)} records for {date}")
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load report:\n{str(e)}")
    
    def export_report(self):
        """Export the current report view to CSV"""
        date = self.date_var.get().strip()
        
        if not date:
            messagebox.showwarning("Input Error", "Please enter a date")
            return
        
        try:
            # Get the current report data
            report_data = []
            for row in self.reports_tree.get_children():
                report_data.append(self.reports_tree.item(row)["values"])
            
            if not report_data:
                messagebox.showinfo("No Data", "No data to export")
                return
            
            # Create a DataFrame
            columns = ["ID", "Name", "Date", "Time", "Status"]
            report_df = pd.DataFrame(report_data, columns=columns)
            
            # Export to CSV
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            
            if file_path:
                report_df.to_csv(file_path, index=False, encoding="utf-8")
                messagebox.showinfo("Export Successful", f"Report exported to:\n{file_path}")
                self.attendance_status.set_status(f"Report exported: {file_path}", "success")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export report:\n{str(e)}")
    
    def update_students_list(self):
        """Update the students list using main system format"""
        try:
            if os.path.exists(self.face_system.students_csv):
                students_df = pd.read_csv(self.face_system.students_csv)
                
                # Clear the treeview
                for i in self.students_tree.get_children():
                    self.students_tree.delete(i)
                
                # Insert new data using main system format
                for _, row in students_df.iterrows():
                    student_id = row.get('student_id', 'N/A')
                    name = row.get('name', 'N/A')
                    email = row.get('email', 'N/A')
                    reg_date = row.get('registration_date', 'N/A')
                    
                    self.students_tree.insert("", "end", values=(
                        student_id, name, email, reg_date
                    ))
                
                self.update_status("Students list updated")
            else:
                self.update_status("No student data found")
        except Exception as e:
            messagebox.showerror("Update Error", f"Failed to update students list:\n{str(e)}")
    
    def test_camera(self):
        """Test the camera functionality"""
        self.camera_test_status.set_status("Starting camera test...", "info")
        
        def run_test():
            try:
                # Open the default camera
                cap = cv2.VideoCapture(0)
                
                if not cap.isOpened():
                    raise Exception("Could not open camera")
                
                self.camera_test_status.set_status("Camera test running. Press 'q' to quit.", "success")
                
                while True:
                    ret, frame = cap.read()
                    
                    if not ret:
                        break
                    
                    # Display the camera feed
                    cv2.imshow("Camera Test", frame)
                    
                    # Wait for key press
                    key = cv2.waitKey(1) & 0xFF
                    
                    if key == ord('q'):  # 'q' key to quit
                        break
                
                cap.release()
                cv2.destroyAllWindows()
                
                self.camera_test_status.set_status("Camera test stopped", "info")
            except Exception as e:
                self.camera_test_status.set_status(f"Error: {str(e)}", "error")
                messagebox.showerror("Camera Test Error", f"An error occurred with the camera:\n{str(e)}")
        
        # Run camera test in a separate thread
        threading.Thread(target=run_test, daemon=True).start()
    
    def change_admin_password(self):
        """Change the admin password using main_system"""
        current_password = self.current_password_entry.get().strip()
        new_password = self.new_password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()
        
        if not current_password or not new_password or not confirm_password:
            messagebox.showwarning("Input Error", "Please fill in all fields")
            return
        
        if new_password != confirm_password:
            messagebox.showwarning("Input Error", "New password and confirm password do not match")
            return
        
        if len(new_password) < 6:
            messagebox.showwarning("Input Error", "Password must be at least 6 characters long")
            return
        
        try:
            # Verify current password using main system
            import getpass
            original_getpass = getpass.getpass
            
            def mock_getpass(prompt="Password: "):
                return current_password
            
            getpass.getpass = mock_getpass
            
            try:
                if not self.face_system.verify_admin_password():
                    messagebox.showerror("Authentication Error", "Current password is incorrect")
                    return
                
                # Now set the new password by mocking the update process
                def mock_new_getpass(prompt="Password: "):
                    if "new" in prompt.lower():
                        return new_password
                    elif "confirm" in prompt.lower():
                        return confirm_password
                    return new_password
                
                getpass.getpass = mock_new_getpass
                
                # Call main system's update password method
                result = self.face_system.update_admin_password()
                
                if result:
                    self.admin_status.set_status("Password changed successfully", "success")
                    messagebox.showinfo("Success", "Admin password updated successfully!")
                    # Clear form after delay
                    self.root.after(1500, self.clear_admin_password_form)
                else:
                    self.admin_status.set_status("Password change failed", "error")
                    messagebox.showerror("Error", "Failed to update password")
                    
            finally:
                getpass.getpass = original_getpass
                
        except Exception as e:
            self.admin_status.set_status(f"Error: {str(e)}", "error")
            messagebox.showerror("Password Change Error", f"Failed to change password:\n{str(e)}")
    
    def clear_admin_password_form(self):
        """Clear the admin password change form"""
        self.current_password_entry.delete(0, tk.END)
        self.new_password_entry.delete(0, tk.END)
        self.confirm_password_entry.delete(0, tk.END)
        self.admin_status.set_status("", "info")

    def verify_admin_password(self, password):
        """Verify admin password using main_system method"""
        try:
            if not self.face_system:
                messagebox.showerror("System Error", "Face recognition system not initialized")
                return False
            
            # Use the main system's password verification
            # Temporarily store the password for verification
            temp_file = "temp_password.txt"
            with open(temp_file, 'w') as f:
                f.write(password)
            
            # Use main system's verify method by temporarily modifying getpass
            import sys
            from io import StringIO
            
            # Backup original stdin
            original_stdin = sys.stdin
            
            try:
                # Create a StringIO object with the password
                sys.stdin = StringIO(password + '\n')
                
                # Call the main system's verify_admin_password method
                result = self.face_system.verify_admin_password()
                
                return result
            finally:
                # Restore original stdin
                sys.stdin = original_stdin
                # Clean up temp file
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    
        except Exception as e:
            messagebox.showerror("Password Error", f"Error verifying password: {str(e)}")
            return False

def run_gui():
    """Run the Tkinter GUI"""
    gui = FaceRecognitionGUI()
    gui.root.mainloop()

if __name__ == "__main__":
    run_gui()
