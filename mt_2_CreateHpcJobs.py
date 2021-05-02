#=============================================================================
# Author: Apurv Kulkarni
#-----------------------------------------------------------------------------
# Creating jobs to be run on HPC 
# Not required to run if analysis is done locally
# Note: This doesn't use TUD's serverJob script
#=============================================================================

from utilities.mt_x_projectUtilities import creat_chain_sbatch, path_format_to_linux
from mt_0_input_factors_all import inputfactors

ip = inputfactors()
project_name = ip['project_name']
total_runs = ip['max_runs']
hpc_scratch_location = ip['hpc_loc']
main_card_dst = hpc_scratch_location + ip['project_name'] + '/'

# Job submition type
# 0: Manual job submission. Creates sbatch scripts. Requires 
#    rsync and running sbatch manually
# 1: Uses University's "serverJobScript" submition script. 
#    Creates lists of jobs in "job" folder.
job_submition_type = 1

# Setup for HPC sbatch files
numCPU          = 30
numNodes        = 2
simTime         = '04:00:00'
account_name    = 'HPC_PROJECT_NAME'
user_email      = 'xyz@abs.com'

if job_submition_type==0:
    
    # Creating analysis runs in chunks
    runsPerSubmission = 1
    chunks = int(total_runs/runsPerSubmission)
    if total_runs%chunks != 0:
        raise ValueError("Number of chuncks must be divisible by total runs")
    print('Total chunks: ', chunks)
        
    chunkBashNameList = ""
    for i in range(1,chunks+1):
        start_id = int((i-1)*total_runs/chunks)
        end_id = int(i*total_runs/chunks-1)
        
        # Job file
        for i in range(start_id,end_id+1):
            s1 = f"""#!/bin/bash

    #SBATCH --cpus-per-task=1
    #SBATCH --threads-per-core=1
    #SBATCH --ntasks {numCPU}
    #SBATCH --nodes={numNodes}
    #SBATCH --mem=12G
    #SBATCH --time={simTime}
    #SBATCH --account={account_name}
    #SBATCH --output={i}.log
    #SBATCH --job-name={i}
    #SBATCH --open-mode=append
    #SBATCH --mail-user={user_email}
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

            job_i = ip['card_destination']+f'{i}/runJob.sh'
            with open(job_i,'w+') as myjob:
                myjob.write(batch)

            # runChain bash file
            s = ''
            for i in range(start_id,end_id+1):
                s+= " " + ip['hpc_loc'] + ip["project_name"] + f"/{i}/"
            chain_str = creat_chain_sbatch(s)
            chunkBashName = 'runChain_'+f'{start_id}_{end_id}' + '.sh'
            with open(ip['card_destination'] + chunkBashName,'w+') as mychain:
                mychain.write(chain_str)
        
        # carefull about indentation here
        chunkBashNameList += ('source"' + chunkBashName + '"\n' + 
                            f'echo "{chunkBashName} started"\n sleep 45m\n')

    # Commands to be run after all analaysis runs are completed
    postSimcomands = """
    source "rm -r */mes*"
    source "rm -r */d3dump*"
    source "rm -r */d3full*"
    source "rm -r */d3hsp*"
    source "rm -r */load*"
    source "rm -r */kill*"
    source "rm -r */bg*"
    source "rm -r */adptmp"
    """

    # Creating main chain submission file
    mainBash_str = ("#!/bin/bash\n"+chunkBashNameList+
                    postSimcomands)
    with open(ip['card_destination']+'runChainChunk.sh','w+') as mychain:
            mychain.write(mainBash_str)

    print("Complete...")
    print(f"""1) On local machine:
    \t\t rsync {path_format_to_linux(ip['card_destination_main'])} {ip['hpc_loc']}

    2) On HPC server
    \t\t cd {main_card_dst}
    \t\t dos2unix *.sh
    \t\t dos2unix */*.sh
    \t\t chmod -R 775 *
    \t\t ./runChainChunk.sh
    """)

    print("""Once all the analysis are complete, 
    please run 'mt_3_createLsppMacro.py'""")

elif job_submition_type==1:
    job_loc = ip['job_dst']
    
    results_location = ip['lsdyna_result_path']
    
    ## Create job for HPC
    job_name = ip['project_name']
        
    card_id = list(range(0,ip['max_runs']))
    list_name_full = job_loc + job_name + '.list'
    with open(list_name_full,'w+') as mylist:
        for run in card_id:
            card_loc = path_format_to_linux(
                ip['card_destination']+f'{run}/')
            mylist.write(f'serverJob --processors {numCPU} --nodes {numNodes} -j {card_loc}{run}.k --jobDir {run} --downloadDir {run} --time {simTime}\n')
    
    with open(f"{job_loc}commands.txt",'w+') as mylist:
        s = f"""To run analysis
\t\t cd {job_loc}
\t\t serverJob -j {job_name}.list --array \n
To get results:
\t\t cd {ip['project_path']}results/
\t\t serverJob -j {job_loc}{job_name}.list --array -d
"""
        print(s)
        mylist.write(s)
