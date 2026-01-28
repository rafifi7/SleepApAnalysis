"""
NHANES Data Merger for Sleep Apnea Social Determinants Study

This script loads NHANES 2017-2018 data files and merges them into a single dataset
for analyzing how social factors relate to sleep apnea diagnosis and treatment.

"""

import pandas as pd
import os


DATA_FOLDER = r"Data"  


print("Loading NHANES data files...")

# Load each file
slq = pd.read_sas(os.path.join(DATA_FOLDER, "SLQ_J.xpt"))
demo = pd.read_sas(os.path.join(DATA_FOLDER, "DEMO_J.xpt"))
hiq = pd.read_sas(os.path.join(DATA_FOLDER, "HIQ_J.xpt"))
hoq = pd.read_sas(os.path.join(DATA_FOLDER, "HOQ_J.xpt"))
bmx = pd.read_sas(os.path.join(DATA_FOLDER, "BMX_J.xpt"))
inq = pd.read_sas(os.path.join(DATA_FOLDER, "INQ_J.xpt"))
cdq = pd.read_sas(os.path.join(DATA_FOLDER, "CDQ_J.xpt"))


# Start with demographics (most complete)
merged = demo.copy()

# Merge each dataset
merged = merged.merge(slq, on='SEQN', how='left')
merged = merged.merge(hiq, on='SEQN', how='left')
merged = merged.merge(hoq, on='SEQN', how='left')
merged = merged.merge(bmx, on='SEQN', how='left')
merged = merged.merge(inq, on='SEQN', how='left')
merged = merged.merge(cdq, on='SEQN', how='left')


merged = merged[merged['RIDAGEYR'] >= 18].copy()


print("\nSelecting key variables...")

# Define the variables you'll need (add more as needed)
key_vars = [
    'SEQN',           # ID
    
    # DEMOGRAPHICS
    'RIDAGEYR',       # Age in years
    'RIAGENDR',       # Gender (1=Male, 2=Female)
    'RIDRETH3',       # Race/ethnicity
    
    # INCOME & SOCIOECONOMIC
    'INDFMPIR',       # Poverty income ratio (from DEMO)
    'INDHHIN2',       # Annual household income (from INQ)
    
    # HOUSING
    'HOD050',         # Number of rooms in home
    'HOQ065',         # Home owned or rented
    
    # HEALTH INSURANCE / ACCESS
    'HIQ011',         # Covered by health insurance
    'HIQ031A',        # Covered by private insurance
    'HIQ031B',        # Covered by Medicare
    'HIQ031D',        # Covered by Medicaid
    
    # SLEEP APNEA (PRIMARY OUTCOME)
    'SLQ050',         # Ever told doctor had trouble sleeping
    'SLQ030',         # How often do you snore
    'SLQ040',         # How often snort or stop breathing
    'SLQ120',         # How often feel overly sleepy during day
    
    # SLEEP DURATION
    'SLD012',         # Sleep hours - weekdays
    'SLD013',         # Sleep hours - weekends
    
    # BMI (IMPORTANT CONFOUNDER)
    'BMXBMI',         # Body Mass Index
    
    # CARDIOVASCULAR (COMORBIDITIES)
    'CDQ001',         # Ever had chest pain
    
    # SURVEY WEIGHTS (for proper statistical analysis)
    'WTMEC2YR',       # Full sample 2-year MEC exam weight
    'WTINT2YR',       # Full sample 2-year interview weight
    'SDMVPSU',        # Masked variance pseudo-PSU
    'SDMVSTRA',       # Masked variance pseudo-stratum
]

available_vars = [var for var in key_vars if var in merged.columns]
missing_vars = [var for var in key_vars if var not in merged.columns]

if missing_vars:
    print(f"\nNote: These variables weren't found in the data: {missing_vars}")

analysis_data = merged[available_vars].copy()

print(f"✓ Selected {len(available_vars)} variables for analysis")


print("\n" + "="*70)
print("DATA SUMMARY")
print("="*70)

print(f"\nTotal adults in dataset: {len(analysis_data)}")
print(f"\nAge range: {analysis_data['RIDAGEYR'].min():.0f} to {analysis_data['RIDAGEYR'].max():.0f} years")

if 'SLQ050' in analysis_data.columns:
    # SLQ050: 1=Yes, 2=No, 7=Refused, 9=Don't know
    sleep_trouble = analysis_data['SLQ050'].value_counts()
    print(f"\nEver told doctor about trouble sleeping (SLQ050):")
    print(sleep_trouble)

if 'INDFMPIR' in analysis_data.columns:
    print(f"\nPoverty-Income Ratio (INDFMPIR):")
    print(f"  Mean: {analysis_data['INDFMPIR'].mean():.2f}")
    print(f"  Median: {analysis_data['INDFMPIR'].median():.2f}")
    print(f"  Missing: {analysis_data['INDFMPIR'].isna().sum()}")

if 'HIQ011' in analysis_data.columns:
    # HIQ011: 1=Yes, 2=No
    insurance = analysis_data['HIQ011'].value_counts()
    print(f"\nHave health insurance (HIQ011):")
    print(insurance)

if 'BMXBMI' in analysis_data.columns:
    print(f"\nBMI:")
    print(f"  Mean: {analysis_data['BMXBMI'].mean():.2f}")
    print(f"  Missing: {analysis_data['BMXBMI'].isna().sum()}")


output_file = os.path.join(DATA_FOLDER, "nhanes_sleep_analysis.csv")
analysis_data.to_csv(output_file, index=False)

print(f"\n{'='*70}")
print(f"SUCCESS! Dataset saved to:")
print(f"{output_file}")
print(f"{'='*70}")


print(analysis_data.head())

