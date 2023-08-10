import csv
from array import array
from binascii import hexlify

def Str2Array(s:str):
    return array('B', [int(c,16) for c in s.split()])

class Command:
    DAP_INFO = 0x00
    DAP_LED = 0x01
    DAP_CONNECT = 0x02
    DAP_DISCONNECT = 0x03
    DAP_TRANSFER_CONFIGURE = 0x04
    DAP_TRANSFER = 0x05
    DAP_TRANSFER_BLOCK = 0x06
    DAP_TRANSFER_ABORT = 0x07
    DAP_WRITE_ABORT = 0x08
    DAP_DELAY = 0x09
    DAP_RESET_TARGET = 0x0a
    DAP_SWJ_PINS = 0x10
    DAP_SWJ_CLOCK = 0x11
    DAP_SWJ_SEQUENCE = 0x12
    DAP_SWD_CONFIGURE = 0x13
    DAP_JTAG_SEQUENCE = 0x14
    DAP_JTAG_CONFIGURE = 0x15
    DAP_JTAG_IDCODE = 0x16
    DAP_SWO_TRANSPORT = 0x17
    DAP_SWO_MODE = 0x18
    DAP_SWO_BAUDRATE = 0x19
    DAP_SWO_CONTROL = 0x1A
    DAP_SWO_STATUS = 0x1B
    DAP_SWO_DATA = 0x1C
    DAP_SWD_SEQUENCE = 0x1D
    DAP_SWO_EXTENDED_STATUS = 0x1E
    DAP_QUEUE_COMMANDS = 0x7E
    DAP_EXECUTE_COMMANDS = 0x7F
    DAP_VENDOR0 = 0x80 # Start of vendor-specific command IDs.

    def __init__(self, cmd, data):
        self.cmd = cmd
        self.data = data
    
    @classmethod
    def Cmd2Name (cls, cmd):
        if cmd >= cls.DAP_VENDOR0:
            return "DAP_VENDOR%s"%cmd
        return {
            cls.DAP_INFO : "DAP_INFO",
            cls.DAP_LED : "DAP_LED",
            cls.DAP_CONNECT : "DAP_CONNECT",
            cls.DAP_DISCONNECT : "",
            cls.DAP_TRANSFER_CONFIGURE : "DAP_TRANSFER_CONFIGURE",
            cls.DAP_TRANSFER : "DAP_TRANSFER",
            cls.DAP_TRANSFER_BLOCK : "DAP_TRANSFER_BLOCK",
            cls.DAP_TRANSFER_ABORT : "DAP_TRANSFER_ABORT",
            cls.DAP_WRITE_ABORT : "DAP_WRITE_ABORT",
            cls.DAP_DELAY : "DAP_DELAY",
            cls.DAP_RESET_TARGET : "DAP_RESET_TARGET",
            cls.DAP_SWJ_PINS : "DAP_SWJ_PINS",
            cls.DAP_SWJ_CLOCK : "DAP_SWJ_CLOCK", 
            cls.DAP_SWJ_SEQUENCE : "DAP_SWJ_SEQUENCE",
            cls.DAP_SWD_CONFIGURE : "DAP_SWD_CONFIGURE",
            cls.DAP_JTAG_SEQUENCE : "DAP_JTAG_SEQUENCE",
            cls.DAP_JTAG_CONFIGURE : "DAP_JTAG_CONFIGURE",
            cls.DAP_JTAG_IDCODE : "DAP_JTAG_IDCODE",
            cls.DAP_SWO_TRANSPORT : "DAP_SWO_TRANSPORT",
            cls.DAP_SWO_MODE : "DAP_SWO_MODE",
            cls.DAP_SWO_BAUDRATE : "DAP_SWO_BAUDRATE",
            cls.DAP_SWO_CONTROL : "DAP_SWO_CONTROL",
            cls.DAP_SWO_STATUS : "DAP_SWO_STATUS",
            cls.DAP_SWO_DATA : "DAP_SWO_DATA",
            cls.DAP_SWD_SEQUENCE : "DAP_SWD_SEQUENCE",
            cls.DAP_SWO_EXTENDED_STATUS : "DAP_SWO_EXTENDED_STATUS",
            cls.DAP_QUEUE_COMMANDS : "",
            cls.DAP_EXECUTE_COMMANDS : "DAP_QUEUE_COMMANDS",
        }[cmd]

    def __str__(self):
        msg = ""
        if self.cmd == self.DAP_INFO:
            msg += ' ' + hex(self.data[0])
        elif self.cmd == self.DAP_TRANSFER_CONFIGURE:
            IdleCycles = self.data[0]
            WAITRetry = self.data[1] | self.data[2]*256
            MatchRetry = self.data[3] | self.data[4]*256
            msg += " IdleCycles=%i, WAITRetry=%i, MatchRetry=%i"%(IdleCycles, WAITRetry, MatchRetry)
        elif self.cmd == self.DAP_TRANSFER_BLOCK:
            tcount = self.data[1] + self.data[2]*256
            msg += " count=%i " % tcount
            treq = self.data[3]
            APnDP = treq & (1<<0)
            msg += ("AP " if APnDP else "DP ")
            RnW = treq & (1<<1)
            msg += ('RD ' if RnW else "WR ")
            msg += '[A3:A2]%i '% ((treq >> 2) & 3)
        elif self.cmd == self.DAP_TRANSFER:
            tcount = self.data[1]
            msg += " count=%i " % tcount
            msg += str(hexlify(self.data))
            i = 2
            try:
                for t in range(tcount):
                    msg += "\n        "
                    treq = self.data[i]
                    APnDP = treq & (1<<0)
                    msg += ("AP " if APnDP else "DP ")
                    RnW = treq & (1<<1)
                    msg += ('RD ' if RnW else "WR ")
                    msg += '[A3:A2]%i '% ((treq >> 2) & 3)
                    VM = False
                    MM = False
                    if RnW:
                        VM = (treq >> 4) & 1
                        if VM:
                            msg += 'VM '
                    else:
                        MM = (treq >> 5) & 1
                        if MM:
                            msg += 'MM '
                    if treq & (1<<7):
                        msg += 'TD'
                    if not RnW or MM or VM:
                        msg += ' 0x%08x' % (self.data[i+1] | self.data[i+2]*256 | (self.data[i+3] << 16) | (self.data[i+4] << 24))
                        i += 4
                    i += 1
            except:
                msg = "\n        Exception! for "
        else:
            msg += ' ' + str(hexlify(self.data))
                        
        return self.Cmd2Name(self.cmd) + msg
    
class Responce(Command):
    def __init__(self, cmd, data):
        super().__init__(cmd, data)
    def __str__(self):
        msg = super().Cmd2Name(self.cmd)
        try:
            if self.cmd == self.DAP_INFO:
                if self.data[0] > 4:
                    msg += ' ' + self.data[1:].tobytes().decode('utf-8')
                else:
                    msg += ' ' + str(self.data[0]) + str(hexlify(self.data[1:]))
            elif self.cmd == self.DAP_WRITE_ABORT:
                if self.data[0] == 0:
                    msg += ' DAP_OK'
                elif self.data[0] == 0xff:
                    msg += 'DAP_ERROR'
            elif self.cmd == self.DAP_TRANSFER:
                msg += ' TCOUNT=%i'% self.data[0]
                tr = self.data[1] & 0x7
                msg += ' ' + {1: 'OK', 2: 'WAIT', 4: 'FAULT', 7:'NO_ACK'}[tr]
                if self.data[1] & (1<<3):
                    msg += ' SWD protocol error'
                if self.data[1] & (1<<4):
                    msg += ' Value mismatch'
                #msg += ' TD_IimeStamp=%i' % (self.data[2] + self.data[3]*256)
                if len(self.data) > 4:
                    msg += ' ' + str(hexlify(self.data))
            elif self.cmd == self.DAP_TRANSFER_BLOCK:
                msg += ' TCOUNT=%i'% (self.data[0] + self.data[1]*256)
                tr = self.data[2] & 0x7
                msg += ' ' + {1: 'OK', 2: 'WAIT', 4: 'FAULT', 7:'NO_ACK'}[tr]
                if self.data[2] & (1<<3):
                    msg += ' SWD protocol error'
        except:
            msg += ' Exception !!!! ' + str(hexlify(self.data))
        return msg
        
class TBeagleDump():
    def __init__(self, fname):
        csvfile = open(fname, "r")
        csvfile.seek(0)
        self.reader = csv.DictReader(csvfile)
    
    def ParseToFile(self, fname, ofile=None):
        transfers = []
        for r in self.reader:
            if r['Record'] == 'Output Report':
                data = Str2Array(r['Data'])
                command = Command(data[0], data[1:])
                transfers.append(command)
                print ('--> ', command)
                if ofile:
                    print ('--> ', command, file=ofile)
            elif r['Record'] == 'Input Report':
                data = Str2Array(r['Data'])
                responce = Responce(data[0], data[1:])
                transfers.append(responce)
                if ofile:
                    print (' <--', responce, file=ofile)
        
if __name__ == "__main__":
    for fname in [
        #"success at 2Mhz.csv",
        #"failed at 10Mhz.csv",
        #"success with 1 warning at 2Mhz.csv",
        #"25mhz_flash_loader_error.json.csv",
        #"pyocd_25.json.csv",
        #"25mhz_flash_loader_error.json.replay.csv",
        #"25mhz_flash_loader_error_crafted.json.replay.csv",
        #"25mhz_flash_loader_error_crafted_short.json.replay.csv",
        #"initflash_error_25Mhz.json.csv",
        #"flashloader_error_25Mhz.json.csv",
        'flashloader_error_25_2Mhz.json.csv',
    ]:
        with open(fname + '.txt', 'w') as ofile:
            dump = TBeagleDump(fname)
            dump.ParseToFile(fname, ofile)
