import os, sys
import psspy
_i = psspy.getdefaultint()
_f = psspy.getdefaultreal()
_s = psspy.getdefaultchar()

# Function
def gen_sub(Ax):
    if Ax == 10:
        psspy.bsys(5,0,[0.0, 500.],0,[],0,[],3,[100,400,600],0,[])
        psspy.bsys(5,0,[0.0, 500.],0,[],0,[],3,[100,400,600],0,[])
    elif Ax == 20:
        psspy.bsys(5,0,[0.0, 500.],0,[],0,[],3,[200,500,700],0,[])
        psspy.bsys(5,0,[0.0, 500.],0,[],0,[],3,[200,500,700],0,[])
    elif Ax == 30:
        psspy.bsys(5,0,[0.0, 500.],0,[],0,[],2,[300,800],0,[])
        psspy.bsys(5,0,[0.0, 500.],0,[],0,[],2,[300,800],0,[])
def dispatch_PQ(s):
    P = [[]]
    Q = [[]]
    for i in range(len(s[0])):
        i_P = s[0][i].real
        i_Q = s[0][i].imag
        P[0].append(i_P)
        Q[0].append(i_Q)
    return P,Q
def def_ratio(bus):
    i_bus = [[]]
    j_bus = [[]]
    k_bus = [[]]
    s_MBA = [[]]
    for i in range(len(bus[0])):
        ib = bus[0][i]
        ier = psspy.inibrn(ib,2)
        ier,jb,kb,ickt = psspy.nxtbrn3(ib)    
        if kb == 0:
            ierr, s_b = psspy.xfrdat(ib, jb, ickt, 'SBASE1')  
        elif kb !=0:
            ierr, s_b = psspy.wnddat(jb, ib, kb, ickt, 'SBASE')                        
            if ierr != 0:
                print('check the bus number'+str(ib))
        while ierr ==3:
            ier,jb,kb,ickt = psspy.nxtbrn3(ib) 
            if kb != 0:
                ierr, s_b = psspy.wnddat(jb, ib, kb, ickt, 'SBASE')
            elif kb == 0:
                ierr, s_b = psspy.xfrdat(ib, jb, ickt, 'SBASE1')
        if ib == 573003 :
            s_b = 0
        i_bus[0].append(ib)
        j_bus[0].append(jb)
        k_bus[0].append(kb)
        s_MBA[0].append(s_b)
    return i_bus,j_bus,k_bus,s_MBA  
def sum_matrix (M) :
    Sum = 0
    for i in range(len(M[0])):
        Sum = Sum + M[0][i]
    return Sum

def Scale_tool (i_Ax,i_scale,scale_mth) : 
    scale_method = int(scale_mth)
    #if i_ch == 0:
    #    print(" INVALID VALUE - DO IT AGIAN")
    gen_sub(i_Ax) # Tao Subsytem for SCALE
    ierr, l_num = psspy.aloadint(5, 1, 'NUMBER') # load num
    ierr, l_name = psspy.aloadchar(5, 1, 'NAME') # load name
    ierr, load = psspy.aloadcplx(5, 1, 'MVAACT') # Actual in-service constant MVA load  
    P_l,Q_l = dispatch_PQ(load)
    POS_b = [[]]
    NEG_b = [[]]
    for i in range(len(l_num[0])):
        if P_l[0][i] < 0 :
            NEG_b[0].append(l_num[0][i])
        else :
            POS_b[0].append(l_num[0][i])
    psspy.bsys(8,0,[0.0, 500.],0,[],len(POS_b[0]),POS_b[0],0,[],0,[]) # POS SUB
    ierr, p_num = psspy.aloadint(8, 1, 'NUMBER') # load num pos
    ierr, p_s = psspy.aloadcplx(8, 1, 'MVAACT') # Actual in-service constant MVA load  pos 
    i_p,j_p,k_p,s_p = def_ratio(p_num)  # 
    p_p, p_q = dispatch_PQ(p_s)
    Pos_P = sum_matrix(p_p)
    Pos_Q = sum_matrix(p_q)
    Pos_Sbase = sum_matrix(s_p)      
    if len(NEG_b[0]) > 0:
        psspy.bsys(9,0,[0.0, 500.],0,[],len(NEG_b[0]),NEG_b[0],0,[],0,[]) # NEG SUB
        psspy.bsys(9,0,[0.0, 500.],0,[],len(NEG_b[0]),NEG_b[0],0,[],0,[]) # NEG SUB
        ierr, ng_num = psspy.aloadint(9, 1, 'NUMBER') # load num neg
        ierr, ng_s = psspy.aloadcplx(9, 1, 'MVAACT') # Actual in-service constant MVA load neg
        ng_p, ng_q = dispatch_PQ(ng_s)
        Neg_P_psse = sum_matrix(ng_p)
        Neg_Q_psse = sum_matrix(ng_q)
        i_ng,j_ng,k_ng,s_ng = def_ratio(ng_num)   #
        Neg_Sbase = sum_matrix(s_ng)
        Neg_Pload_est = Pos_P * Neg_Sbase / Pos_Sbase   # Predicted Load
        Neg_res_est = Neg_Pload_est - Neg_P_psse   # Presicted RES
    else :
        Neg_Pload_est = 0
        Neg_res_est = 0
        Neg_Q_psse = 0
    Pos_p_chg = i_scale * Pos_P / ( Pos_P + Neg_Pload_est)
    Neg_p_chg = i_scale - Pos_p_chg
    i_ratio = i_scale / (Pos_P + Neg_Pload_est)
    new_pos_p = Pos_P + Pos_p_chg ######New P in POs
    new_neg_p = Neg_Pload_est - Neg_res_est + Neg_p_chg  # New P in Neg
    if scale_method == 0:
        new_pos_q = Pos_Q  
        new_neg_q = Neg_Q_psse
    if scale_method == 1:
        new_pos_q = Pos_Q * (1 + i_ratio)
        new_neg_q = Neg_Q_psse * (1 + i_ratio)
    psspy.bsys(8,0,[0.0, 500.],0,[],len(POS_b[0]),POS_b[0],0,[],0,[])
    psspy.bsys(8,0,[0.0, 500.],0,[],len(POS_b[0]),POS_b[0],0,[],0,[])
    psspy.scal_2(8,0,1,[0,0,0,0,0],[0.0,0.0,0.0,0.0,0.0,0.0,0.0])
    psspy.scal_2(8,1,2,[_i,1,0,scale_method,0],[ new_pos_p,_f,_f,_f,_f,_f, new_pos_q])
    if len(NEG_b[0]) > 0: 
        psspy.bsys(9,0,[0.0, 500.],0,[],len(NEG_b[0]),NEG_b[0],0,[],0,[]) # NEG SUB
        psspy.bsys(9,0,[0.0, 500.],0,[],len(NEG_b[0]),NEG_b[0],0,[],0,[]) # NEG SUB     
        psspy.scal_2(9,0,1,[0,0,0,0,0],[0.0,0.0,0.0,0.0,0.0,0.0,0.0])
        psspy.scal_2(9,1,2,[_i,1,0,scale_method,0],[ new_neg_p,_f,_f,_f,_f,_f, new_neg_q])