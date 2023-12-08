import pandas as pd
import numpy as np 
import sys
import csv
import math
import os
import time
import warnings
import random
import shutil
import multiprocessing

# Ini SEtting
import IniStep_Config
#Import Input
from IniStep_Config import Input,NetworkData
from Gen_Config import GenConfiguration
from Load_Config import LoadConfiguration
from Disturbance import Disturbance

input           = Input()
Python_func     = input.Python_func
gen_dyrfile     = input.dyrfile
load_dyrfile    = input.load_dyrfile
out_dyfile      = input.out_dyrfile
PSSE_Data       = input.PSSE_Data
Out_Data        = input.Out_Data

sys.path.insert(0,Python_func) 

sys.path.insert(0,Python_func)                                     #------path of tool to read EMS data
    # Self_Lib
from PSSE_Basic_tool import ini_new_PSSE,PSSE_Solve,PSSE_open,PLB_machine,PLB_remove,Channel_Bus,PSSE_close,PSSE_save,P_out_hung
from PSSE_Basic_tool import Channel_Bus
# from PSSE_CCT import CCT_dynaSim,PSSE_clone
import psspy
import dyntools
import redirect

_i = psspy.getdefaultint()
_f = psspy.getdefaultreal()
_s = psspy.getdefaultchar()
redirect.psse2py



# -------------------------------- MAIN -----------------------------------------------------------#
    # Configuration
    # Step 1: Load Data
if input.__check_input_value_data__():

    genconfig   = GenConfiguration(input.gen_config,gen_dyrfile)
    loadconfig  = LoadConfiguration(input.load_config,load_dyrfile)
    disturb     = Disturbance(input.disturb)
    nw_dt       = NetworkData()
    allbus = nw_dt.__get_all_bus__()
    allarea = nw_dt.__get_all_area__()
    mchn_info = nw_dt.__get_machine_info__()
    
    for case_no in input.case:
        file_PSSE    = 'test'   
        PSSE_open(file_PSSE,PSSE_Data)
        sol = PSSE_Solve()
        P_out_hung()
        # Specify the path for the new folder
        Out_folder_path = Out_Data + 'case' + str(case_no)
        # Create the new folder
        os.makedirs(Out_folder_path, exist_ok=True)
        outdyr = Out_folder_path + '\\' + 'outdyr.dyr'
        genconfig.export_dyrfile(out_file=outdyr,case_no=case_no)
        loadconfig.export_dyrfile(outdyr,case_no,allbus,allarea)
        psspy.dyre_new([1,1,1,1],outdyr)
        # Create Subsystem
        psspy.bsys(0,0,[13.8,500.],3,[1,2,5],0,[],0,[],0,[])    
        psspy.bsys(0,0,[13.8,500.],3,[1,2,5],0,[],0,[],0,[])
        #convert gen
        psspy.cong(0)
        # convert load w constant load
        psspy.conl(0,1,1,[0,0],[0.0,0.0,0.0,100.0])               # check API Option1 : Contant
        psspy.conl(0,1,2,[0,0],[0.0,0.0,0.0,100.0])               # check API
        psspy.conl(0,1,3,[0,0],[0.0,0.0,0.0,100.0])

        psspy.ordr(0)
        psspy.fact()
        psspy.tysl(0)

        # define channel output
        psspy.chsb(0,0,[-1,-1,-1,1,2,0])    # PELEC, machine electrical power (pu on SBASE).
        #psspy.chsb(0,0,[-1,-1,-1,1,3,0])    # QELEC, machine reactive power
        psspy.chsb(0,0,[-1,-1,-1,1,12,0])   # BSFREQ, bus pu frequency deviations.
        #psspy.chsb(0,0,[-1,-1,-1,1,13,0])   # Machine / VOLT, bus pu voltages (complex)
        psspy.chsb(0,0,[-1,-1,-1,1,14,0])   # voltage and angle
        psspy.chsb(0,0,[-1,-1,-1,1,15,0])   # Machine / flow P
        #psspy.chsb(0,0,[-1,-1,-1,1,17,0])   # Machine / flow MVA 
        psspy.chsb(0,0,[-1,-1,-1,1,25,0])   # PLoad
        #psspy.chsb(0,0,[-1,-1,-1,1,26,0])   # QLoad
        
        # Step 5: Run simulation
        psspy.set_chnfil_type(0)
        outfile = Out_folder_path + '\\'  + str(case_no) + '.out'
        psspy.strt_2([0,1],outfile)              # Hung_35.4
        psspy.run(0,1.0,0,0,0)
        disturb.__simulate__(case_no)
        # run to 10s
        psspy.run(0,5.0,0,0,0)
            # Step 6 : Read ".out" file to convert out data into readable data
        i_out = Out_folder_path + '\\' + str(case_no) + '.out'
        chnfobj    = dyntools.CHNF(i_out, outvrsn=0)
        data_tuple = chnfobj.get_data()
        chan_id    = chnfobj.get_id()
        # out_range  =chnfobj.get_range()
        col_df     = list(data_tuple[2].values())
        data_dict = dict()
        # init a nested dict
        data_dict['VOLT'] = {}
        data_dict['ANGLE'] = {}
        data_dict['P_TRANSFER'] = {}
        data_dict['PLoad'] = {}
        data_dict['PMachine'] = {}
        data_dict['BUS FREQUENCY'] ={}
        data_dict['H_Machine'] = {}
        # add time into data
        for v in data_dict.values():
            v[chan_id[1]['time']] = data_tuple[2]['time']

        # rename variables
        volt_dict   = data_dict['VOLT']
        powr_dict   = data_dict['P_TRANSFER']
        ang_dict    = data_dict['ANGLE']
        plod_dict   = data_dict['PLoad']
        pma_dict    = data_dict['PMachine'] 
        inertia     = data_dict['H_Machine']
        freq_dict   = data_dict['BUS FREQUENCY']
        # categorize channel
        for k,v in chan_id[1].items():
            delspace    = ' '.join(v.split())
            val_split   = delspace.split()
            # property 
            prop        = val_split[0]
            if prop == 'POWR':
                prop2 = val_split[2]
                if prop2 == 'TO':
                    # P transfer df
                    powr_dict[v]   = data_tuple[2][k]
                else:
                    # P machine df
                    pma_dict[v]    = data_tuple[2][k]
            elif prop == 'VOLT':
                # voltage df
                volt_dict[v]   = data_tuple[2][k]
            elif prop == 'ANGL':
                # ANGLE df
                ang_dict[v]    = data_tuple[2][k]
            elif prop == 'PLOD':
                # Pload df
                plod_dict[v]   = data_tuple[2][k]
            elif prop == 'FREQ':
                #bus frequency
                freq_dict[v]   = data_tuple[2][k]
        # convert from pu to normal
        for k,v in volt_dict.items():
            if k != 'Time(s)':
                kedt = k 
                kedt = kedt.replace('[',' ')
                kedt = kedt.replace(']',' ')
                delspace        = ' '.join(kedt.split())
                k_split         = delspace.split()
                l               = len(k_split)
                nominal_volt    = float(k_split[l-1])
                for idx in range(len(v)):
                    volt_dict[k][idx] *= nominal_volt 
        for k,v in plod_dict.items():
            if k != 'Time(s)':
                for idx in range(len(v)):
                    plod_dict[k][idx] *= 100
        for k,v in pma_dict.items():
            if k != 'Time(s)':
                for idx in range(len(v)):
                    pma_dict[k][idx] *= 100
        for k,v in freq_dict.items():
            if k != 'Time(s)':
                for idx in range(len(v)):
                    freq_dict[k][idx] *= 50

        # create H sheet
        if not pd.isna(genconfig.H_all[case_no-1]):
            Hcase = genconfig.H_all[case_no-1]
            if not pd.isna(disturb.Trip_Gen[case_no-1]):
                trip_info = disturb.__get_trip_gen_data__(disturb.Trip_Gen[case_no-1])
                for mchn_val in mchn_info:
                    if mchn_val in trip_info:
                        pre_disturb = [Hcase for _ in range(0,106)]
                        after_disturb = [0 for _ in range(106,len(inertia['Time(s)']))]
                        col_name = str(mchn_val[0]) + '_' + str(mchn_val[1])
                        inertia[col_name] = []
                        inertia[col_name].extend(pre_disturb)
                        inertia[col_name].extend(after_disturb)
                    else:
                        col_name = str(mchn_val[0]) + '_' + str(mchn_val[1])
                        inertia[col_name] = [Hcase for _ in range(len(inertia['Time(s)']))]
            else:
                for mchn_val in mchn_info:
                    col_name = str(mchn_val[0]) + '_' + str(mchn_val[1])
                    inertia[col_name] = [Hcase for _ in range(len(inertia['Time(s)']))]
        else:
            if not pd.isna(disturb.Trip_Gen[case_no-1]):
                trip_info = disturb.__get_trip_load_data__(disturb.Trip_Gen[case_no-1])
                for mchn_val in mchn_info:
                    col_name = str(mchn_val[0]) + '_' + str(mchn_val[1])
                    Hthis_mchn = genconfig.H[col_name][case_no-1]
                    if mchn_val in trip_info:
                        pre_disturb = [Hthis_mchn for _ in range(0,106)]
                        after_disturb = [0 for _ in range(106,len(inertia['Time(s)']))]
                        col_name = str(mchn_val[0]) + '_' + str(mchn_val[1])
                        inertia[col_name] = []
                        inertia[col_name].extend(pre_disturb)
                        inertia[col_name].extend(after_disturb)
                    else:
                        col_name = str(mchn_val[0]) + '_' + str(mchn_val[1])
                        inertia[col_name] = [Hthis_mchn for _ in range(len(inertia['Time(s)']))]
            else:
                for mchn_val in mchn_info:
                    col_name = str(mchn_val[0]) + '_' + str(mchn_val[1])
                    Hthis_mchn = genconfig.H[col_name][case_no-1]
                    inertia[col_name] = [Hthis_mchn for _ in range(len(inertia['Time(s)']))]

        # export to excel file
        xlsname = Out_folder_path + '\\' + str(case_no) + '.xlsx'
        # Create a new Excel writer object
        with pd.ExcelWriter(xlsname) as writer:
            # Write the DataFrame to the Excel sheet
            for k,v in data_dict.items():
                df = pd.DataFrame(v)
                df.to_excel(writer,sheet_name=k,index=False)

        





