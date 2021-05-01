#=============================================================================
# Author: Apurv Kulkarni
#-----------------------------------------------------------------------------
# Data analysis using scatterplot, heatmap, regression, OLS, PCC, SRCC
#=============================================================================

from utilities.mt_x_projectUtilities import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
from mt_0_input_factors_all import inputfactors
from statsmodels.formula.api import ols
import seaborn as sns

# for Latex fonts
rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
rc({'font.size':20})
plt.rc('text', usetex=True)
plt.rc('font', family='serif')
fontsize=14

# for timestamp on saved plots filename
import datetime
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

# get input data
ip = inputfactors()

# Project name
project_name = ip['project_name']

# loc = "D:/Academics/MasterThesisData/DataAnalysis/"
extractedDatabse_loc = ip['extractedDatabase']

extractedDatabse_loc = "D:\\Academics\\MasterThesisData\\DataAnalysis\\mainProject_all3\\output_csv\\output_dataframe\\"

plot_path = "D:\\Academics\\MasterThesisData\\DataAnalysis\\AllPlots\\"

# Flags to create corresponding plot type
#-----------------------------------------------------------------------------

scatterPlot     = 0     # Scatter plot flag
heatmap         = 0     # heatmap flag
multiLinearReg  = 1     # Multiple linear regrression (OLS)

# Whether to normalize the plots (for both x- and y-axes)
normalize        = 1

# Getting extracted data
#-----------------------------------------------------------------------------
# Initializing dataframes
df_maxLoad_all = pd.DataFrame()
df_maxVal_all = pd.DataFrame()
df_input_all = pd.DataFrame()
    
df_loc = extractedDatabse_loc      

df_filename = 'material_dataframe.csv'
df_ = pd.read_csv(df_loc + df_filename)
df_.drop(df_.columns[[0]], axis=1, inplace=True)
if 'rad' not in df_.columns:
    df_['rad'] = 0.0024
df_frames = [df_input_all,df_]
df_input_all = pd.concat(df_frames,axis=0)

# cleaning database
df_input_all = df_input_all.replace([np.inf, -np.inf], np.nan)

df_filename = 'df_maxLoad.csv'
df_ = pd.read_csv(df_loc + df_filename)
df_.drop(df_.columns[[0]], axis=1, inplace=True)
df_frames = [df_maxLoad_all,df_]
df_maxLoad_all = pd.concat(df_frames,axis=0)
# df_maxLoad_all = df_maxLoad_all.drop(columns='MFA')
   

# Selecting design variables to plot
# Uncomment or comment to skip or plot, respectively
# ---------------------------------------------------------------------------

df_input_all_new = pd.DataFrame()

df_input_all_new['XT']      = df_input_all['xt']
df_input_all_new['XC']      = df_input_all['xc']
df_input_all_new['YT']      = df_input_all['yt']
df_input_all_new['YC']      = df_input_all['yc']
df_input_all_new['SL']      = df_input_all['sl']

df_input_all_new['ENKINK']  = df_input_all['enk']
df_input_all_new['ENA']     = df_input_all['ena']
df_input_all_new['ENB']     = df_input_all['enb']
df_input_all_new['ENT']     = df_input_all['ent']
df_input_all_new['ENL']     = df_input_all['enl']
df_input_all_new['GI']      = df_input_all['gi']
df_input_all_new['GII']     = df_input_all['gii']

df_input_all_new['EA']      = df_input_all['ea']
df_input_all_new['EB']      = df_input_all['eb']
df_input_all_new['EC']      = df_input_all['ec']
df_input_all_new['GAB']     = df_input_all['gab']
df_input_all_new['GCA']     = df_input_all['gca']
df_input_all_new['GBC']     = df_input_all['gbc']
df_input_all_new['PBA']     = df_input_all['pba']
df_input_all_new['PCA']     = df_input_all['pca']
df_input_all_new['PCB']     = df_input_all['pcb']

df_input_all_new['MANG']    = df_input_all['mang']
df_input_all_new['RHO']     = df_input_all['rho']
df_input_all_new['RHOC']    = df_input_all['rhC']
df_input_all_new['EFS']     = df_input_all['efs']
df_input_all_new['SIGY']    = df_input_all['sig']
df_input_all_new['FIO']     = df_input_all['fio']
df_input_all_new['T']       = df_input_all['t']
df_input_all_new['S']       = df_input_all['s']
df_input_all_new['NOTCHR']  = df_input_all['rad'] / 0.0024

xvar = df_input_all_new.columns

# Selecting output variables
#-----------------------------------------------------------------------------
# Select which database is required for plotting
# level = 'laminate': global values
#       = 'ply'     : ply values (0deg,90deg,cohesive layer)
#       = 'both'    : a;; values
level = 'laminate'

df_maxLoad_all_new = pd.DataFrame()

if level == 'laminate':
    
    df_maxLoad_all_new['TimeMAS']   = df_maxLoad_all['Time']
    
    df_maxLoad_all_new['gMAS']      = df_maxLoad_all['X-Stress']
    df_maxLoad_all_new['gMLS']      = df_maxLoad_all['gMLS']
    df_maxLoad_all_new['gMTS']      = df_maxLoad_all['gMTS']
    df_maxLoad_all_new['gMPS']      = df_maxLoad_all['gMPS']    
    df_maxLoad_all_new['gMSS']      = df_maxLoad_all['gMSS']
    df_maxLoad_all_new['gMIPSS']    = df_maxLoad_all['gMIPSS']
    df_maxLoad_all_new['SC']        = df_maxLoad_all['SC']
    df_maxLoad_all_new['gIE']       = df_maxLoad_all['gIE']

    
if level == 'ply' or 'both':
    df_maxLoad_all_new['0MLS']      = df_maxLoad_all['0MLS']
    df_maxLoad_all_new['90MLS']     = df_maxLoad_all['90MLS']
    df_maxLoad_all_new['cMLS']      = df_maxLoad_all['cMLS']

    df_maxLoad_all_new['0MTS']      = df_maxLoad_all['0MTS']
    df_maxLoad_all_new['90MTS']     = df_maxLoad_all['90MTS']
    df_maxLoad_all_new['cMTS']      = df_maxLoad_all['cMTS']

    df_maxLoad_all_new['0MPS']      = df_maxLoad_all['0MPS']
    df_maxLoad_all_new['90MPS']     = df_maxLoad_all['90MPS']
    df_maxLoad_all_new['cMPS']      = df_maxLoad_all['cMPS']

    df_maxLoad_all_new['0MSS']      = df_maxLoad_all['0MSS']
    df_maxLoad_all_new['90MSS']     = df_maxLoad_all['90MSS']
    df_maxLoad_all_new['cMSS']      = df_maxLoad_all['cMSS']

    df_maxLoad_all_new['0MIPSS']    = df_maxLoad_all['0MIPSS']
    df_maxLoad_all_new['90MIPSS']   = df_maxLoad_all['90MIPSS']


yvarMaxLoad = df_maxLoad_all_new.columns

df_maxLoad_frames = [df_input_all_new,df_maxLoad_all_new]
df_maxLoad = pd.concat(df_maxLoad_frames,axis=1)

if normalize:
    df_maxLoad = min_max_scaling(df_maxLoad)

# Scatter plot
if scatterPlot:
    scale='linear' # plotting on linear or log scale
    yVarTotal = df_maxLoad_all_new.columns
    
    # plotting for each output variable one at a time
    for i in yVarTotal:
        var = [*xvar,i]
        df_maxLoad_ = df_maxLoad[var]
        
        analysis_plot(df       = df_maxLoad_,
                      xvar     = xvar,
                      yvar     = [i],
                      typ      = 1,
                      file_name= (plot_path+f'{xvar[0]}VS{i}_ScatterPlot.png'), 
                      scale    = scale)
        
        print(xvar, ' vs ', i, ' complete...')

if heatmap:
    x_tick= xvar
    y_tick= yVarTotal
    total_var = [*x_tick,*y_tick]
    heatmap(data=df_maxLoad[total_var],
            x_var = x_tick,
            y_var = y_tick,
            destination=plot_path,
            filename='heatmap.png',
            compact=True,
            fig_kws={'figsize':[40,20],'dpi':150},
            anno_kws={'size':17,'rotation':0},
            cbar_kws={'label':'Correlation coefficient','label_size':30,
                      'tick_size':19},
            label={'size':50},
            tick={'size':20,'xrotation':0},
            cmap_='viridis')


if multiLinearReg:
    # Ordinary least square (OLS)
    # y_i = intercept + c1x1 + c2x2 + ... + cnxn
    
    # Initializing coefficient dataframe
    coeff = pd.DataFrame()
    
    # RHS of multiple linear regression equation
    # Note :intercept is added automatically in OLS
    RHS = ' + '.join(xvar[:])

    i=0
    for yvar in yVarTotal:
        
        # Fitting model
        model = ols(f"{yvar} ~ {RHS}", data=df_maxLoad_all_new).fit()
        
        # Get coefficients of the fitted model
        coeff[yvar] = model.params
        
        # Writing model summary    
        if i == 0:
            typ = 'w+'
        else:
            typ = 'a'
        with open(plot_path + 'MultivarRegInfo.txt',typ) as summary:
            summary.write(
    '\nxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' +
    '\nxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n\n'+ 
    str(model.summary2())
    )
        i+=1
    
    # Creating heatmap of coefficient of fitted data
    plt.figure(figsize=(15, 3), dpi=100)
    sns.heatmap(coeff.transpose(), cmap='coolwarm', annot=True, fmt=".3f",
                annot_kws={'size':9,'rotation':45},robust=True,
                cbar_kws={'label': 'Coefficient value'},)
    plt.savefig(plot_path + 'MultipleLinearRegressionCoefficients.png')
    plt.close()