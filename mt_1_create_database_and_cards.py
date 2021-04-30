##############################################################################
# Used to create LS-Dyna cards with given geometry
# Author: Apurv Kulkarni
##############################################################################

# Loading dependencies      
import os
import pandas as pd
import numpy as np
import pyDOE2 as doe
from mt_0_input_factors_all import *
from utilities.mt_x_projectUtilities import *
from utilities.mt_x_OHT_StructuredMesh_GmshLsdyna import create_geo
from datetime import datetime
now = datetime.now()
current_time = now.strftime("%H:%M:%S")

# Get input data
ip = inputfactors()

# Create project directory structure
createProjDirStruct(ip)

project_name        = ip['project_name']
project_path        = ip['project_path']
factor_list         = ip['factor_list']
card_destination    = ip['card_destination']
geometry_loc        = ip['geo_dest']
ana_type            = ip['analysis_type'] 
remote_setup        = ip['remote_setup']
max_runs            = ip['max_runs']
# if ana_type == 1: # varying only material parameters
#     # geo_srcloc =ip['geo_srcloc'] 
#     # geo_file = geo_srcloc + ip['geo_srcfilename']
#     geo_file_dest = ip['geo_dest']
# elif ana_type == 2: # varying only geometry parameters
    # mat_srcloc = ip['mat_srcloc']
    # mat_dst = ip['mat_dst']
    # mat_filename = ip['mat_filename']

print("Project: ",project_name)
print("Project_path: ",project_path)
print("Number of input factors: ",len(ip['factor_list']))
print("Total number of experiments: ", ip['max_runs'])

##############################################################################
# Create design matrix
##############################################################################

# Get all input factors (design variables)
factor_key = list(factor_list.keys())

# Flags
create_database_flag = 1
create_card_flag = 1
create_material_dataframe = 1

# Creating min/max values for factors
factor_list = factor_minmax(factor_list)

# Create LHD matrix
seed = np.random.randint(0,100)
print("Random seed: ", seed)
with open(project_path+'seed_value.info','a') as myseed:
    str_seed = current_time + ' - ' + str(seed) + '\n'
    myseed.write(str_seed)
    
sample_space = doe.lhs(n=len(factor_list),samples=ip['max_runs'], 
                       criterion='correlation',iterations=ip['lhs_iteration'],
                       random_state=seed).transpose()

# Transforming LHD samples into experimental samples
sample_trafo = transform_samplespace(sample_space, factor_list)

# Creating material angles (vectors) from misalignment angles
# a_1,d_1 - vectors of 0deg ply
# a_2,d_2 - vectors of 90deg ply
if ana_type == 1 or ana_type == 3:
    mang = sample_trafo['mang']
    a1_ang = mang
    a1_ang = np.asarray(a1_ang)
    a_1 = direction_vector(a1_ang)
    sample_trafo['a_1'] = a_1
    d1_ang = a1_ang + 90
    d_1 = direction_vector(d1_ang)
    sample_trafo['d_1'] = d_1
    a_2 = d_1
    sample_trafo['a_2'] = a_2
    d2_ang = a1_ang + 180
    d_2 = direction_vector(d2_ang)
    sample_trafo['d_2'] = d_2

    factor_key.extend(['a_1','d_1','a_2','d_2'])

    # Formatting sample according to LS-Dyna layout (10 nonospaced length)
    sample_formatted = format_val(sample_trafo)

##############################################################################
# Creating analysis cards
##############################################################################
# Material card:
# mid 1.... ply 0deg
# mid 2.... ply 90deg
# mid 3.... cohesive element layer

# Initializing database dictionary
database = {}

if remote_setup:
    saveMacroBash_str = ''

for run in range(0,max_runs):
    
    # Creating database
    #-------------------------------------------------------------------------
    layerAll_database = {}
    layer1_database = {}
    layer2_database = {}
    cohesive_mat_database = {}
    if create_database_flag == 1:
        
        # common material paramters
        layerAll_material_parameters = factor_key.copy()
        layerAll_material_parameters.remove('a_1')
        layerAll_material_parameters.remove('a_2')
        layerAll_material_parameters.remove('d_1')
        layerAll_material_parameters.remove('d_2')        
        for key in layerAll_material_parameters:
            layerAll_database[key] = sample_formatted[key][run]
        
        # Composite material - 0deg plies
        layer1_database = layerAll_database.copy()
        mid = 1
        layer1_database['mid'] = ' '*(10 - len(str(mid))) + str(mid)
        for key in ['a_1','d_1']:#splitting angle vectors into sub components
            layer1_database[f'{key[0]}1'] = sample_formatted[key][run][0]
            layer1_database[f'{key[0]}2'] = sample_formatted[key][run][1]    
        
        # Composite material - 90deg plies
        layer2_database = layerAll_database.copy()
        mid = 2
        layer2_database['mid'] = ' '*(10 - len(str(mid))) + str(mid)
        for key in ['a_2','d_2']:#splitting angle vectors into sub components
            layer2_database[f'{key[0]}1'] = sample_formatted[key][run][0]
            layer2_database[f'{key[0]}2'] = sample_formatted[key][run][1] 
        
        # Cohesive material
        cohesive_mat_database = layerAll_database.copy()
        mid = 3 # adding material id
        cohesive_mat_database['mid'] = ' '*(10 - len(str(mid))) + str(mid)
        
    if create_material_dataframe == 1:
        # for creating data frame
        database[run] = cohesive_mat_database.copy()
        database[run].pop('mid')
        
        # converting strings into float values        
        for key in database[run]:
            database[run][key] = float(database[run][key])
    
    # Creating cards
    #-------------------------------------------------------------------------     
    if create_card_flag == 1:
        l1_str = create_mat_card(mat_database = layer1_database, typ = 1)
        l2_str = create_mat_card(mat_database = layer2_database, typ = 1)
        coh_str = create_mat_card(mat_database = cohesive_mat_database, typ = 2)
        misc_str = create_mat_card(typ=3)
        mat_str = l1_str + l2_str + coh_str + misc_str
        
        # Creating main card
        # Get geometry 
        geo_file_loc = geometry_loc + f'{run}/'*(ana_type!=1)
        geo_full_loc = geo_file_loc + 'geo.k'
            
        # else:
        #     geo_file_loc = project_path+'geometry\\'+ f'{run}\\' * (ana_type!=1)
        #     geo_filename = f'{run}'
        #     geo_full_loc = geo_file_loc + geo_filename + '.k'
        #     try: os.mkdir(project_path+'geometry\\'+f'{run}\\')
        #     except: pass
        
        if ana_type == 2 or ana_type == 3:
            radius = float(sample_formatted['rad'][run])
            
            create_geo(Rx               =radius,
                       filename         = 'geo.k',
                       file_dst         = geo_file_loc,
                       numCurveElem     = 35,
                       numClampXElem    = 4,
                       numMainbodyXElem = 12,
                       numCSElem        = 20)
       
        with open(geo_full_loc) as mygeo:
            geo_str = mygeo.read()
            geo_str = geo_str[:-5]      # removing "*END" from geomtery file
    
        
        output_curve_string = dyna_output_curve(plot = ip['output_file_curve'])
        full_str = geo_str + output_curve_string + mat_str + "\n*END"
        
        try:
            if local_hpc:
                os.mkdir(card_destination+f"{run}/")
                os.mkdir(card_destination+"savemacro/")  
            else:
                os.mkdir(card_destination + f"{ip['project_name']}")
                os.mkdir(card_destination + f"{ip['project_name']}//{run}//")
                
        except:
            try:
                if local_hpc:
                    os.mkdir(card_destination+"savemacro/")  
                    os.mkdir(card_destination + f"{run}//")
                else:
                    os.mkdir(card_destination + f"{ip['project_name']}//" + f"{run}//")
            except:
                if local_hpc:
                    try:
                         os.mkdir(card_destination + f"{run}//")
                    except: pass
        
        filename_main=card_destination + f"{run}//" + f'{run}.k' # dyna filename
        with open(filename_main,'w+') as myfile:
            myfile.write(full_str)
            
        save_macro = f"""*lsprepost macro command file
*macro begin macro_post
openc keyword "../{run}/{run}.k"

elemedit createnode accept
genselect target node
elemedit delenode delete
elemedit delenode accept 1
Build Rendering data
genselect clear

save keywordabsolute 0
save keywordbylongfmt 0
save keywordbyi10fmt 0
save outversion 10
save keyword specialsubsystem "../{run}/{run}.k" 1
*macro end
"""
        if ana_type == 2 or ana_type == 3:
    #         with open(f'savemacro/save{run}.cfile','w+') as mysave:
            with open(f'/scratch/ws/0/apku868a-mt/{project_name}/savemacro/save{run}.cfile','w+') as mysave:
                mysave.write(save_macro)
            saveMacroBash_str += f'/home/apku868a/lsprepost4.8_common/lspp48 -nographics c="save{run}.cfile"' + '\n'
        
    print(run, 'Complete')

#%%
# panda frame
if create_material_dataframe == 1:
    df = pd.DataFrame.from_dict(database, orient='index')
    df.to_csv(ip['mat_dataframe_filename_full'])

# complete
print("Complete ...")


with open(f'/scratch/ws/0/apku868a-mt/{project_name}/savemacro/saveMacro_bash.sh','w+') as mybash:
    mybash.write(saveMacroBash_str)