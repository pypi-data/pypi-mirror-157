""" Tools for reading, manipulating, and writing positions (POF stuff) """


import xml.etree.ElementTree as ET


__all__ = ["Positions", "load", "loads"]


class Positions:
    """
    Store/manipulate POF positions
    (See www.asrc.info/ASRC%20Documentation/Configuration.html)
    """

    def __init__(self):
        self._positions = {}

    def __repr__(self):
        return f"Positions({self._positions})"

    def add(self, name, rname, freq, secid, artstag, callprefix, callsuffix,
            line1, line2, lsquawk, hsquawk):
        """ Add new position """
        p = {}
        p["rname"] = name if rname == "-" else rname
        p["freq"] = str(freq).ljust(7, "0")
        p["secid"] = secid
        p["artstag"] = artstag
        p["callprefix"] = callprefix
        p["callsuffix"] = callsuffix
        p["line1"] = line1
        p["line2"] = line2
        p["lsquawk"] = str(lsquawk)
        p["hsquawk"] = str(hsquawk)
        self._positions[name] = p

    def set(self, name, **kwargs):
        # Check if position even exists
        if name not in self._positions:
            raise KeyError(f'"{name}" is not an existing position')
        """ Set/change a property of a position """
        params = [
            "rname", "freq", "secid", "artstag", "callprefix", "callsuffix",
            "line1", "line2", "hsquawk", "lsquawk"
        ]
        for k, v in kwargs.items():
            # Check if k is a valid property name
            if k not in params:
                raise KeyError(f'"{k}" is not a recognized property name')
            # Update each property
            val = v
            if k == "rname":
                # Format rname
                val = name if v == "-" else v
            elif k == "freq":
                # Pad frequency
                val = str(v).ljust(7, "0")
            elif k in ["hsquawk", "lsquawk"]:
                val = str(v)
            self._positions[name][k] = val

    def rename(self, old, new):
        # Check if position even exists
        if old not in self._positions:
            raise KeyError(f'"{old}" is not an existing position')
        # Clone & remove
        self._positions[new] = self._positions[old]
        self.remove(old)

    def get(self, name, attrib=None):
        # Check if position even exists
        if name not in self._positions:
            raise KeyError(f'"{name}" is not an existing position')
        # Return specific attrib if specified, else return the whole position
        if attrib:
            return self._positions[name][attrib]
        return self._positions[name]

    def remove(self, name):
        # Check if position even exists
        if name not in self._positions:
            raise KeyError(f'"{name}" is not an existing position')
        del self._positions[name]

    def positions(self):
        return list(self._positions.keys())

    def dump(self, file, client):
        """ Writes Positions to file """
        if type(file) is str:
            with open(file, "w") as f:
                f.write(self.dumps(client))
        else:
            file.write(self.dumps(client))

    def dumps(self, client):
        """ Returns a string in either the VRC txt or vSTARS/vERAM xml format """
        if client.lower() == "vrc":
            # Write to '.txt' format (VRC)
            output = ""
            for name, p in self._positions.items():
                output += name + ":"
                output += ("-" if p["rname"] == name else p["rname"]) + ":"
                output += ":".join([str(item) for item in p.values()][1:]) + "\n"
            return output
        elif client.lower() in ["vstars", "veram"]:
            # Write to '.xml' format (vSTARS & vERAM)
            root = self._dumpxml()
            # (ET.indent only works in Python 3.9+)
            try:
                ET.indent(root)
            except:
                pass
            return ET.tostring(root, encoding="unicode")
        else:
            raise ValueError("unknown client " + repr(client))

    def _dumpxml(self):
        """ Returns an xml.etree.ElementTree Element object """
        root = ET.Element("Positions")
        for name, attribs in self._positions.items():
            posXML = ET.SubElement(root, "PositionInfo")
            posXML.attrib = {
                "PositionType": "Other",
                "SectorName": name,
                "RadioName": attribs["rname"],
                "Prefix": attribs["callprefix"],
                "Suffix": attribs["callsuffix"],
                "Frequency": None,
                "SectorID": attribs["secid"],
                "PositionSymbol": attribs["artstag"]
            }
            # Format frequency separately
            freq = str(attribs["freq"]).replace(".", "")[1:]
            posXML.attrib["Frequency"] = freq
        return root


def load(file):
    """ Makes Positions from a file """
    # If file name, open file first
    if type(file) is str:
        with open(file) as f:
            return loads(f.read())
    # If already file obj, just use that
    return loads(file.read())

def loads(text):
    """ Makes Positions from a string """
    if text.strip().startswith("<"):
        # load xml
        root = ET.fromstring(text)
        pos = Positions()
        for node in root.findall("PositionInfo"):
            name = node.attrib["SectorName"]
            rname = node.attrib["RadioName"]
            prefix = node.attrib["Prefix"]
            suffix = node.attrib["Suffix"]
            secid = node.attrib["SectorID"]
            artstag = node.attrib["PositionSymbol"]
            # Format freq  120300
            freq = "1" + node.attrib["Frequency"]
            freq = freq[:3] + "." + freq[3:]
            # Save position
            pos.add(name, rname, freq, secid, artstag, prefix, suffix, "", "", "", "")
        return pos
    else:
        # load txt (VRC)
        pos = Positions()
        for row in text.split("\n"):
            line = row.strip()
            # Skip comments and empty lines
            if line.startswith(";") or line == "":
                continue
            # Remove same-line comments
            if ";" in line:
                line = line[:line.index(";")].strip()
            # Parse line
            name, *items = line.split(":")
            pos.add(name, *items)
        return pos