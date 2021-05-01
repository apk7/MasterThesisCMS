#=============================================================================
# Author: Apurv Kulkarni
#-----------------------------------------------------------------------------
# Data extraction and data cleaning of csv database extracted from results
#=============================================================================

import pandas as pd
import numpy as np
import sys
from utilities.mt_x_projectUtilities import *
import os
from mt_0_input_factors_all import inputfactors

ip = inputfactors()
csv_dest = ip['csv_destination']

start_exp_id = 0
end_exp_id   = ip['max_runs']-1

max_val = {}
max_val_idx = {}
max_stress = pd.DataFrame()
df_op = {}

for i in range(start_exp_id,end_exp_id+1):
    
    dfo = pd.DataFrame()
    fileName = {}
    csv_destination = csv_dest + f"{i}/"
    
    # Force_values
    df = pd.read_csv(csv_destination + "gForce.csv" ,skiprows=1)
    df.drop(df.columns[[-1]],axis=1, inplace=True)
    df['gMAS'] = df['X-Force']/df['Area']
    dfo = df.copy()
    dfo.drop(['Area','X-Force','Y-Force','Resultant Force'],axis=1, inplace=True)
    
    # Internal energy
    df = pd.read_csv(csv_destination + "gIntEnergy.csv" ,skiprows=1)
    df.drop(df.columns[[-1]],axis=1, inplace=True)
    df.columns = ['Time', 'gIE']
    df_frames = [dfo,df[df.columns[[1]][0]]]
    dfo = pd.concat(df_frames,axis=1)
    
    # extracting ply-wise values
    for ii in ['0','90','c']:
        # x stress
        dfo = getData(csv_destination, ii +'MLS', dfo)
    
        # y stress
        dfo = getData(csv_destination, ii +'MTS', dfo)
    
        # in-plane stress
        if ii != 'c':
            dfo = getData(csv_destination, ii +'MIPSS', dfo)
        
        # principle stress
        dfo = getData(csv_destination, ii + 'MPS', dfo)
    
        # shear stress
        dfo = getData(csv_destination,ii + 'MSS',dfo)
    
    # getting global values
    # Global maximum longitudinal stress observed in elements
    cols = ['0MLS','90MLS','cMLS']
    dfo['gMLS'] = dfo[cols].max(axis=1)
    
    # Global maximum transverse stress observed in elements
    cols = ['0MTS','90MTS','cMTS']
    dfo['gMTS'] = dfo[cols].max(axis=1)
    
    # Global maximum principle stress observed in elements
    cols = ['0MPS','90MPS','cMPS']
    dfo['gMPS'] = dfo[cols].max(axis=1)
    
    # Global maximum shear stress (Vin tresca)
    cols = ['0MSS','90MSS','cMSS']
    dfo['gMSS'] = dfo[cols].max(axis=1)
    
    # Global maximum in-plane shear stress
    cols = ['0MIPSS','90MIPSS']
    dfo['gMIPSS'] = dfo[cols].max(axis=1)
    
    # Stress concentration
    df_pStress = pd.read_csv(csv_destination + "gNotchElem_maxPrinc_max.csv",
                             index_col=False, skiprows=1, sep=',') 
    df_pStress = df_pStress.drop(df_pStress.columns[2:], axis=1)
    df_pStress.columns = ['Time','maxPrincStress']
    
    df_nStress = pd.DataFrame(dfo['gMAS'])
    dfo['SC'] = df_pStress['maxPrincStress']/df_nStress['gMAS']
    
    # Get nodal displacements of moving head
    df = pd.read_csv(csv_destination + "header_disp.csv", index_col=False, skiprows=1, sep=',') 
    df = df.drop(df.columns[5:], axis=1)
    df.columns = ['Time','xDispHeader','yDisp','zDisp','resDisp']
    df_frames = [dfo,df[df.columns[1:]]]
    dfo = pd.concat(df_frames,axis=1)
    
    # Values of elements near notch
    # Maximum value of damage activation function  and damage variables
    dfo = getDamageVarData(file=csv_destination+"gNotchElem_fa_max.csv",   
                           header='MFA', dfo=dfo)
    dfo = getDamageVarData(file=csv_destination+"gNotchElem_fmat_max.csv",
                           header='MFMAT', dfo=dfo)
    dfo = getDamageVarData(file=csv_destination+"gNotchElem_da_max.csv",
                           header='MDA', dfo=dfo)
    dfo = getDamageVarData(file=csv_destination+"gNotchElem_dmat.csv",
                           header='MDMAT', dfo=dfo)
    
    # Maximum longitudinal and transvserse stress value
    dfo = getDamageVarData(file=csv_destination + "gNotchElem_xStress_max.csv",
                           header='notch_xMaxStress', dfo=dfo)
    dfo = getDamageVarData(file=csv_destination + "gNotchElem_yStress_max.csv",
                           header='notch_yMaxStress', dfo=dfo)
    
    # Cleaning database
    dfo = dfo.replace([np.inf, -np.inf], np.nan)
        
    # Creating directory
    op_dataFrame_dir = ip['extractedDatabase']
    try: os.mkdir(csv_dest + op_dataFrame_dir)
    except: pass
    
    # saving the dataframe to dictionary
    df_op[i] = dfo
    
    # getting index of maximum applied stress
    temp = dfo.nlargest(n=1,columns='gMAS')
    temp['max_stress_idx'] = temp.index.values[0]
    temp.index.values[0] = i                        # assgning experiment number as index column 
    if i == list(range(start_exp_id,end_exp_id+1))[0]:
         max_stress=temp.copy(deep=True)
    else:
        max_stress = max_stress.append(temp,ignore_index=False)
    
    # Maximum value database (dictionary database)
    columns = dfo.columns.values
    max_val[i] = {}
    max_val_idx[i] = {}
    for col in columns:
        temp2 = dfo.nlargest(n=1,columns=col)
        max_val[i][col] = temp2[col].values[0]
        max_val_idx[i][col] = temp2.index.values[0] + 1 # index starts at 0 but state id starts at 1
    
    print(i, '\tcomplete')
    
# converting maximum value dictionary database into dataframe
df_max_val = pd.DataFrame.from_dict(max_val,orient='index') 
df_max_val_idx = pd.DataFrame.from_dict(max_val_idx,orient='index') 

# Saving dictionary of dataframes
import pickle
with open(f"{csv_dest}/{op_dataFrame_dir}/df_full.pickle", 'wb') as handle:
    pickle.dump(df_op, handle, protocol=pickle.HIGHEST_PROTOCOL)

# Saving dataframes
if 'X-Stress' in dfo.columns:
    if local_hpc:
        max_stress.to_csv(f"{csv_dest}{op_dataFrame_dir}/df_maxLoad.csv")
        df_max_force_norm = min_max_scaling(max_stress)
        df_max_force_norm.to_csv(f"{csv_dest}{op_dataFrame_dir}/df_maxLoad_norm.csv")
    else:
        max_stress.to_csv(f"{csv_dest}{op_dataFrame_dir}\\df_maxLoad.csv")
        df_max_force_norm = min_max_scaling(max_stress)
        df_max_force_norm.to_csv(f"{csv_dest}{op_dataFrame_dir}\\df_maxLoad_norm.csv")

df_max_val.to_csv(f"{csv_dest}{op_dataFrame_dir}/df_maxVal.csv")
df_max_val_idx.to_csv(f"{csv_dest}{op_dataFrame_dir}/df_maxVal_idx.csv")
df_max_val_norm = min_max_scaling(df_max_val)
df_max_val_norm = df_max_val_norm.to_csv(f"{csv_dest}{op_dataFrame_dir}/df_maxVal_norm.csv")