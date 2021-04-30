# %%
from mt_0_input_factors_all import inputfactors
import sys
sys.path.insert(1, "/home/apku868a/pyUtilities/")
from mt_x_dynaUtilities import create_job_list, creat_chain_sbatch, path_format_to_linux
ip = inputfactors()
import subprocess
import os

hpc = 1

numCPU = 30
numNodes = 2
simTime = '04:00:00'
#%% Copying cards manually to hpc, without serverJob script
if hpc:
    hpc_scratch_location = '/scratch/ws/0/apku868a-mt/'
else:
    hpc_scratch_location = 'apku868a@taurusexport3.hrsk.tu-dresden.de:/scratch/ws/0/apku868a-mt/'
main_card_dst = hpc_scratch_location + ip['project_name'] + '/'

if hpc:
    main_card_src = ip['card_destination']
    list_location = main_card_src
    
#     main_card_src = 'cards/'
#     list_location = main_card_src + ip['project_name'] +'/'
    
else:
    main_card_src = path_format_to_linux(ip['card_location'])
    list_location = ip['card_location']+ ip['project_name'] +'\\'

project_name = ip['project_name']
total_runs = ip['max_runs']
runsPerSubmission = 30
chunks = int(total_runs/runsPerSubmission)
if total_runs%chunks != 0:
    raise ValueError("Number of chuncks must be divisible by total runs")
print('Total chunks: ',chunks)
    
chunkBashNameList = ""
for i in range(1,chunks+1):
    
    start_id = int((i-1)*total_runs/chunks)
    end_id = int(i*total_runs/chunks-1)
    # print(i,start_,end_)
    
#     print(start_id)
#     print(end_id)
    
#     job_name = ip['project_name']+ f'_{i}'
#     create_job_list(job_name,start_run_id= start_,
#                     last_run_id= end_,
#                     hpc_result_destination=ip['hpc_result'],job_location=ip['job_location'])
#     with open(f"{card_destination}/{job_name}_commands.txt",'w+') as mylist:
#         s = f"""To run analysis\n
#         cd {path_format_to_linux(card_location)}
#         serverJob -j {job_name}.list --array \n
#     To get results:\n
#         cd {path_format_to_linux(results_location)}
#         serverJob -j {path_format_to_linux(card_location)}{job_name}.list --array -d
#     """
#         print(s)
#         mylist.write(s)


    #%% Job file
    for i in range(start_id,end_id+1):
        s1 = f"""#!/bin/bash

#SBATCH --cpus-per-task=1
#SBATCH --threads-per-core=1
#SBATCH --ntasks {numCPU}
#SBATCH --nodes={numNodes}
#SBATCH --mem=12G
#SBATCH --time={simTime}
#SBATCH --account=p_fkv_laser
#SBATCH --output={i}.log
#SBATCH --job-name={i}
#SBATCH --open-mode=append
#SBATCH --mail-user=apurv.kulkarni@mailbox.tu-dresden.de
#SBATCH --mail-type=Begin,End,Fail

# update info file (job has started):
echo "Job {i+1} - running ($(pwd)/{i}.k)" > {i}.info

# load SLURM environment
ml modenv/scs5

# load program and additional modules if needed
ml LS-DYNA/12.0.0

# call program
srun mpp-dyna i={i}.k
EXITSTATUS=$?

# update info file (print exit status):
if [ "$EXITSTATUS" == "0" ]; then JOBSTATUS="finished"; else JOBSTATUS="cancelled";fi
echo "Job {i+1} - """
        s2 = "${JOBSTATUS} " 
        s3 = f"""($(pwd)/{i}.k)" > {i}.info

# clean up:
rm jobID
"""
        batch = s1+s2+s3

        if hpc:
            list_full = list_location+f'/{i}/runJob.sh'
        else:
            list_full = list_location+f'\\{i}\\runJob.sh'
        with open(list_full,'w+') as myjob:
            myjob.write(batch)


        #%% runChain bash file
        s = ''
        for i in range(start_id,end_id+1):
            s+= f' /scratch/ws/0/apku868a-mt/{ip["project_name"]}/{i}/'
        chain_str = creat_chain_sbatch(s)
        chunkBashName = 'runChain_'+f'{start_id}_{end_id}' + '.sh'
        with open(list_location+chunkBashName,'w+') as mychain:
            mychain.write(chain_str)
    
    # carefull about indentation here
    chunkBashNameList += 'source"' + chunkBashName + '"\n' + f'echo "{chunkBashName} started"\n sleep 45m\n' 
#     chunkBashNameList += f'source "/home/apku868a/mainProject_all/macro/batch_LSPost_{start_id}{end_id}.sh"'
    chunkBashNameList += 'source "' + chunkBashName + '"\n' + f' echo "{chunkBashName} started"\n sleep 45m\n' 
#     chunkBashNameList += f' tmux new-window -n {start_id}_{end_id} -t {project_name}\n tmux send-key -t {project_name}:{start_id}_{end_id} "/home/apku868a/{project_name}/macro/batch_LSPost_{start_id}{end_id}.sh" Enter\n'
    

# print(chunkBashNameList)
postSimcomands = f"""
source "cd {list_location}"
source "rm -r */mes*"
source "rm -r */scr*"
source "rm -r */d3dump*"
source "rm -r */d3full*"
source "rm -r */d3hsp*"
source "rm -r */load*"
source "rm -r */kill*"
source "rm -r */bg*"
source "rm -r */adptmp"
"""

#setting up tmux sessions
mainBash_str = "#!/bin/bash\n" + chunkBashNameList + postSimcomands
# mainBash_str = "#!/bin/bash\n" + chunkBashNameList + postSimcomands
with open(list_location+'runChainChunk.sh','w+') as mychain:
        mychain.write(mainBash_str)

tmux_Str = f"""#!/bin/bash
source "cd  {ip['macro_destination']}"
source "dos2unix *.sh"
source "dos2unix */*.sh"
source "chmod -R 775 *"
tmux new-session -d -s {project_name} './runChainChunk.sh'
tmux a
"""
with open(list_location+'tmuxChain.sh','w+') as mychain:
        mychain.write(tmux_Str)

# if hpc:
#     print(rf"""run in mobaxterm
#           cd list_location
#           sed -i -e 's/\r$//' runChain.sh""")
# else:
#     print(rf"""run in mobaxterm
#           cd {path_format_to_linux(list_location)}
#           sed -i -e 's/\r$//' runChain.sh""")

# # s1 = f"""On MobaXterm:
# #         rsync -avz {main_card_src} {hpc_scratch_location}
# #     """
# # print(s1)

# print("\nOn Taurus")
print('\t',f"cd /scratch/ws/0/apku868a-mt/{ip['project_name']}")
print('\t',r"dos2unix *.sh")
print('\t',r"dos2unix */runJob.sh")

# # with open(f"{ip['card_destination']}/{ip['project_name']}_commands.txt",'w+') as mylist:
# #     mylist.write(s1 + s2)
