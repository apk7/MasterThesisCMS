# %%
import pandas as pd
import os
from mt_0_input_factors_all import inputfactors
ip = inputfactors()
local_hpc = ip['local_hpc']
import sys
if local_hpc:
    sys.path.insert(1,"/home/apku868a/pyUtilities")
else:
    sys.path.insert(1,"D:\\Academics\\MasterThesisData\\main_functions\\utilities")
from mt_x_dynaUtilities import plot_scatter,heatmap, min_max_scaling


#%%

project_name = ip['project_name']
project_path = ip['hpc_project'] # ip['project_path']
try: os.mkdir(project_path + 'dataplots/')
except: pass

# df_loc = f"D:\\Academics\\MasterThesisData\\DataAnalysis\\{project_name}\\output_csv\\output_dataframe\\"
# df_loc = f"//home//apku868a//{project_name}//output_csv//output_dataframe//"
df_loc = f"{ip['hpc_csv']}output_dataframe/"

# %%

maxLoad         = 1
maxVal          = 1
scatterMatrix   = 1
heatMap         = 1
delElem         = 0
norm = 1
#%%

df_ip_filename = 'material_dataframe.csv'
print('########', df_loc + df_ip_filename)
df_ip = pd.read_csv(df_loc + df_ip_filename)
df_ip.drop(df_ip.columns[[0]], axis=1, inplace=True)
if norm == 1:
    df_ip = min_max_scaling(df_ip)

# %% Max force plots
if norm == 1:
    df_filename = 'df_maxLoad_norm.csv'
else:
    df_filename = 'df_maxLoad.csv'
    
df_maxLoad_ = pd.read_csv(df_loc + df_filename)

print("Read successfull ")
df_maxLoad_.drop(df_maxLoad_.columns[[0]], axis=1, inplace=True)
# df_maxLoad_.drop(columns=['c_max_xy_stress'], inplace=True)

df_maxLoad_frames = [df_ip,df_maxLoad_]
df_maxLoad = pd.concat(df_maxLoad_frames,axis=1)

# %%
if norm == 1:
    df_filename = 'df_maxVal_norm.csv'
else:
    df_filename = 'df_maxVal.csv'
df_maxVal_ = pd.read_csv(df_loc + df_filename)
df_maxVal_.drop(df_maxVal_.columns[[0]], axis=1, inplace=True)
df_maxVal_.drop(columns=['Time'],axis=1,inplace=True)
# df_maxVal_.drop(columns=['c_max_xy_stress'], inplace=True)
df_maxVal_frames = [df_ip,df_maxVal_]
df_maxVal = pd.concat(df_maxVal_frames,axis=1)

#%%
# if delElem:
#     df_filename = 'df_deleted_elem.csv'
#     df_delElem_ = pd.read_csv(df_loc + df_filename)
#     df_delElem_.drop(df_delElem_.columns[[0]], axis=1, inplace=True)
#     df_delElem_frames = [df_maxLoad,df_delElem_]
#     df_maxLoad = pd.concat(df_delElem_frames,axis=1)


y_var = df_maxVal_.columns


if ip['analysis_type'] == 1:
    x_var={
           # 'angles':["mang"],
           'modulus':["rho","ea","eb","ec","gab","gca","gbc","efs","pba","pca","pcb"],
           'toughness':["enk","ena","enb","ent","enl","gi","gii"],
           'strength':["xc","xt","yc","yt","sl","s"],
           'other':["mang",'rad',"sig","fio","rhC"],
           }
    x_var_cat_list =  ['modulus','toughness','strength','other']
elif ip['analysis_type'] == 2:
    x_var={
           'other':['rad'],
           }
    x_var_cat_list =  ['other']
elif ip['analysis_type'] == 3:
    x_var={
           # 'angles':["mang"],
           'modulus':["rho","ea","eb","ec","gab","gca","gbc","efs","pba","pca","pcb"],
           'toughness':["enk","ena","enb","ent","enl","gi","gii"],
           'strength':["xc","xt","yc","yt","sl","s"],
           'other':["mang",'rad',"sig","fio","rhC"],
           }
    x_var_cat_list =  ['modulus','toughness','strength','other']
# y_var = df_maxLoad.columns

# y_var = ["xForce","yForce","resForce","gIntEnergy",
#          "0_max_x_stress","90_max_x_stress","c_max_x_stress",
#          "0_max_y_stress","90_max_y_stress","c_max_y_stress","0_max_xy_stress", "90_max_xy_stress",
#          "0_max_effective_stress","90_max_effective_stress","c_max_effective_stress",
#          "0_max_shear_stress","90_max_shear_stress","c_max_shear_stress",
#          "0_max_princ_stress","90_max_princ_stress","c_max_princ_stress",
#          'xDisp','yDisp','zDisp','resDisp',
#          'Kt',
# #          'xElemForce0deg','yElemForce0deg','zElemForce0deg','xElemForce90deg','yElemForce90deg','zElemForce90deg',
# #          "del_elem_0deg","del_elem_90deg","del_elem_cohesive",
#          ]

# # if delElem==0:
# #     y_var = y_var[:-3]
    
# df_columns_x1 = df_ip.columns.values
# df_columns_x2 = ["mass density",
#                  "modulus a",
#                  "modulus b",
#                  "modulus c",
#                  "shear modulus ab",
#                  "shear modulus ca",
#                  "shear modulus bc",
#                  "maximum effective strain",
#                  "Poissons ratio ba",
#                  "Poissons ratio ca",
#                  "Poissons ratio cb",
#                  "misalignment angle",
#                  "fracture toughness longitudinal compressive failure",
#                  "fracture toughness longitudinal tensile failure",
#                  "fracture toughness intralaminar matrix tensile failure",
#                  "fracture toughness intralaminar transverse shear failure",
#                  "fracture toughness intralaminar longitudinal shear failure",
#                  "longitudinal compressive strength",
#                  "longitudinal tensile strength",
#                  "transverse compressive strength",
#                  "transverse tensile strength",
#                  "longitudinal shear strength",
#                  "in-plane shear yield stress",
#                  "fracture angle pure transverse comp",
#                  "cohesive density",
#                  "cohesive fracture toughness mode 1",
#                  "cohesive fracture toughness mode 2",
#                  "cohesive peak traction longitudinal",
#                  "cohesive peak traction tangential"]


# footer_dictionary = {}
# text = 'x-axis variables: \n=================== \n'
# # for txt in range(0,32):    
# for i,txtx in enumerate(df_columns_x1):    
#     footer_dictionary[txtx] = txtx+': '+df_columns_x2[i]

# footer_dictionary['xForce']                 = 'xForce: maximum load in longitudinal direction'
# footer_dictionary['yForce']                 = 'yForce: maximum load in transeverse direction'
# footer_dictionary['resForce']               = 'resForce: maximum resultant load'
# footer_dictionary['gIntEnergy']             = 'gIntEnergy: global internal energy'
# footer_dictionary['0_max_x_stress']         = '0_max_x_stress: maximum stress in longitudinal direction in 0 degree plies'
# footer_dictionary['90_max_x_stress']        = '90_max_x_stress: maximum stress in longitudinal direction in 90 degree plies'
# footer_dictionary['c_max_x_stress']         = 'c_max_x_stress: maximum stress in longitudinal direction in cohesive material'
# footer_dictionary['0_max_y_stress']         = '0_max_y_stress: maximum stress in transverse direction in 0 degree plies'
# footer_dictionary['90_max_y_stress']        = '90_max_y_stress: maximum stress in transverse direction in 90 degree plies'
# footer_dictionary['c_max_y_stress']         = 'c_max_y_stress: maximum stress in transverse direction in cohesive material'
# # footer_dictionary['0_max_xy_stress']        = '0_max_xy_stress: maximum stress in xy plane in 0 degree plies'
# footer_dictionary['90_max_xy_stress']       = '90_max_xy_stress: maximum stress in xy plane in 90 degree plies'
# footer_dictionary['0_max_effective_stress'] = '0_max_effective_stress: maximum effective stress in 0 degree plies'
# footer_dictionary['90_max_effective_stress']= '90_max_effective_stress: maximum effective stress in 90 degree plies'
# footer_dictionary['c_max_effective_stress'] = 'c_max_effective_stress: maximum effective stress in cohesive'
# footer_dictionary['0_max_shear_stress']     = '0_max_shear_stress: maximum shear stress in 0 degree plies'
# footer_dictionary['90_max_shear_stress']    = '90_max_shear_stress: maximum shear stress in 90 degree plies'
# footer_dictionary['c_max_shear_stress']     = 'c_max_shear_stress: maximum shear stress in cohesive material'
# footer_dictionary['0_max_princ_stress']     = '0_max_princ_stress: maximum principle stress in 0 degree plies'
# footer_dictionary['90_max_princ_stress']    = '90_max_princ_stress: maximum principle stress in 90 degree plies'
# footer_dictionary['c_max_princ_stress']     = 'c_max_princ_stress: maximum principle stress in cohesive'
# footer_dictionary['del_elem_0deg']          = 'del_elem_0deg: number of deleted element at maximum load in 0 degree plies'
# footer_dictionary['del_elem_90deg']         = 'del_elem_90deg: number of deleted element at maximum load in 90 degree plies'
# footer_dictionary['del_elem_cohesive']      = 'del_elem_cohesive: number of deleted element at maximum load in cohesive material'
# footer_dictionary['xDisp']                  = 'xDisp: x displacement of node at the middle'
# footer_dictionary['yDisp']                  = 'yDisp: y displacement of node at the middle'
# footer_dictionary['zDisp']                  = 'zDisp: z displacement of node at the middle'
# footer_dictionary['resDisp']                = 'resDisp: resultant displacement of node at the middle'
# # footer_dictionary['xElemForce0deg']         = 'xElemForce0deg: Force in x-direction for a 0deg element'
# # footer_dictionary['yElemForce0deg']         = 'yElemForce0deg: Force in y-direction for a 0deg element'
# # footer_dictionary['zElemForce0deg']         = 'zElemForce0deg: Force in z-direction for a 0deg element'
# # footer_dictionary['xElemForce90deg']        = 'xElemForce90deg: Force in x-direction for a 90deg element'
# # footer_dictionary['yElemForce90deg']        = 'yElemForce90deg: Force in y-direction for a 90deg element'
# # footer_dictionary['zElemForce90deg']        = 'zElemForce90deg: Force in z-direction for a 90deg element'
# footer_dictionary['Kt']                     = 'maximum stress concentration near the notch'

# def get_footer_var(x,y,xy_dict):
#     textx = 'x-axis variables: \n=================== \n'
#     for xi in x:
#         textx += xy_dict[xi] + ',  '
    
#     texty = 'y-axis variables: \n=================== \n'
#     for yi in y:
#         texty += xy_dict[yi] + ',  '
    
#     return textx + '\n\n' + texty +'\n'

#%% Testing (delete later)
# random_enkink = np.random.random_sample(130)*1e8
# df_maxLoad['enk'] = random_enkink
# df_maxVal['enk'] = random_enkink

#%% ################# Scatter plots #####################

if scatterMatrix:
    if maxLoad:
        # scale = 'log'
        scale = 'linear'
        x_var1={}
        for var in x_var_cat_list:
            x_var1[var] = x_var[var]
        
        for i in x_var1:
            x = x_var1[i]
            y = df_maxLoad_.columns
            
#             footer = get_footer_var(x,y,footer_dictionary)
            plot_scatter(df_maxLoad,
                         xvar=x,
                         yvar=y,
                         typ=1,
                         title=f'Regression plots: value of o/p at maximum load vs {i}', 
                         corr_type='pearson', 
                         file_name= project_path +'dataplots/' + f'corr_scatter_matrix_maxload_{i}_norm.pdf', 
                         scale=scale,
                         grid=True,
                         r2score_flag=False,
                         order=2,
#                          text={'data':footer,'rel_xyloc':[0.01,0],'fontsize':12}
                        )
            print(i, ' complete....')
        print('Scatterplot maxLoad complete ... ')
            
    if maxVal:
        df = df_maxVal
        # scale='log'
        scale = 'linear'
        x_var2={}
        for var in x_var_cat_list:
            x_var2[var] = x_var[var]
            
        for i in x_var2:
            print(i)
            x=x_var2[i]
            y=df_maxVal_.columns
#             footer = get_footer_var(x,y,footer_dictionary)
            plot_scatter(df,
                         xvar=x,
                         yvar=y,
                         typ=1,
                         title=f'Regression plots: maximum value of o/p variables vs {i} \n', 
                         corr_type='pearson', 
                         file_name= project_path +'dataplots/' + f'corr_scatter_matrix_maxval_{i}_norm.pdf', 
                         scale=scale,
                         grid=True,
                         r2score_flag=False,
                         order=2,
#                          text={'data':footer,'rel_xyloc':[0.01,0],'fontsize':12}
                        )
                        
            print(i, ' complete....')
        print('Scatterplot maxVal complete ... ')
            
#%%    
############### heatmap #################

if heatMap:
    
    # flattening x_var dictionary into list
    x_tick = []
    for i in x_var:
        for ii in x_var[i]:
            x_tick.append(ii)
    
    destination = project_path +'dataplots/' 

    # colormap = 'hot'
    # colormap = 'viridis'
    # colormap = 'inferno'
    # colormap = 'cividis'
    # colormap = 'binary'
    # colormap = "YlGnBu"
    
    if maxLoad:
        y_tick= df_maxLoad_.columns
        total_var = [*x_tick,*y_tick]
#         footer = get_footer_var(x_tick,y_tick,footer_dictionary)
        heatmap(data=df_maxLoad[total_var],
                x_var = x_tick,
                y_var = y_tick,
                destination=destination,
                filename='heatmap_max_load'+ "_norm"*norm +'.pdf',
                compact=True,
                title={'label':'Heatmap at maximum load\n','size':30},
                fig_kws={'figsize':[40,20],'dpi':150},
                anno_kws={'size':17,'rotation':0},
                cbar_kws={'label':'Correlation coefficient','label_size':30,'tick_size':19},
                label={'size':50},
                tick={'size':20,'xrotation':0},
                cmap_='viridis',
#                 text = {'data':footer,'rel_xyloc':[0,45],'fontsize':16}
               )
    if maxVal:
        y_tick= df_maxVal_.columns
        total_var = [*x_tick,*y_tick]
#         footer = get_footer_var(x_tick,y_tick,footer_dictionary)
#         footer = get_footer_var(x_tick,y_tick,footer_dictionary)
        heatmap(data=df_maxVal[total_var],
                x_var = x_tick,
                y_var = y_tick,
                destination=destination,
                filename='heatmap_max_val' + "_norm"*norm +'.pdf',
                compact=True,
                title={'label':'Heatmap of maximum values in analysis\n','size':30},
                fig_kws={'figsize':[40,20],'dpi':150},
                anno_kws={'size':17,'rotation':0},
                cbar_kws={'label':'Correlation coefficient','label_size':30,'tick_size':19},
                label={'size':50},
                tick={'size':20,'xrotation':0},
                cmap_='viridis',
#                 text={'data':footer,'rel_xyloc':[0,35],'fontsize':16}
               )
