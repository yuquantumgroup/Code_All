from __future__ import annotations
import serial
import time
from typing import Optional

PORT = 'COM6'   # Change this to CAN accordingly
USB_BAUDRATE = 1_000_000 # Sets the serial communication speed between the computer and USB adapter
READ_TIMEOUT = 0.10      # seconds

from serial.tools import list_ports

ser = None
KP = 5
KD = 5
MOTOR_ID = 0x001
frame = None
payload = None




print("Basic workflow: init() -> setup() -> move() x N -> deinit()")

def init(PORT='COM6') -> bool:
    print("Opening " + PORT + "...")
    global ser 
    ser = serial.Serial(
        port=PORT,
        baudrate=USB_BAUDRATE,
        timeout=READ_TIMEOUT,
        write_timeout=1.0,
        parity=serial.PARITY_NONE,
        bytesize=serial.EIGHTBITS, # by default
        stopbits=serial.STOPBITS_ONE,
    )
    print('Port open:', ser.is_open)
    #print('Port settings:', ser.get_settings())

    return ser.is_open





def send_raw(command: bytes, pause: float = 0.05) -> None:
    """Send raw bytes to the adapter and print exactly what was sent."""
    if not ser.is_open:
        raise RuntimeError('Serial port is closed.')
    ser.write(command)
    ser.flush()
    #print('TX raw:', repr(command))
    time.sleep(pause) #0.05 s pause


def read_one():
    """Read one carriage-return-terminated ASCII response."""
    raw = ser.read_until(b'\r')
    if not raw:
        return None
    text = raw.decode('ascii', errors='replace').strip('\r\n')
    return text


def listen(duration: float = 2.0):
    """Collect and print frames received during a fixed time interval."""
    frames = []
    deadline = time.monotonic() + duration

    while time.monotonic() < deadline:
        frame = read_one(timeout=0.05)
        if frame:
            frames.append(frame)
            print('RX:', frame)

    if not frames:
        print('No complete CR-terminated frame received.')

    return frames


def setup():
    global ser
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    send_raw(b'S8\r') #configure the CAN arbitration bitrate
    send_raw(b'Y5\r') #configure the CAN-FD data bitrate
    send_raw(b'O\r\n') # open the CAN channel

    print('Initialization commands sent.')





def make_canfd_position(
    position_deg,
    speed_hz,
    current_a,
    kp,
    kd,
    run=False,
):
    global payload
    # Position: 1 revolution = 1,048,576 counts
    position_code = round(position_deg / 360.0 * 1_048_576)

    # Velocity field uses electrical frequency in Hz
    velocity_code = round(speed_hz / 1000.0 * 8_388_608)

    # Current field: ±100 A corresponds to signed 16-bit range
    current_code = round(current_a / 100.0 * 32_768)

    if not 0 <= kp <= 255:
        raise ValueError("kp must be between 0 and 255")

    if not 0 <= kd <= 255:
        raise ValueError("kd must be between 0 and 255")

    payload = (
        position_code.to_bytes(5, byteorder="big", signed=True)
        + velocity_code.to_bytes(4, byteorder="big", signed=True)
        + current_code.to_bytes(2, byteorder="big", signed=True)
        + bytes([
            2,          # ModeSel = 2: position mode
            int(run),   # RunCmd: 0 = stopped/free, 1 = run
            kp,
            kd,
            0,          # Zero command inactive
        ])
    )

    return payload





def move(position=0, MOTOR_ID=0x001, speed=20):
    global move_payload
    global KP
    global KD

    move_payload = make_canfd_position(
    position_deg=position,
    speed_hz=speed,
    current_a=0.1,
    kp=KP,
    kd=KD,
    run=True,
    )

    #print("KP ", KP)
    #print("KD ", KD)

    move_frame = f"d{MOTOR_ID:03X}A{move_payload.hex().upper()}\r"

    #print("Serial frame:", repr(frame))

    send_raw(move_frame.encode("ascii"))
    time.sleep(0.05)
    send_raw(move_frame.encode("ascii"))

    print("Moving motor ", MOTOR_ID, " to ", position)

    return (MOTOR_ID, position)


def deinit():
    global ser
    move_payload = make_canfd_position(
    position_deg=0,
    speed_hz=20,
    current_a=0.1,
    kp=KP,
    kd=KD,
    run=True,
    )
    # Stop and close the COM port
    stop_payload = bytearray(move_payload)

    # Byte 12 is RunCmd
    stop_payload[12] = 0

    MOTOR_ID = 1
    # Build the CAN-FD serial frame
    stop_frame1 = (
        f"d{MOTOR_ID:03X}A"
        f"{bytes(stop_payload).hex().upper()}\r"
    ).encode("ascii")
    
    MOTOR_ID = 2
    # Build the CAN-FD serial frame
    stop_frame2 = (
        f"d{MOTOR_ID:03X}A"
        f"{bytes(stop_payload).hex().upper()}\r"
    ).encode("ascii")

    # Stop/disable the motor
    send_raw(stop_frame1)
    send_raw(stop_frame2)

    response = read_one()
    print("Stop response:", response)

    # Then close the COM port
    ser.close()
    print("Serial port closed:", not ser.is_open)



'''
setup()
init()
move_to()
time.sleep(5)
move_to(10)
time.sleep(5)
move_to(-10, 4)
time.sleep(5)

loop = ''
while loop != 'q':
    print("q to quit, s to set speed, p and d for setting kp and kd, m to move to a position")
    input(loop)
    if True:
        deinit()
        break
'''