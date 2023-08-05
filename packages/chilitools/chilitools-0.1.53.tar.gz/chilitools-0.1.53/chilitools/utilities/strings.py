from datetime import datetime

def currentDatetime() -> str:
  return datetime.now().strftime("%m/%d/%Y, %I:%M:%S %p")

def convertFileSize(bytesSize: int, unit: str, roundingPlaces: int = 2) -> str:
  bytesSize = round(bytesSize, roundingPlaces)
  unit = unit.lower()

  if unit == 'kb':
    return str(bytesSize/1024) + ' Kb'
  if unit == 'mb':
    return str(bytesSize/1048576) + ' Mb'
  if unit == 'gb':
    return str(bytesSize/1073741824) + ' Kb'
  return bytesSize
