import serial
from ublox_gps import UbloxGps

# Serial port configuration
port = "/dev/ttyACM0"  # Adjust this according to your GPS module's serial port
baudrate = 115200

# Function to read GPS data using ublox_gps
def read_gps_data_ublox():
    try:
        with serial.Serial(port, baudrate=baudrate, timeout=1) as ser:
            gps = UbloxGps(ser)
            try:
                geo = gps.geo_coords()
                latitude = geo.lat
                longitude = geo.lon
                return latitude, longitude
            except Exception as e:
                #print(f"An error occurred while reading GPS data: {e}")
                return None, None
    except serial.SerialException as e:
        #print(f"An error occurred while opening the serial port: {e}")
        return None, None