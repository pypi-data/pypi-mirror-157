import re as _re


def ddtosct2(decLat: float, decLon: float) -> tuple:
    """ Converts decimal degrees to the sct2 Hddd.mm.ss.sss format """
    try:
        lat = float(decLat)
        lon = float(decLon)
    except ValueError as e:
        raise e
    # Get declination
    ns = "N" if lat >= 0 else "S"
    ew = "E" if lon >= 0 else "W"
    lat = abs(lat)
    lon = abs(lon)
    # Floor to get degrees
    latD = int(lat)
    lonD = int(lon)
    # Get minutes
    latM = 60*(lat - latD)
    lonM = 60*(lon - lonD)
    # Get seconds
    latS = 60*(latM - int(latM))
    lonS = 60*(lonM - int(lonM))
    # Assemble output
    latOut = f"{ns}{int(latD):03}.{int(latM):02}.{latS:06.3f}"
    lonOut = f"{ew}{int(lonD):03}.{int(lonM):02}.{lonS:06.3f}"
    return latOut, lonOut
ddtodms = ddtosct2


def sct2todd(lat:str, lon:str) -> tuple:
    """ Converts sct2 Hddd.mm.ss.sss format to decimal degrees """
    # Check if args are correct type
    if not isinstance(lat, str):
        raise TypeError(repr(lat) + " is not a valid coordinate point. It must be a string")
    if not isinstance(lon, str):
        raise TypeError(repr(lon) + " is not a valid coordinate point. It must be a string")
    # Regex matches
    latPattern = r"([NS])(\d{3})\.(\d{2})\.(\d{2}\.\d{1,3})"
    lonPattern = r"([EW])(\d{3})\.(\d{2})\.(\d{2}\.\d{1,3})"
    latMatch = _re.fullmatch(latPattern, lat.strip())
    lonMatch = _re.fullmatch(lonPattern, lon.strip())
    # Check if point found
    if not latMatch:
        raise ValueError(repr(lat) + "not a valid lat coordinate")
    if not lonMatch:
        raise ValueError(repr(lon) + "not a valid lon coordinate")
    # Format lat
    ns = "-" if latMatch.group(1)=="S" else ""
    latD = int(latMatch.group(2))
    latM = int(latMatch.group(3))
    latS = float(latMatch.group(4))
    # Format lon
    ew = "-" if lonMatch.group(1)=="W" else ""
    lonD = int(lonMatch.group(2))
    lonM = int(lonMatch.group(3))
    lonS = float(lonMatch.group(4))
    # Convert to decimal degrees
    latOut = ns + str(latD + latM/60 + latS/3600)
    lonOut = ew + str(lonD + lonM/60 + lonS/3600)
    return latOut, lonOut
dmstodd = sct2todd


def nasrtodd(latText, lonText) -> tuple:
  """ Converts the NASR ddd-mm-ss.sssH format to decimal degrees """
  # Latitude
  latDecl = latText[-1]
  latVals = latText.split("-")
  latDeg = int(latVals[0])
  latMin = int(latVals[1])
  latSec = float(latVals[2][:-1])
  latDD = latDeg + latMin/60 + latSec/3600
  if latDecl == "S":
    latDD *= -1
  # Longitude
  lonDecl = lonText[-1]
  lonVals = lonText.split("-")
  lonDeg = int(lonVals[0])
  lonMin = int(lonVals[1])
  lonSec = float(lonVals[2][:-1])
  lonDD = lonDeg + lonMin/60 + lonSec/3600
  if lonDecl == "W":
    lonDD *= -1
  # Return result
  return latDD, lonDD


def ddtonasr(latDD, lonDD):
    """ Converts decimal degrees to the NASR ddd-mm-ss.sssH format """
  # Latitude
  latDecl = "N" if latDD >= 0 else "S"
  latDD = abs(latDD)
  latDeg = int(latDD)
  latMin = int((latDD-latDeg) * 60)
  latSec = round(((latDD-latDeg)*60 - latMin) * 60, 3)
  lat = f"{latDeg}-{latMin}-{latSec:06.3f}{latDecl}"
  # Longitude
  lonDecl = "E" if lonDD >= 0 else "W"
  lonDD = abs(lonDD)
  lonDeg = int(lonDD)
  lonMin = int((lonDD-lonDeg) * 60)
  lonSec = round(((lonDD-lonDeg)*60 - lonMin) * 60, 3)
  lon = f"{lonDeg}-{lonMin}-{lonSec:06.3f}{lonDecl}"
  # Return result
  return lat, lon
