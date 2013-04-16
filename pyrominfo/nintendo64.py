# Copyright (C) 2013 Garrett Brown
# See Copyright Notice in rominfo.py

from rominfo import RomInfoParser

class Nintendo64Parser(RomInfoParser):
    """
    Parse a Nintendo 64 image. Valid extensions are z64 (native byte order),
    n64 (wordswapped), and v64 (byteswapped). Nintendo 64 header references and
    related source code:
    * rom.c of the Mupen64Plus project:
    * https://bitbucket.org/richard42/mupen64plus-core/src/4cd70c2b5d38/src/main/rom.c
    """

    def getValidExtensions(self):
        return ["n64", "v64", "z64"]

    def parse(self, filename):
        props = {}
        with open(filename, "rb") as f:
            data = bytearray(f.read(64))
            if self.isValidData(data):
                props = self.parseBuffer(data)
        return props

    def isValidData(self, data):
        """
        Test for a valid N64 image by checking the first 4 bytes for the magic word.
        """
        if len(data) >= 64:
            # Test if rom is a native .z64 image with header 0x80371240. [ABCD]
            if [b for b in data[:4]] == [0x80, 0x37, 0x12, 0x40]:
                return True
            # Test if rom is a byteswapped .v64 image with header 0x37804012. [BADC]
            if [b for b in data[:4]] == [0x37, 0x80, 0x40, 0x12]:
                return False # TODO: Add byte-swapping
            # Test if rom is a wordswapped .n64 image with header  0x40123780. [DCBA]
            if [b for b in data[:4]] == [0x40, 0x12, 0x37, 0x80]:
                return False # TODO: Add word-swapping
        return False

    def parseBuffer(self, data):
        props = {}

        props["title"] = self._sanitize(data[0x20 : 0x20 + 20])

        # Big endian (I presume)
        props["clock_rate"] = "%08X" % (data[0x04] << 24 | data[0x05] << 16 | data[0x06] << 8 | data[0x07])

        props["version"] = "%08X" % (data[0x0c] << 24 | data[0x0d] << 16 | data[0x0e] << 8 | data[0x0f])

        props["crc1"] = "%08X" % (data[0x10] << 24 | data[0x11] << 16 | data[0x12] << 8 | data[0x13])
        props["crc2"] = "%08X" % (data[0x14] << 24 | data[0x15] << 16 | data[0x16] << 8 | data[0x17])

        pub = data[0x38 : 0x38 + 4].decode("ascii", "ignore")
        props["publisher"] = n64_publishers.get(pub[3], "") # Low byte of int
        props["publisher_code"] = pub.strip()

        props["code"] = self._sanitize(data[0x3c : 0x3c + 2])

        props["region"] = n64_regions.get(data[0x3e], "")
        if props["region"] or data[0x3e] in [0x00, 0x37]:
            props["region_code"] = "%02X" % data[0x3e]
        else:
            props["region_code"] = ""

        props["image_format"] = "native" # TODO

        return props

RomInfoParser.registerParser(Nintendo64Parser())


n64_regions = {
    0x00: None, # Demo games
    0x37: None, # Beta games
    0x41: "Japan/USA",
    0x44: "Germany",
    0x45: "USA",
    0x46: "France",
    0x49: "Italy",
    0x4A: "Japan",
    0x50: "Europe",
    0x53: "Spain",
    0x55: "Australia",
    0x59: "Australia",
    # Other PAL European codes
    0x58: "Europe",
    0x20: "Europe",
    0x21: "Europe",
    0x38: "Europe",
    0x70: "Europe",
}

n64_publishers = {
    "N": "Nintendo",
}
