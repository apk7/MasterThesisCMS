# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 14:22:42 2021

@author: apurv
"""
import numpy as np
import pandas as pd
from scipy.stats import loguniform
nan = np.nan
import os
import sys
import re
import matplotlib.pyplot as plt

def get_angle(x,y,typ='rad'):
    # if angle < 0. -1 deg will be interpreted as 359deg
    # note this function is not usd for calculating min_max values.
    # for calculating min_max between say 0deg +-4 deg
    # the min_max value of this example will be +4deg and -4deg throughout this project.
    # this function is only used for creating panda dataframe of all the runs. (line:84-88 in CreateCard.py)
    # there no negative angle degree is present (0,360).
    if type(x) != float or type(y) != float:
        x = float(x)
        y = float(y)
    
    angle = np.arctan2(y,x)
    
    if typ=='deg':
        angle *= 180 / np.pi
        angle = angle + 360 * (1 - np.sign(angle)) / 2
        angle = round(angle,3)
       
    return angle
    
def min_max(value,variation,type_variation=10):
    value = np.asarray(value)
    if type_variation==10 or type_variation==11 or type_variation==51 or type_variation==50: # % variation
        var_val = [(1+variation/100)* value, (1-variation/100)* value]
        max_val = max(var_val)
        min_val = min(var_val)
    elif type_variation==20 or type_variation==21 or type_variation==61 or type_variation==60: # absolute variation
        max_val = value + variation
        min_val = value - variation
    return min_val,max_val

def factor_minmax(factor_list):
    for i in factor_list:
        if factor_list[i]['type'] == 4:
            continue
        else:
            if 'min_val' not in factor_list[i] and 'max_val' not in factor_list[i]:
                factor_list[i]['min_val'],factor_list[i]['max_val'] = \
                    min_max(factor_list[i]['value'],factor_list[i]['vari'],factor_list[i]['type'])
    return factor_list

def direction_vector(theta): # only in x and y direction
    theta = np.asarray(theta)
    return np.round([np.cos(theta*np.pi/180),np.sin(theta*np.pi/180)],10).transpose()
    # return [np.cos(theta*np.pi/180),np.sin(theta*np.pi/180)]

def scale(val,new_min,new_max,scale=''):
    """
    Parameters
    ----------
    val : integer/float
        value to be scaled to certain range.
    new_min : integer/float
        minimum value in the range.
    new_max : integer/float
        maximum value in the range.
    scale : string, optional
        Scales to linear ('') or log uniform ('log'). The default is ''.

    Returns
    -------
    scaled_val : integer/float
        DESCRIPTION.

    """
    if scale=='log':
        new_min = np.log10(new_min)
        new_max = np.log10(new_max)
        # print(new_min,new_max)
    old_min,old_max=0,1
    old_range = old_max-old_min
    new_range = new_max-new_min
    scaled_val = (val-old_min) * new_range / old_range + new_min
    # print(scaled_val)
    if scale=='log':
        scaled_val = 10**scaled_val
        # print(scaled_val)
    return scaled_val

def transform_samplespace(sample_space,factor_list,angle_keys=[]):
    from scipy.stats import loguniform
    sample_loguniform={}
    for count,fac in enumerate(factor_list):
        temp_fac = factor_list[fac]
        if temp_fac['type'] == 11 or temp_fac['type'] == 21 or temp_fac['type'] == 51:
            sample_ = scale(val=sample_space[count],new_min=temp_fac['min_val'],new_max=temp_fac['max_val']).tolist()
            # if fac in angle_keys:
            #     sample_ = direction_vector(sample_) # creating vectors
        elif temp_fac['type'] == 10 or temp_fac['type'] == 20 or temp_fac['type'] == 50:
            if temp_fac['min_val'] < 0 and temp_fac['max_val'] < 0:
                temp_val = [abs(temp_fac['max_val']),abs(temp_fac['min_val'])]
                min_val,max_val = min(temp_val),max(temp_val)
                sample_ = loguniform(min_val,max_val,loc=0, scale=1).ppf(sample_space[count])*-1
                sample_.tolist()
            else:
                sample_ = loguniform(temp_fac['min_val'],temp_fac['max_val'],loc=0, scale=1).ppf(sample_space[count]).tolist()
        elif temp_fac['type'] == 3:
            levels = temp_fac['levels']
            num_level = len(levels)
            chunks = np.linspace(0,1,num_level+1)
            range_list=[]
            for i in range(len(chunks)-1):
                range_list.append([chunks[i],chunks[i+1]])
            sample_ = pd.cut(sample_space[count], bins=num_level, include_lowest=True, labels=levels).to_list()
        # sample_loguniform[factor_list[count][0]] = sample_
        sample_loguniform[fac] = sample_
    return sample_loguniform

def format_val(array=None):
    "Formats value in 10 digits spaces as per LS-Dyna cards"
    formatted_dic = {}
    if array == None:
        return 0
    if type(array)==dict:
        for key in array:
            val = array[key]
            formatted_val = []
            for val1 in val:
                if type(val1) != np.ndarray:
                    if len(str(val1)) > 10:
                        if val1 < 0:
                            formatted_val.append(str(format(val1,'6.3E')))
                        else:
                            formatted_val.append(str(format(val1,'6.4E')))
                        # formatted_val.append(str(format(val1,'6.4E')))
                    else:
                        formatted_val.append(' '*(10 - len(str(val1))) + str(val1))
                else: # When each val1 is a list of items. support only upto 2 levels of depth
                    temp_vector = []
                    for i in val1:
                        if len(str(i)) > 10:
                            if i < 0:
                                temp_vector.append(str(format(i,'6.3E')))
                            else:
                                temp_vector.append(str(format(i,'6.4E')))
                        else:
                            temp_vector.append(' '*(10 - len(str(i))) + str(i))
                    formatted_val.append(temp_vector)
            formatted_dic[key] = formatted_val
        return formatted_dic
    elif type(array)==int or type(array)==float:
        if len(str(array)) > 10:
            return str(format(array,'6.4E'))
        else:
            return ' '*(10 - len(str(array))) + str(array)


def create_mat_database(mat_id=0,mat_ref=0,sample_dic=[],key_list=[],misc=[]):
    """
    Parameters
    ----------
    mat_id : LIST, optional
        material id to be set in card. The default is 0.
    mat_ref : LIST, optional
        Which material reference parameter from sample_dic to use. The default is 0. Length should be equal to len(mat_id)
        mat_id = [2,5,6], mat_ref=[1,2,3] → while createing card database, for card number 2,5,6 material parameters from 1,2,3 will be used respectively
        mat_id = [2,5,6], mat_ref=[2,2,2] →
    sample_dic : TYPE, optional
        DESCRIPTION. The default is None.
    keys : TYPE, optional
        DESCRIPTION. The default is None.
    misc : TYPE, optional
        DESCRIPTION. The default is None.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    if type(mat_id)==int:
        mat_card = {}
        mat_ref = int(mat_ref)
        mat_card['mid']=' '*(10 - len(str(mat_id))) + str(mat_id)
        for key in key_list:
            if key in misc:
                for i,angle_key in enumerate(misc[key]):
                    mat_card[angle_key] = sample_dic[key][mat_ref][i]
                    # mat_card[misc[key]]=mat_card.pop(key)
            else:
                mat_card[key]=sample_dic[key][mat_ref]
        return mat_card
    elif type(mat_id)==list or type(mat_id)==np.ndarray:
        assert(len(mat_id)==len(mat_ref))
        mat_database={}
        for matref,i in enumerate(mat_id):
            mat_database[int(i)] = create_mat_database(
                int(i),
                mat_ref[matref],
                sample_dic,
                key_list=key_list,
                misc=misc)
        return mat_database


# def create_mat_card(mat_database=None,typ=None,filename='default',mat_id=0,meth='w+'):
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


def dyna_output_curve(lcid=7, sfa=1, sfo=1,plot = []):
    lcid = format_val(lcid)
    sfa  = format_val(sfa)
    sfo  = format_val(sfo)
    curve =f"""$#
*DEFINE_CURVE_TITLE
Force
$#    lcid      sidr       sfa       sfo      offa      offo    dattyp     lcint
{  lcid  }         0{  sfa   }{  sfo   }       0.0       0.0         0         0
$#                a1                  o1
"""
    for coord in plot:
        #print("ip- ",coord[0],coord[1])
        f_x = format_val(coord[0])
        f_y = format_val(coord[1])
        #print(f_x,f_y)
        plotval = " "*10 + f_x + " "*10 + f_y + "\n"
        #print(plotval)
        curve = curve + plotval
    curve += "$#\n"
    #print(curve)
    
    return curve

#=======================================================================================
# Creating HPC jobs
#=======================================================================================
def create_job_list(list_name='list1',start_run_id=0,last_run_id = 0,job_location='',hpc_result_destination=''):
    card_list = list(range(start_run_id,last_run_id+1))
    list_name_full = job_location + list_name + '.list'
    with open(list_name_full,'w+') as mylist:
        for run in card_list:
            mylist.write(f'serverJob --processors 40 --nodes 2 -j {run}.k --jobDir {run} --downloadDir {run} --time 02:00:00\n')

def path_format_to_linux(path):
    match_obj = re.search('[a-zA-Z]:',path)
    drive_letter = path[match_obj.span()[0]]
    drive_letter = drive_letter.lower()
    path = path.replace(match_obj.group(0), f'/mnt/{drive_letter}/')
    path = path.replace('\\','/')
    path = path.replace('//','/')
    return path

def creat_chain_sbatch(list_str):
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


##############################################################################
# apply the min-max scaling in Pandas using the .min() and .max() methods
def min_max_scaling(df,allColumns=False):
    # copy the dataframe
    df_norm = df.copy()
    
    if allColumns == False:
        # apply min-max scaling
        for column in df_norm.columns:
            df_norm[column] = (df_norm[column] - df_norm[column].min()) / (df_norm[column].max() - df_norm[column].min())
    else:
        minVal = min(df_norm.min())
        maxVal = max(df_norm.max())
        for column in df_norm.columns:
            df_norm[column] = (df_norm[column] - minVal) / (maxVal - minVal)
            
    return df_norm



##############################################################################
#
# PLot utilities
#
##############################################################################

def plot_scatter(df, file_name='', xvar=[], yvar=[], typ=1, title='fig', grid=True,
                 corr_type='pearson', scale='linear',r2score_flag=False,order=1,
                 text={'data':'','rel_xyloc':[0,0],'fontsize':19},ci=False):
    from scipy import stats
    import seaborn as sns
    # from pandas.plotting import scatter_matrix
    # import pandas as pd
    # import matplotlib.pyplot as plt

    if typ==2:
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
        
        # if xvar==[] and yvar==[]:
        #     g = sns.PairGrid(df, aspect=1.4, diag_sharey=False)
        # elif xvar==[] and yvar!=[]:       
        #     g = sns.PairGrid(df, aspect=1.4, diag_sharey=False, x_vars=xvar)
        # elif xvar!=[] and yvar==[]:       
        #     g = sns.PairGrid(df, aspect=1.4, diag_sharey=False, y_vars=yvar)
        # elif xvar!=[] and yvar!=[]:       
        g = sns.PairGrid(df, aspect=1.4, diag_sharey=False, x_vars=xvar, y_vars=yvar)
        
        g.set(xscale=scale,yscale=scale)
        g.map_lower(sns.regplot, lowess=True, ci=ci, line_kws={'color': 'black'})
        g.map_diag(sns.distplot, kde_kws={'color': 'black'})
        g.map_upper(corrdot)
        
    elif typ==1:
        def corrfunc(x, y, ax, corr_type = 'pearson',r2_score_flag=False,order=1):
            if r2score_flag:
                from sklearn.metrics import r2_score
                import numpy as np
                fit = np.polyfit(df[col], df[row], order)
                poly = np.poly1d(fit) # polynomial of fit[0]*x^n + fit[1]*x^(n-1) + fit[2]*x^(n-2) + ...
                y_pred = poly(df[col])
                r2_score = r2_score(df[row], y_pred)
                
                props = dict(boxstyle='round', facecolor='wheat', alpha=1) # these are matplotlib.patch.Patch properties
                ax.text(0.05, 0.95, "r2={:.4f}\npoly. order={:.0f}".format(r2_score,order), transform=ax.transAxes, fontsize=14, verticalalignment='top', bbox=props) # place a text box in upper left in axes coords
                
                return fit
            else:
                # if corr_type=='pearson':
                pcc,_ = stats.pearsonr(x, y)
                # elif corr_type=='spearman':
                srcc,_ = stats.spearmanr(x,y)
                
                props = dict(boxstyle='round', facecolor='wheat', alpha=1) # these are matplotlib.patch.Patch properties
                ax.text(0.05, 0.95, "PCC = {:.2f} \nSRCC = {:.2f}".format(pcc,srcc), transform=ax.transAxes, fontsize=14, verticalalignment='top', bbox=props) # place a text box in upper left in axes coords
                # ax.text(0.05, 0.95, "pcc = {:.2f}".format(r), transform=ax.transAxes, fontsize=11, verticalalignment='top', bbox=props) # place a text box in upper left in axes coords
                return 0

        col_len = len(xvar)
        row_len = len(yvar)
        
        # if col_len == 1:
        #     xvar,yvar = yvar,xvar
        #     col_len = len(xvar)
        #     row_len = len(yvar)
            
        sns.set_context("paper", font_scale=1)
        
        # fig, axes = plt.subplots(row_len, col_len, figsize=(7.2*col_len,7*row_len))
        # fig, axes = plt.subplots(row_len, col_len, figsize=(4*col_len,3.8*row_len))
        fig, axes = plt.subplots(row_len, col_len, figsize=(4*col_len,3.6*row_len))
        # fig, axes = plt.subplots(row_len, col_len)
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
                    fit = corrfunc(df[col], df[row], ax, r2_score_flag=True,order=order)
                    poly = np.poly1d(fit) # polynomial of fit[0]*x^n + fit[1]*x^(n-1) + fit[2]*x^(n-2) + ...
                    x=np.linspace(min(df[col]),max(df[col]),num = 100)
                    y = poly(x)
                    ax.plot(x,y,color='black',linestyle='-',linewidth=2)
                    ax.set_xlabel(col)
                    ax.set_ylabel(row)
                else:
                    g = sns.regplot(x=df[col], y=df[row], ax=ax, line_kws={'color': 'black'}, robust=True, ci=ci)   
                    corrfunc(df[col], df[row], g)
                    
                    g.set_xlabel(xlabel=col,fontsize=14)
                    g.set_ylabel(ylabel=row,fontsize=14)
                
                    # ax.tick_params(axis='x',labelrotation=90)
                    # # ax.tick_params(labelsize=10)
                    # if col == 'a_1' or col == 'a_2' or col == 'd_1' or col == 'd_2' or col == 'efs':
                    #     g.set_xscale('linear')
                    #     g.set_yscale('linear')
                    # else:
                    g.set_xscale(scale)
                    g.set_yscale(scale)
                
                if grid:
                    ax.grid(b=True, which='both', color='0.65', linestyle='dotted')
                    
        fig.suptitle(title,fontsize=20,weight="bold")
        plt.tight_layout(pad=2)
        
        if text['data']!='':
            plt.text(x=text['rel_xyloc'][0], y=text['rel_xyloc'][1], s=text['data'], fontsize=text['fontsize'], ha="left", transform=fig.transFigure,wrap=True)
       
        # plt.subplots_adjust(top=0,bottom=0)
    if file_name != '':
        plt.savefig(file_name)
        plt.close()
        
#========================================================================================================        
#========================================================================================================

def heatmap(data,destination,filename,x_var='',y_var='',compact=False,title={'label':'','size':30},
            fig_kws={'figsize':[27,27],'dpi':150},
            anno_kws={'annot':True,'size':15,'rotation':45},
            cbar_kws={'label':'cbar_label','label_size':20,'tick_size':19},
            # label={'size':20},
            tick={'size':19,'xrotation':0},
            cmap_='viridis',
            text={'data':'','rel_xyloc':[0,0],'fontsize':19},
            mask={'mask':False,'absThreshold':0.1},
            method='pearson'):
    
    import seaborn as sns
    import matplotlib.pyplot as plt
    
    if 'annot' not in anno_kws.keys():
        anno_kws['annot'] = False
    
    plt.figure(figsize=(fig_kws['figsize'][0], fig_kws['figsize'][1]), dpi=fig_kws['dpi'])
    
    corr_ = round(data.corr(method = method),2)
    
    if compact:
        try:corr_.drop(columns=y_var, inplace=True)
        except:pass
        try:corr_.drop(x_var, axis=0,inplace=True)
        except: pass
            
    if mask['mask']:
        mask_filter1 = corr_> mask['absThreshold']
        mask_filter2 = corr_< -1 * mask['absThreshold']
        mask_filter = mask_filter1 | mask_filter2
        corr_ = corr_[mask_filter]
        
    if anno_kws['annot']:
        dataplot = sns.heatmap(corr_, cmap=cmap_, annot=True, fmt='.2f',
                               annot_kws={'size':anno_kws['size'],'rotation':anno_kws['rotation'],
                                          # 'color':'k'
                                          },
                               cbar_kws={'label': cbar_kws['label']},
                               vmin=-1, vmax=1)
    else:
        dataplot = sns.heatmap(corr_, cmap=cmap_, cbar_kws={'label': cbar_kws['label']},vmin=-1, vmax=1)
               
    dataplot.figure.axes[-1].yaxis.label.set_size(cbar_kws['label_size'])
    dataplot.figure.axes[-1].tick_params(labelsize=cbar_kws['tick_size'])
    
    # dataplot.tick_params(axis='y',labelsize=tick['size'])
    plt.xticks(fontsize=tick['size'], rotation=tick['xrotation'])
    plt.yticks(fontsize=tick['size'],rotation=0)
    plt.tight_layout()
    if text['data']!='':
        plt.text(text['rel_xyloc'][0],text['rel_xyloc'][1], text['data'], ha='left',fontsize=text['fontsize'],wrap=True)
        
    plt.title(title['label'], fontsize=title['size'])
    # plt.subplots_adjust(top=0.91,bottom=0.3)
    file_name = destination+filename
    plt.savefig(file_name)
    plt.close()

#========================================================================================================
#========================================================================================================

def fitSurfLinearQuadratic(dataFull,xvar,yvar,file_name='',title=''):
    import scipy.linalg
    import pandas as pd
    
    print(' '.join(xvar), ' vs ', yvar[0])
    
    fig = plt.figure(figsize=(12,4))
    fig.suptitle(title, fontsize=14)
    
    # for num,i in enumerate(combi):
    #     print(i)
    data = dataFull[[*xvar,*yvar]]
    # fitSurf(df_,surf_order=2,file_name= i[0]+ '_' + i[1] + '_quad.pdf',title='')
    # fitSurf2(df_,file_name= i[0]+ '_' + i[1] + '_quad.pdf',title=i[0]+ ', ' + i[1] + ' vs ' + var[-1])
    
    if type(data) == pd.core.frame.DataFrame:
        x_label = data.columns[0]
        y_label = data.columns[1]
        z_label = data.columns[2]
        data = data.values       

  
    # if surf_order == 1: # best-fit linear plane (1st-order)
    A1 = np.c_[data[:,0], data[:,1], np.ones(data.shape[0])]
    C1,resid1,_,_ = scipy.linalg.lstsq(A1, data[:,2])    # coefficients
    
    mn = np.min(data, axis=0)
    mx = np.max(data, axis=0)
    numPoints = 200
    X,Y = np.meshgrid(np.linspace(mn[0], mx[0], numPoints), np.linspace(mn[1], mx[1], numPoints))
    XX = X.flatten()
    YY = Y.flatten()
    
    # evaluate it on grid
    Z1 = C1[0]*X + C1[1]*Y + C1[2]
    
    r2 = 1 - resid1 / (Z1.size * Z1.var())
    print('Linear surface r2 score: ',r2)
    
    # normalize = 1
    # if normalize:
        # print('')
    
    # elif surf_order == 2:
    A2 = np.c_[np.ones(data.shape[0]), data[:,:2], np.prod(data[:,:2], axis=1), data[:,:2]**2]
    C2,resid2,_,_ = scipy.linalg.lstsq(A2, data[:,2])

    # evaluate it on a grid
    Z2 = np.dot(np.c_[np.ones(XX.shape), XX, YY, XX*YY, XX**2, YY**2], C2).reshape(X.shape)
    
    
    
    r2 = 1 - resid2 / (Z2.size * Z2.var())
    print('Quadratic surface r2 score: ',r2)
        
    # # plot points and fitted surface using Matplotlib
    # fig = plt.figure(figsize=(20, 15))
    # fig.suptitle(title, fontsize=16)
    
    elev = 20
    azim = -130
    
    ax = fig.add_subplot(121, projection='3d')
    # surf = ax.plot_surface(X, Y, Z1, rstride=1, cstride=1, alpha=1,cmap='viridis')
    surf1 = ax.plot_surface(X, Y, Z1,cmap='viridis',rstride=1, cstride=1, linewidth=0, alpha=0.7)
    fig.colorbar(surf1, shrink=0.5, aspect=5)     # Add a color bar which maps values to colors.
    ax.scatter(data[:,0], data[:,1], data[:,2], c='g', s=5)
    
    plt.xlabel(x_label)    
    plt.ylabel(y_label)
    
    
    # ax.set_xticks(np.linspace(0,1,5))
    # ax.set_yticks(np.linspace(0,1,5))
    # ax.set_zticks(np.linspace(0,1,5))
    
    # ax.axes.set_xlim3d(left=0, right=1) 
    # ax.axes.set_ylim3d(bottom=0, top=1) 
    # ax.axes.set_zlim3d(bottom=0, top=1) 
    
    
    # # ax.set_zlim3d(0, 1)
    # # ax.set_ylim3d(0, 1)
    # # ax.set_xlim3d(0, 1)
    ax.set_zlabel(z_label)
    ax.title.set_text('Linear surface fit')
    ax.axis('auto')
    ax.axis('tight')
    ax.elev = elev
    ax.azim = azim
    
    ax = fig.add_subplot(122, projection='3d')
    # surf = ax.plot_surface(X, Y, Z2, rstride=1, cstride=1, alpha=1,cmap='viridis')
    surf = ax.plot_surface(X, Y, Z2,cmap='viridis', rstride=1, cstride=1, linewidth=0, alpha=0.7)
    fig.colorbar(surf, shrink=0.5, aspect=5)     # Add a color bar which maps values to colors.
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


