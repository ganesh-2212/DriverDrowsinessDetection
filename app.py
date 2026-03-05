from datetime import datetime
import cv2
from flask import Flask, jsonify
import serial
import time
import threading
import numpy as np
from ultralytics import YOLO
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation

flask_app = Flask(__name__)
driver_app_instance = None
class DriverMonitoringApp:
    def __init__(self):
        # Initialize main window
        self.last_boxes = []
        self.last_update_time = time.time()

        self.root = tk.Tk()
        self.root.title("Driver Monitoring Dashboard")
        self.root.geometry("1400x800")
        self.root.configure(bg='#0c0c0c')
        
        # Configure style
        self.setup_styles()
        
        # Initialize components
        self.setup_serial()
        self.setup_yolo()
        self.setup_camera()
        
        # Detection data
        self.detection_data = {
            "Drowsy": 0.0,
            "Awake": 0.0,
            "Yawning": 0.0,
            "Mobile": 0.0,
            "Drinking": 0.0
        }
        self.detection_lock = threading.Lock()
        
        # Setup GUI
        self.setup_gui()
        self.drowsy_start_time = None
        self.is_drowsy_sent = False

        
        # Start processing threads
        self.running = True
        self.start_threads()
        
    def setup_styles(self):
        """Configure tkinter styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Title.TLabel', 
                       background='#0c0c0c', 
                       foreground='#00d4ff', 
                       font=('Arial', 24, 'bold'))
        
        style.configure('Section.TLabel', 
                       background='#1a1a2e', 
                       foreground='#ffffff', 
                       font=('Arial', 16, 'bold'))
        
        style.configure('Value.TLabel', 
                       background='#1a1a2e', 
                       foreground='#00d4ff', 
                       font=('Arial', 12, 'bold'))
        
    def setup_serial(self):
        """Initialize serial connection"""
        try:
            self.ser = serial.Serial("COM14", 9600, timeout=1)
            time.sleep(2)
            print("✅ Serial connection established")
        except:
            print("⚠️ Warning: Could not connect to serial port")
            self.ser = None
            
    def setup_yolo(self):
        """Initialize YOLO model"""
        try:
            self.model = YOLO("runs/detect/merged_yolo8_drive3/weights/best.pt")
            print("✅ YOLO model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading YOLO model: {e}")
            self.model = None
            
    def setup_camera(self):
        """Initialize camera"""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise RuntimeError("❌ Error: Could not open webcam")
            
        # Optimize camera settings
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        print("✅ Camera initialized")
        
    def setup_gui(self):
        """Setup the GUI layout"""
        # Main title
        title_label = ttk.Label(self.root, text="Driver Monitoring Dashboard", style='Title.TLabel')
        title_label.pack(pady=20)
        
        # Create main frame
        main_frame = tk.Frame(self.root, bg='#0c0c0c')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left side - Video feed
        self.setup_video_frame(main_frame)
        
        # Right side - Chart and indicators
        self.setup_chart_frame(main_frame)
        
    def setup_video_frame(self, parent):
        """Setup video display frame"""
        video_frame = tk.Frame(parent, bg='#1a1a2e', relief=tk.RAISED, bd=2)
        video_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Video title
        video_title = ttk.Label(video_frame, text="LIVE CAMERA FEED", style='Section.TLabel')
        video_title.pack(pady=10)
        
        # Video display
        self.video_label = tk.Label(video_frame, bg='#000000')
        self.video_label.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Status indicators
        status_frame = tk.Frame(video_frame, bg='#1a1a2e')
        status_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Live indicator
        live_frame = tk.Frame(status_frame, bg='#1a1a2e')
        live_frame.pack(side=tk.RIGHT)
        
        self.live_dot = tk.Label(live_frame, text="●", fg='#4caf50', bg='#1a1a2e', font=('Arial', 16))
        self.live_dot.pack(side=tk.LEFT)
        
        live_text = tk.Label(live_frame, text="LIVE", fg='#4caf50', bg='#1a1a2e', font=('Arial', 12, 'bold'))
        live_text.pack(side=tk.LEFT, padx=(5, 0))
        
    def setup_chart_frame(self, parent):
        """Setup chart and indicators frame"""
        chart_frame = tk.Frame(parent, bg='#1a1a2e', relief=tk.RAISED, bd=2)
        chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Chart title
        chart_title = ttk.Label(chart_frame, text="DETECTION CONFIDENCE", style='Section.TLabel')
        chart_title.pack(pady=10)
        
        # Setup matplotlib chart
        self.setup_matplotlib_chart(chart_frame)
        
        # Setup value indicators
        self.setup_indicators(chart_frame)
        
    def setup_matplotlib_chart(self, parent):
        """Setup matplotlib bar chart"""
        # Create figure with dark theme
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(figsize=(8, 6), facecolor='#1a1a2e')
        self.ax.set_facecolor('#1a1a2e')
        
        # Initialize bars
        self.categories = list(self.detection_data.keys())
        self.values = list(self.detection_data.values())
        
        # Color scheme for bars
        self.colors = {
            'Drowsy': '#ff6b6b',
            'Awake': '#4ecdc4', 
            'Yawning': '#ffe66d',
            'Mobile': '#ff8b94',
            'Drinking': '#a8e6cf'
        }
        
        bar_colors = [self.colors[cat] for cat in self.categories]
        self.bars = self.ax.bar(self.categories, self.values, color=bar_colors, alpha=0.8)
        
        # Customize chart
        self.ax.set_ylim(0, 1.0)
        self.ax.set_ylabel('Confidence', color='#ffffff', fontsize=12)
        self.ax.set_title('Real-time Detection Confidence', color='#00d4ff', fontsize=14, fontweight='bold')
        self.ax.tick_params(colors='#ffffff')
        self.ax.grid(True, alpha=0.3)
        
        # Rotate x-axis labels
        plt.setp(self.ax.get_xticklabels(), rotation=45, ha='right')
        
        # Add value labels on bars
        self.value_labels = []
        for i, bar in enumerate(self.bars):
            label = self.ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                               '0.00', ha='center', va='bottom', color='#ffffff', fontweight='bold')
            self.value_labels.append(label)
        
        # Embed in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
    def setup_indicators(self, parent):
        """Setup numerical indicators"""
        indicators_frame = tk.Frame(parent, bg='#1a1a2e')
        indicators_frame.pack(fill=tk.X, pady=10, padx=10)
        
        self.indicator_labels = {}
        
        for i, (category, value) in enumerate(self.detection_data.items()):
            # Create indicator frame
            indicator_frame = tk.Frame(indicators_frame, bg='#2a2a3e', relief=tk.RAISED, bd=1)
            indicator_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, pady=5)
            
            # Category label
            cat_label = tk.Label(indicator_frame, text=category, 
                               bg='#2a2a3e', fg='#888888', font=('Arial', 10))
            cat_label.pack(pady=(5, 0))
            
            # Value label
            value_label = tk.Label(indicator_frame, text="0.00", 
                                 bg='#2a2a3e', fg='#ffffff', font=('Arial', 14, 'bold'))
            value_label.pack(pady=(0, 5))
            
            self.indicator_labels[category] = {
                'frame': indicator_frame,
                'value': value_label
            }
    
    def start_threads(self):
        """Start processing threads"""
        # Video processing thread
        self.video_thread = threading.Thread(target=self.video_loop, daemon=True)
        self.video_thread.start()
        
        # Detection processing thread
        self.detection_thread = threading.Thread(target=self.detection_loop, daemon=True)
        self.detection_thread.start()
        
        self.update_chart_loop()

        
        # Live indicator animation
        self.animate_live_indicator()
        
    def video_loop(self):
        """Main video processing loop"""
        frame_count = 0
        
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue
                
            frame_count += 1
            frame = cv2.resize(frame, (640, 480))
            
            if frame_count % 3 == 0 and self.model:
                # process_detection now draws bounding boxes
                annotated_frame = frame.copy()
                self.process_detection(annotated_frame)
            else:
                annotated_frame = frame

            # Convert frame for display
            frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            frame_pil = Image.fromarray(frame_rgb)
            frame_tk = ImageTk.PhotoImage(frame_pil)
            
            # Update video display
            self.video_label.configure(image=frame_tk)
            self.video_label.image = frame_tk
            
            time.sleep(0.033)  # ~30 FPS

    def process_detection(self, frame):
      
      try:
        results = self.model(frame)
        
        current_detections = {
            "Drowsy": 0.0,
            "Awake": 0.0,
            "Yawning": 0.0,
            "Mobile": 0.0,
            "Drinking": 0.0
        }
        new_boxes = []
        
        if results[0].boxes is not None and len(results[0].boxes) > 0:
            names = results[0].names
            boxes = results[0].boxes
            
            for box in boxes:
                class_id = int(box.cls.cpu().numpy())
                confidence = float(box.conf.cpu().numpy())
                xyxy = box.xyxy.cpu().numpy().astype(int)[0]  # [x1, y1, x2, y2]
                
                if class_id in names:
                    class_name = names[class_id]
                    if class_name in current_detections:
                        current_detections[class_name] = max(current_detections[class_name], confidence)
                        new_boxes.append((class_name, confidence, xyxy))
        
        # ✅ Keep last boxes for 0.5 sec if nothing new
        if new_boxes:
            self.last_boxes = new_boxes
            self.last_update_time = time.time()
        elif time.time() - self.last_update_time < 0.5:
            new_boxes = self.last_boxes
        
        # Draw boxes manually to avoid flicker
        for (cls, conf, (x1, y1, x2, y2)) in new_boxes:
            label = f"{cls} {conf:.2f}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,0,255), 2)  # red box
            cv2.putText(frame, label, (x1, y1-10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)  # red text

        
        # Smooth detection scores
        with self.detection_lock:
            for key, value in current_detections.items():
                self.detection_data[key] = self.detection_data[key] * 0.7 + value * 0.3
        
        self.send_serial_data(current_detections)
        
      except Exception as e:
        print(f"Detection error: {e}")

    def send_serial_data(self, detections):
        """Send detection data to serial port"""
        if not self.ser:
            return

        try:
            max_detection = max(detections.items(), key=lambda x: x[1])
            label, confidence = max_detection

            # ✅ If Drowsy detected
            if label == "Drowsy" and confidence > 0.5:  
                if self.drowsy_start_time is None:
                    self.drowsy_start_time = time.time()
                elif time.time() - self.drowsy_start_time >= 3.0 and not self.is_drowsy_sent:
                    self.ser.write(b"Drowsy\n")
                    self.is_drowsy_sent = True
            else:
                # Reset when not Drowsy
                self.drowsy_start_time = None
                self.is_drowsy_sent = False

                if confidence > 0.3:
                    self.ser.write((label + "\n").encode("utf-8"))
                else:
                    self.ser.write(b"None\n")

        except Exception as e:
            print(f"Serial send error: {e}")

            
    def detection_loop(self):
        """Detection processing loop"""
        while self.running:
            time.sleep(0.1)  # 10 FPS for detection updates
            
    def chart_update_loop(self):
        """Chart update loop"""
        while self.running:
            self.update_chart()
            time.sleep(0.2)  # 5 FPS for chart updates
            
    def update_chart(self):
        """Update the bar chart and indicators"""
        try:
            with self.detection_lock:
                current_data = self.detection_data.copy()
            
            # Update bars
            for i, (category, value) in enumerate(current_data.items()):
                self.bars[i].set_height(value)
                self.value_labels[i].set_text(f'{value:.2f}')
                self.value_labels[i].set_position((self.bars[i].get_x() + self.bars[i].get_width()/2, value + 0.01))
                
                # Update indicator
                if category in self.indicator_labels:
                    self.indicator_labels[category]['value'].configure(text=f'{value:.2f}')
                    
                    # Highlight active indicators
                    if value > 0.5:
                        self.indicator_labels[category]['frame'].configure(bg='#00d4ff', relief=tk.RAISED)
                        self.indicator_labels[category]['value'].configure(fg='#000000')
                    else:
                        self.indicator_labels[category]['frame'].configure(bg='#2a2a3e', relief=tk.RAISED)
                        self.indicator_labels[category]['value'].configure(fg='#ffffff')
            
            # Redraw canvas
            self.canvas.draw_idle()
            
        except Exception as e:
            print(f"Chart update error: {e}")
    
    def update_chart_loop(self):

        self.update_chart()
        if self.running:
           self.root.after(200, self.update_chart_loop)  # update every 200ms

            
    def animate_live_indicator(self):
        """Animate the live indicator"""
        current_color = self.live_dot.cget('fg')
        new_color = '#4caf50' if current_color == '#2e7d32' else '#2e7d32'
        self.live_dot.configure(fg=new_color)
        
        if self.running:
            self.root.after(1000, self.animate_live_indicator)
            
    def cleanup(self):
        """Cleanup resources"""
        self.running = False
        
        if self.cap:
            self.cap.release()
            
        if self.ser:
            self.ser.close()
            
        cv2.destroyAllWindows()              
    
        
    def run(self):
        """Run the application"""
        try:
            print("🚀 Starting Driver Monitoring Dashboard...")
            print("📊 Dashboard window should open shortly...")
            print("⚡ Optimized for real-time performance")
            
            # Handle window close
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            # Start the GUI
            self.root.mainloop()
            
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.cleanup()
            
    def on_closing(self):
        """Handle window closing"""
        self.cleanup()
        self.root.destroy()

@flask_app.route("/detections", methods=["GET"])
def get_detections():
    """Return the latest detection data as JSON"""
    global driver_app_instance
    if driver_app_instance:
        with driver_app_instance.detection_lock:
            # Round values to 2 decimals
            rounded_data = {k: round(v, 2) for k, v in driver_app_instance.detection_data.items()}

            # Pick the most confident detection
            status = max(rounded_data, key=rounded_data.get)

            # Custom timestamp format: dd-mm-yyyy h:m:s
            timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

            # Build clean response
            response = {
                "status": status if rounded_data[status] > 0.3 else "None",
                "detections": rounded_data,
                "timestamp": timestamp
            }
            return jsonify(response)
    else:
        return jsonify({"error": "Driver app not initialized"}), 500

def run_flask():
    flask_app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

if __name__ == "__main__":

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    driver_app_instance = DriverMonitoringApp()
    driver_app_instance.run()