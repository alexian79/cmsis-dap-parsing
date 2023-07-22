import json
import usb.backend.libusb1
import hid
from parse_usb_trace import Str2Array
IS_V1 = 1
SERIAL = 0
VENDOR_ID = 0x1209
PRODUCT_ID = 0x3443
if (~IS_V1):
    INTERFACE = 4
    IN_EP = (5|0x80)
    OUT_EP = 3
else:
    INTERFACE = 3
    IN_EP = (4|0x80)
    OUT_EP = 2



def write_to_usb(dev, msg_str):

    print(">>>",end="")
    for p in msg_str:
        print(f' 0x{p:02x}', end="")

    try:
        num_bytes_written = dev.write(OUT_EP, msg_str)

    except usb.core.USBError as e:
        print (e.args)

    print(f" [{num_bytes_written}]")
    return num_bytes_written

def read_from_usb(dev, rxlen, timeout):
    try:
	# try to read a maximum of 2^16-1 bytes from 0x81 (IN endpoint)
        data = dev.read(IN_EP, 60000, timeout)
    except usb.core.USBError as e:
        print ("Error reading response: {}".format(e.args))
        exit(-1)

    if len(data) == 0:
        print ("Zero length response")
        exit(-1)

    return data

def write_to_hid(dev, msg_str):

#    print(">>>",end="")
#    for p in msg_str:
#        print(f' 0x{p:02x}', end="")

    byte_str = b'\0' + bytes(msg_str) + b'\0' * max(64 - len(msg_str), 0)

    dev.write(byte_str)
    print()
    
if __name__ == '__main__':
    fname = '25mhz_flash_loader_error.json'
    fname = '25mhz_flash_loader_error_crafted.json'
    #fname = 'pyocd_25.json'
    with open(fname, 'rb') as f:
        js = json.load(f)
    
    device = hid.device()
    device.open(VENDOR_ID, PRODUCT_ID)

    if device is None:
        raise ValueError('Device not found. Please ensure it is connected')
        sys.exit(1)

    print("Interface claimed")

    with open(fname + '.replay.csv', 'w') as of:
        of.write('Record,Data\n')
        for packet in js:
            layers = packet["_source"]["layers"]
            if layers["usb"]["usb.src"] == "host":
                if "usbhid.data" in layers:
                    data = layers["usbhid.data"]
                else:
                    data = None
                if data:
                    of.write("Output Report," + data.replace(':', ' ') + '\n')
                    data = Str2Array(data.replace(':', ' '))
                    write_to_hid(device, data)
                    r=device.read(127)
                    of.write("Input Report," + " ".join('%02x'%x for x in r) + '\n')
                    
            