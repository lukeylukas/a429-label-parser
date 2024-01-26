# this file adds the correct label data to a csv file

import csv

columnLabelName = 0
columnStartBit = 0
columnNumBits = 0
columnEngUnit = 0
columnResolution = 0
columnSigned = 0
columnValue = 0

def GetFileAsCsvReader( fileName ):
  with open(fileName, encoding='ISO-8859-1') as csv_file: #one or more chars were not UTF-8
    csv_reader = csv.reader(csv_file)
    csv_data = []
    for row in csv_reader:
      csv_data.append(row)
  csv_file.close()
  return csv_data

def GetColumns( reader ):
  titleRow = reader[0]

  global columnLabelName
  global columnStartBit
  global columnNumBits
  global columnEngUnit
  global columnResolution
  global columnSigned
  global columnValue

  columnLabelName = titleRow.index('Label Name')
  columnStartBit = titleRow.index('Start Bit (LSB)')
  columnNumBits = titleRow.index('#Bits')
  columnEngUnit = titleRow.index('Eng Unit')
  columnResolution = titleRow.index('Resolution')
  columnSigned = titleRow.index('Signed')
  columnValue = titleRow.index('Label Value')
  
def ProcessCsvData( reader ):
  newArray = []
  newArray.append(reader[0])
  newArray[0].append('Field Value')

  for row in reader[1:]:
    if RowIsUseful(row):
      newRow = AddLabelValue(row)
      newArray.append(newRow)

  return newArray

def RowIsUseful( row ):
  return row[columnValue].isnumeric() \
         & (row[columnEngUnit] != "") \
         & (row[columnLabelName].lower() != 'spare') \
         & (row[columnLabelName].lower() != 'sdi') \
         & (row[columnLabelName].lower() != 'ssm') \
         & (int(row[columnNumBits]) != 23)

def AddLabelValue( row ):
  rawValue = int(row[columnValue])
  startBit = int(row[columnStartBit]) - 1
  numBits = int(row[columnNumBits])
  scaleFactor = float(row[columnResolution])
  signBit = 0

  signed = (row[columnSigned] == 'Y')
  if signed:
    numBits -= 1
    shiftedToSign = (rawValue >> (startBit + numBits))
    signBit = (shiftedToSign % 2)

  fieldValue = IsolateField( rawValue, startBit, numBits )
  scaledValue = ApplyScaling( fieldValue, scaleFactor, (signBit == 1) )

  row.append(str(scaledValue))
  return row

def IsolateField( labelValue, startBit, numBits ):
  shiftedValue = labelValue >> startBit
  maskedValue = shiftedValue & (2**numBits - 1)
  return maskedValue

def ApplyScaling( intValue, scaleFactor, isNegative ):
  scaledValue = intValue * scaleFactor
  if isNegative:
    scaledValue = -scaledValue
  return scaledValue

def WriteToCsv( fileName, csvData ):
  with open(fileName, 'w') as csvfile:
    fileWriter = csv.writer( csvfile )
    fileWriter.writerows(csvData)
  csvfile.close()

#########################################################
#                           Main
#########################################################
if __name__ == "__main__":
  fileName = input('file (path) to convert: ')
  #fileName = "TestValuesBadDistress.csv"
  reader = GetFileAsCsvReader( fileName )
  print(', '.join(reader[0]))
  GetColumns( reader )
  newData = ProcessCsvData( reader )
  #print (', '.join(newData[0]))
  WriteToCsv( fileName, newData )