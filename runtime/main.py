import os
import sys
import cv2
import depthai as dai
import numpy as np
from PIL import Image
from queue import Queue, Empty
import threading
from ultralytics import YOLO  
from calc import HostSpatialsCalc

# System Call

from runtime.utility import *
from camera import *
from engine import *

                                
########################
# Main Block
######################## 

def main():
    
    results_queue = Queue()
    stop_event = threading.Event()
    
    min_devices_required = 2
    retry_delay = 5
    max_retries = 10
    deviceInfos = []  # Placeholder for device information retrieval
    
    # This part remains unchanged
    for attempt in range(max_retries):
        deviceInfos = dai.Device.getAllAvailableDevices()
        if len(deviceInfos) >= min_devices_required:
            print(f"Found {len(deviceInfos)} devices.")
            break  # Required number of devices found, exit the loop
        else:
            print(f"Less than {min_devices_required} devices found, retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)

    if len(deviceInfos) < min_devices_required:
        print(f"Less than {min_devices_required} devices found after retrying, exiting.")
        sys.exit(0)

    model_paths = ['/home/ndaimm/ndaimm/onhost/custom1.pt', '/home/ndaimm/ndaimm/onhost/custom2.pt']
    threads = []

    for i, deviceInfo in enumerate(deviceInfos):
        model_path = model_paths[i % len(model_paths)]
        # Pass display_queue as an argument to processCamera
        t = threading.Thread(target=processCamera, args=(deviceInfo, model_path, results_queue))
        t.start()
        threads.append(t)
        
    consumer_thread = threading.Thread(target=results_consumer, args=(results_queue, stop_event))
    consumer_thread.start()

    for t in threads:
        t.join()  # Ensure all threads have finished before exiting
        
    stop_event.set()
    consumer_thread.join()

if __name__ == "__main__":
    main()