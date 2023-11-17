# Tran My Hung
# Date : 06/04/2023
import pandas as pd
import numpy as np 
from psse_path35 import path_direction,psse_file,open_case,pout 
from solve_35 import solve_py
import psse35
import psspy
_i = psspy.getdefaultint()
_f = psspy.getdefaultreal()
_s = psspy.getdefaultchar()

def PSSE_open(psse_name,psse_dir):           # Open PSSE nhap ten file ko can .sav
    SAV_folder = psse_dir                                        #------Folder of psse file 
    wrk_direction = psse_file(psse_name,SAV_folder)                                          #------Got link of psse file      
    # path_direction()                                                                         #------PSSE 34 path
    open_case(wrk_direction)                                                                 #------open PSSE

def PSSE_close():                   # Clode PSSE
    psspy.stop_2()

def PSSE_default_var():             # Default Value in PSSE
    import psspy
    _i = psspy.getdefaultint()
    _f = psspy.getdefaultreal()
    _s = psspy.getdefaultchar()
    return _i,_f,_s

def P_out_hung():                   # No output in PSSE
    import psspy
    psspy.report_output(6,'',0)
    psspy.progress_output(6,'',0)
    psspy.alert_output(6,'',0)
    psspy.prompt_output(6,'',0)

def PSSE_Solve():                   # Solve Power Flow
    from solve_35 import solve_py                                                                #------Solve file psse
    i_solve = solve_py()
    PSSE_default_var()
    P_out_hung()                                                                            #------1 : Convergence
                                                                                            #------2 : Blown up  
                                                                                            #------3 : Not Convergence 
    return i_solve

def PSSE_save(file):
    ier = psspy.save(file)
    return ier
################## Inicase
def ini_new_PSSE():
    path_direction()
#PSSE_open(psse_Detail)
# sol = PSSE_Solve ()
    import psse35
    import psspy
    _i = psspy.getdefaultint()
    _f = psspy.getdefaultreal()
    _s = psspy.getdefaultchar()
    import redirect
    redirect.psse2py()
    psspy.psseinit(100000)
    # ierr = psspy.progress_output(islct=6)
    ier = psspy.newcase_2([1,1],100.0,50.0,"hung",r"test")
    return ier

############################# PLB ############################################

# -- Def fpr PLB creation
def PLB_machine (bus_Grid, bus_Plb):
    ier,kV_Gird = psspy.busdat(bus_Grid, 'BASE')
    type_Code = 2
    ier, Plb_Vsched = psspy.busdat(bus_Grid, 'PU')
    # Tao DZ noi bus_Plb toi bus_Grid
    if psspy.busexs(bus_Plb)>0 : psspy.bus_data_3(bus_Plb,[1,1,1,1],[kV_Gird,_f,_f,_f,_f,_f,_f],"PLB_GEN")
    if psspy.busexs(bus_Grid)>0 : psspy.bus_data_3(bus_Grid,[1,10,50,10],[kV_Gird,_f,_f,_f,_f,_f,_f],"NAME_")
    
    psspy.bus_chng_3(bus_Plb,[_i,_i,_i,_i],[kV_Gird,_f,_f,_f,_f,_f,_f],_s)
    psspy.bus_chng_3(bus_Grid,[_i,_i,_i,_i],[kV_Gird,_f,_f,_f,_f,_f,_f],_s)
    psspy.branch_data(bus_Plb,bus_Grid,"1",[_i,_i,_i,_i,_i,_i],[0,0,0,1732.1,1732.1,1732.1,_f,_f,_f,_f,0,_f,_f,_f,_f])
    psspy.seq_branch_data_3(bus_Plb,bus_Grid,"1",_i,[0,0,0,_f,_f,_f,_f,_f])

    # Tao Gen
    if psspy.busexs(bus_Plb)>0 : psspy.bus_data_3(bus_Plb,[1,1,1,1],[kV_Gird,_f,_f,_f,_f,_f,_f],"PLB_GEN")
    psspy.bus_chng_3(bus_Plb,[type_Code,_i,_i,_i],[kV_Gird,_f,_f,_f,_f,_f,_f],_s)       #Type of Bus
    psspy.plant_data(bus_Plb,_i,[Plb_Vsched,_f])
    psspy.machine_data_2(bus_Plb,"1",[_i,_i,_i,_i,_i,_i],[0,0,0,0,0,0,99999,_f,0.2136,_f,_f,_f,_f,_f,_f,_f,_f])
    psspy.seq_machine_data_3(bus_Plb,"1",_i,[_f,0.1965,_f,0.1965,_f,0.0955,0.2767,2.18,_f,_f])
    i_solve = PSSE_Solve()

def PLB_remove (bus_Grid, bus_Plb):
    psspy.purgmac(bus_Plb,r"""1""")
    psspy.purgbrn(bus_Grid,bus_Plb,r"""1""")
    psspy.bsysinit(1)
    psspy.bsyso(1,bus_Plb)
    psspy.extr(1,0,[0,0])

def Channel_Bus():
    ier, Mch_Data1 = psspy.amachint (-1, 3, ['NUMBER','STATUS'])
    ier, Mch_Data2 = psspy.amachchar(-1, 3, ['ID','NAME'])

    df_Mch     =pd.DataFrame ({ 'BusNum'     : Mch_Data1[0]        , 'STATUS'       : Mch_Data1[1]     ,
                                'ID'         : Mch_Data2[0]        , 'Name'         : Mch_Data2[1]     })

    ierr, Bus1 = psspy.abusint(-1, 2, ['NUMBER','OWNER'])
    df_Bus     = pd.DataFrame({'key' : Bus1[0] ,'OWNER' : Bus1[1]  })

    df_Mch['key'] = df_Mch['BusNum']
    df_Mch = pd.merge(df_Mch,df_Bus[['key','OWNER']], on='key', how= 'left')
    df_Mch['keep'] =np.where((df_Mch['OWNER'] == 1000)| 
                             (df_Mch['OWNER'] == 2000)|
                             (df_Mch['OWNER'] == 3000)|
                             (df_Mch['OWNER'] == 3100) , 'chn','ign')
    df_Mch = df_Mch[df_Mch['keep'] == 'chn']
    df_Mch['BusNum'] = df_Mch['BusNum'].astype(int)
    # MchBus_ang = list(set(df_Mch['BusNum'].values))
    MchBus_ang =df_Mch['BusNum'].tolist()
    MchBus_ang =list(set(MchBus_ang))
    
    return MchBus_ang