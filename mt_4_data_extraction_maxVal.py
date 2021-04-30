import pandas as pd
import numpy as np
import sys
from mt_0_input_factors_all import inputfactors
ip = inputfactors()
local_hpc = ip['local_hpc']
if local_hpc:
    sys.path.insert(1,"/home/apku868a/pyUtilities")
else:
    sys.path.insert(1,"D:\\Academics\\MasterThesisData\\main_functions\\utilities")
from mt_x_dynaUtilities import min_max_scaling
import os

pd.set_option('display.max_columns', 100)
pd.set_option('display.max_rows', 500)


def getData(var,dfo):
    df = pd.read_csv(csv_destination + f"{var}.csv" ,skiprows=7, delim_whitespace=True)
    df.drop(df.columns[2:],axis=1, inplace=True)
    df = df.head(-1)   
    df.columns = ['Time', var]
    df = df.astype(float)
    df_frames = [dfo,df[df.columns[[1]][0]]]
    dfo = pd.concat(df_frames,axis=1)
    return dfo

def getDamageVarData(file,header,dfo):
    df = pd.read_csv(file, index_col=False, skiprows=1, sep=',') 
    df = df.drop(df.columns[-1], axis=1)
    df =  df.max(axis=1)
    dfo[header] = df
    return dfo

start_exp_id = 0
end_exp_id   = ip['max_runs']-1
csv_dest = ip['csv_destination']

max_val = {}
max_val_idx = {}
max_stress = pd.DataFrame()
df_op = {}


for i in range(start_exp_id,end_exp_id+1):
    
    dfo = pd.DataFrame()
    fileName = {}
    if local_hpc:
        csv_destination = csv_dest + f"{i}/"
    else:
        csv_destination = csv_dest + f"{i}\\"
    
    # Force_values
    df = pd.read_csv(csv_destination + "gForce.csv" ,skiprows=1)
    df.drop(df.columns[[-1]],axis=1, inplace=True)
    df['X-Stress'] = df['X-Force']/df['Area']
    dfo = df.copy()
    dfo.drop(['Area','X-Force','Y-Force','Resultant Force'],axis=1, inplace=True)
    
    # Internal energy
    df = pd.read_csv(csv_destination + "gIntEnergy.csv" ,skiprows=1)
    df.drop(df.columns[[-1]],axis=1, inplace=True)
    df.columns = ['Time', 'Int. Energy']
    df_frames = [dfo,df[df.columns[[1]][0]]]
    dfo = pd.concat(df_frames,axis=1)
    
    # extracting ply-wise values
    for ii in ['0','90','c']:
        # principle stress
        var = ii + '_max_princ_stress'
        dfo = getData(var,dfo)
    
    for ii in ['0','90','c']:
        # shear stress
        var = ii +'_max_shear_stress'
        dfo = getData(var,dfo)
    
    for ii in ['0','90','c']:    
        # x stress
        var = ii +'_max_x_stress'
        dfo = getData(var,dfo)
    
    for ii in ['0','90','c']:    
        # y stress
        var = ii +'_max_y_stress'
        dfo = getData(var,dfo)
    
    for ii in ['0','90','c']:
        # in-plane stress
        if ii != 'c':
            var = ii +'_max_xy_stress'
            dfo = getData(var,dfo)
    
    # getting global values
    # Maximum longitudinal stress observed in elements
    cols = ['0_max_x_stress','90_max_x_stress','c_max_x_stress']
    dfo['gMaxXStress'] = dfo[cols].max(axis=1)
    
    # Maximum transverse stress observed in elements
    cols = ['0_max_y_stress','90_max_y_stress','c_max_y_stress']
    dfo['gMaxYStress'] = dfo[cols].max(axis=1)
    
    # Maximum principle stress observed in elements
    cols = ['0_max_princ_stress','90_max_princ_stress','c_max_princ_stress']
    dfo['gMaxPrincStress'] = dfo[cols].max(axis=1)
    
    # MAximum 
    cols = ['0_max_shear_stress','90_max_shear_stress','c_max_shear_stress']
    dfo['gMaxShearStress'] = dfo[cols].max(axis=1)
    
    
    cols = ['0_max_xy_stress','90_max_xy_stress']
    dfo['gMaxXYStress'] = dfo[cols].max(axis=1)
    
    # Stress concentration
    df_pStress = pd.read_csv(csv_destination + "gNotchElem_maxPrinc_max.csv", index_col=False, skiprows=1, sep=',') 
    df_pStress = df_pStress.drop(df_pStress.columns[2:], axis=1)
    df_pStress.columns = ['Time','maxPrincStress']
    
    df_nStress = pd.DataFrame(dfo['X-Stress'])
    # df_nStress = pd.read_csv(csv_destination + "nStress.csv", index_col=False, skiprows=1, sep=',') 
    # df_nStress.columns = ['time','maxNominalStress']
    # df_nStress = df_nStress.iloc[1:,:]    
    dfo['Kt'] = df_pStress['maxPrincStress']/df_nStress['X-Stress']
    
    # # getting nodal displacements
    # df = pd.read_csv(csv_destination + "node_middle.csv", index_col=False, skiprows=1, sep=',') 
    # df = df.drop(df.columns[5:], axis=1)
    # df.columns = ['Time','xDisp','yDisp','zDisp','resDisp']
    # df_frames = [dfo,df[df.columns[1:]]]
    # dfo = pd.concat(df_frames,axis=1)
    
    # # getting node displacement at moving head
    # df = pd.read_csv(csv_destination + "header_disp.csv", index_col=False, skiprows=1, sep=',') 
    # df = df.drop(df.columns[5:], axis=1)
    # df.columns = ['Time','xDispHeader','yDisp','zDisp','resDisp']
    # df_frames = [dfo,df[df.columns[1:]]]
    # dfo = pd.concat(df_frames,axis=1)
    
    # maximum damage activation function value in fiber tensile mode, of elements near notch
    dfo = getDamageVarData(file=csv_destination + "gNotchElem_fa_max.csv",   header='max_fa_notch', dfo=dfo)
    dfo = getDamageVarData(file=csv_destination + "gNotchElem_fmat_max.csv", header='max_fmat_notch', dfo=dfo)
    dfo = getDamageVarData(file=csv_destination + "gNotchElem_da_max.csv", header='max_da_notch', dfo=dfo)
    dfo = getDamageVarData(file=csv_destination + "gNotchElem_dmat.csv", header='max_dmat_notch', dfo=dfo)
    
    dfo = getDamageVarData(file=csv_destination + "gNotchElem_xStress_max.csv", header='notch_xMaxStress', dfo=dfo)
    dfo = getDamageVarData(file=csv_destination + "gNotchElem_yStress_max.csv", header='notch_yMaxStress', dfo=dfo)
    
    # cleaning database
    dfo = dfo.replace([np.inf, -np.inf], np.nan)
        
    # creating directory
    op_dataFrame_dir = 'output_dataframe'
    try: os.mkdir(csv_dest + op_dataFrame_dir)
    except: pass
    
    # saving the dataframe to dictionary
    df_op[i] = dfo
    
    # getting index of maximum applied stress
    temp = dfo.nlargest(n=1,columns='X-Stress')
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