import serial

print('opening port...', end='')
port = serial.Serial(port='COM6', baudrate=115200, timeout=1)
print('done.')

cmd = b'\x23\x02\x00\x00\x50\x01'   # MGMSG_MOD_IDENTIFY
print('sending cmd = %s...'%cmd, end='')
port.write(cmd)
assert port.inWaiting() == 0        # (response_bytes=None)
print('done.')

print("closing...", end='')
port.close()
print("done.")
