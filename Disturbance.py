import sys
import pandas as pd
import numpy as np
from IniStep_Config import Input,NetworkData
input = Input()
import psse35
import psspy

_i = psspy.getdefaultint()
_f = psspy.getdefaultreal()
_s = psspy.getdefaultchar()
class Disturbance():
    def __init__(self,disturb_df:pd.DataFrame):
        self.df             = disturb_df
        self.delta_P_gen    = self.df['Delta_P_Gen_change'].values
        self.delta_P_load   = self.df['Delta_P_Load_change'].values
        self.Trip_Gen       = self.df['Trip_Gen'].values
        self.Trip_Load      = self.df['Trip_Load'].values
        self.Change_Gen     = self.df['Change_Gen'].values
        self.Change_Load    = self.df['Change_Load'].values
        self.nw_dt          = NetworkData()
        self.Pnw            = self.nw_dt.__get_Pnw__()
        self.Pmin           = self.nw_dt.__get_Pmin__()
        self.Pmax           = self.nw_dt.__get_Pmax__()

    def __simulate__(self,caseno):
        idx = caseno - 1
        if not pd.isna(self.Trip_Gen[idx]) and self.Trip_Gen[idx] != 0:
            # execute trip machine if value trip machine exist in excel file
            val = str(self.Trip_Gen[idx])
            modl_data = self.__get_trip_gen_data__(val)
            for mchn in modl_data:
                mchn_id = str(mchn[1])
                tripbus = mchn[0]
                psspy.dist_machine_trip(tripbus,mchn_id)
        

        if not pd.isna(self.Change_Load[idx]) and self.Change_Load[idx] != 0:
            # identify region to stimulate and increase load
            region,lis_val = self.__get_change_load_data__(str(self.Change_Load[idx]))
            DeltaP = self.delta_P_gen[idx]
            if   region == 'Area':
                numarea = len(lis_val)
                psspy.bsys(0,0,[13.8,500.],numarea,lis_val,0,[],0,[],0,[])
                psspy.scal_4(0,1,1,[0,0,0,0,0,0],[0.0,0.0,0.0,0.0,0.0,0.0,0.0])
                psspy.scal_4(0,1,2,[_i,_i,_i,3,0,0],[DeltaP,0.0,0.0,0.0,0.0,0.0,0.0])

            elif region == 'Owner':
                numowner = len(lis_val)
                psspy.bsys(0,0,[13.8,500.],0,[],0,[],numowner,lis_val,0,[])
                psspy.scal_4(0,1,1,[0,0,0,0,0,0],[0.0,0.0,0.0,0.0,0.0,0.0,0.0])
                psspy.scal_4(0,1,2,[_i,_i,_i,3,0,0],[DeltaP,0.0,0.0,0.0,0.0,0.0,0.0])

            elif region == 'Zone':
                numzone = len(lis_val)
                psspy.bsys(0,0,[13.8,500.],0,[],0,[],0,[],numzone,lis_val)
                psspy.scal_4(0,1,1,[0,0,0,0,0,0],[0.0,0.0,0.0,0.0,0.0,0.0,0.0])
                psspy.scal_4(0,1,2,[_i,_i,_i,3,0,0],[DeltaP,0.0,0.0,0.0,0.0,0.0,0.0])

            elif region == 'Bus':
                numbus  = len(lis_val)
                psspy.bsys(0,0,[ 13.8, 500.],0,[],numbus,lis_val,0,[],0,[])
                psspy.scal_4(0,1,1,[0,0,0,0,0,0],[0.0,0.0,0.0,0.0,0.0,0.0,0.0])
                psspy.scal_4(0,1,2,[_i,_i,_i,3,0,0],[DeltaP,0.0,0.0,0.0,0.0,0.0,0.0])
                

        if not pd.isna(self.Change_Gen[idx]) and self.Change_Gen[idx] != 0:
            # Disturbance due to change gref or incre/decre 
            mchn_dict = self.__get_change_gen_data__(self.Change_Gen[idx])
            Ptotal    = self.delta_P_gen[idx]
            set_mchn  = set()
            for busno in mchn_dict.keys():
                set_mchn.add(busno)
            Pfinal = distribute_P(Ptotal,set_mchn,self.Pnw,self.Pmax,self.Pmin)
            for busno,mchn_id in mchn_dict.items():
                psspy.increment_gref(busno,mchn_id, Pfinal[busno])


        if not pd.isna(self.Trip_Load[idx]) and self.Trip_Load[idx] != 0:
            # execute trip bus if value trip bus exist in excel file
            val = self.Trip_Load[idx]
            set_bus = self.__get_trip_load_data__(str(val))
            for bus_no in set_bus:
                psspy.dist_bus_trip(bus_no)


    def __get_change_load_data__(self,value:str):
        value.replace('"',' ')
        value.replace('[',' ')
        value.replace(']',' ')
        value.replace(',',' ')
        value       = value.split()
        region      = value[0]
        val_list    = []
        for idx in range(1,len(value)):
            digit = int(value[idx])
            val_list.append(digit)
        return region,val_list
    
    def __get_change_gen_data__(self,value:str):
        """split string and get list of integers including bus number and machine id"""
        value     = value.replace(',',' ')
        value     = value.replace('[',' ')
        value     = value.replace(']',' ')
        value     = value.split()
        modl_dict = {}
        for string in value:
            for i in range(len(string)):
                if string[i] == '_':
                    break
            bus_no              = int(string[:i])
            mchn_id             = string[i+1:]
            modl_dict[bus_no]   = mchn_id
        return modl_dict
    
    def __get_trip_gen_data__(self,value:str):
        """split string and get list of integers including bus number and machine id"""
        value.replace(',',' ')
        value.replace('[',' ')
        value.replace(']',' ')
        val_split = value.split()
        modl_list = []
        for string in val_split:
            for i in range(len(string)):
                if string[i] == '_':
                    break
            bus_no  = int(string[:i])
            mchn_id = int(string[i+1:])
            modl_list.append([bus_no,mchn_id])
        return modl_list
    
    def __get_trip_load_data__(self,value:str):
        """split string and get list of integers with bus number """
        value     = value.replace(',',' ')
        value     = value.replace('[',' ')
        value     = value.replace(']',' ')
        val_split = value.split()
        setbus = set()
        for bus_no in val_split:
            setbus.add(int(bus_no))
        return setbus

    
def distribute_P(Ptotal,set_mchn:set,Pnw:dict,Pmax=dict(),Pmin=dict()):
    """take total P divide by machines in set machine. if a machine exceed Pmax or Pmin, 
    set the value of this machine is Pmin or Pmax. the remained power of that machine is 
    proceeded similarly to the rest  """
    Pnew   = {}
    Pfinal = {}
    sav_set_mchn = set_mchn.copy()
    if Ptotal >= 0:
        # With Ptotal >= 0 check Pmax condition
        while set_mchn:
            P_1mchn = Ptotal / len(set_mchn)
            for mchn in set_mchn:
                Pnew[mchn] = Pnw[mchn] + P_1mchn
                if Pnew[mchn] > Pmax[mchn]:
                    Pfinal[mchn] = Pmax[mchn]
                    Ptotal      += Pnew[mchn] - Pmax[mchn] - P_1mchn
                    sav_set_mchn.discard(mchn) 
                
            if len(sav_set_mchn) == len(set_mchn):
                for mchn in set_mchn:
                    Pfinal[mchn] = Pnew[mchn]
                break
            else:
                set_mchn = sav_set_mchn.copy()
    else:
        # exactly the same as if condition except that this case check Pmin condition
        while set_mchn:
            P_1mchn = Ptotal / len(set_mchn)
            for mchn in set_mchn:
                Pnew[mchn] = Pnw[mchn] + P_1mchn
                if Pnew[mchn] < Pmin[mchn]:
                    Pfinal[mchn] = Pmin[mchn]
                    Ptotal      += Pnew[mchn] - Pmin[mchn] - P_1mchn
                    sav_set_mchn.discard(mchn)     
            if len(sav_set_mchn) == len(set_mchn):
                for mchn in set_mchn:
                    Pfinal[mchn] = Pnew[mchn]
                break
            else:
                set_mchn = sav_set_mchn.copy()
    return Pfinal           


if __name__ == '__main__':
    disturb_df     = pd.read_excel('Input_Value_1.xlsx',sheet_name='Disturbance')
    Change_Load    = disturb_df['Change_Load'].values
    delta_P_load   = disturb_df['Delta_P_Load_change'].values
    Ptotal = 1000
    set_mchn = {1,2}
    Pnw = {1:100,2:200}
    Pmax = {1:150,2:3000}
    Pmin = {1:0,2:0}
    Pfinal =  distribute_P(Ptotal,set_mchn,Pnw,Pmax,Pmin)
    print(Pfinal)


    
    
    
 
