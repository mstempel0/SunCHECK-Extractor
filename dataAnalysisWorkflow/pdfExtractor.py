import json
import fitz  # PDF Extractor
import numpy as np
import glob
import os
from datetime import datetime

# Directory containing SunCheck files
directory_path = "/Users/stempel/Desktop/UWMRRC/Linac Measurements/"

# Get all pdf files in the directory
pdf_paths = glob.glob(os.path.join(directory_path, "*.pdf"))

# Sort files so dates are ordered
def getDate(pdf_path):
    filename = os.path.basename(pdf_path)
    month_day = filename.replace('.pdf', '')
    return datetime.strptime(month_day, "%B %d")

pdf_paths = sorted(pdf_paths, key=getDate)

print(pdf_paths)

numDocs = len(pdf_paths)

# Setup dictionaries to hold all data extracted from pdf. ICP is the profiler, IC is chamber in phantom.
data = {
    "ICP": {
        "photon": {},
        "electron": {}
    },
    "IC": {
        "photon": {},
        "electron": {}
    }
}

# Other setup for finding data in pdf (in theory could be changed depending on pdf)
keywords = ("MU", "profile constancy", "Flatness", "Symmetry", "Beam Quality", "Dose", "Wedge factor", "EDW", "energy")
exclusions = ("Photon", "Electron")

# Function setup
def checkSubsection(line):
    # Determines if at a subsection containing data or not
    return any(keyword in line for keyword in keywords) and not any(exclusion in line for exclusion in exclusions)

def getSubsection(line):
    # Returns the name of the subsection (complicated since names vary greatly)
    space = line.find(' ')
    remainingText = line[space + 1:].strip()
    if any(char.isdigit() for char in remainingText):
        return line[:space].strip()  # Extract everything before the first space
    else:
        return line.strip()

def getQuadWedges(line):
    # Used to check if profiler is being used
    return "quad wedges" in line

def getParticleType(line):
    # Determines photon or electron
    if "Photon" in line:
        return 'photon'
    elif "Electron" in line:
        return 'electron'

def getEnergyLevel(line):
    # Returns energy level, 6 MV, 10 MV etc.
    return line.split(" - ")[1].strip()

def getMeasurement(line):
    # Returns the measured value from SunCheck
    return float(lines[i + 1].strip())

def addMeasurement(chamberType, particleType, energyLevel, subsection, day):
    # Adds measured value and creates subdictionary if doesn't exist
    if subsection not in data[chamberType][particleType][energyLevel]:
        data[chamberType][particleType][energyLevel][subsection] = {}
    data[chamberType][particleType][energyLevel][subsection][day] = measurement

# Main loop
for day, pdf_path in enumerate(pdf_paths, start=1):
    doc = fitz.open(pdf_path)

    # Loop through each page
    page_num = 0
    while page_num < len(doc):
        page = doc[page_num]  # Sets up document variables to loop
        text = page.get_text()
        lines = text.split("\n")

        # Loop line by line
        i = 0  # line counter
        while i < len(lines):

            quadWedges = getQuadWedges(lines[i])  # Determines whether profiler is being used, returns boolean

            if getParticleType(lines[i]) == 'photon':  # Extract data for photons
                energyLevel = getEnergyLevel(lines[i])

                if quadWedges:  # Will setup energy levels, e.g. 6MV 10MV etc.
                    if energyLevel not in data["ICP"]["photon"]:
                        data["ICP"]["photon"][energyLevel] = {}
                else:
                    if energyLevel not in data["IC"]["photon"]:
                        data["IC"]["photon"][energyLevel] = {}

                # For each energy level that was tested, this will go through and take only the measurement for each specified section we want, i.e. flatness symmetry, dose etc. This excludes all other info in the pdf
                i += 1
                while i < len(lines) or page_num < len(doc) - 1:
                    if i == len(lines):
                        page_num += 1  # annoying code to not stop at the end of the page since some data spans multiple pages
                        page = doc[page_num]
                        text = page.get_text()
                        lines = text.split("\n")
                        i = 0
                        continue

                    if getParticleType(lines[i]) in ['photon', 'electron']:  # Breaks the loop when a new section is reached
                        break

                    if checkSubsection(lines[i]):  # Checks to see if the line we are on is a line containing a subsection that has data we want.
                        subsection = getSubsection(lines[i])
                        measurement = getMeasurement(lines[i])

                        if quadWedges:  # Where the data is actually added to the dictionary, making sure that no new dictionaries are being created
                            addMeasurement('ICP', 'photon', energyLevel, subsection, day)

                        else:
                            addMeasurement('IC', 'photon', energyLevel, subsection, day)
                    i += 1

            # Exact same process but with electron
            elif "Electron constancy with quad wedges" in lines[i]:
                energyLevel = getEnergyLevel(lines[i])

                if quadWedges:
                    if energyLevel not in data["ICP"]["electron"]:
                        data["ICP"]["electron"][energyLevel] = {}
                else:
                    if energyLevel not in data["IC"]["electron"]:
                        data["IC"]["electron"][energyLevel] = {}

                i += 1
                while i < len(lines) or page_num < len(doc) - 1:
                    if i == len(lines):
                        page_num += 1
                        page = doc[page_num]
                        text = page.get_text()
                        lines = text.split("\n")
                        i = 0
                        continue

                    if getParticleType(lines[i]) in ['photon', 'electron']:
                        break

                    if checkSubsection(lines[i]):
                        subsection = getSubsection(lines[i])
                        measurement = float(lines[i + 1].strip())

                        if quadWedges:
                            addMeasurement('ICP', 'electron', energyLevel, subsection, day)
                        else:
                            addMeasurement('IC', 'electron', energyLevel, subsection, day)
                    i += 1

            # Same process again because of typage intricacies in the specific pdf
            elif "Electron constancy - VW Stack" in lines[i]:
                energyLevel = lines[i].split(" - ")[2].strip()

                if quadWedges:
                    if energyLevel not in data["ICP"]["electron"]:
                        data["ICP"]["electron"][energyLevel] = {}
                else:
                    if energyLevel not in data["IC"]["electron"]:
                        data["IC"]["electron"][energyLevel] = {}

                i += 1
                while i < len(lines) or page_num < len(doc) - 1:
                    if i == len(lines):
                        page_num += 1
                        page = doc[page_num]
                        text = page.get_text()
                        lines = text.split("\n")
                        i = 0
                        continue

                    if getParticleType(lines[i]) in ['photon', 'electron']:
                        break

                    if checkSubsection(lines[i]):
                        subsection = getSubsection(lines[i])
                        measurement = getMeasurement(lines[i])

                        if quadWedges:
                            addMeasurement('ICP', 'electron', energyLevel, subsection, day)

                        else:
                            addMeasurement('IC', 'electron', energyLevel, subsection, day)

                    i += 1
            else:
                i += 1

        page_num += 1

# Convert to numpy arrays
for quadWedges in ["ICP", "IC"]:
    for particleType in ["photon", "electron"]:
        for energyLevel, energyData in data[quadWedges][particleType].items():
            for subsection, measurements in energyData.items():
                data[quadWedges][particleType][energyLevel][subsection] = np.array(list(measurements.values()))

def numpy_array_to_list(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: numpy_array_to_list(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [numpy_array_to_list(item) for item in obj]
    else:
        return obj
            
# Convert numpy arrays to lists and creates JSON file
json_data = json.dumps(numpy_array_to_list(data))
with open('/Users/stempel/Desktop/UWMRRC/Data/extracted_data.json', 'w') as f:
    f.write(json_data)
