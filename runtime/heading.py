from adafruit_bno08x_rvc import BNO08x_RVC
import serial

uart = serial.Serial("/dev/ttyTHS0", baudrate=115200)
rvc = BNO08x_RVC(uart)

def get_heading():
    uart.reset_input_buffer()  # Clear the input buffer
    yaw, _, _, _, _, _ = rvc.heading
    return yaw

x = get_heading()

print(x)
