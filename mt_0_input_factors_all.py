#=============================================================================
# Author: Apurv Kulkarni
#-----------------------------------------------------------------------------
# Analysis setup
#=============================================================================

def inputfactors():
    #=========================================================================
    # Project directory setup
    #=========================================================================

    # Initializing input parameter dictionary
    ip = {}
    
    # Analysis Type
    # 1 : Material parameters as the only design variable
    # 2 : Notch geometry as the only design variable
    # 3 : Material parameter and Notch geometry as the only design variable
    ip['analysis_type'] = 3
         
    # Main project folder name (contains all the files where database will be created)
    project_name = 'project_xyz'
    ip['project_name'] = project_name
    
    # Flag for setting if the python scripts are on "local location" or on "remote location"
    # remote_setup = 0
    # ip['remote_setup'] = remote_setup
        
    # Database main folder with project folder
    project_path = f"D:\\Academics\\MasterThesisData\\DataAnalysis\\{project_name}\\"
    ip['project_path'] = project_path
            
    # Database main folder with project folder
    # project_path = '/home/apku868a/' + project_name
    # ip['project_path'] = project_path      

    # Path for LS-Dyna result folder
    # This is the main folder which contains subfolders with run id as their 
    # name as shown below:
    #
    # <ip['lsdyna_result_path']>
    # |
    # `-- 1
    # |   `-- d3plot files (LS_Dyna results)
    # `-- 2
    #     `-- d3plot files
    # ip['lsdyna_result_path'] = ip['project_path'] + 'results/'
    ip['lsdyna_result_path'] = f"/scratch/ws/0/apku868a-mt/{project_name}/"
    
    # App path for LS-PrePost
    ip['lsdyna_app'] = 'lspp'
    # ip['lsdyna_app'] = '/home/apku868a/lsprepost4.8_common/lspp48'
    
    # LS-Dyna card destination
    ip['card_destination_main']= ip['project_path'] + "cards/"
    ip['card_destination']= ip['card_destination_main']+ip['project_name']+'/'
    
    # Directory for saving "serverJob" script lists (if job_submission_type=1).
    # Please refer to "mt_2_CreateHpcJobs.py" for more info
    ip['job_dst']= ip['project_path'] + "hpc_jobs/"
    
    # Location of macros for data cleaning and extraction
    ip['macro_dst_newFormat'] = ip['project_path'] + "macro\\" + "newFormat/"
    ip['macro_dst_data'] = ip['project_path'] + "macro\\" + "dataExtraction/"
    ip['csv_destination']   = ip['project_path'] + "output_csv/"
    
    # Result location on local machine
    ip['results_location']  = ip['project_path'] + "results/"
    
    # Directory where, data extracted and cleaned, from all the csv ouput,
    # is saved
    ip['extractedDatabase'] = ip['project_path'] + 'extractedDatabase/'
    
    # If analysis is run on HPC server    
    ip['hpc_loc'] = "/scratch/ws/0/apku868a-mt/"
    
    # Plot file location for data analysis
    ip['plot_loc'] = ip['project_path'] + 'plots/'
    
    # Default geometry and material location 
    # For analysis_type = 1 : default geometry is required
    # For analysis_type = 2 : default material is required
    ip['default_cards'] = 'default_cards/'      
    
    ip['geo_dest'] = ip['project_path'] + 'geometry/'
    if ip['analysis_type'] == 1:        
        ip['geo_srcfilename'] = ip['default_cards'] + 'default_geometry.k'        
    elif ip['analysis_type'] == 2:
        ip['mat_srcloc'] = ip['default_cards'] + 'default_material.k'
        ip['mat_dst'] = ip['project_path'] + 'material/'

    #=========================================================================
    # Input parameter setup
    #=========================================================================
    #=========================================================================
    # Type val        | Variation type | Distribution type | Requirements
    #-------------------------------------------------------------------------
    #   10             percentage(%)      log uniform       'value','vari'
    #   11             percentage(%)      linear            'value','vari'
    #   20             absolute values    log uniform       'min_val','max_val'
    #   21             absolute values    linear            'min_val','max_val'
    # 3(experimental)  percentage(%)      discrete levels   'levels'
    #-------------------------------------------------------------------------
    # 'value'   : basevalue
    # 'vari'    : % variation
    # 'min_val' : minimum value
    # 'max_val' : maximum value
    # 'levels'  : discrete levels.
    #             Eg: var:{'type':3,'levels':[5,8,9]}. 'var' will have only
    #             these discrete values assigned in random order.
    # ========================================================================
    
    variation1 = 20
    variation2 = 40
    variation3 = 80
    
    factor_list = {
        # Pinho material model
        #---------------------------------------------------------------------
        # Mass Density
        'rho' :{'type':11, 'value': 1530,    'vari':variation1},               
        # Young's modulus in longitudinal direction (a)
        'ea'  :{'type':11, 'value': 1.21e+11,'vari':variation1},
        # _||_ in transverse direction (b)                
        'eb'  :{'type':11, 'value': 9.24e+9, 'vari':variation1},                
        # _||_ in through thickness direction (c)
        'ec'  :{'type':11, 'value': 9.24e+9, 'vari':variation1},
        # Shear modulus ab                
        'gab' :{'type':11, 'value': 1.35e+10,'vari':variation1},
        # Shear modulus ca                
        'gca' :{'type':11, 'value': 1.35e+10,'vari':variation1},
        # Shear modulus bc                
        'gbc' :{'type':11, 'value': 2.92e+9, 'vari':variation1},                
        # Maximum effective strain for element layer failure
        'efs' :{'type':21, 'min_val':-0.4, 'max_val':-0.1},
        # Poisson's ratio in ba
        'pba' :{'type':11, 'value': 0.015,   'vari':variation1},                
        # Poisson's ratio in ca
        'pca' :{'type':11, 'value': 0.015,   'vari':variation1},
        # Poisson's ratio in cb
        'pcb' :{'type':11, 'value': 0.37,    'vari':variation1},
        # Misalignment angle
        'mang':{'type':21, 'min_val':0, 'max_val': 10},
        # Fracture toughness for longitudinal (fiber) compressive failure mode.
        'enk' :{'type':11, 'value': 4e+7,    'vari':variation3},
        # Fracture toughness for longitudinal (fiber) tensile failure mode.
        'ena' :{'type':11, 'value': 4.5e+7,  'vari':variation3},
        # Fracture toughness for intralaminar matrix tensile failure.
        'enb' :{'type':11, 'value': 2.5e+3,  'vari':variation3},
        # Fracture toughness for intralaminar matrix transverse shear failure.
        'ent' :{'type':11, 'value': 4e+3,    'vari':variation3},
        # Fracture toughness for intralaminar matrix longitudinal shear failure.
        'enl' :{'type':11, 'value': 4e+3,    'vari':variation3},
        # Longitudinal compressive strength, a-axis (positive value).
        'xc'  :{'type':11, 'value': 6.5e+9,  'vari':variation2},
        # Longitudinal tensile strength, a-axis.
        'xt'  :{'type':11, 'value': 1.79e+9, 'vari':variation2},
        # Transverse compressive strength, b-axis (positive value).
        'yc'  :{'type':11, 'value': 1.3e+8,  'vari':variation2},
        # Transverse tensile strength, b-axis.
        'yt'  :{'type':11, 'value': 4.2e+7,  'vari':variation2},
        # Longitudinal shear strength.
        'sl'  :{'type':11, 'value': 7.4e+7,  'vari':variation2},               
        # In-plane shear yield stress
        'sig' :{'type':11, 'value': 0.75e+6, 'vari':variation2},
        # Fracture angle in pure transverse compression
        'fio' :{'type':21, 'min_val':51, 'max_val': 55},
    
        # Cohesive material parameters
        #---------------------------------------------------------------------
        # Mass Density of cohesive material
        'rhC' :{'type':11, 'value': 6.50,    'vari':variation1},
        # Fracture toughness / energy release rate   for mode I.                
        'gi'  :{'type':11, 'value': 500,     'vari':variation3},
        # Fracture toughness / energy release rate   for mode II.
        'gii' :{'type':11, 'value': 800,     'vari':variation3},
        # peak traction in normal direction mode
        't'   :{'type':21, 'min_val':0.37E+08, 'max_val':4.37E+08},
        # Peak traction in tangential direction (mode II).
        's'   :{'type':21, 'min_val':0.37E+08, 'max_val':4.37E+08},
        
        # Geometry parameters
        #---------------------------------------------------------------------
        # Longitudinal radius
        'rad' :{'type':21,'value':'nan','min_val':0.0005, 'max_val':0.01}                                                                  
        }

    ip['factor_list'] = factor_list

    # Total number of experiments (experiment ID: 0,1,..., max_runs-1)
    ip['max_runs'] = 210

    # MAximum number of iterations for generating optimum LHD matrix
    ip['lhs_iteration'] = 1000
    
    # For frequency of output (d3plot files): [[time,time_step_size],[],..]
    ip['output_file_curve'] = [
        [0,0.0014],[0.0005, 1.00E-04],[0.0009, 1.00E-05],[0.00128, 5.00E-06],        
        [0.00192, 5.00E-06],[0.0022, 8.00E-05],[0.0025, 7.00E-04],
        [0.0035, 0.001]
        ]
    
    return ip


def createProjDirStruct(ip):
    #=========================================================================
    # Creating project directory structure
    #=========================================================================
    import os
    import shutil
    
    assert(type(ip)==dict)
    # Creating project directory structure
    os.makedirs(ip['project_path'], exist_ok=True)
    os.makedirs(ip['card_destination'], exist_ok=True)
    for run in range(0,ip['max_runs']):
        os.makedirs(ip['card_destination'] + f'{run}/', exist_ok=True)
    os.makedirs(ip['job_dst'], exist_ok=True)
    # os.makedirs(ip['results_location'], exist_ok=True)
    os.makedirs(ip['macro_dst_newFormat'], exist_ok=True)
    os.makedirs(ip['macro_dst_data'], exist_ok=True)
    os.makedirs(ip['csv_destination'], exist_ok=True)
    for run in range(0,ip['max_runs']):
            os.makedirs(ip['csv_destination'] + f'{run}/', exist_ok=True)
    os.makedirs(ip['extractedDatabase'], exist_ok=True)
    os.makedirs(ip['geo_dest'], exist_ok=True)
    os.makedirs(ip['plot_loc'], exist_ok=True)
    if ip['analysis_type']==1:
        shutil.copy2(ip['geo_srcfilename'], ip['geo_dest']+'geo.k')
    elif ip['analysis_type']==2 or 3:
        for run in range(0,ip['max_runs']):
            os.makedirs(ip['geo_dest'] + f'{run}/', exist_ok=True)            
        if ip['analysis_type']==2:
            os.makedirs(ip['mat_dst'], exist_ok=True)            
            shutil.copy2(ip['mat_srcloc'], ip['mat_dst'])
    