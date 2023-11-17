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

Python_func = IniStep_Config.Python_func
dyrfile     = IniStep_Config.dyrfile
PSSE_Data   = IniStep_Config.PSSE_Data
Out_Data    = IniStep_Config.Out_Data

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
file_PSSE    = 'test'   
PSSE_open(file_PSSE,PSSE_Data)
sol = PSSE_Solve()
P_out_hung()
casename = 'case7'

# Specify the path for the new folder
folder_path = Out_Data + casename
# Create the new folder
os.makedirs(folder_path, exist_ok=True)



    # Step 2 : Dyr Read Data
    # Step 3: Dynamic Run
psspy.dyre_new([1,1,1,1],dyrfile)
psspy.bsys(0,0,[13.8,500.],3,[1,2,5],0,[],0,[],0,[])    # Create Subsystem
psspy.bsys(0,0,[13.8,500.],3,[1,2,5],0,[],0,[],0,[])

psspy.cong(0)
# constant load
# psspy.conl(0,1,1,[0,0],[0.0,0.0,0.0,0.0])               # check API Option1 : Contant
# psspy.conl(0,1,2,[0,0],[0.0,0.0,0.0,0.0])               # check API
# psspy.conl(0,1,3,[0,0],[0.0,0.0,0.0,0.0])
 
# load base on voltage
psspy.conl(0,1,1,[1,0],[ 100.0,0.0,0.0, 100.0])
psspy.conl(0,1,2,[1,0],[ 100.0,0.0,0.0, 100.0])
psspy.conl(0,1,3,[1,0],[ 100.0,0.0,0.0, 100.0])

# load base on frequency
#psspy.add_load_model(4, "*", 4, 1, r"""CMLDALU2""", 12, 0, ' ',132, 0.0)


#               # Check API
# psspy.conl(0,1,1,[0,0],[ 100.0,0.0,0.0, 100.0])     
# psspy.conl(0,1,2,[0,0],[ 100.0,0.0,0.0, 100.0])     
# psspy.conl(0,1,3,[0,0],[ 100.0,0.0,0.0, 100.0]) 
# constant Gen by change Droop = 0 ( R= 0)

# psspy.change_plmod_con(101,r"""1""",r"""TGOV1""",1,0.0)
# psspy.change_plmod_con(102,r"""1""",r"""TGOV1""",1,0.0)
# psspy.change_plmod_con(206,r"""1""",r"""TGOV1""",1,0.0)  
# psspy.change_plmod_con(211,r"""1""",r"""HYGOV""",1,0.0) 


psspy.ordr(0)
psspy.fact()
psspy.tysl(0)
oss_angle = 180
# psspy.set_genang_3(0, oss_angle,0.0,0)
# psspy.set_relang(1,300710,"1")
psspy.set_osscan(1,0)
psspy.dynamics_solution_param_2([_i,_i,_i,_i,_i,_i,_i,_i],[_f,_f, 0.001,_f,_f,_f,_f,_f])

    # Step 4 : Define Channel to scan
        # Review Chapter 8 API
            # Machine : Vol/ Angle / flow P
            # DZ : Volt/Angle at from and to Bus / P flow
# psspy.bsys(1,0,[0.0,0.0],0,[],len(Bus_Chn),Bus_Chn,0,[],0,[])

#psspy.chsb(0,0,[-1,-1,-1,1,1 ,0])  # Machine / ANGLE
#psspy.chsb(0,0,[-1,-1,-1,1,4 ,0])  # Machine / ETERM Machine terminal Voltage
psspy.chsb(0,0,[-1,-1,-1,1,2,0])    # PELEC, machine electrical power (pu on SBASE).
psspy.chsb(0,0,[-1,-1,-1,1,3,0])    # QELEC, machine reactive power
psspy.chsb(0,0,[-1,-1,-1,1,14,0])   #voltage and angle
psspy.chsb(0,0,[-1,-1,-1,1,15,0])   # Machine / flow P
psspy.chsb(0,0,[-1,-1,-1,1,17,0])   # Machine / flow MVA 
psspy.chsb(0,0,[-1,-1,-1,1,13,0])   # Machine / VOLT, bus pu voltages (complex)
psspy.chsb(0,0,[-1,-1,-1,1,25,0])   # PLoad
psspy.chsb(0,0,[-1,-1,-1,1,26,0])   # QLoad

    # Step 5: Run simulation
psspy.set_chnfil_type(0)
outfile = Out_Data + casename + '\\' + casename + '.out'
psspy.strt_2([0,1],outfile)              # Hung_35.4
psspy.run(0,1.0,0,0,0)
        # Create Disturbance 
            # Option 1 : Scaling Load  'SCAL' command in API chapter 
#more 15%
# psspy.scal_4(0,1,1,[0,0,0,0,0,0],[0.0,0.0,0.0,0.0,0.0,0.0,0.0])
# psspy.scal_4(0,1,2,[_i,_i,_i,1,0,1],[ 3680.0, 3258.6,0.0,-600.0, 950.0,-.0, 2242.5])
#less 15%
# psspy.scal_4(0,1,1,[0,0,0,0,0,0],[0.0,0.0,0.0,0.0,0.0,0.0,0.0])
# psspy.scal_4(0,1,2,[_i,_i,_i,1,0,1],[ 2720.0, 3258.6,0.0,-600.0, 950.0,-.0, 1657.5])
            # Option 2 : Change the Gen : 
                # 2.1 : Change G_ref   'increment_gref' in API
#psspy.increment_gref(101,r"""1""", 0.02)
psspy.increment_gref(211,r"""1""", -0.02)
                # 2.2 : Disconnect Gen  ''dist_machine_trip' in API
#trip_machine_number = 3011
if "trip_machine_number" in locals():
    psspy.dist_machine_trip(trip_machine_number,'1')                

# run to 10s
psspy.run(0,5.0,0,0,0)
    # Step 6 : Read ".out" file to convert out data into readable data

i_out = Out_Data + casename + '\\' + casename + '.out'
chnfobj    = dyntools.CHNF(i_out, outvrsn=0)
data_tuple = chnfobj.get_data()
chan_id    = chnfobj.get_id()
# out_range  =chnfobj.get_range()
col_df     = list(data_tuple[2].values())
data_dict = dict()
# init a nested dict
#data_dict['INFO'] = {}
data_dict['VOLT'] = {}
data_dict['ANGLE'] = {}
data_dict['P_TRANSFER'] = {}
data_dict['PLoad and QLoad'] = {}
data_dict['PMachine and QMachine'] = {}
data_dict['H_Machine'] = {}
#data_dict['INFO']["Require"] = 'P_load base on vol'
#data_dict['INFO']["Disturbance"] = 'machine 101 trip'
volt_dict = data_dict['VOLT']
powr_dict = data_dict['P_TRANSFER']
ang_dict = data_dict['ANGLE']
plod_dict = data_dict['PLoad and QLoad']
pma_dict = data_dict['PMachine and QMachine'] 

for v in data_dict.values():
    v['time'] = data_tuple[2]['time']
dyr_data = {}
l = 1
mchn_data = ''
with open('01_Data\\savnw.dyr', 'r') as file:
    for line in file:
        if "/" not in line:
            mchn_data += line
        else:
            dyr_data[l] = mchn_data
            l += 1
            mchn_data = ''
inertia = data_dict['H_Machine']
for v in dyr_data.values():
    if 'GENROU' in v:
        # Replace multiple spaces with a single space
        v = ' '.join(v.split())
        space = 0
        for i in range(len(v)):
            if v[i] == ' ':
                if space == 0:
                    machine_number = ''.join([v[k] for k in range(i+1)])
                space += 1
                if space == 7:
                    k = i + 1
                    h = str()
                    while v[k] != " ":
                        h += v[k]
                        k += 1
                    inertia[int(machine_number)] = float(h) 
                    break  
    if 'GENSAL' in v:
            # Replace multiple spaces with a single space
            v = ' '.join(v.split())
            space = 0
            for i in range(len(v)):
                if v[i] == ' ':
                    if space == 0:
                        machine_number = ''.join([v[k] for k in range(i+1)])
                    space += 1
                    if space == 6:
                        k = i + 1
                        h = str()
                        while v[k] != " ":
                            h += v[k]
                            k += 1
                        inertia[int(machine_number)] = float(h) 
                        break 
# check if is there any trip machine:
if "trip_machine_number" in locals():
    Hsaved = inertia[trip_machine_number]
    trip_machine_list = [Hsaved for i in range(1003)]
    after_trip = [0 for i in range(1003,len(inertia['time']))]
    trip_machine_list.extend(after_trip)
    inertia[trip_machine_number] = trip_machine_list
# add another channel and data to dict
for k,v in chan_id[1].items():
    if "VOLT" in v:
        volt_dict[v] = data_tuple[2][k]
    elif ("POWR" in v and "TO" in v) or "MVA" in v:
        powr_dict[v] = data_tuple[2][k]
    elif "ANGL" in v:
        ang_dict[v] = data_tuple[2][k]
    elif "PLOD" in v or "QLOD" in v:
        plod_dict[v] = data_tuple[2][k]
    elif ("POWR" in v and "TO" not in v) or "VARS" in v:
        pma_dict[v] = data_tuple[2][k]
"""convert per unit data"""
file_path = IniStep_Config.PSSE_Data + '\\busdata.xlsx'
busdf = pd.read_excel(file_path)
vbase = dict()
busno = busdf.loc[:,'Bus  Number']
vbus = busdf.loc[:,'Base kV']
for k in range(len(busno)):
    vbase[busno[k]] = vbus[k]

for k,v in volt_dict.items():
    if k != 'time':
        i = 5
        busnumber = str()
        while k[i] != " ":
            busnumber += k[i]
            i += 1
        busnumber = int(busnumber)
        archive = [element * vbase[busnumber] for element in v]
        volt_dict[k] = archive
for k,v in pma_dict.items():
    if k != 'time':
        archive = [element * 100 for element in v]
        pma_dict[k] = archive
for k,v in plod_dict.items():
    if k != 'time':
        archive = [element * 100 for element in v]
        plod_dict[k] = archive       



xlsname = Out_Data + casename + '\\' + casename + '.xlsx'
# Create a new Excel writer object
with pd.ExcelWriter(xlsname) as writer:
    # Write the DataFrame to the Excel sheet
    for k,v in data_dict.items():
        df = pd.DataFrame(v)
        df.to_excel(writer,sheet_name=k,index=False)
print(casename)


