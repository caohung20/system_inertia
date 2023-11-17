import os
import sys
# import win32com.client
#
def pout(t): 
    import psspy   
    if t>0:
        psspy.progress_output(1, "", 0)
        psspy.alert_output(1, "", 0)
    else:
        psspy.progress_output(6, "", 0)
        psspy.alert_output(6, "", 0)
def psse_file(psse,link) : 
    ilink = link + psse + '.sav'
    return ilink 
def path_direction() :
#def get_machine_plexo() :
    versionPsse = 35.3
    #
    if os.path.isdir("C:\\Program Files (x86)\\PTI"):
        pathPSSE   = 'C:\\Program Files\\PTI\\PSSE35\\'+str(versionPsse)+'\\PSSBIN'
        pathPSSE34 = 'C:\\Program Files\\PTI\\PSSE35\\'+str(versionPsse)+'\\PSSPY39'
    else:
        pathPSSE = 'C:\\Program Files\\PTI\\PSSE'+str(versionPsse)+'\\PSSBIN'
        pathPSSE34 = 'C:\\Program Files\\PTI\\PSSE'+str(versionPsse)+'\\PSSPY27'
    #
    sys.path.append(pathPSSE)
    sys.path.append(pathPSSE34)
    #
    os.environ['PATH'] = pathPSSE + ";" + os.environ['PATH']
    #psspy.psseinit(100)
    #Xoa file
    #if os.path.exists('demo.xlsx'):
    #    os.remove('demo.xlsx')
def open_case(path_file) :
    import psse35
    import psspy
    import redirect
    redirect.psse2py()
    psspy.psseinit(100000)
    ierr = psspy.progress_output(islct=6)
    psspy.case(path_file) 
