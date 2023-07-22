from pcapng import FileScanner

with open('orbtrace_25Mhz_flash_loader_error.pcapng', 'rb') as fp:
    scanner = FileScanner(fp)
    for block in scanner:
        pass  # do something with the block...