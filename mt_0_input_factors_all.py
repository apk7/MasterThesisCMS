
#%%

def inputfactors():
    #Setup

    ip = {}
    
    ## Analysis Type
    # 1 : Material parameters as the only design variable
    # 2 : Notch geometry as the only design variable
    # 3 : Material parameter and Notch geometry as the only design variable
    ip['analysis_type'] = 3 
         
    # Main project folder name (contains all the files where database will be created)
    project_name = 'mainProject_test'
    ip['project_name'] = project_name
    
    # Flag for setting if the python scripts are on "local location" or on "remote location"
    # remote_setup = 0
    # ip['remote_setup'] = remote_setup
        
    # Database main folder with project folder
    project_path = f"D:\\Academics\\MasterThesisData\\DataAnalysis\\{project_name}\\"
    ip['project_path'] = project_path
    
    # Path to python libraries used in this project
    ip['python_library_path'] = "D:\\Academics\\MasterThesisData\\main_functions\\utilities\\"
        
    # Database main folder with project folder
    # project_path = '/home/apku868a/' + project_name
    # ip['project_path'] = project_path
    # Path to python libraries used in this project
    # ip['python_library_path'] = "/home/apku868a/pyUtilities/"

    # Path for LS-Dyna result folder
    # This is the main folder which contains subfolders with run id as their name as shown below:
    #
    # <ip['lsdyna_result_path']>
    # |
    # `-- 1
    # |   `-- d3plot files (LS_Dyna results)
    # `-- 2
    #     `-- d3plot files
    # ip['lsdyna_result_path'] = f"/scratch/ws/0/apku868a-mt/{project_name}/"
    ip['lsdyna_result_path'] = ip['project_path'] + 'results/'
    
    # App path for LS-PrePost
    ip['lsdyna_app'] = 'lspp'
    # ip['lsdyna_app'] = '/home/apku868a/lsprepost4.8_common/lspp48'
    
    # LS-Dyna card destination
    card_destination = ip['project_path'] + "cards\\"
    ip['card_destination']=card_destination
    
    # 
    job_destination  = ip['project_path'] + "job_cards\\"
    ip['job_destination']=job_destination
    
    job_list_name = project_name
    ip['job_location']= job_destination
    ip['job_list_name'] = job_list_name
    
    ip['mat_dataframe_file_full'] = ip['project_path'] + "material_dataframe.csv"
    
    # for generating macros
    ip['macro_destination'] = ip['project_path'] + "macro\\"
    ip['csv_destination']   = ip['project_path'] + "output_csv\\"
    
    # Result location on local machine
    ip['results_location']  = ip['project_path'] + "results/"
    
    if ip['remote_setup']:
        
        card_destination = "/scratch/ws/0/apku868a-mt/" + project_name +'/'      
        ip['card_destination']=card_destination
        
        job_destination  = "job_cards/"
        ip['job_destination']=job_destination
        
        job_list_name = project_name
        ip['job_location']= job_destination
        ip['job_list_name'] = job_list_name
        
        
        # for generating macros
        macro_destination = "macro/"
        ip['macro_destination'] = macro_destination
        csv_destination = "output_csv/"
        ip['csv_destination']=csv_destination
        
        ip['mat_dataframe_file_full'] = csv_destination + "material_dataframe.csv"
        
        results_location= "results/"
        ip['results_location'] = results_location
    
    
    # %%
    #-------------------------------------------------------------------------
    # Type | 
    # type = 10 :Variation is considered according to %.
    #            Sample distribution is log uniform.
    # type = 11 :Variation is considered according to %.
    #            Sample distribution is linear.
    # type = 20 :variation is considered according to absolute values
    #            Sample distribution is log uniform.
    # type = 21 :variation is considered according to absolute values
    #            Sample distribution is linear
    # type = 3  :Variation is considered according to %,
    #            Samples generated are bound to specified levels
    # type = 4 : Varilables depending upon some other variables. Example var = 0.95* other_variable _value
    # type = 50,51 : Varilables depending upon some other variables but also need to be bounded. Example normalizinz values w.r.t some other values.
    
    
    variation1 = 20 #10
    variation2 = 40 #15
    variation3 = 80 #40
    
    factor_list = {
        # Pinho material model
        #---------------------------------------------------------------------
        # Mass Density
        'rho' :{'type':10, 'value': 1530,    'vari':variation1},               
        # Young's modulus in longitudinal direction (a)
        'ea'  :{'type':10, 'value': 1.21e+11,'vari':variation1},
        # _||_ in transverse direction (b)                
        'eb'  :{'type':10, 'value': 9.24e+9, 'vari':variation1},                
        # _||_ in through thickness direction (c)
        'ec'  :{'type':10, 'value': 9.24e+9, 'vari':variation1},
        # Shear modulus ab                
        'gab' :{'type':10, 'value': 1.35e+10,'vari':variation1},
        # Shear modulus ca                
        'gca' :{'type':10, 'value': 1.35e+10,'vari':variation1},
        # Shear modulus bc                
        'gbc' :{'type':11, 'value': 2.92e+9, 'vari':variation1},                
        # Maximum effective strain for element layer failure
        'efs' :{'type':11, 'value': 'nan',   'min_val':-0.4, 'max_val':-0.1},
        # Poisson's ratio in ba
        'pba' :{'type':11, 'value': 0.015,   'vari':variation1},                
        # Poisson's ratio in ca
        'pca' :{'type':11, 'value': 0.015,   'vari':variation1},
        # Poisson's ratio in cb
        'pcb' :{'type':11, 'value': 0.37,    'vari':variation1},
        # Misalignment angle
        'mang':{'type':21, 'value': 0,       'min_val':0, 'max_val': 10},
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
        'fio' :{'type':21, 'value': 53,      'vari':2},
    
        # Cohesive material parameters
        #---------------------------------------------------------------------
        # Mass Density of cohesive material
        'rhC' :{'type':11, 'value': 6.50,    'vari':variation1},
        # Fracture toughness / energy release rate   for mode I.                
        'gi'  :{'type':11, 'value': 500,     'vari':variation3},
        # Fracture toughness / energy release rate   for mode II.
        'gii' :{'type':11, 'value': 800,     'vari':variation3},
        # peak traction in normal direction mode
        't'   :{'type':11, 'value': 'nan', 'min_val':2.780E+07, 'max_val':6.520E+07},
        # Peak traction in tangential direction (mode II).
        's'   :{'type':11, 'value': 'nan', 'min_val':0.37E+08, 'max_val':4.37E+08},
        
        # Geometry parameters
        #---------------------------------------------------------------------
        'rad' :{'type':11,'value':'nan','min_val':0.0005, 'max_val':0.01}                                                                  
        }
    
    max_runs = 210
    lhs_iteration = 1000
    
    # output_file_curve = [
    #     [0.000000,5.00e-4],
    #     [0.001250,1.20e-5],
    #     [0.001550,0.80e-5],
    #     [0.002125,1.20e-5],
    #     [0.002400,4.00e-4],
    #     [0.003500,9.00e-4],
    #     [0.030400,4.00e-1],
    #     ]
    
    # output_file_curve = [
    #     [0,0.001],
    #     [0.00125,5.00E-06],
    #     [0.0025,5.00E-06],
    #     [0.0035,0.0009],
    #     [0.0304,4e-1]
    #     ]
    
    output_file_curve = [
        [0,0.0014],
        [0.0005, 1.00E-04],
        [0.0009, 1.00E-05],
        [0.00128, 5.00E-06],        
        [0.00192, 5.00E-06],
        [0.0022, 8.00E-05],
        [0.0025, 7.00E-04],
        [0.0035, 0.001]
        ]
    
    ip['factor_list'] = factor_list
    ip['max_runs'] = max_runs
    ip['lhs_iteration'] = lhs_iteration
    ip['output_file_curve'] = output_file_curve
    
    ip['geo_dest'] = ip['project_path'] + 'geometry/'
    if ip['analysis_type'] == 1:        
        ip['geo_srcloc'] = 'default_files/'      # Default geometry location
        ip['geo_srcfilename'] = 'default_geo'
        
    elif ip['analysis_type'] == 2:
        ip['mat_filename'] = 'default_mat.k'
        ip['mat_srcloc'] = "D:\\Academics\\MasterThesisData\\main_functions\\geometry\\" + ip['mat_filename']
        ip['mat_dst'] = ip['project_path'] + 'material\\'
    return ip

def createProjDirStruct(ip):
    import os
    assert(type(ip)==dict)
    # Creating project directory structure
    os.makedirs(ip['project_path'], exist_ok=True)
    os.makedirs(ip['card_destination'], exist_ok=True)
    os.makedirs(ip['job_destination'], exist_ok=True)
    # os.makedirs(ip['results_location'], exist_ok=True)
    os.makedirs(ip['macro_destination'], exist_ok=True)
    os.makedirs(ip['csv_destination'], exist_ok=True)
    
    os.makedirs(ip['geo_dest'], exist_ok=True)
    if ip['analysis_type']==1:
        os.copy(ip['geo_srcloc']+ip['geo_srcfilename'], ip['geo_dest'][:-1], exist_ok=True)    
    elif ip['analysis_type']==2 or 3:
        for run in range(0,ip['max_runs']):
            os.makedirs(ip['geo_dest'] + f'{run}/', exist_ok=True)
    
        if ip['analysis_type']==2:
            os.makedirs(ip['mat_dst'], exist_ok=True)
            os.copy(ip['mat_srcloc'], ip['mat_dst'][:-1], exist_ok=True)
    
   
    # if ana_type == 1: # varying only material parameters
    #     geo_srcloc =ip['geo_srcloc'] 
    #     geo_file = geo_srcloc + ip['geo_srcfilename']
    #     geo_file_dest = ip['geo_dest']
    #     try: 
    #         os.mkdir(geo_file_dest)    
    #         os.copy(geo_file, geo_file_dest[:-1])
    #     except: 
    #         try: os.copy(geo_file, geo_file_dest[:-1])
    #         except: pass
    # elif ana_type == 2: # varying only geometry parameters
    #     mat_srcloc = ip['mat_srcloc']
    #     mat_dst = ip['mat_dst']
    #     mat_filename = ip['mat_filename']
    #     try:
    #         os.mkdir(mat_dst)
    #         copy(mat_srcloc,mat_dst)
    #     except:
    #         try: copy(mat_srcloc,mat_dst)
    #         except: pass
    
    