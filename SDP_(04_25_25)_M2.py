import numpy as np
import sounddevice as sd
import librosa
import time
import warnings
from scipy import signal
import threading
import os

# For BLE implementation
import asyncio
from bleak import BleakClient, BleakScanner
from bleak.backends.service import BleakGATTServiceCollection
from bleak.backends.characteristic import BleakGATTCharacteristic
import struct
import json

warnings.filterwarnings('ignore')

print("Setting up macOS-compatible baby cry and siren detection with BLE...")

# Configuration
sample_rate = 16000  # Sample rate in Hz
recording_duration = 2.5  # seconds to record at a time
detection_threshold = 0.48  # Base threshold
noise_floor = 0.015  # Noise floor threshold

# Sound classes we're interested in
target_classes = ["baby_cry", "siren"]

# Class-specific thresholds
class_thresholds = {
    "baby_cry": 0.45,
    "siren": 0.40
}

# Initialize detection history globally
detection_history = []

# Define frequency ranges and characteristics for our target sounds
sound_ranges = {
    "baby_cry": {
        "freq_range": (400, 1500),
        "primary_band": (800, 1200),
        "duration_range": (0.6, 3.0),
        "amplitude_variation": "high",
        "spectral_flux": "high"
    },
    "siren": {
        "freq_range": (700, 2200),
        "primary_band": (1000, 1800),
        "duration_range": (1.0, 5.0),
        "amplitude_variation": "medium",
        "spectral_flux": "medium"
    }
}

# UUID constants for BLE Service and Characteristics
DETECTION_SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
DETECTION_CHARACTERISTIC_UUID = "12345678-1234-5678-1234-56789abcdef1"
COMMAND_CHARACTERISTIC_UUID = "12345678-1234-5678-1234-56789abcdef2"

# Global variables for BLE
connected_devices = set()
notification_handler = None
ble_server = None
stop_event = threading.Event()

# Bluetooth Low Energy implementation
class DetectionService(BleakGATTServiceCollection):
    """GATT Service for sending sound detection notifications"""
    
    def __init__(self):
        super().__init__()
        self.detection_characteristic = None
        self.command_characteristic = None
        self._setup_service()
    
    def _setup_service(self):
        """Set up the GATT service with characteristics"""
        # Create detection service
        detection_service = self.add_service(DETECTION_SERVICE_UUID)
        
        # Create notification characteristic for sending detection results
        self.detection_characteristic = detection_service.add_characteristic(
            DETECTION_CHARACTERISTIC_UUID,
            BleakGATTCharacteristic(
                properties=["notify", "read"],  # Allow notifications and reads
                value=bytes([0x00])  # Initial value
            )
        )
        
        # Create command characteristic for receiving commands
        self.command_characteristic = detection_service.add_characteristic(
            COMMAND_CHARACTERISTIC_UUID,
            BleakGATTCharacteristic(
                properties=["write", "read"],  # Allow writes and reads
                value=bytes([0x00]),  # Initial value
                descriptors=[]
            )
        )
        
        # Set up command handling
        self.command_characteristic.on_write = self._handle_command
    
    async def _handle_command(self, data):
        """Handle commands received from clients"""
        try:
            command = data.decode('utf-8').strip()
            print(f"Received command: {command}")
            
            if command == "STOP":
                print("Client requested stop")
                # Handle any cleanup needed
        except Exception as e:
            print(f"Error handling command: {e}")
    
    async def send_detection(self, detected_sound, confidence):
        """Send detection information to connected devices"""
        if not connected_devices:
            return False
        
        try:
            # Prepare message
            message = {
                "sound": detected_sound,
                "confidence": round(confidence, 2),
                "timestamp": time.time()
            }
            json_data = json.dumps(message).encode('utf-8')
            
            # Send the notification
            for device in connected_devices:
                try:
                    await self.detection_characteristic.notify(device, json_data)
                    print(f"Sent detection to device: {device}")
                except Exception as e:
                    print(f"Error sending notification: {e}")
            
            return True
        except Exception as e:
            print(f"Error preparing notification: {e}")
            return False


class BLEServer:
    """BLE Server to manage connections and send notifications"""
    
    def __init__(self):
        self.service = DetectionService()
        self.server = None
        self.server_task = None
        self.is_running = True
    
    async def start(self):
        """Start the BLE server"""
        try:
            print("Starting BLE server...")
            
            # Create BLE server with our service collection
            self.server = await BleakServer.create(
                self.service,
                name="BabyCryDetector",
                loop=asyncio.get_event_loop()
            )
            
            # Set up connection callbacks
            self.server.on_connect = self._on_device_connect
            self.server.on_disconnect = self._on_device_disconnect
            
            # Start advertising
            await self.server.start()
            print(f"BLE server started. Advertising as 'BabyCryDetector'")
            print(f"Detection Service UUID: {DETECTION_SERVICE_UUID}")
            
            # Keep server running
            while self.is_running and not stop_event.is_set():
                await asyncio.sleep(1)
        
        except Exception as e:
            print(f"BLE server error: {e}")
        finally:
            await self.stop()
    
    async def _on_device_connect(self, device):
        """Handle device connection"""
        print(f"New device connected: {device}")
        connected_devices.add(device)
    
    async def _on_device_disconnect(self, device):
        """Handle device disconnection"""
        print(f"Device disconnected: {device}")
        if device in connected_devices:
            connected_devices.remove(device)
    
    async def send_detection(self, detected_sound, confidence):
        """Send detection to connected clients"""
        if self.service:
            return await self.service.send_detection(detected_sound, confidence)
        return False
    
    async def stop(self):
        """Stop the BLE server"""
        self.is_running = False
        if self.server:
            await self.server.stop()
            print("BLE server stopped")
        
        self.server = None

# Start BLE server in a separate thread
def start_ble_server():
    """Start the BLE server in a separate thread"""
    async def run_server():
        global ble_server
        ble_server = BLEServer()
        await ble_server.start()
    
    def thread_target():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_server())
    
    thread = threading.Thread(target=thread_target)
    thread.daemon = True
    thread.start()
    print("BLE server thread started")
    return thread

# Send detection through BLE
async def send_ble_detection(detected_sound, confidence):
    """Send detection via BLE"""
    if ble_server:
        await ble_server.send_detection(detected_sound, confidence)

# Optimized audio recording function
def record_audio(duration=recording_duration, fs=sample_rate):
    print("Listening...")
    try:
        # Use a higher sample rate for better quality
        recording_fs = 44100  # Increased from 22050 for better quality
        audio = sd.rec(int(duration * recording_fs), samplerate=recording_fs, channels=1)
        sd.wait()
        audio = audio.flatten()
        
        # Resample to target sample rate
        if len(audio) > 0:
            audio = librosa.resample(y=audio, orig_sr=recording_fs, target_sr=fs)
        
        # Amplify the audio slightly to improve detection
        audio = audio * 1.2
        
        return audio
    except Exception as e:
        print(f"Recording error: {e}")
        return np.zeros(int(duration * fs))

# Optimized preprocessing
def preprocess_audio(audio):
    # Check if audio has enough energy to process
    if np.max(np.abs(audio)) < noise_floor:
        return np.zeros_like(audio)
    
    # Normalize audio
    audio = audio / np.max(np.abs(audio))
    
    # Apply focused noise filtering
    try:
        # High-pass filter to reduce low-frequency noise
        audio = librosa.effects.preemphasis(audio, coef=0.95)
        
        # Lower noise gate for better sensitivity
        noise_gate = 0.03
        mask = np.abs(audio) > noise_gate
        audio = audio * mask
        
        # Re-normalize
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio))
    except Exception as e:
        print(f"Preprocessing error: {e}")
    
    return audio

# Efficient spectral flux calculation
def calculate_spectral_flux(spectrogram):
    diff = np.diff(spectrogram, axis=1)
    flux = np.sum(diff**2, axis=0)
    return np.mean(flux), np.std(flux)

# Optimized periodicity detection
def detect_periodicity(audio, fs=sample_rate):
    # Calculate autocorrelation (optimized window)
    # Use a subset of the audio for efficiency
    segment_length = min(len(audio), 8000)  # ~0.5s at 16kHz
    segment = audio[:segment_length]
    
    corr = np.correlate(segment, segment, mode='full')
    corr = corr[len(corr)//2:]
    
    # Normalize
    if np.max(corr) > 0:
        corr = corr / np.max(corr)
    
    # Find peaks with REDUCED height threshold for better detection
    peaks, properties = signal.find_peaks(corr, height=0.2, distance=5)
    
    # Calculate metrics
    periodicity_strength = 0
    periodicity_rate = 0
    
    if len(peaks) > 2:
        periodicity_strength = np.mean(properties['peak_heights'])
        if len(peaks) > 3:
            peak_distances = np.diff(peaks)
            avg_samples_between_peaks = np.mean(peak_distances)
            if avg_samples_between_peaks > 0:
                periodicity_rate = fs / avg_samples_between_peaks
    
    return periodicity_strength, periodicity_rate, len(peaks)

# Optimized feature extraction
def extract_features(audio, fs=sample_rate):
    # Calculate RMS energy
    rms_energy = np.sqrt(np.mean(audio**2))
    
    # Skip processing if energy too low
    if rms_energy < noise_floor * 0.8:
        return None
    
    # Parameters
    hop_length = 512
    n_fft = 1024  
    n_mels = 80
    
    # Compute spectrogram
    D = np.abs(librosa.stft(audio, n_fft=n_fft, hop_length=hop_length))
    
    # Convert to mel scale
    mel_spec = librosa.feature.melspectrogram(S=D, sr=fs, n_mels=n_mels)
    
    # Calculate spectral features
    centroids = librosa.feature.spectral_centroid(S=D, sr=fs)[0]
    mean_centroid = np.mean(centroids)
    std_centroid = np.std(centroids)
    
    # Calculate spectral flux
    flux_mean, flux_std = calculate_spectral_flux(mel_spec)
    
    # Calculate onset strength
    onset_env = librosa.onset.onset_strength(S=D, sr=fs)
    onset_mean = np.mean(onset_env)
    onset_max = np.max(onset_env)
    
    # Calculate harmonic and percussive components
    y_harmonic, y_percussive = librosa.effects.hpss(audio)
    harmonic_ratio = np.mean(y_harmonic**2) / (np.mean(y_harmonic**2) + np.mean(y_percussive**2) + 1e-8)
    
    # Detect periodicity
    periodicity_strength, periodicity_rate, num_peaks = detect_periodicity(audio)
    
    # Calculate temporal features
    frame_length = 1024
    hop_length = 512
    rms = librosa.feature.rms(y=audio, frame_length=frame_length, hop_length=hop_length)[0]
    
    if np.max(rms) > 0:
        rms_norm = rms / np.max(rms)
    else:
        rms_norm = rms
    
    # Return the feature set
    return {
        "rms_energy": rms_energy,
        "mean_centroid": mean_centroid,
        "std_centroid": std_centroid,
        "flux_mean": flux_mean,
        "flux_std": flux_std,
        "onset_mean": onset_mean,
        "onset_max": onset_max,
        "harmonic_ratio": harmonic_ratio,
        "periodicity_strength": periodicity_strength,
        "periodicity_rate": periodicity_rate,
        "num_peaks": num_peaks,
        "rms_std": np.std(rms),
        "mel_spec": mel_spec,
        "fs": fs,
        "n_mels": n_mels
    }

# Helper function to get band energy ratio
def get_band_energy_ratio(mel_spec, low_freq, high_freq, sample_rate, n_mels):
    # Convert frequency to mel bins
    low_bin = max(0, int((n_mels * low_freq) / (sample_rate / 2)))
    high_bin = min(mel_spec.shape[0], int((n_mels * high_freq) / (sample_rate / 2)))
    
    # Calculate energy in the band
    band_energy = np.mean(mel_spec[low_bin:high_bin, :])
    total_energy = np.mean(mel_spec)
    
    if total_energy > 0:
        return band_energy / total_energy
    else:
        return 0

# Sound detection function
def detect_sound(audio):
    # Check if the audio has enough energy
    rms_energy = np.sqrt(np.mean(audio**2))
    if rms_energy < noise_floor * 0.7:
        return "no sound detected", 0
    
    # Preprocess audio
    audio = preprocess_audio(audio)
    
    # Extract features
    try:
        features = extract_features(audio)
        
        if features is None:
            return "no sound detected", 0
        
        mel_spec = features["mel_spec"]
        fs = features["fs"]
        n_mels = features["n_mels"]
        
        # Calculate confidence scores
        confidence_scores = {}
        
        # For each target sound type, calculate confidence
        for sound_type, properties in sound_ranges.items():
            # Extract frequency ranges
            main_freq_range = properties["freq_range"]
            primary_band = properties["primary_band"]
            
            # Calculate energy ratios
            freq_range_ratio = get_band_energy_ratio(mel_spec, main_freq_range[0], main_freq_range[1], fs, n_mels)
            primary_band_ratio = get_band_energy_ratio(mel_spec, primary_band[0], primary_band[1], fs, n_mels)
            
            # Base confidence
            confidence = 0.35 * freq_range_ratio + 0.65 * primary_band_ratio
            
            # Apply sound-specific adjustments
            if sound_type == "baby_cry":
                # Check spectral flux
                if 0.2 < features["flux_mean"] < 0.8:
                    confidence *= 1.4
                
                # Check harmonic structure
                if 0.35 < features["harmonic_ratio"] < 0.9:
                    confidence *= 1.3
                
                # Check spectral centroid variation
                if features["std_centroid"] > 180:
                    confidence *= 1.3
                
                # Penalize if too periodic
                if features["periodicity_strength"] > 0.8:
                    confidence *= 0.7
                    
            elif sound_type == "siren":
                # Check periodicity
                if features["periodicity_strength"] > 0.5:
                    # Extra boost if periodicity rate is in typical siren range
                    if 0.8 < features["periodicity_rate"] < 5:
                        confidence *= 2.2
                    else:
                        confidence *= 1.7
                else:
                    confidence *= 0.6
                
                # Check sustained energy
                if features["rms_std"] < 0.25:
                    confidence *= 1.4
                
                # Check harmonic content
                if features["harmonic_ratio"] > 0.55:
                    confidence *= 1.3
            
            # Apply threshold
            threshold = class_thresholds.get(sound_type, detection_threshold)
            confidence_adjusted = confidence
            
            # Store final confidence score
            confidence_scores[sound_type] = min(0.99, max(0, confidence_adjusted))
        
        # Print confidence scores
        print("\nConfidence Scores:")
        for sound_type, confidence in confidence_scores.items():
            print(f"{sound_type}: {confidence:.4f} (threshold: {class_thresholds.get(sound_type, detection_threshold):.4f})")
        
        # Find the sound with highest confidence that exceeds threshold
        detected_sound = "no sound detected"
        max_confidence = 0
        
        for sound_type, confidence in confidence_scores.items():
            specific_threshold = class_thresholds.get(sound_type, detection_threshold)
            if confidence > specific_threshold and confidence > max_confidence:
                max_confidence = confidence
                detected_sound = sound_type
        
        return detected_sound, max_confidence
        
    except Exception as e:
        print(f"Detection error: {e}")
        return "error in detection", 0

def adapt_thresholds(history, current_thresholds):
    """Dynamically adjust thresholds based on recent performance"""
    if len(history) < 5:  # Need sufficient history
        return current_thresholds
    
    # Copy current thresholds
    adapted_thresholds = current_thresholds.copy()
    
    # Calculate confidence distributions by class
    class_confidences = {}
    for sound_class in target_classes:
        class_confidences[sound_class] = [item['confidence'] for item in history 
                                         if item['detected'] == sound_class]
    
    # Adjust thresholds if needed
    for sound_class in target_classes:
        if len(class_confidences[sound_class]) >= 3:
            conf_mean = np.mean(class_confidences[sound_class])
            conf_std = np.std(class_confidences[sound_class])
            
            # If we have consistent high confidences, slightly lower threshold
            if conf_mean > adapted_thresholds[sound_class] * 1.2 and conf_std < 0.1:
                adapted_thresholds[sound_class] *= 0.96
                print(f"Lowering threshold for {sound_class} to {adapted_thresholds[sound_class]:.4f}")
            
            # If we have confidences just above threshold, slightly raise it
            elif conf_mean < adapted_thresholds[sound_class] * 1.1 and conf_std < 0.1:
                adapted_thresholds[sound_class] *= 1.02
                print(f"Raising threshold for {sound_class} to {adapted_thresholds[sound_class]:.4f}")
    
    return adapted_thresholds

def print_ble_connection_info():
    """Print BLE connection information for client devices"""
    print("\n=== BLE CONNECTION INFORMATION ===")
    print("Device Name: BabyCryDetector")
    print(f"Service UUID: {DETECTION_SERVICE_UUID}")
    print(f"Detection Characteristic UUID (Notify): {DETECTION_CHARACTERISTIC_UUID}")
    print(f"Command Characteristic UUID (Write): {COMMAND_CHARACTERISTIC_UUID}")
    print("\nNOTE: For iOS/Android app development, use these UUIDs to connect to this device.")
    print("\nExample iOS Swift code for connecting to this device:")
    print("""
    import CoreBluetooth
    
    class BLEClient: NSObject, CBCentralManagerDelegate, CBPeripheralDelegate {
        private var centralManager: CBCentralManager!
        private var babyCryDetector: CBPeripheral?
        
        private let serviceUUID = CBUUID(string: "12345678-1234-5678-1234-56789abcdef0")
        private let detectionUUID = CBUUID(string: "12345678-1234-5678-1234-56789abcdef1")
        private let commandUUID = CBUUID(string: "12345678-1234-5678-1234-56789abcdef2")
        
        override init() {
            super.init()
            centralManager = CBCentralManager(delegate: self, queue: nil)
        }
        
        func centralManagerDidUpdateState(_ central: CBCentralManager) {
            if central.state == .poweredOn {
                centralManager.scanForPeripherals(withServices: [serviceUUID], options: nil)
            }
        }
        
        func centralManager(_ central: CBCentralManager, didDiscover peripheral: CBPeripheral, 
                           advertisementData: [String: Any], rssi RSSI: NSNumber) {
            if peripheral.name == "BabyCryDetector" {
                babyCryDetector = peripheral
                babyCryDetector?.delegate = self
                centralManager.connect(peripheral, options: nil)
                centralManager.stopScan()
            }
        }
        
        func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
            peripheral.discoverServices([serviceUUID])
        }
        
        func peripheral(_ peripheral: CBPeripheral, didDiscoverServices error: Error?) {
            for service in peripheral.services ?? [] {
                peripheral.discoverCharacteristics(nil, for: service)
            }
        }
        
        func peripheral(_ peripheral: CBPeripheral, didDiscoverCharacteristicsFor service: CBService, 
                       error: Error?) {
            for characteristic in service.characteristics ?? [] {
                if characteristic.uuid == detectionUUID {
                    peripheral.setNotifyValue(true, for: characteristic)
                }
            }
        }
        
        func peripheral(_ peripheral: CBPeripheral, didUpdateValueFor characteristic: CBCharacteristic, 
                       error: Error?) {
            if let data = characteristic.value,
               let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
               let sound = json["sound"] as? String,
               let confidence = json["confidence"] as? Double {
                print("Detected: \\(sound) with confidence \\(confidence)")
            }
        }
    }
    """)
    print("\nExample Android Kotlin code:")
    print("""
    // Required permissions in AndroidManifest.xml:
    // <uses-permission android:name="android.permission.BLUETOOTH" />
    // <uses-permission android:name="android.permission.BLUETOOTH_ADMIN" />
    // <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    // <uses-permission android:name="android.permission.BLUETOOTH_SCAN" />
    // <uses-permission android:name="android.permission.BLUETOOTH_CONNECT" />
    
    import android.bluetooth.*
    import android.bluetooth.le.*
    import android.content.Context
    import android.os.ParcelUuid
    import java.util.*
    
    class BLEClient(private val context: Context) {
        private val bluetoothAdapter: BluetoothAdapter = BluetoothAdapter.getDefaultAdapter()
        private var gatt: BluetoothGatt? = null
        
        private val SERVICE_UUID = UUID.fromString("12345678-1234-5678-1234-56789abcdef0")
        private val DETECTION_UUID = UUID.fromString("12345678-1234-5678-1234-56789abcdef1")
        private val COMMAND_UUID = UUID.fromString("12345678-1234-5678-1234-56789abcdef2")
        
        fun startScan() {
            val scanner = bluetoothAdapter.bluetoothLeScanner
            val scanFilter = ScanFilter.Builder()
                .setServiceUuid(ParcelUuid(SERVICE_UUID))
                .build()
            
            val scanSettings = ScanSettings.Builder()
                .setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY)
                .build()
                
            scanner.startScan(listOf(scanFilter), scanSettings, scanCallback)
        }
        
        private val scanCallback = object : ScanCallback() {
            override fun onScanResult(callbackType: Int, result: ScanResult) {
                val device = result.device
                if (device.name == "BabyCryDetector") {
                    // Connect to the device
                    scanner.stopScan(this)
                    device.connectGatt(context, false, gattCallback)
                }
            }
        }
        
        private val gattCallback = object : BluetoothGattCallback() {
            override fun onConnectionStateChange(gatt: BluetoothGatt, status: Int, newState: Int) {
                if (newState == BluetoothProfile.STATE_CONNECTED) {
                    this@BLEClient.gatt = gatt
                    gatt.discoverServices()
                }
            }
            
            override fun onServicesDiscovered(gatt: BluetoothGatt, status: Int) {
                val service = gatt.getService(SERVICE_UUID)
                val detectionChar = service.getCharacteristic(DETECTION_UUID)
                
                // Enable notifications
                gatt.setCharacteristicNotification(detectionChar, true)
                
                // Write the descriptor to enable notifications
                val descriptor = detectionChar.getDescriptor(
                    UUID.fromString("00002902-0000-1000-8000-00805f9b34fb"))
                descriptor.value = BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE
                gatt.writeDescriptor(descriptor)
            }
            
            override fun onCharacteristicChanged(
                gatt: BluetoothGatt, 
                characteristic: BluetoothGattCharacteristic
            ) {
                if (characteristic.uuid == DETECTION_UUID) {
                    val data = characteristic.value
                    val jsonStr = String(data)
                    // Parse JSON and handle detection
                    println("Received detection: $jsonStr")
                }
            }
        }
    }
    """)
    print("=====================================")

# Main function - rewritten to work with BLE
async def run_main_loop():
    global detection_history, class_thresholds
    
    try:
        # Counter for periodic threshold adaptation
        counter = 0
        
        # Initialize detection_history if empty
        if not detection_history:
            detection_history = []
        
        print("Starting main detection loop...")
        
        while not stop_event.is_set():
            # Record audio
            audio = record_audio()
            
            # Detect sound
            detected_sound, confidence = detect_sound(audio)
            
            # Store detection in history
            if detected_sound not in ["no sound detected", "error in detection"]:
                detection_history.append({
                    'detected': detected_sound,
                    'confidence': confidence,
                    'timestamp': time.time()
                })
                
                # Keep history manageable
                if len(detection_history) > 30:
                    detection_history = detection_history[-30:]
            
            # Print result with confidence score
            if detected_sound not in ["no sound detected", "error in detection"]:
                print(f"\n>>> DETECTED: {detected_sound.upper()} (confidence: {confidence:.2f}) <<<")
                
                # Send detection via BLE
                await send_ble_detection(detected_sound, confidence)
            else:
                print(f"Status: {detected_sound}")
            
            # Periodically adapt thresholds
            counter += 1
            if counter % 15 == 0:
                class_thresholds = adapt_thresholds(detection_history, class_thresholds)
                counter = 0
            
            # Small pause
            await asyncio.sleep(0.3)
            
    except Exception as e:
        print(f"Main loop error: {e}")
    finally:
        print("Main detection loop ended")

# Main function
def main():
    print("\nStarting baby cry and siren detection system with BLE...")
    print("Initializing BLE server...")
    
    # Start BLE server
    ble_thread = start_ble_server()
    
    # Wait a bit for BLE to initialize
    time.sleep(2)
    
    # Print connection information
    try:
        print_ble_connection_info()
    except Exception as e:
        print(f"Error printing connection info: {e}")
    
    print("Listening for baby crying and sirens...")
    print("Press Ctrl+C to exit")
    
    try:
        # Run the main detection loop
        loop = asyncio.get_event_loop()
        main_task = loop.create_task(run_main_loop())
        
        # Run until interrupted
        loop.run_until_complete(main_task)
        
    except KeyboardInterrupt:
        print("\nExiting sound detection program")
    finally:
        # Set stop event to terminate threads
        stop_event.set()
        
        # Wait for the BLE thread to finish
        if ble_thread.is_alive():
            ble_thread.join(timeout=2)
        
        print("Resources cleaned up. Exiting.")

if __name__ == "__main__":
    # Run main program
    main()