from mt_0_input_factors_all import inputfactors
ip = inputfactors()
import os
import utilities.mt_x_lsppMacro as mc
#%%
project_name = ip["project_name"]
project_path = ip["project_path"]
lsdyna_result_path = ip["lsdyna_result_path"]

macro_dst = ip['macro_dst_data']
local_csv_dst = ip['csv_destination']

os.makedirs(macro_dst, exist_ok=True)
os.makedirs(local_csv_dst, exist_ok=True)

print("output CSV destination: ",local_csv_dst)
print("Macro destination: ",macro_dst)

start_id=0
end_id=ip["max_runs"]-1

part_id_0 = [*list(range(1,6,2)),*list(range(8,13,2))]  # 0deg ply
part_id_90 = [*list(range(2,7,2)),*list(range(7,13,2))] # 90deg ply
part_id_c = [13]                                        # cohesive layer 

for exp_id in range(start_id,end_id+1):
    macro_dst   = macro_dst
    csv_dst     = local_csv_dst + f"{exp_id}/"
    result_loc  = lsdyna_result_path + f"{exp_id}/"
    os.makedirs(csv_dst, exist_ok=True)   
    
    macroMain = ""
        
    # Global applied force
    macroMain += mc.global_bodyforce_100(filename="gForce",
                                         csv_destination=csv_dst) 
    
    # Global internal energy
    macroMain += mc.global_internal_energy(filename="gIntEnergy",
                                           csv_destination=csv_dst)
    
    # Maximum stress values for 0 deg ply
    macroMain += mc.get_history_data(part_id=[*part_id_0], val=1,
                                     filename="0MLS", destination_csv=csv_dst)
    macroMain += mc.get_history_data(part_id=[*part_id_0], val=2,
                                     filename="0MTS",destination_csv=csv_dst)
    macroMain += mc.get_history_data(part_id=[*part_id_0], val=4,
                                     filename="0MIPSS",destination_csv=csv_dst)
    macroMain += mc.get_history_data(part_id=[*part_id_0], val=9,
                                     filename="0MES",destination_csv=csv_dst) 
    macroMain += mc.get_history_data(part_id=[*part_id_0], val=13,
                                     filename="0MSS",destination_csv=csv_dst)
    macroMain += mc.get_history_data(part_id=[*part_id_0], val=14,
                                     filename="0MPS",destination_csv=csv_dst)
    
    # Maximum stress values for 90 deg ply
    macroMain += mc.get_history_data(part_id=[*part_id_90], val=1,
                                     filename="90MLS",destination_csv=csv_dst)
    macroMain += mc.get_history_data(part_id=[*part_id_90], val=2,
                                     filename="90MTS",destination_csv=csv_dst) 
    macroMain += mc.get_history_data(part_id=[*part_id_0], val=4,
                                     filename="90MIPSS",destination_csv=csv_dst) 
    macroMain += mc.get_history_data(part_id=[*part_id_90], val=9,
                                     filename="90MES",destination_csv=csv_dst)
    macroMain += mc.get_history_data(part_id=[*part_id_90], val=13,
                                     filename="90MSS",destination_csv=csv_dst)
    macroMain += mc.get_history_data(part_id=[*part_id_90], val=14,
                                     filename="90MPS",destination_csv=csv_dst)
    
    # Maximum stress values for cohesive layer
    macroMain += mc.get_history_data(part_id=[*part_id_c], val=1,
                                     filename="cMLS",destination_csv=csv_dst)
    macroMain += mc.get_history_data(part_id=[*part_id_c], val=2,
                                     filename="cMTS",destination_csv=csv_dst)
    macroMain += mc.get_history_data(part_id=[*part_id_0], val=4,
                                     filename="cMIPSS",destination_csv=csv_dst)
    macroMain += mc.get_history_data(part_id=[*part_id_c], val=9,
                                     filename="cMES",destination_csv=csv_dst)
    macroMain += mc.get_history_data(part_id=[*part_id_c], val=13,
                                     filename="cMSS",destination_csv=csv_dst)
    macroMain += mc.get_history_data(part_id=[*part_id_c], val=14,
                                     filename="cMPS",destination_csv=csv_dst)
    
    # Global maximum strain values
    macroMain += mc.get_history_data(part_id=[*part_id_0,*part_id_90,*part_id_c],
                                     val=57, filename="gMax_xStrain",
                                     destination_csv=csv_dst,
                                     data_file_suffix='_0')
    macroMain += mc.get_history_data(part_id=[*part_id_0,*part_id_90,*part_id_c],
                                     val=58, filename="gMax_yStrain",
                                     destination_csv=csv_dst,
                                     data_file_suffix='_90')
    macroMain += mc.get_history_data(part_id=[*part_id_0,*part_id_90,*part_id_c],
                                     val=77, filename="gMax_PrincStrain",
                                     destination_csv=csv_dst,
                                     data_file_suffix='_c')
    
    # Nodal displacements
    macroMain += mc.nodal_data_disp(nodeid=119495, filename = "header_disp",
                                    destination_csv=csv_dst)
    
    # Element data near notch
    macroMain += mc.getNotchElemDataGlobal(csv_dst) 
    
    # Get elementwise fringe data
    macroMain += mc.get_fringe_data([0,12],9,'',[1,2])

    # Wrapping macro with open and close file commands
    macro_str = mc.macro_wrapper(macroMain,file_loc=result_loc)
    
    # Wriritng macros to a file
    with open(macro_dst+f"{exp_id}.cfile","w+") as mymacro:
        mymacro.write(macro_str)

# Creating bash scripts to run the macros    
total_runs = ip["max_runs"]
# runsPerSubmission = total_runs/4            # number of runs per bash scripts (to run multiple extractions at a time)
chunks = 1#int(total_runs/runsPerSubmission)  # number of chunks for extraction
if total_runs%chunks != 0:
    raise ValueError("Number of chuncks must be divisible by total runs")

chunkBashfilenameList = ""
for i in range(1,chunks+1):
    chunk_start_id = int((i-1)*total_runs/chunks)
    chunk_end_id   = int(i*total_runs/chunks-1)
    mc.write_bash(chunk_start_id,chunk_end_id,
                  macro_destination=macro_dst,
                  file_suffix=f"_{chunk_start_id}{chunk_end_id}",
                  lspp_loc=ip['lsdyna_app'] )

######### Commands to run
print("Complete...\n")
print("Run following commands to proceed:")
i=1
print(f"1) cd {macro_dst}")
i+=1
print(f"{i}) dos2unix *.sh")
i+=1
print(f"{i}) chmod -R 775 *")
i+=1
print(f"{i}) run batch scripts")