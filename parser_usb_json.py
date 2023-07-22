import json


if __name__ == '__main__':
    fname = '25mhz_flash_loader_error.json'
    fname = 'pyocd_25.json'
    with open(fname, 'rb') as f:
        js = json.load(f)
    with open(fname + '.csv', 'w') as of:
        of.write('Record,Data\n')
        for packet in js:
            layers = packet["_source"]["layers"]
            if layers["usb"]["usb.src"] == "host":
                if "usbhid.data" in layers:
                    data = layers["usbhid.data"]
                elif "usb.capdata" in layers:
                    data = layers["usb.capdata"]
                else:
                    data = None
                if data:
                    of.write("Output Report," + data.replace(':', ' ') + '\n')
            else:
                if "usbhid.data" in layers:
                    data = layers["usbhid.data"]
                elif "usb.capdata" in layers:
                    data = layers["usb.capdata"]
                else:
                    data = None
                if data:
                    of.write("Input Report," + data.replace(':', ' ') + '\n')