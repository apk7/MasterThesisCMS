#=============================================================================
# Author: Apurv Kulkarni
#-----------------------------------------------------------------------------
# Creating LHD experiment and LS-Dyna cards
#=============================================================================

# Loading dependencies      
import os
import pandas as pd
import numpy as np
import pyDOE2 as doe
from shutil import rmtree
from mt_0_input_factors_all import *
from utilities.mt_x_projectUtilities import *
from utilities.mt_x_lsppMacro import newCardFormat
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
max_runs            = ip['max_runs']

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
seed = 74 #np.random.randint(0,100)
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

# if remote_setup:
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
        
        # Get materaial data from database
        # --------------------------------------------------------------------
        # 0 deg ply
        l1_str = create_mat_card(mat_database=layer1_database, typ=1)
        # 90 deg ply
        l2_str = create_mat_card(mat_database=layer2_database, typ=1)
        # cohesive layer
        coh_str = create_mat_card(mat_database=cohesive_mat_database, typ=2)
        # Other information
        misc_str = create_mat_card(typ=3)
        
        mat_str = l1_str + l2_str + coh_str + misc_str
                
        # Get geometry 
        # --------------------------------------------------------------------
        geo_file_loc = geometry_loc + f'{run}/'*(ana_type!=1)
        geo_full_loc = geo_file_loc + 'geo.k'
        
        # Create new geometry if radius is a design varible
        if ana_type == 2 or ana_type == 3:
            radius = float(sample_formatted['rad'][run])
            
            create_geo(Rx               = radius,
                        filename         = 'geo',
                        file_dst         = geo_file_loc,
                        numCurveElem     = 35,
                        numClampXElem    = 4,
                        numMainbodyXElem = 12,
                        numCSElem        = 20)
            
        # Get string containing mesh information from the file
        with open(geo_full_loc) as mygeo:
            geo_str = mygeo.read()
            geo_str = geo_str[:-5]      # removing "*END" from geomtery file
        
        # Get string with curve info about d3plot output generation frequency
        output_curve_string = dyna_output_curve(plot = ip['output_file_curve'])
        
        # Create final card with geometry and material data
        # --------------------------------------------------------------------
        full_str = geo_str + output_curve_string + mat_str + "\n*END"
        
        card_dst = (card_destination + str(run) + '\\'*(os.name=='nt') + 
                    '/' * (os.name=='posix'))
        filename_main = card_dst + f'{run}.k'
        with open(filename_main,'w+') as myfile:
            myfile.write(full_str)
        
        # "create_geo" function fails to convert the geometry file into new 
        # format following macro can be run to convert the cards into 
        # new format. This can happen when setup is on remote server (HPC)
        macrofilename = f'{run}.cfile'
        saveMacroBash_str += newCardFormat(
            macro_file      = ip['macro_dst_newFormat']+ macrofilename,
            dyna_card_loc   = filename_main,
            lspp_loc        = ip['lsdyna_app'])
            
        # Cleaning temporary temporary geomerty files
        if ana_type == 2 or ana_type == 3:
            rmtree(geometry_loc + str(run))
    
    print(run, 'Complete')

# Dave input design matrix
if create_material_dataframe == 1:
    df = pd.DataFrame.from_dict(database, orient='index')
    df.to_csv(ip['extractedDatabase'] + "material_dataframe.csv")

#
with open(ip['macro_dst_newFormat'] + 'saveMacro_bash.sh','w+') as mybash:
    mybash.write(saveMacroBash_str)

print("Complete .....")
print("####################################################################")
print(f"""1) Please run 
\t\t cd {ip['macro_dst_newFormat']}
\t\t dos2unix *.sh
\t\t chmod -R 775 *
   if required.""")
print(f"""2) Please run \n\t\t {ip['macro_dst_newFormat']}saveMacro_bash.sh 
   to convert cards into new format. """)
print("""3) Please run 'mt_2_createHpcJobs' for creating HPC job scripts as a 
   next step in the analysis workflow.""")


