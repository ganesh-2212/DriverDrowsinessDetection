# Driver Drowsiness Monitoring System

A real-time driver monitoring system that uses YOLOv8-based computer vision to detect unsafe driver behaviors such as drowsiness, yawning, mobile phone usage, and drinking. The system generates instant alerts via hardware communication and enables remote monitoring through a mobile application.

---

## System Overview

The system consists of two integrated components:

- A Python-based desktop application that captures webcam input, performs real-time detection, displays a live dashboard, and sends alerts through serial communication.
- A mobile application developed using React Native that retrieves driver status from a backend API and displays location-based monitoring.

---

## Features

- Real-time detection of driver states:
  - Drowsy
  - Awake
  - Yawning
  - Mobile phone usage
  - Drinking

- YOLOv8-based object detection with confidence scoring
- Confidence smoothing using exponential moving average
- Time-based drowsiness alert to reduce false positives
- Real-time dashboard with visual indicators
- REST API for live data access
- Mobile-based monitoring with location tracking

---

## Technology Stack

- YOLOv8 for object detection
- Python with OpenCV for video processing
- Tkinter and Matplotlib for desktop interface
- Flask for REST API
- PySerial for hardware communication
- React Native (Expo) for mobile application
- Map and location libraries for tracking

---

## Setup and Installation

### Python Application

Install dependencies:

pip install ultralytics opencv-python flask pyserial Pillow matplotlib numpy

Run the application:

python main.py

Ensure the trained model file is correctly configured and update the serial port if required.

---

### Mobile Application

Install dependencies:

npm install

Start the application:

npx expo start

Update the API endpoint in the mobile code to match the backend server IP.

---

## API Endpoint

GET /detections

Sample response:

{
  "status": "Drowsy",
  "detections": {
    "Drowsy": 0.82,
    "Awake": 0.10,
    "Yawning": 0.05,
    "Mobile": 0.00,
    "Drinking": 0.00
  },
  "timestamp": "05-03-2026 14:32:01"
}

---

## Alert Logic

- Drowsiness above threshold for a continuous duration triggers a hardware alert
- Other detected states send corresponding signals
- No detection results in a default signal

---

## Project Structure

driver_drowsiness/
├── app/
│   └── (tabs)/
│       ├── _layout.tsx
│       ├── index.tsx
│       └── explore.tsx
├── assets/images/
├── components/
│   └── ui/
├── constants/
├── hooks/
├── scripts/
├── app.json
├── package.json
├── tsconfig.json
└── README.md

---

## License

This project is intended for educational and research purposes.