import serial

class Controller:
    '''
    Basic device adaptor for thorlabs MFF101 motorized filter flip mount
    with Ø1" optic holder. Test code runs and seems robust.
    '''
    def __init__(
        self, which_port, name='MFF101', verbose=True, very_verbose=False):
        self.name = name
        self.verbose = verbose
        self.very_verbose = very_verbose
        if self.verbose: print("%s: opening..."%self.name, end='')
        try:
            self.port = serial.Serial(
                port=which_port, baudrate=115200, timeout=1)
        except serial.serialutil.SerialException:
            raise IOError(
                '%s: no connection on port %s'%(self.name, which_port))
        if self.verbose: print(" done.")
        self._get_info()
        assert self.model_number == 'MFF002\x00\x00'
        assert self.firmware_v == 65539
        self.get_position()
        self._flipping = False

    def _send(self, cmd, response_bytes=None):
        if self.very_verbose: print('%s: sending cmd ='%self.name, cmd)
        self.port.write(cmd)
        if response_bytes is not None:
            response = self.port.read(response_bytes)
        else:
            response = None
        assert self.port.inWaiting() == 0
        if self.very_verbose: print('%s: -> response = '%self.name, response)
        return response

    def _get_info(self): # MGMSG_HW_REQ_INFO
        if self.verbose:
            print('%s: getting info'%self.name)
        cmd = b'\x05\x00\x00\x00\x21\x01'
        response = self._send(cmd, response_bytes=90)
        self.model_number = response[10:18].decode('ascii')
        self.type = int.from_bytes(response[18:20], byteorder='little')
        self.serial_number = int.from_bytes(response[6:10], byteorder='little')
        self.firmware_v = int.from_bytes(response[20:24], byteorder='little')
        self.hardware_v = int.from_bytes(response[84:86], byteorder='little')
        if self.verbose:
            print('%s: -> model number  = %s'%(self.name, self.model_number))
            print('%s: -> type          = %s'%(self.name, self.type))
            print('%s: -> serial number = %s'%(self.name, self.serial_number))
            print('%s: -> firmware version = %s'%(self.name, self.firmware_v))
            print('%s: -> hardware version = %s'%(self.name, self.hardware_v))
        return response

    def identify(self): # MGMSG_MOD_IDENTIFY
        if self.verbose:
            print('%s: -> flashing front panel LEDs'%self.name)
        cmd = b'\x23\x02\x00\x00\x21\x01'
        self._send(cmd)
        return None

    def get_position(self): # MGMSG_MOT_REQ_STATUSBITS
        if self.verbose:
            print('%s: getting position...'%self.name)
        cmd = b'\x29\x04\x00\x00\x21\x01'
        status_bits = self._send(cmd, response_bytes=12)[8:]
        self.position = int(status_bits[0])
        if self.verbose:
            print('%s: -> position = %s'%(self.name, self.position))
        return self.position

    def _finish_flip(self):
        if not self._flipping: return
        # MGMSG_MOT_MOVE_COMPLETED
        self.port.read(20) # collect bytes to confirm move (could parse too...)
        self.get_position()
        self._flipping = False
        if self.verbose:
            print('%s: -> finished flip'%(self.name))
        return None

    def flip(self, position, block=True):
        if self._flipping: self._finish_flip()
        if self.verbose:
            print('%s: flipping to position = %s'%(self.name, position))
        assert isinstance(position, int)
        assert position in (1, 2), 'position not in (1, 2)'
        # MGMSG_MOT_MOVE_JOG
        d = (b'\x01', b'\x02')[position - 1] # direction to byte
        cmd = (b'\x6A\x04\x00' + d + b'\x21\x01')
        self._send(cmd)
        self._flipping = True
        if block:
            self._finish_flip()
        return None

    def close(self):
        if self.verbose: print("%s: closing..."%self.name, end=' ')
        self.port.close()
        if self.verbose: print("done.")
        return None

if __name__ == '__main__':
    stage = Controller('COM8', verbose=True, very_verbose=False)

##    stage.identify()

    print('\n# Get position:')
    stage.get_position()

    print('\n# Do some flips:')
    stage.flip(2)
    stage.flip(1)

    print('\n# Non-blocking move:')
    stage.flip(2, block=False)
    stage.flip(1, block=False)
    print('(immediate follow up call forces finish on pending flip)')
    print('doing something else')
    stage._finish_flip()

    stage.close()
