import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd

import json
import glob
import os

directory_path = "/Users/stempel/Desktop/UWMRRC/Linac Measurements/"
pdf_paths = glob.glob(os.path.join(directory_path, "*.pdf"))

# Sort files so dates are ordered
def getDate(pdf_path):
    filename = os.path.basename(pdf_path)
    month_day = filename.replace('.pdf', '')
    return datetime.strptime(month_day, "%B %d")

pdf_paths = sorted(pdf_paths, key=getDate)

savePath = "/Users/stempel/Desktop/UWMRRC/Data/"

# Open json file with data
with open(savePath + 'extracted_data.json', 'r') as f:
    data = json.load(f)

def list_to_numpy_array(obj):
    if isinstance(obj, list):
        return np.array(obj)
    elif isinstance(obj, dict):
        return {key: list_to_numpy_array(value) for key, value in obj.items()}
    else:
        return obj

data = list_to_numpy_array(data)

# Dose ratio between ICP and VW Stack Photon for all energies
ICType1 = 'ICP'
ICType2 = 'IC'
particleType = 'photon'
energyLevels = ['6 MV', '10 MV', '6 FFF', '10 FFF', '15 MV']
measurement1 = 'Adjusted Dose / MU'
measurement2 = 'Dose / MU'
markers = ['o', 's', 'd', '<', '>']
i = 0

dates = [path.split('/')[-1].replace('.pdf', '') for path in pdf_paths]

xValues = [datetime.strptime(date, '%B %d') for date in dates]

for energyLevel in energyLevels:
    icpDoseValues = data[ICType1][particleType][energyLevel][measurement1]
    icDoseValues = data[ICType2][particleType][energyLevel][measurement2]

    # Create a pandas dataframe
    df1 = pd.DataFrame({
        'Date': xValues,
        'ICP': icpDoseValues,
        'IC': icDoseValues
    })

    df1['doseRatio'] = df1['ICP'] / df1['IC']
    
    plt.plot(xValues, df1['doseRatio'], markers[i], linestyle='-', linewidth=1.0)
    
    plt.xlabel('Day')
    plt.ylabel('Dose Ratio')
    plt.title('Ratio of ICP Photon vs IC Photon Dose')
    plt.legend(['6 MV', '10 MV', '6 FFF', '10 FFF', '15 MV'], frameon=False)
    
    plt.gca().set_xticks(xValues)
    plt.gca().set_xticklabels(dates, rotation=30, ha='right')

    mean = df1['doseRatio'].mean()
    stdm = df1['doseRatio'].std() / np.sqrt(len(df1['doseRatio']))
    max_val = df1['doseRatio'].max()
    min_val = df1['doseRatio'].min()
    
    print(f"Dose Ratio {energyLevel} Mean: {mean:.4f} ± {stdm:.4f}")
    print(f"Max = {max_val:.3f}")
    print(f"Min = {min_val:.3f}")
    print('')
    
    i += 1

plt.axhline(y=1, color='black', linestyle='--')
plt.tight_layout()
plt.savefig(savePath + 'doseRatioPhoton.png')
plt.close()

#Dose ratio between ICP and VW Stack Electron for all energies
ICType1 = 'ICP'
ICType2 = 'IC'
particleType = 'electron'
energyLevels = ['6 MeV', '9 MeV', '12 MeV', '15 MeV', '18 MeV']
measurement1 = 'Adjusted Dose / MU'
measurement2 = 'Dose / MU'

i = 0
for energyLevel in energyLevels:
    icpDoseValues = data[ICType1][particleType][energyLevel][measurement1]
    icDoseValues = data[ICType2][particleType][energyLevel][measurement2]
    
    #Create a pandas dataframe
    df2 = pd.DataFrame({
        'Date': xValues,
        'ICP': icpDoseValues,
        'IC': icDoseValues
    })

    df2['doseRatio'] = df2['ICP']/df2['IC']
    
    plt.plot(xValues, df2['doseRatio'], markers[i], linestyle = '-', linewidth = 1.0)
    
    plt.xlabel('Day')
    plt.ylabel('Dose Ratio')
    plt.title('Ratio of ICP Electron vs IC Electron Dose')
    plt.legend(['6 MeV', '9 MeV', '12 MeV', '15 MeV', '18 MeV'], frameon = False)

    plt.gca().set_xticks(xValues)
    plt.gca().set_xticklabels(dates, rotation=30, ha='right')

    mean = df2['doseRatio'].mean()
    stdm = df2['doseRatio'].std() / np.sqrt(len(df2['doseRatio']))
    max = df2['doseRatio'].max()
    min = df2['doseRatio'].min()
    
    print(f"Dose Ratio {energyLevel} Mean: {mean:.4f} ± {stdm:.4f}")
    print(f"Max = {max:.3f}")
    print(f"Min = {min:.3f}")
    print('')
    
    i += 1

plt.axhline(y=1, color='black', linestyle='--')
plt.tight_layout()

plt.savefig(savePath + 'doseRatioElectron.png')
plt.close()

#Normalized energy data photon, individual energies
ICType1 = 'ICP'
ICType2 = 'IC'
particleType = 'photon'
energyLevels = ['6 MV', '10 MV', '6 FFF', '10 FFF', '15 MV']
measurement1 = 'd10 Beam Quality'
measurement2 = 'Beam energy'

#10 cm first depth, 20cm second depth

i = 0
for energyLevel in energyLevels:
    icpD10Values = (data[ICType1][particleType][energyLevel][measurement1])/100
    icBeamValues = data[ICType2][particleType][energyLevel][measurement2]

    #Create a pandas dataframe
    df3 = pd.DataFrame({
    'Date': xValues,
    'ICP': icpD10Values,
    'IC': icBeamValues
    })
        
    df3['NormICP'] = df3['ICP']/df3['ICP'].iloc[0]
    df3['NormIC'] = df3['IC']/df3['IC'].iloc[0]
    
    df3['NormEnergyRatio'] = df3['NormICP']/df3['NormIC']
    
    plt.figure(dpi=100)
    plt.plot(xValues[1:], df3['NormICP'][1:], '^', mfc = 'none', markersize = 10)
    plt.plot(xValues[1:], df3['NormIC'][1:], '.', markersize = 10)
    
    plt.xlabel('Day')
    plt.ylabel('Normalized Beam Energy')
    plt.title('IC Profiler and IC in VW Stack Normalized Photon Beam Energies')
    plt.legend(['IC Profiler ' + str(energyLevel), 'IC in VW Stack ' + str(energyLevel)])

    plt.gca().set_xticks(xValues[1:])
    plt.gca().set_xticklabels(dates[1:], rotation=45, ha='right')
    plt.gca().set_ylim([0.995, 1.005])
    
    i += 1
    plt.axhline(y=1, color='black', linestyle='--', linewidth = 1)
    plt.tight_layout()
    
    plt.savefig(savePath + 'normalizedPhotonEnergy' + energyLevel)
    plt.close()
    
    mean = df3['NormICP'][1:].mean()
    stdm = df3['NormICP'][1:].std() / np.sqrt(len(df3['NormICP'][1:]))
    max = df3['NormICP'][1:].max()
    min = df3['NormICP'][1:].min()
    percentDifference = (df3['NormICP'][1:]-1)*100

    print(f"Normalized IC Profiler Photon Beam {energyLevel} Mean: {mean:.3f} ± {stdm:.3f}")
    print(f"Max = {max:.3f}")
    print(f"Min = {min:.3f}")
    print(percentDifference.max())
    print(percentDifference.min())
    print(percentDifference.mean())
    print(percentDifference.std())
    
    
    mean = df3['NormIC'][1:].mean()
    stdm = df3['NormIC'][1:].std() / np.sqrt(len(df3['NormIC'][1:]))
    max = df3['NormIC'][1:].max()
    min = df3['NormIC'][1:].min()
    percentDifference = (df3['NormIC'][1:]-1)*100

    print('')
    print(f"Normalized IC in VW Stack Photon Beam {energyLevel} Mean: {mean:.3f} ± {stdm:.3f}")
    print(f"Max = {max:.3f}")
    print(f"Min = {min:.3f}")
    print(percentDifference.max())
    print(percentDifference.min())
    print(percentDifference.mean())
    print(percentDifference.std())

#Normalized energy data electron, individual energies
ICType1 = 'ICP'
ICType2 = 'IC'
particleType = 'electron'
energyLevels = ['6 MeV', '9 MeV', '12 MeV', '15 MeV', '18 MeV']
measurement1 = 'R50 Beam Quality'
measurement2 = 'Beam energy'

#1.5 cm first depth
#6 MeV second depth 2.5cm
#9 3.5
#12 5
#15, 18 6.5


i = 0
for energyLevel in energyLevels:
    icpR50Values = data[ICType1][particleType][energyLevel][measurement1]
    icBeamValues = data[ICType2][particleType][energyLevel][measurement2]

    #Create a pandas dataframe
    df4 = pd.DataFrame({
    'Date': xValues,
    'ICP': icpR50Values,
    'IC': icBeamValues
    })
        
    df4['NormICP'] = df4['ICP']/df4['ICP'].iloc[0]
    df4['NormIC'] = df4['IC']/df4['IC'].iloc[0]
    
    
    plt.plot(xValues[1:], df4['NormICP'][1:], '^', mfc = 'none', markersize = 10)
    plt.plot(xValues[1:], df4['NormIC'][1:], '.', markersize = 10)
    
    plt.xlabel('Day')
    plt.ylabel('Normalized Beam Energy')
    plt.title('IC Profiler and IC in VW Stack Normalized Electron Beam Energies')
    plt.legend(['IC Profiler ' + str(energyLevel), 'IC in VW Stack ' + str(energyLevel)])

    
    plt.gca().set_xticks(xValues[1:])
    plt.gca().set_xticklabels(dates[1:], rotation=45, ha='right')
    plt.gca().set_ymargin(0.5)
    
    
    i += 1
    plt.axhline(y=1, color='black', linestyle='--', linewidth = 1)
    plt.tight_layout()
    
    plt.savefig(savePath + 'normalizedElectronEnergy' + energyLevel)
    plt.close()
    
    mean = df4['NormICP'][1:].mean()
    stdm = df4['NormICP'][1:].std() / np.sqrt(len(df4['NormICP'][1:]))
    max = df4['NormICP'][1:].max()
    min = df4['NormICP'][1:].min()

    print(f"Normalized IC Profiler Electron Beam {energyLevel} Mean: {mean:.3f} ± {stdm:.3f}")
    print(f"Max = {max:.3f}")
    print(f"Min = {min:.3f}")
    
    mean = df4['NormIC'][1:].mean()
    stdm = df4['NormIC'][1:].std() / np.sqrt(len(df4['NormIC'][1:]))
    max = df4['NormIC'][1:].max()
    min = df4['NormIC'][1:].min()

    print('')
    print(f"Normalized IC in VW Stack Electron Beam {energyLevel} Mean: {mean:.3f} ± {stdm:.3f}")
    print(f"Max = {max:.3f}")
    print(f"Min = {min:.3f}")

#Temp and pressure

#Probe temperature and pressure
tempProbe = [22.8, 21.9, 22.0, 22.6, 22.4]
pressureProbe = [98.34, 98.08, 99.41, 98.53, 98.21]

#Profiler temperature and pressure
tempProfiler = [22.1, 21.4, 21.2, 21.1, 21.1]
pressureProfiler = [100.4, 100.5, 101.9, 100.9, 100.7]

#ktp correction factor

def correctionFactor(temp, pressure):
    factor = ((273.2+temp)/(273.2+22.0))*(101.33/pressure)
    return factor

probeCorrectionFactors = []
profilerCorrectionFactors = []

for temp, pressure in zip(tempProbe, pressureProbe):
    probeCorrectionFactors.append(correctionFactor(temp, pressure))

for temp, pressure in zip(tempProfiler, pressureProfiler):
    profilerCorrectionFactors.append(correctionFactor(temp, pressure))

probeCorrectionFactors = np.array(probeCorrectionFactors)
profilerCorrectionFactors = np.array(profilerCorrectionFactors)

plt.plot(xValues[1:], probeCorrectionFactors, '^', linestyle = '-', linewidth = 1.0)
plt.plot(xValues[1:], profilerCorrectionFactors, '.', linestyle = '-', linewidth = 1.0)

plt.xlabel('Day')
plt.ylabel('Temperature and Pressure Correction Factor')
plt.title('Temperature and Pressure Correction Factor of Probe and Profiler Over Time')
plt.legend(['Probe','Profiler'], frameon = False)

plt.gca().set_xticks(xValues[1:])
plt.gca().set_xticklabels(dates[1:], rotation=30, ha='right')

plt.savefig(savePath + 'tempPressure')
plt.close()
