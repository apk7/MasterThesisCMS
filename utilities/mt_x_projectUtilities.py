# ============================================================================
# Author: Apurv Kulkarni
# ----------------------------------------------------------------------------
# Contains all the utilities used in completing thesis
# ============================================================================

import numpy as np
import pandas as pd
from scipy.stats import loguniform
nan = np.nan
import os
import sys
import re
import matplotlib.pyplot as plt


#=============================================================================
# Experiment and LS-Dyna card utilities
#=============================================================================
def factor_minmax(factor_list):
    """Creates minimum and maximum values"""
    def min_max(value,variation,type_variation=10):
        value = np.asarray(value)
        if type_variation in [10,11]: # % variation
            var_val = [(1+variation/100)* value, (1-variation/100)* value]
            max_val = max(var_val)
            min_val = min(var_val)
        # elif type_variation in [40,41]: # absolute variation
        #     max_val = value + variation
        #     min_val = value - variation
        return min_val,max_val

    for i in factor_list:
        # if factor_list[i]['type'] in [10,11]:
        if 'min_val' not in factor_list[i] and 'max_val' not in factor_list[i]:
            factor_list[i]['min_val'],factor_list[i]['max_val'] = \
                min_max(factor_list[i]['value'],factor_list[i]['vari'],
                        factor_list[i]['type'])
    return factor_list

def direction_vector(theta): 
    """Angle to vector"""
    theta = np.asarray(theta)
    return np.round([np.cos(theta*np.pi/180),
                     np.sin(theta*np.pi/180)],10).transpose()


def transform_samplespace(sample_space,factor_list,angle_keys=[]):
    from scipy.stats import loguniform
    
    def scale(val,new_min,new_max,scale=''):
        if scale=='log':
            new_min = np.log10(new_min)
            new_max = np.log10(new_max)
        old_min,old_max=0,1
        old_range = old_max-old_min
        new_range = new_max-new_min
        scaled_val = (val-old_min) * new_range / old_range + new_min
        if scale=='log':
            scaled_val = 10**scaled_val
        return scaled_val
    
    sample_loguniform={}
    for count,fac in enumerate(factor_list):
        temp_fac = factor_list[fac]
        
        # Linear scaling
        if temp_fac['type'] in [11,21]:
            sample_ = scale(val=sample_space[count],new_min=temp_fac['min_val'],
                            new_max=temp_fac['max_val']).tolist()
        
        # Log scaling
        elif temp_fac['type'] in [10,20]:
            if temp_fac['min_val'] < 0 and temp_fac['max_val'] < 0:
                temp_val = [abs(temp_fac['max_val']),abs(temp_fac['min_val'])]
                min_val,max_val = min(temp_val),max(temp_val)
                sample_ = loguniform(min_val,max_val,loc=0, 
                                     scale=1).ppf(sample_space[count])*-1
                sample_.tolist()
            else:
                sample_ = loguniform(temp_fac['min_val'],
                                     temp_fac['max_val'],loc=0, 
                                     scale=1).ppf(sample_space[count]).tolist()
        # Discrete levels
        elif temp_fac['type'] in [3]:
            levels = temp_fac['levels']
            num_level = len(levels)
            chunks = np.linspace(0,1,num_level+1)
            range_list=[]
            for i in range(len(chunks)-1):
                range_list.append([chunks[i],chunks[i+1]])
            sample_ = pd.cut(sample_space[count], bins=num_level, 
                             include_lowest=True, labels=levels).to_list()
        sample_loguniform[fac] = sample_
    return sample_loguniform

def format_val(array=None):
    """Formats value in 10 digits spaces as per LS-Dyna cards
    
    Returns
    -------
    Formatted value
    """
    
    def format_val_i(val):
        if len(str(val)) > 10:
            if val < 0: 
                fval = str(format(val,'6.3E'))
            else:
                fval = str(format(val,'6.4E'))
        else:
            fval = ' '*(10 - len(str(val))) + str(val)

        return fval

    formatted_dic = {}
    for key in array:
        val = array[key]
        formatted_val = []
        for val1 in val:
            if type(val1) != np.ndarray:
                formatted_val.append(format_val_i(val1))
            else:
                temp_vector = []
                for i in val1:
                    temp_vector.append(format_val_i(i))
                formatted_val.append(temp_vector)
        formatted_dic[key] = formatted_val
    return formatted_dic

  
def create_mat_card(mat_database=None,typ=None,filename='default',meth='w+'):
    if typ == 1:
        m = mat_database
        card_data = f"""$#
*MAT_LAMINATED_FRACTURE_DAIMLER_PINHO
$#     mid        ro        ea        eb        ec      prba      prca      prcb
{m['mid']}{m['rho']}{ m['ea']}{ m['eb']}{ m['eb']}{m['pba']}{m['pca']}{m['pcb']}
$#     gab       gbc       gca      aopt       daf       dkf       dmf       efs
{m['gab']}{m['gbc']}{m['gca']}         2       0.0       1.0       1.0{m['efs']}
$#      xp        yp        zp        a1        a2        a3
       0.0       0.0       0.0{m['a1'] }{ m['a2']}       0.0
$#      v1        v2        v3        d1        d2        d3    mangle
       0.0       0.0       0.0{m['d1'] }{ m['d2']}       0.0
$#  enkink       ena       enb       ent       enl
{m['enk']}{m['ena']}{m['enb']}{m['ent']}{m['enl']}
$#      xc        xt        yc        yt        sl
{ m['xc']}{ m['xt']}{ m['yc']}{ m['yt']}{ m['sl']}
$#     fio      sigy      lcss      beta       pfl      puck      soft
{m['fio']}{m['sig']}         2     0.000   100.000     0.000     0.000
$#\n"""
    if typ == 2:
        m = mat_database
        card_data = f"""$#
*MAT_COHESIVE_GENERAL
$#     mid        ro     roflg   intfall       tes      tslc       gic      giic
{m['mid']}{m['rhC']}         1       1.0       1.0         3{m ['gi']}{m['gii']}
$#     xmu         t         s     stfsf     tslc2
       1.0{m ['t'] }{m ['s'] }       1.0       4.0
$#\n"""
    if typ==3:
        card_data = f"""$#
*CONTROL_TIMESTEP
$#  dtinit    tssfac      isdo    tslimt     dt2ms      lctm     erode     ms1st
      0.00      0.90         0      0.00-1.000E-08         0         0         0
$#  dt2msf   dt2mslc     imscl    unused    unused     rmscl
       0.0         0         0                           0.0
$#
*DEFINE_CURVE_TITLE
shear
$#    lcid      sidr       sfa       sfo      offa      offo    dattyp     lcint
         2         0     1.400     0.900       0.0       0.0         0         0
$#                a1                  o1
                   0               0e+08
              0.0007          0.0533e+08
              0.0016          0.1277e+08
              0.0028          0.1949e+08
              0.0044          0.2788e+08
              0.0067          0.3638e+08
              0.0102          0.4440e+08
              0.0137          0.5136e+08
              0.0185          0.5670e+08
              0.0243          0.6050e+08
              0.0284          0.6311e+08
              0.0328          0.6482e+08
              0.0374          0.6595e+08
              0.0423          0.6677e+08
              0.0472          0.6758e+08
              0.0522          0.6869e+08
              0.0571          0.7038e+08
              0.0621          0.7229e+08
              0.0673          0.7422e+08
              0.0727          0.7620e+08
              0.0808          0.7942e+08
              0.0946          0.8574e+08
              0.1058          0.9060e+08
              0.1179          0.9688e+08
              0.1297          1.0325e+08
              0.1426          1.0972e+08
              0.1695          1.2442e+08
$#
*DEFINE_CURVE_TITLE
fail_cohesive
$#    lcid      sidr       sfa       sfo      offa      offo    dattyp     lcint
         3         0       1.0       1.0       0.0       0.0         0         0
$#                a1                  o1
                 0.0                 0.0
                 0.2                 1.0
                 1.0                 0.0
$#
*DEFINE_CURVE_TITLE
fail_cohesive
$#    lcid      sidr       sfa       sfo      offa      offo    dattyp     lcint
         4         0       1.0       1.0       0.0       0.0         0         0
$#                a1                  o1
                 0.0                 0.0
                 0.2                 1.0
                 0.4                 0.9
                 0.7                 0.6
                 1.0                 0.0
$#"""            
    return card_data


def format_val_i(val):
        if len(str(val)) > 10:
            if val < 0: 
                fval = str(format(val,'6.3E'))
            else:
                fval = str(format(val,'6.4E'))
        else:
            fval = ' '*(10 - len(str(val))) + str(val)

        return fval

def dyna_output_curve(lcid=7, sfa=1, sfo=1,plot = []):
    lcid = format_val_i(lcid)
    sfa  = format_val_i(sfa)
    sfo  = format_val_i(sfo)
    curve =f"""$#
*DEFINE_CURVE_TITLE
Force
$#    lcid      sidr       sfa       sfo      offa      offo    dattyp     lcint
{  lcid  }         0{  sfa   }{  sfo   }       0.0       0.0         0         0
$#                a1                  o1
"""
    for coord in plot:
        #print("ip- ",coord[0],coord[1])
        f_x = format_val_i(coord[0])
        f_y = format_val_i(coord[1])
        #print(f_x,f_y)
        plotval = " "*10 + f_x + " "*10 + f_y + "\n"
        #print(plotval)
        curve = curve + plotval
    curve += "$#\n"
    #print(curve)
    
    return curve

#=============================================================================
# HPC jobs submition utilities
#=============================================================================
def path_format_to_linux(path):
    """Converts a windows path to linux machine path"""
    match_obj = re.search('[a-zA-Z]:',path)
    drive_letter = path[match_obj.span()[0]]
    drive_letter = drive_letter.lower()
    path = path.replace(match_obj.group(0), f'/mnt/{drive_letter}/')
    path = path.replace('\\','/')
    path = path.replace('//','/')
    return path

def creat_chain_sbatch(list_str):
    """Creates main submisison file for HPC systems"""
    s1 = f'JOBDIRS="{list_str}"'
    s2 = r"""
 DEPENDENCY="" 
 PREVIOUSJOBDIR="" # is used to identify restart jobs 
 for CURRENTJOBDIR in $JOBDIRS; do 
	 JOB_CMD="sbatch" 
	 if [ -n "$DEPENDENCY" ] && ! true; then 
	 	JOB_CMD="$JOB_CMD --dependency afterany:$DEPENDENCY" 
	 fi 
	 JOB_CMD="$JOB_CMD run*.sh 2>&1" 
	 OUT=`cd $CURRENTJOBDIR; $JOB_CMD` 
	 DEPENDENCY=`echo $OUT | awk '{print $4}'` 
	 if [ "$CURRENTJOBDIR" == "$PREVIOUSJOBDIR" ]; then 
		 echo $DEPENDENCY >> $CURRENTJOBDIR/jobID 
	 else 
	 echo $DEPENDENCY > $CURRENTJOBDIR/jobID 
	 fi 
	 PREVIOUSJOBDIR=$CURRENTJOBDIR 
 done
"""
    s= s1+s2
    return s


#=============================================================================
# Data extraction and cleaning utilities
#=============================================================================
def min_max_scaling(df,allColumns=False):
    """Scales the given dataframe :
        > columnwise (allColumns=False) or 
        > on a global scale (allColumns=True)"""
    
    # copy the dataframe
    df_norm = df.copy()
    
    if allColumns == False:
        # apply min-max scaling
        for column in df_norm.columns:
            df_norm[column] = ((df_norm[column] - df_norm[column].min()) / 
                               (df_norm[column].max() - df_norm[column].min()))
    else:
        minVal = min(df_norm.min())
        maxVal = max(df_norm.max())
        for column in df_norm.columns:
            df_norm[column] = (df_norm[column] - minVal) / (maxVal - minVal)
            
    return df_norm


# Data extraction utilities
def getData(file_dst,var,dfo):
    df = pd.read_csv(file_dst+var+'.csv' ,skiprows=7, delim_whitespace=True)
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

#=============================================================================
# Plot utilities
#=============================================================================

# Scatter + regression + correlation plots
#-----------------------------------------------------------------------------
def analysis_plot(df, file_name='fig.png', xvar=[], yvar=[], typ=1, title='fig', 
                 grid=True, scale='linear',r2score_flag=False,order=1,ci=False,
                 text={'data':'','rel_xyloc':[0,0],'fontsize':19}):
    
    """Analysis plot used for data analysis. It plots scatter plots, regression
       plots, and correlation values(PCC and SRCC)"""
    
    from scipy import stats
    import seaborn as sns
        
    if typ==1:
        def corrfunc(x, y, ax, corr_type = 'pearson',r2_score_flag=False,order=1):
            if r2score_flag:
                # R-squared statistics
                from sklearn.metrics import r2_score
                import numpy as np
                fit = np.polyfit(df[col], df[row], order)
                # polynomial:
                # fit[0]*x^n + fit[1]*x^(n-1) + fit[2]*x^(n-2) + ...
                poly = np.poly1d(fit) 
                y_pred = poly(df[col])
                r2_score = r2_score(df[row], y_pred)
                
                # place a text box in upper left in axes coords (0.05,0.95)
                props = dict(boxstyle='round', facecolor='wheat', alpha=1) 
                ax.text(0.05, 0.95, 
                        "r2={:.4f}\npoly. order={:.0f}".format(r2_score,order),
                        transform=ax.transAxes, fontsize=14,
                        verticalalignment='top', bbox=props) 
                
                return fit
            else:
                # Correlation statistics
                pcc,_ = stats.pearsonr(x, y)
                srcc,_ = stats.spearmanr(x,y)
                
                # place a text box in upper left in axes coords (0.05,0.95)
                props = dict(boxstyle='round', facecolor='wheat', alpha=1) 
                ax.text(0.05, 0.95, "PCC = {:.2f} \nSRCC = {:.2f}".format(pcc,srcc),
                        transform=ax.transAxes, fontsize=14,
                        verticalalignment='top', bbox=props)
                return 0

        col_len = len(xvar)
        row_len = len(yvar)
        sns.set_context("paper", font_scale=1)
        fig, axes = plt.subplots(row_len, col_len, figsize=(4*col_len,3.6*row_len))
        for row_num, row in enumerate(yvar):
            for col_num,col in enumerate(xvar):
                if row_len == 1 and col_len == 1:
                    ax = axes
                elif row_len == 1:
                    ax = axes[col_num]
                elif col_len==1:
                    ax = axes[row_num]
                else:
                    ax = axes[row_num,col_num]
                
                if r2score_flag:
                    ax.scatter(df[col], df[row], alpha=0.5)
                    fit = corrfunc(df[col], df[row], ax, 
                                   r2_score_flag=True,order=order)
                    # polynomial of 
                    # fit[0]*x^n + fit[1]*x^(n-1) + fit[2]*x^(n-2) + ...
                    poly = np.poly1d(fit) 
                    x=np.linspace(min(df[col]),max(df[col]),num = 100)
                    y = poly(x)
                    ax.plot(x,y,color='black',linestyle='-',linewidth=2)
                    ax.set_xlabel(col)
                    ax.set_ylabel(row)
                else:
                    g = sns.regplot(x=df[col], y=df[row], ax=ax,
                                    line_kws={'color': 'black'},
                                    robust=True, ci=ci)   
                    corrfunc(df[col], df[row], g)
                    g.set_xlabel(xlabel=col,fontsize=14)
                    g.set_ylabel(ylabel=row,fontsize=14)
                    g.set_xscale(scale)
                    g.set_yscale(scale)
                
                if grid:
                    ax.grid(b=True, which='both', color='0.65', linestyle='dotted')
                    
        fig.suptitle(title,fontsize=20,weight="bold")
        plt.tight_layout(pad=2)
        
        if text['data']!='':
            plt.text(x=text['rel_xyloc'][0], y=text['rel_xyloc'][1],
                     s=text['data'], fontsize=text['fontsize'], ha="left",
                     transform=fig.transFigure,wrap=True)
        # plt.subplots_adjust(top=0,bottom=0)
        
    elif typ==2:
        # Plots full pairplot of input and output variables
        # source: https://stackoverflow.com/questions/48139899/correlation-matrix-plot-with-coefficients-on-one-side-scatterplots-on-another
        def corrdot(*args, **kwargs):
            corr_r = args[0].corr(args[1], 'pearson')
            corr_text = f"{corr_r:2.2f}".replace("0.", ".")
            ax = plt.gca()
            ax.set_axis_off()
            marker_size = abs(corr_r) * 10000
            ax.scatter([.5], [.5], marker_size, [corr_r], alpha=0.6, cmap="coolwarm",
                       vmin=-1, vmax=1, transform=ax.transAxes)
            font_size = abs(corr_r) * 40 + 5
            ax.annotate(corr_text, [.5, .5,],  xycoords="axes fraction",
                        ha='center', va='center',fontsize=font_size)
        
        sns.set(style='white', font_scale=1.6)
        
          
        g = sns.PairGrid(df, aspect=1.5, diag_sharey=False, despine=False)
        
        g.set(xscale=scale,yscale=scale)
        g.map_lower(sns.regplot, lowess=True, ci=ci,
                    line_kws={'color': 'red', 'lw': 1},
                    scatter_kws={'color': 'black', 's': 20})
        g.map_diag(sns.distplot, kde_kws={'color': 'black'})
        g.map_upper(corrdot)
    
    plt.savefig(file_name)
    plt.close()
    
    return 0

# Heatmap for correlation values
#-----------------------------------------------------------------------------
def heatmap(data,destination,filename,x_var='',y_var='',compact=False,
            title={'label':'','size':30},
            fig_kws={'figsize':[27,27],'dpi':150},
            anno_kws={'annot':True,'size':15,'rotation':45},
            cbar_kws={'label':'cbar_label','label_size':20,'tick_size':19},
            tick={'size':19,'xrotation':0},
            cmap_='viridis',
            text={'data':'','rel_xyloc':[0,0],'fontsize':19},
            mask={'mask':False,'absThreshold':0.1},
            method='pearson'):
    
    import seaborn as sns
    import matplotlib.pyplot as plt
    
    if 'annot' not in anno_kws.keys():
        anno_kws['annot'] = False
    
    plt.figure(figsize=(fig_kws['figsize'][0], fig_kws['figsize'][1]), 
               dpi=fig_kws['dpi'])
    
    # Correlation values from the dataframe
    corr_ = round(data.corr(method = method),2)
    
    # To plot full heatmap or only output vs input values
    if compact:
        try:corr_.drop(columns=y_var, inplace=True)
        except:pass
        try:corr_.drop(x_var, axis=0,inplace=True)
        except: pass
    
    # For applying filter in plots with some threshold values
    if mask['mask']:
        mask_filter1 = corr_> mask['absThreshold']
        mask_filter2 = corr_< -1 * mask['absThreshold']
        mask_filter = mask_filter1 | mask_filter2
        corr_ = corr_[mask_filter]
        
    if anno_kws['annot']:
        dataplot = sns.heatmap(corr_, cmap=cmap_, annot=True, fmt='.2f',
                               annot_kws={'size':anno_kws['size'],
                                          'rotation':anno_kws['rotation']},
                               cbar_kws={'label': cbar_kws['label']},
                               vmin=-1, vmax=1)
    else:
        dataplot = sns.heatmap(corr_, cmap=cmap_,
                               cbar_kws={'label': cbar_kws['label']},
                               vmin=-1, vmax=1)
               
    dataplot.figure.axes[-1].yaxis.label.set_size(cbar_kws['label_size'])
    dataplot.figure.axes[-1].tick_params(labelsize=cbar_kws['tick_size'])
    
    # dataplot.tick_params(axis='y',labelsize=tick['size'])
    plt.xticks(fontsize=tick['size'], rotation=tick['xrotation'])
    plt.yticks(fontsize=tick['size'],rotation=0)
    plt.tight_layout()
    
    # Plotting annotation texts (if any)
    if text['data']!='':
        plt.text(text['rel_xyloc'][0],text['rel_xyloc'][1], text['data'],
                 ha='left',fontsize=text['fontsize'],wrap=True)
        
    plt.title(title['label'], fontsize=title['size'])
    # plt.subplots_adjust(top=0.91,bottom=0.3)
    file_name = destination+filename
    plt.savefig(file_name)
    plt.close()


# Fitting linear and quadratic surface for interaction plots
# ----------------------------------------------------------------------------

def fitSurfLinearQuadratic(dataFull,xvar,yvar,file_name='',title=''):
    import scipy.linalg
    import pandas as pd
    
    print(' '.join(xvar), ' vs ', yvar[0])
    
    fig = plt.figure(figsize=(12,4))
    fig.suptitle(title, fontsize=14)
    
    data = dataFull[[*xvar,*yvar]]
    
    if type(data) == pd.core.frame.DataFrame:
        x_label = data.columns[0]
        y_label = data.columns[1]
        z_label = data.columns[2]
        data = data.values       

    # Fitting 1st order surface
    A1 = np.c_[data[:,0], data[:,1], np.ones(data.shape[0])]
    C1,resid1,_,_ = scipy.linalg.lstsq(A1, data[:,2])    # coefficients
    
    mn = np.min(data, axis=0)
    mx = np.max(data, axis=0)
    numPoints = 200
    X,Y = np.meshgrid(np.linspace(mn[0], mx[0], numPoints), 
                      np.linspace(mn[1], mx[1], numPoints))
    XX = X.flatten()
    YY = Y.flatten()
    Z1 = C1[0]*X + C1[1]*Y + C1[2]
    r2 = 1 - resid1 / (Z1.size * Z1.var())
    print('Linear surface r2 score: ',r2)
    
    # Fitting quadratic surface
    A2 = np.c_[np.ones(data.shape[0]), data[:,:2], 
               np.prod(data[:,:2], axis=1), data[:,:2]**2]
    C2,resid2,_,_ = scipy.linalg.lstsq(A2, data[:,2])
    Z2 = np.dot(np.c_[np.ones(XX.shape), XX, YY, XX*YY, XX**2, YY**2], C2).reshape(X.shape)
    
    r2 = 1 - resid2 / (Z2.size * Z2.var())
    print('Quadratic surface r2 score: ',r2)
    
    # Figure settings        
    elev = 20   # rotation about horizontal axis
    azim = -130 # rotation about vertical axis
    
    # plotting linear fitted surface on LHS
    ax = fig.add_subplot(121, projection='3d')
    surf1 = ax.plot_surface(X, Y, Z1,cmap='viridis',rstride=1, cstride=1,
                            linewidth=0, alpha=0.7)
    
    # Add a color bar which maps values to colors.
    fig.colorbar(surf1, shrink=0.5, aspect=5)     
    ax.scatter(data[:,0], data[:,1], data[:,2], c='g', s=5)
    plt.xlabel(x_label)    
    plt.ylabel(y_label)
    ax.set_zlabel(z_label)
    ax.title.set_text('Linear surface fit')
    ax.axis('auto')
    ax.axis('tight')
    ax.elev = elev
    ax.azim = azim
    
    # plotting quadratic surface on RHS
    ax = fig.add_subplot(122, projection='3d')
    surf2 = ax.plot_surface(X, Y, Z2,cmap='viridis', rstride=1, cstride=1, 
                            linewidth=0, alpha=0.7)
    
    # Add a color bar which maps values to colors.
    fig.colorbar(surf2, shrink=0.5, aspect=5)     
    ax.scatter(data[:,0], data[:,1], data[:,2], c='g', s=5)    
    plt.xlabel(x_label)
    plt.ylabel(y_label)    
    ax.set_zlim3d(0, 1)
    ax.set_ylim3d(0, 1)
    ax.set_xlim3d(0, 1)
    ax.set_zlabel(z_label)
    ax.title.set_text('Quadratic surface fit')
    ax.axis('auto')
    ax.axis('tight')
    ax.elev = elev
    ax.azim = azim
    
    plt.savefig(file_name)
    plt.close()


