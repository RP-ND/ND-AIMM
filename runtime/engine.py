import serial
import time

def control_motors(pwm1_speed, pwm2_speed, command):
    # Hardcoded serial port details
    port = '/dev/ttyACM1'  # Serial port
    baudrate = 9600  # Baud rate
    timeout = 5  # Timeout in seconds

    # Attempt to establish serial connection
    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
        ser.flush()

        if command in ['forward', 'left', 'right', 'stop', 'brake']:
            # Construct the command string including direction, speeds, and multipliers
            command_str = f"{command},{pwm1_speed},{pwm2_speed}\n"

            # Send the command over serial
            ser.write(command_str.encode('utf-8'))
            print(f"Sent command: {command_str.strip()}")
        else:
            print(f"Invalid command: {command}")

    except serial.SerialException as e:
        print(f"Serial connection error: {e}")

    finally:
        # Ensure the serial connection is closed after sending the command
        if 'ser' in locals() and ser.is_open:
            ser.close()

# Example usage
control_motors(10, 10, 'stop')
