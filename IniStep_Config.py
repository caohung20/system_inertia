import os
import pandas as pd
import numpy as np

class Input():
    def __init__(self):
        self.link_Project = os.getcwd() + '\\' 
        self.Python_func  = self.link_Project  + '02_Python tool\\'   
        self.PSSE_Data    = self.link_Project  + '01_Data\\'
        self.Out_Data     = self.link_Project  + '03_Out_Data\\'
        # Dyr_Data     = link_Project  + '04_dyr\\'
        # Clone_Psse   = link_Project  + '05_ClonePsse'
        # PSSE_Out     = link_Project  + '06_PSSE_cal\\'
        # Out_folder   = link_Project  + '07_DyrOut\\'

        
                # Dynamic Configuration
        self.dyrfile      = self.PSSE_Data     + "savnw-unmodifiedver.dyr"  
        self.out_dyrfile  = self.PSSE_Data     + "modified.dyr" 
        self.load_dyrfile = self.PSSE_Data     + 'load-unmodifiedver.dyr'     

        # oss_angle    = 180
        # time_frame = 3
        # faultType = "1_phase" 
        # t_fault = 0.5
        self.input_value = 'Input_Value_1.xlsx'
        self.gen_config     = pd.read_excel(self.input_value,sheet_name='Gen_Configure')
        self.load_config    = pd.read_excel(self.input_value,sheet_name='Load_Configure')
        self.disturb        = pd.read_excel(self.input_value,sheet_name='Disturbance')
        self.case           = self.gen_config['Case'].values

    def __check_input_value_data__(self):
        gen_len     = len(self.gen_config)
        load_len    = len(self.load_config)
        disturb_len = len(self.disturb)
        if gen_len == load_len and load_len == disturb_len:
            return True
        else: 
            return False
        

class NetworkData():
    def __init__(self):
        self.link_Project = os.getcwd() + '\\'
        self.PSSE_Data    = self.link_Project  + '01_Data\\'
        # network data from a csv file
        self.mchn_path  = self.PSSE_Data     + 'MachineData.csv'
        self.bus_path   = self.PSSE_Data     + 'BusData.csv'
        self.plant_path = self.PSSE_Data     + 'PlantData.csv'
        # take data from csv with machine_path,plant_path,bus_path in class Input
        self.machine_df = pd.read_csv(self.mchn_path, sep=';',skiprows=1)
        self.plant_df   = pd.read_csv(self.plant_path,sep=';',skiprows=1)
        self.bus_df     = pd.read_csv(self.bus_path,  sep=';',skiprows=1)

    def __get_Pmax__(self):
        Pmax    = dict()
        busno   = self.machine_df['Bus  Number']
        Pm      = self.machine_df['PMax (MW)']
        for idx in range(len(busno)):
            if not np.isnan(Pm[idx]) and not np.isnan(busno[idx]):
                k       = int(busno[idx])
                Pmax[k] = Pm[idx]
        return Pmax 

    def __get_Pmin__(self):
        Pmin    = dict()
        busno   = self.machine_df['Bus  Number']
        Pm      = self.machine_df['PMin (MW)']
        for idx in range(len(busno)):
            if not np.isnan(Pm[idx]) and not np.isnan(busno[idx]):
                k       = int(busno[idx])
                Pmin[k] = Pm[idx]
        return Pmin
    
     
    def __get_Pnw__(self):
        Pnw    = dict()
        busno   = self.plant_df['Bus  Number']
        Pm      = self.plant_df['PGen (MW)']
        for idx in range(len(busno)):
            if not np.isnan(Pm[idx]) and not np.isnan(busno[idx]):
                k       = int(busno[idx])
                Pnw[k] = Pm[idx]
        return Pnw
    
    def __get_all_bus__(self):
        """get all bus in set type"""
        busno = self.bus_df['Bus  Number'].values
        setbus = set()
        for v in busno:
            if not np.isnan(v):
                setbus.add(v)
        return setbus
    
    def __get_machine_info__(self):
        """return a nested list include [busnumber,id]"""
        info_mchn   = []
        busno       = self.machine_df['Bus  Number'].values
        mchn_id     = self.machine_df['Id'].values
        # Create a boolean mask to identify NaN values
        mask = ~np.isnan(busno)
        newbusno  = busno[mask]
        new_mchn_id = mchn_id[mask]
        for idx in range(len(newbusno)):
            bus_num = int(newbusno[idx])
            machn_id = int(new_mchn_id[idx])
            info_mchn.append([bus_num,machn_id])
        return info_mchn
        
    
    def __get_all_area__(self):
        """get all bus in set type"""
        areano = self.bus_df[' Area Num'].values
        setarea = set()
        for v in areano:
            if not np.isnan(v):
                setarea.add(v)
        return setarea


if __name__ == '__main__':
    imput = Input()
    nw_dt = NetworkData()
    column_name = nw_dt.__get_Pmin__()
    print(column_name)

