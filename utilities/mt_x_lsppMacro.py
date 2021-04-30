##############################################################################
# LS-PrePost Macros
##############################################################################

def write_bash(start_id,end_id,macro_destination,lspp_loc='/home/apku868a/lsprepost4.8_common/lspp48',file_suffix='',macro_suffix=''):
    """Creates bash script containig code to run marcros using LS-PrePost application.
    Args:
        start_id (int): start id of the experiment
        end_id (int): last id of the experiment
        macro_destination (str): location of the macro to be saved
        lspp_loc (str, optional): Location of ls-prepost app that will be called to run macro. Defaults to '/home/apku868a/lsprepost4.8_common/lspp48'.
        file_suffix (str, optional): suffix of the bash script filename. Defaults to ''.
        macro_suffix (str, optional): suffix of the macro files. Defaults to ''.
    """    
    import os

    # Adding preamble
    s_temp = f"{start_id}..{end_id}"
    s = f"""#!/bin/bash
for i in {{{s_temp}}}
do
"""
    # Adding command to run macros
    s+=f"""    echo ########################  $i{macro_suffix}.cfile  ########################
echo "$i{macro_suffix}.cfile - running" > {start_id}_{end_id}.info
{lspp_loc} -nographics c="$i{macro_suffix}.cfile"
done
"""
    # Creating bash script
    batch_macro_name = macro_destination+f'batch_LSPost{file_suffix}.sh'    
    if os.path.isfile(batch_macro_name):
        os.remove(batch_macro_name)
    with open(batch_macro_name,'a+') as mybatch:
        mybatch.write(s)
    return 0


def macro_wrapper(commands,file_loc):
    """ Adds initla lintes and ending lines to macro data. LAso adds line that opens d3Plot file.

    Args:
        commands (str): All the macro commands
        file_loc (str): d3Plot file location / Results location.
    """    
    s1 = f"""*lsprepost macro command file
*macro begin macro_post\n
$# ============================
open d3plot "{file_loc}d3plot"\n"""
    s2 = "\n*macro end"
    
    return s1 + commands + s2
    
def global_bodyforce_100(filename,csv_destination):
    """Model is cut at plane:
    origin:  0.12 0.042 0.00093 
    normals: 1.000  0.000  0.000
    
    This extracts following components from the model cut from above plane:
        3  - resultant force, 
        4  - normal (body) force (x),
        5  - shear (body) force (y), 
        13 - cs area

    Args:
        csv_destination (str): Desitnation path for output database csv
        name (str): output csv file name.

    Returns:
        str: string with macro for data extraction
    """
    s = f"""splane dep0 0.12 0.042 0.00093  1.000  0.000  0.000
splane setbasept 0.12 0.042 0.00093
splane drawcut
$# Extracting: resultant force, x-force,y-force,crossection area
splane xsection 3 4 5 13
xyplot 1 savefile ms_csv "{csv_destination}{filename}.csv" 1 all
xyplot 1 donemenu
deletewin 1
splane done
"""
    return s

def elem_force(elem_id,name,csv_destination):
    """Extracting forces in an element.
    1- x-force
    2- y-force
    3- Resultant force

    Args:
        elem_id (int): Element ID
        name (str): Output data filename
        csv_destination (str): Output data file location
    """    
    s = f"""
genselect target element
genselect element add element {elem_id}/0 
etime 1 
addplot 
etime 2 
addplot 
etime 3 
xyplot 1 savefile ms_csv "{csv_destination}{name}.csv" 1 all
clearpick
"""
    return s

def global_internal_energy(filename,csv_destination):
    """Extracts the global internal energy data

    Args:
        filename (str): Output data filename
        csv_destination (str): Output data file location
    """    
    s = f"""gtime 2
xyplot 1 savefile ms_csv_multiple "{csv_destination}{filename}.csv" 1 all
    """
    return s


def get_history_data(part_id,val,filename,destination_csv,data_file_suffix='',curve_operation_id=0):
    """Get part data

    Args:
        part_id (int): Part ID whose data needs to be extracted
        val (int): Data ID that needs to be extracted.
                    1 - Longitudinal stress (x-stress)
                    2 - Transverse stress (y-stress)
                    4 - In-plane stress (xy-stress)
                    9 - Effective stress
                   13 - Max shear stress (Von Tresca)
                   14 - Principle stress

        filename (str): Output data filename
        destination_csv (str): Output data file location
        data_file_suffix (str, optional): Suffix of data filename. Defaults to ''.
        curve_operation_id (int): Operations to be performed on the collected time curve. Defaults to 0 (maximum curve).
                                  0 - Maximum of all extracted curves
                                  1 - Average of all extracted curves
    """    
    assert(type(part_id)==list)
    s_heading = f"$# {filename} ==================================\n"    
    s0 = """\ngenselect clear all\n"""
    s1 = '\n'
    for part in part_id:
        s1 += f"""genselect part add part {part}/0""" + '\n'

    if curve_operation_id==0:
        curve_operation = 'max_curve'
    elif curve_operation_id==0:
        curve_operation = 'average_curves'

    s2 = f"""
maxvalue {val} 
xyplot 1 select all
xyplot 1 operation {curve_operation} all
xyplot 1 operation save "{destination_csv}{filename}{data_file_suffix}.csv" MSoft_CSV
deletewin 1
"""
    s = s_heading + s0+s1+s2+s0+"\n"
    return s
        


def get_fringe_data(state_id,fringe_val,macro_dest,part_ID=[]):
    """Extract fringe data elementwise for selected layer

    Args:
        state_id (list): <[lower id, upper id]> - Time steps to extract element level data
        fringe_val ([type]): fringe value that needs to be extracted.
                    1 - Longitudinal stress (x-stress)
                    2 - Transverse stress (y-stress)
                    4 - In-plane stress (xy-stress)
                    9 - Effective stress
                   13 - Max shear stress (Von Tresca)
                   14 - Principle stress
                   81 - fibre damage
                   83 - matrix damage
                   85 - damage variable fibres
                   87 - damage variable matrix
        macro_dest ([type]): [description]
        part (str, optional): [description]. Defaults to 'all'.
    """    
    if part_ID==[]:
        s0="postmodel off\npostmodel on \n"
    else:
        s0="postmodel off\n+M "
        for i in part_ID:
            s0 += ' ' + str(i)        
        s0 += ' \n'

    s1 = f"fringe {fringe_val}\npfringe\n"
    
    list_ = list(range(state_id[0],state_id[1]+1))
    s2 = ''
    for i in list_:
        s2 += f"""output "{macro_dest}{i}.csv" {i} 1 0 1 0 0 0 0 1 0 0 0 0 0 0 1.000000\n"""
    s = s0+s1+s2
    return s


def nodal_data_disp(nodeid,filename,destination_csv):
    """Extracting nodal displacement

    ntime 5 - Resultant displacement
    ntime 6 - x displacement
    ntime 7 - y displacement
    ntime 8 - z displacement

    Args:
        nodeid (int): Node ID
        filename (str): Name of output data file
        destination_csv (str): Location of output data file
    """    
    s = f"""
$# {filename}
genselect node add node {nodeid}/0 
ntime 5 
addplot 
ntime 6 
addplot 
ntime 7 
addplot 
ntime 8 
xyplot 1 select all
xyplot 1 savefile ms_csv "{destination_csv}{filename}.csv" 1 all
deletewin 1
clearpick
"""
    return s
    
def getNotchElemDataGlobal(csv_dst):
    """Extracting element data near notches

    Args:
        csv_dst (str): Output datafile location
    """    
    
    # range of coordinates over which element values are extracted
    x1 = 0.118
    x2 = 0.122
    
    y1 = 0.0115 
    y2 = 0.0175 
    
    s = f"""
$# Notch element data

postmodel off 
postmodel on

genselect target element solid
switch2selection
clearpick
genselect target element solid

genselect element add plane in 0.119865 0.0105 7.91667e-05 0 0 1 0.01 0
genselect element remove plane in 0.12 {y1} 0 0 -1 0 1 1
genselect element remove plane in 0.12 {y2} 0 0 1 0 1 1
genselect element remove plane in {x1} 0.0144 0 -1 0 0 1 1
genselect element remove plane in {x2} 0.0144 0 1 0 0 1 1

maxvalue 1 
xyplot 1 operation max_curve all
xyplot 1 savefile ms_csv "{csv_dst}gNotchElem_xStress_max.csv" 1 all
deletewin 1

maxvalue 2 
xyplot 1 operation max_curve all
xyplot 1 savefile ms_csv "{csv_dst}gNotchElem_yStress_max.csv" 1 all
deletewin 1

maxvalue 14 
xyplot 1 operation max_curve all
xyplot 1 savefile ms_csv "{csv_dst}gNotchElem_maxPrinc_max.csv" 1 all
deletewin 1

maxvalue 81
xyplot 1 operation max_curve all
xyplot 1 savefile ms_csv "{csv_dst}gNotchElem_fa_max.csv" 1 all
deletewin 1

maxvalue 83
xyplot 1 operation max_curve all
xyplot 1 savefile ms_csv "{csv_dst}gNotchElem_fmat_max.csv" 1 all
deletewin 1

maxvalue 85
xyplot 1 operation max_curve all
xyplot 1 savefile ms_csv "{csv_dst}gNotchElem_da_max.csv" 1 all
deletewin 1

maxvalue 87
xyplot 1 operation max_curve all
xyplot 1 savefile ms_csv "{csv_dst}gNotchElem_dmat.csv" 1 all
deletewin 1

etime 87
xyplot 1 operation average_curves all
xyplot 1 savefile ms_csv "{csv_dst}gNotchElem_dmat_avg.csv" 1 all
deletewin 1

clearpick
postmodel on
"""
    return s