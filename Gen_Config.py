import re
import copy
import pandas as pd
import numpy as np
 


class GenConfiguration():
    def __init__(self,gen_df:pd.DataFrame,in_file):
        self.df = gen_df
        self.H_all  = self.df['Gen_all_H'].values
        self.R_all  = self.df['Gen_all_R'].values
        self.Ty_all = self.df['Gen_all_Ty'].values
        self.col_name = self.df.columns
        self.H = {}
        self.R = {}
        self.Ty = {}
        for  idx in range(4,len(self.col_name)):
            v = self.col_name[idx]
            v_split  = v.split('_')
            busno   = v_split[1]
            mchn_id = v_split[2]
            prop    = v_split[3]    #property
            key = busno + '_' + mchn_id
            if prop =='H':
                self.H[key]     = self.df.iloc[:,idx].values
            elif prop == 'Ty':
                self.Ty[key]    = self.df.iloc[:,idx].values
            elif prop == 'R':
                self.R[key]     = self.df.iloc[:,idx].values
                
        self.unedited_model = self.get_model(in_file)
        self.__sort_model__(self.unedited_model)
    
    def export_dyrfile(self,out_file,case_no):
        """vhange value of gen, exciter and export data to .dyr file"""
        edited_gen      = copy.deepcopy(self.generator)
        edited_excitr   = copy.deepcopy(self.exciter)
        edited_tgov     = copy.deepcopy(self.tgov)
        idx             = case_no - 1
        if np.isnan(self.H_all[idx]):
            for h_key in self.H.keys():
                newval = self.H[h_key][idx]
                if not np.isnan(newval):
                    # if value for this machine is empty, keep the old value
                    edited_gen  = change_value(edited_gen,h_key,position=8,newvalue=newval)
        else:
            newval  = self.H_all[idx]
            for h_key in self.H.keys():
                edited_gen  = change_value(edited_gen,h_key,position=8,newvalue=newval)
             

        if np.isnan(self.R_all[idx]):
            for r_key in self.R.keys():
                newval      = self.R[r_key][idx]
                if not np.isnan(newval):
                    edited_tgov  = change_value(edited_tgov,r_key,position=4,newvalue=newval)
        else:
            newval  = self.R_all[idx]
            for r_key in self.R.keys():
                edited_tgov  = change_value(edited_tgov,r_key,position=4,newvalue=newval)

        
        if np.isnan(self.Ty_all[idx]):
            for ty_key in self.Ty.keys():
                newval       = self.Ty[ty_key][idx]
                if not np.isnan(newval):
                    edited_tgov  = change_value(edited_tgov,ty_key,position=5,newvalue=newval)
        else:
            newval  = self.Ty_all[idx]
            for ty_key in self.Ty.keys():
                edited_tgov  = change_value(edited_tgov,ty_key,position=5,newvalue=newval)
        with open(out_file,'w') as file:
            for gen_val in edited_gen.values():
                file.write(gen_val)
            for exctr_val in edited_excitr.values():
                file.write(exctr_val)
            for tgov_val in edited_tgov.values():
                file.write(tgov_val)


    def __sort_model__(self,model:dict):
        "Sort dynamic model to generator, exciter and turbine governor from model"
        self.generator = {}
        self.exciter = {}
        self.tgov = {}
        for v in model.values():
            del_space = ' '.join(v.split())
            val_split = del_space.split()
            modl_name = val_split[1]
            key = val_split[0] + '_' + val_split[2]
            if r'GENROU' in modl_name:
                self.generator[key] = v
            
            elif r'TGOV1' in modl_name:
                self.tgov[key] = v
                
            elif r'IEEET1' in modl_name:
                self.exciter[key] = v


    def change_dyr_file(self,filename):
        string = ''
        model = {}
        count_modl = 0
        # read file and turn file into models
        with open(filename,'r') as file:
            for line in file:
                string += line + '\n' 
                if '/' not in line:
                    pass
                else:
                    count_modl += 1 
                    model[count_modl] = string
                    string = ''

    def get_model(self,filename):
        string = ''
        model = {}
        count_modl = 0
        # read file and turn file into models
        with open(filename,'r') as file:
            for line in file:
                string += line  
        string = string.split("/")
        for v in string:
            v += '    /'
            model[count_modl]   =   v
            count_modl          +=  1
        count_modl          -=  1
        model.pop(count_modl)
        return model

def change_value(dict_name:dict,busnumber,position,newvalue):
    """change value at position X belongs to bus number and id, position is the number of space before X, 
    busnumber structure is busno_mchnid """
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




if __name__ == '__main__':
    gen_config     = pd.read_excel('Input_Value_1.xlsx',sheet_name='Gen_Configure')
    filename = '01_Data\\' + 'savnw-unmodifiedver' +'.dyr'
    df = GenConfiguration(gen_df=gen_config,in_file=filename)
    model = df.get_model(filename)







    

    