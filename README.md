# 🚗 Driver Drowsiness Monitoring System

A real-time driver monitoring system that uses computer vision (YOLOv8) to detect driver states such as drowsiness, yawning, phone usage, and drinking — with live alerts via serial communication and a companion mobile app for location tracking.

---

## 📸 System Overview

The system consists of two components:

1. **Python Desktop App** — captures webcam feed, runs YOLO inference, displays a live dashboard, and sends alerts to a hardware device via serial (e.g., Arduino).
2. **React Native Mobile App** — polls the Flask API for driver status, shows the driver's location on a map, and allows sharing status via WhatsApp.

---

## 🧠 Features

- **Real-time detection** of: Drowsy, Awake, Yawning, Mobile (phone use), Drinking
- **YOLOv8-powered** bounding box detection with confidence scores
- **Smoothed confidence scores** using exponential moving average
- **Drowsiness alert**: triggers serial signal after 3 continuous seconds of drowsiness
- **Live Tkinter dashboard** with animated bar chart and detection indicators
- **Flask REST API** (`/detections`) exposing real-time detection status as JSON
- **React Native mobile app** with map view, live status polling, and WhatsApp sharing

---

## 🗂️ Project Structure

```
driver_drowsiness/
├── app/
│   └── (tabs)/
│       ├── _layout.tsx       # Tab navigator layout
│       ├── index.tsx         # Main screen: map + driver status + WhatsApp share
│       └── explore.tsx       # Explore tab with app info
├── assets/images/            # App icons and splash screen
├── components/               # Reusable UI components
│   └── ui/
│       ├── collapsible.tsx
│       ├── icon-symbol.tsx
│       └── icon-symbol.ios.tsx
├── constants/theme.ts        # Colors and fonts
├── hooks/                    # Custom React hooks
├── scripts/reset-project.js  # Project reset utility
├── app.json                  # Expo configuration
├── package.json
├── tsconfig.json
└── README.md
```

> The Python desktop app (`main.py` or equivalent) lives outside the Expo project directory.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Detection Model | YOLOv8 (Ultralytics) |
| Desktop UI | Python, Tkinter, Matplotlib |
| Video Capture | OpenCV |
| Serial Communication | PySerial |
| REST API | Flask |
| Mobile App | React Native (Expo) |
| Maps | `react-native-maps` |
| Location | `expo-location` |

---

## ⚙️ Setup & Installation

### Python Desktop App

**Requirements:** Python 3.8+

```bash
pip install ultralytics opencv-python flask pyserial Pillow matplotlib
```

**Run:**

```bash
python main.py
```

> Make sure your YOLO model weights are at:
> `runs/detect/merged_yolo8_drive3/weights/best.pt`

> Update the serial port in `setup_serial()` if not using `COM14`.

---

### React Native Mobile App

**Requirements:** Node.js 18+, Expo CLI

```bash
cd driver_drowsiness
npm install
npx expo start
```

> Update the Flask server IP in `index.tsx`:
> ```ts
> const response = await fetch("http://<YOUR_IP>:5000/detections");
> ```

---

## 📡 Flask API

The Python app exposes a REST endpoint:

**`GET /detections`**

```json
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
```

- `status` returns the highest-confidence label (or `"None"` if below 0.3 threshold).
- The mobile app polls this endpoint every 5 seconds.

---

## 📲 Mobile App Features

- **Map View** — shows current device location with a color-coded marker (🔴 Drowsy / 🟢 Safe)
- **Status Panel** — displays driver state, timestamp, and per-class confidence scores
- **WhatsApp Share** — sends a formatted message with driver status, detections, Google Maps link, and live API link

---

## 🚨 Alert Logic

| Condition | Action |
|---|---|
| Drowsy > 0.5 for ≥ 3 seconds | Sends `"Drowsy\n"` via serial (once per event) |
| Other class > 0.3 | Sends class name via serial |
| No strong detection | Sends `"None\n"` via serial |

---

## 🔧 Configuration

| Setting | Location | Default |
|---|---|---|
| Serial port | `setup_serial()` | `COM14` |
| Baud rate | `setup_serial()` | `9600` |
| YOLO model path | `setup_yolo()` | `runs/detect/merged_yolo8_drive3/weights/best.pt` |
| Flask host/port | `run_flask()` | `0.0.0.0:5000` |
| Flask API IP (mobile) | `index.tsx` | `192.168.224.188:5000` |
| Drowsiness threshold | `send_serial_data()` | `0.5` confidence, `3.0` seconds |

---

## 📷 Screenshots

### Desktop Dashboard — Awake Detection
![Awake Detection](screenshots/dashboard_awake.png)
> Driver detected as **Awake** with 0.11 confidence. The teal bar is highlighted in the chart and the bottom indicator panel updates in real time.

### Desktop Dashboard — Drowsy Detection
![Drowsy Detection](screenshots/dashboard_drowsy.png)
> Driver detected as **Drowsy** with 0.60 confidence. The Drowsy indicator panel lights up in cyan to alert the system. After 3 continuous seconds above 0.5 confidence, a serial alert is triggered.

### Desktop Dashboard — Mobile Phone Detection
![Mobile Detection](screenshots/dashboard_mobile.png)
> Driver detected holding a **mobile phone** with 0.76 confidence. The Mobile bar peaks and the indicator highlights immediately.

### Mobile App — Driver Awake
![Mobile Awake](screenshots/mobile_awake.png)
> The React Native app showing driver status as **Awake**. The map marker is green, and the status panel shows per-class confidence scores polled from the Flask API. Location is near Pondicherry, India.

### Mobile App — Driver Drowsy
![Mobile Drowsy](screenshots/mobile_drowsy.png)
> The React Native app detecting **Drowsy** status (Drowsy: 0.69). The status panel updates and the WhatsApp share button lets a guardian receive the driver's location and detection details instantly.

---

## 📋 Requirements

### Python
```
ultralytics
opencv-python
flask
pyserial
Pillow
matplotlib
numpy
```

### React Native
```
expo
expo-location
expo-router
react-native-maps
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add your feature'`
4. Push and open a Pull Request

---

## 📄 License

This project is for educational and research purposes.
