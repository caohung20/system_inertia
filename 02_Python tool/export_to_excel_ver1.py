import psspy 
import os 
import excelpy
# Machine Data 
def export_ini(file_name):
    file = file_name +'.xlsx'
    ierr, Gen_Name   = psspy.amachchar(-1, 4, ['ID','NAME'])                                
    ierr, Gen_data1  = psspy.amachint(-1, 4, ['NUMBER','STATUS','OWN1'])
    ierr, Gen_data2  = psspy.amachreal(-1, 4, ['PGEN','QGEN','PMAX','PMIN','QMAX','QMIN'])
# Plant Bus Data
    ierr, Plant_name = psspy.agenbuschar(-1, 4, 'NAME')
    ierr, Plant_Data1 = psspy.agenbusint(-1, 4, ['NUMBER','TYPE','AREA','ZONE','OWNER'])
# Print test
    #if os.path.exists(file):
    #    os.remove(file)
    xl = excelpy.workbook(file)
    xl.show()
    # Machine data
    xl.set_cell('a1','Machine Name')
    xl.set_cell('b1','Machine ID')
    xl.set_cell('c1','Machine Bus Num')
    xl.set_cell('d1','Machine Status')
    xl.set_cell('e1','Machine OWNER')
    xl.set_cell('f1','Machine PGEN')
    xl.set_cell('g1','Machine PMAX')
    xl.set_cell('h1','Machine QGEN')
    xl.set_cell('i1','Machine QMAX')
    # Plant data
    xl.set_cell('j1','Plant Name')
    xl.set_cell('k1','Plant BusNum')
    xl.set_cell('l1','Plant Type')
    xl.set_cell('m1','Plant Area')
    xl.set_cell('n1','Plant Zone')
    xl.set_cell('o1','Plant Owner')
    # Add to excel Machine Data
    xl.set_range(2,'a',zip(*[Gen_Name[1]]))
    xl.set_range(2,'b',zip(*[Gen_Name[0]]))
    xl.set_range(2,'c',zip(*[Gen_data1[0]]))
    xl.set_range(2,'d',zip(*[Gen_data1[1]]))
    xl.set_range(2,'e',zip(*[Gen_data1[2]]))
    xl.set_range(2,'f',zip(*[Gen_data2[0]]))
    xl.set_range(2,'g',zip(*[Gen_data2[3]]))
    xl.set_range(2,'h',zip(*[Gen_data2[1]]))
    xl.set_range(2,'i',zip(*[Gen_data2[4]]))
    # Add to excel Plant Data
    xl.set_range(2,'j',zip(*Plant_name))
    xl.set_range(2,'k',zip(*[Plant_Data1[0]]))
    xl.set_range(2,'l',zip(*[Plant_Data1[1]]))
    xl.set_range(2,'m',zip(*[Plant_Data1[2]]))
    xl.set_range(2,'n',zip(*[Plant_Data1[3]]))
    xl.set_range(2,'o',zip(*[Plant_Data1[4]]))
    # Save ------------take time ----> reduced performance
    xl.set_range(2,'b',zip(*[Plant_Data1[4]]))
    xl.save(file)
    xl.close()
    # Def 2
