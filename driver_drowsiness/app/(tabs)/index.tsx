import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, TouchableOpacity, Linking } from "react-native";
import MapView, { Marker } from "react-native-maps";
import * as Location from "expo-location";

export default function App() {
  const [location, setLocation] = useState<Location.LocationObjectCoords | null>(null);
  const [driverStatus, setDriverStatus] = useState("Unknown");
  const [timestamp, setTimestamp] = useState("");
  const [detections, setDetections] = useState<any>({});

  // Get current device location
  useEffect(() => {
    (async () => {
      let { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== "granted") {
        console.log("Permission denied");
        return;
      }
      let loc = await Location.getCurrentPositionAsync({});
      setLocation(loc.coords);
    })();
  }, []);

  // Fetch driver status from Flask API every 5s
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch("http://192.168.224.188:5000/detections");// 👈 your Flask server
        const data = await response.json();

        if (data && data.status) {
          setDriverStatus(data.status);
          setTimestamp(data.timestamp);
          setDetections(data.detections || {});
        }
      } catch (error) {
        console.log("Error fetching driver status:", error);
      }
    }, 5000);

    return () => clearInterval(interval);
  }, []);

const shareWhatsApp = () => {
  if (!location) {
    alert("Location not available yet");
    return;
  }

  // Convert detections to percentages
  const formatDetection = (value: number | undefined) =>
    value !== undefined ? `${(value * 100).toFixed(0)}%` : "0%";

  // Static Google Maps link for current location
  const locationLink = `https://www.google.com/maps?q=${location.latitude},${location.longitude}`;

  // Live status link (your ngrok URL)
  const liveStatusLink = "https://8db0d71b0152.ngrok-free.app/detections";

  // Build the message with explicit line breaks
  const message =
    "🚗 Driver Status: " + driverStatus + "\n" +
    "🕒 Time: " + timestamp + "\n" +
    "📊 Detections: Awake=" + formatDetection(detections.Awake) +
    ", Drowsy=" + formatDetection(detections.Drowsy) +
    ", Yawning=" + formatDetection(detections.Yawning) +
    ", Mobile=" + formatDetection(detections.Mobile) +
    ", Drinking=" + formatDetection(detections.Drinking) + "\n" +
    "📍 Current Location: " + locationLink + "\n" +
    "🌐 Live Status: " + liveStatusLink;

  // Encode and open WhatsApp
  const url = `whatsapp://send?text=${encodeURIComponent(message)}`;
  Linking.openURL(url).catch(() => {
    alert("Make sure WhatsApp is installed on your device");
  });
};

  return (
    <View style={styles.container}>
      {location ? (
        <MapView
          style={styles.map}
          initialRegion={{
            latitude: location.latitude,
            longitude: location.longitude,
            latitudeDelta: 0.01,
            longitudeDelta: 0.01,
          }}
        >
          <Marker
            coordinate={{
              latitude: location.latitude,
              longitude: location.longitude,
            }}
            title="Driver"
            description={`${driverStatus} @ ${timestamp}`}
            pinColor={driverStatus === "Drowsy" ? "red" : "green"}
          />
        </MapView>
      ) : (
        <Text style={styles.loadingText}>Getting location...</Text>
      )}

      <View style={styles.statusBox}>
        <Text style={styles.statusText}>🚦 Driver Status: {driverStatus}</Text>
        <Text style={styles.timeText}>🕒 Last Update: {timestamp}</Text>
        <Text style={styles.detectionText}>
          Awake: {detections.Awake} | Drowsy: {detections.Drowsy} | Yawning: {detections.Yawning} | Mobile: {detections.Mobile} | Drinking: {detections.Drinking}
        </Text>
        <TouchableOpacity style={styles.button} onPress={shareWhatsApp}>
          <Text style={styles.buttonText}>Share via WhatsApp</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  map: { flex: 1 },
  loadingText: { textAlign: "center", marginTop: 20, fontSize: 18 },
  statusBox: {
    position: "absolute",
    bottom: 20,
    left: 20,
    right: 20,
    backgroundColor: "white",
    padding: 15,
    borderRadius: 10,
    shadowColor: "#000",
    shadowOpacity: 0.3,
    shadowRadius: 5,
    elevation: 5,
  },
  statusText: { fontSize: 18, marginBottom: 5, fontWeight: "bold" },
  timeText: { fontSize: 14, marginBottom: 5, color: "#555" },
  detectionText: { fontSize: 14, marginBottom: 10, color: "#333" },
  button: { backgroundColor: "#25D366", padding: 12, borderRadius: 8 },
  buttonText: { color: "white", textAlign: "center", fontWeight: "bold" },
});
