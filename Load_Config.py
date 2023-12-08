import re
import copy
import pandas as pd
import numpy as np 

def change_value(dict_name:dict,busnumber,position,newvalue):
    "change value at position X belongs to bus number, position is the number of space before X"
    v = dict_name[busnumber]
    current_pos = 0
    i = 0
    count = 0
    for i in range(1,len(v)):
        if v[i-1] != v[i] and v[i-1] == ' ':
            current_pos += 1
            if current_pos == position:
                break
    starting_idx = i
    while v[i] != ' ':
        count += 1
        i += 1
    v = v[:starting_idx-1] + str(newvalue) + v[starting_idx+count:]
    dict_name[busnumber] = v
    return dict_name 

class LoadConfiguration():
    def __init__(self,load_df:pd.DataFrame,infile):
        self.df = load_df
        self.all_area_freq  = self.df['Load_all_area_freq'].values
        self.all_area_kz    = self.df['Load_all_area_kz'].values      
        self.all_area_kp    = self.df['Load_all_area_kp'].values
        self.all_area_ki    = self.df['Load_all_area_ki'].values

        self.area1_freq  = self.df['Load_area01_freq'].values
        self.area1_kz    = self.df['Load_area01_kz'].values
        self.area1_kp    = self.df['Load_area01_kp'].values
        self.area1_ki    = self.df['Load_area01_ki'].values

        self.area2_freq  = self.df['Load_area02_freq'].values
        self.area2_kz    = self.df['Load_area02_kz'].values
        self.area2_kp    = self.df['Load_area02_kp'].values
        self.area2_ki    = self.df['Load_area02_ki'].values

        self.area5_freq  = self.df['Load_area05_freq'].values
        self.area5_kz    = self.df['Load_area05_kz'].values
        self.area5_kp    = self.df['Load_area05_kp'].values
        self.area5_ki    = self.df['Load_area05_ki'].values

        self.load_modl  = self.get_model(infile)
        self.modl_fr_area,self.modl_fr_bus = self.__sort_load_model__()

    def get_model(self,filename):
        string = ''
        model = {}
        count_modl = 1
        # read file and turn file into models
        with open(filename,'r') as file:
            for line in file:
                string += line  
        string = string.split("/")
        for v in string:
            v += '    /'
            model[count_modl]   =   v
            count_modl          +=  1
        count_modl -= 1
        model.pop(count_modl)
        return model
    """
    def divide_area(self,caseno,allbus=set(), allarea=set()):
        idx     = caseno - 1
        string  = self.sub1[idx]
        string.replace('[',' ')
        string.replace(']',' ')
        string.replace(',',' ')
        string = string.split(' ')
        area = {}
        sub1 = set()
        area['key'] = string[0].lower()
        if area['key'] == 'area':
            for i in range (1,len(string)):
                num = int(string[i])
                sub1.add(num)
            area['sub1']    = sub1
            sub2            = allarea - sub1
            area['sub2']    = sub2

        elif area['key'] == 'machine' or area['key'] == 'bus':
            for i in range (1,len(string)):
                num = int(string[i])
                sub1.add(num)
            area['sub1'] = sub1
            sub2            = allbus - sub1
            area['sub2']    = sub2
        return area
    """

    def export_dyrfile(self,out_file,case_no,allbus:set(),allarea:set()):
        """change value of load data to .dyr file"""
        idx             = case_no - 1
        area            = self.divide_area(case_no,allbus,allarea)
        if area['key'] == 'machine' or area['key'] == 'bus':
            edited_load     = copy.deepcopy(self.modl_fr_bus)
            for busno in area['sub1']:
                kz1             = self.area1_kz[idx]
                if not np.isnan(kz1):
                    edited_load     = change_value(edited_load,busno,4,kz1)

                ki1             = self.area1_ki[idx]
                if not np.isnan(ki1):
                    edited_load     = change_value(edited_load,busno,5,ki1)

                kp1             = self.area1_kp[idx]
                if not np.isnan(kp1):
                    edited_load     = change_value(edited_load,busno,6,kp1)

                a71             = self.sub1_freq[idx]
                if not np.isnan(a71):
                    edited_load     = change_value(edited_load,busno,10,a71)

            for busno in area['sub2']:
                kz2             = self.area2_kz[idx]
                if not np.isnan(kz2):
                    edited_load     = change_value(edited_load,busno,4,kz2)

                ki2             = self.area2_ki[idx]
                if not np.isnan(ki2):
                    edited_load     = change_value(edited_load,busno,5,ki2)

                kp2             = self.area2_kp[idx]
                if not np.isnan(kp2):
                    edited_load     = change_value(edited_load,busno,6,kp2)

                a72             = self.area2_freq[idx] 
                if not np.isnan(a72):
                    edited_load     = change_value(edited_load,busno,10,a72)

        elif area['key'] == 'area':
            edited_load     = copy.deepcopy(self.modl_fr_area)
            for areano in area['sub1']:
            
                kz1             = self.area1_kz[idx]
                if not np.isnan(kz1):
                    edited_load     = change_value(edited_load,areano,4,kz1)

                ki1             = self.area1_ki[idx]
                if not np.isnan(ki1):
                    edited_load     = change_value(edited_load,areano,5,ki1)

                kp1             = self.area1_kp[idx]
                if not np.isnan(kp1):
                    edited_load     = change_value(edited_load,areano,6,kp1)

                a71             = self.sub1_freq[idx]
                if not np.isnan(a71):
                    edited_load     = change_value(edited_load,areano,10,a71)

            for areano in area['sub2']:
                kz2             = self.area2_kz[idx]
                if not np.isnan(kz2):
                    edited_load     = change_value(edited_load,areano,4,kz2)

                ki2             = self.area2_ki[idx]
                if not np.isnan(ki2):
                    edited_load     = change_value(edited_load,areano,5,ki2)

                kp2             = self.area2_kp[idx]
                if not np.isnan(kp2):
                    edited_load     = change_value(edited_load,areano,6,kp2)

                a72             = self.area2_freq[idx] 
                if not np.isnan(a72):
                    edited_load     = change_value(edited_load,areano,10,a72)
        sav_str = ''
        with open(out_file,"r") as file:
            for line in file:
                sav_str += line + '\n'

        with open(out_file,'w') as file:
            for load_val in edited_load.values():
                file.write(load_val)
            file.write('\n')
            file.write(sav_str)
        return

    def __sort_load_model__(self):
        load_bus_modl     = {}
        load_area_modl    = {}
        for modl in self.load_modl.values():
            split_val = re.split(r'\s+', modl)
            name = split_val[2]
            if r'IEELBL' in name:
                busno = int(split_val[1])
                load_bus_modl[busno] = modl
            elif r'IEELAR' in name:
                areano = int(split_val[1])
                load_area_modl[areano] = modl

        return load_area_modl, load_bus_modl



if __name__ == '__main__':
    load_config     = pd.read_excel('Input_Value.xlsx',sheet_name='Load_Configure')
    filename = '01_Data\\' + 'load-unmodifiedver' +'.dyr'
    lc = LoadConfiguration(load_config,infile=filename)
    print(lc.modl_fr_bus,lc.modl_fr_area)

        