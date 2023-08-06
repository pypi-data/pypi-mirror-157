        Se = T__ * V(:,modes)
        sid.modes = modes
    else:
        Se = T__
    
    #  Se= T__;
    nq = Se.shape[2-1]
    # (6.479) S. 367
    mE = np.transpose(St) * MF * St
    I0 = np.transpose(Sr) * MF * Sr
    Me = np.transpose(Se) * MF * Se
    mc0 = np.transpose(Sr) * MF * St
    Ct0 = np.transpose(Se) * MF * St
    
    Ct0_ = np.transpose(T__) * MF * St
    
    Cr0 = np.transpose(Se) * MF * Sr
    C3 = cell(ne,1)
    for e in np.arange(1,ne+1).reshape(-1):
        le = data(e).l
        if isfield(data,'A') and isfield(data,'rho'):
            me01 = getElementValue(data,e,'A') * le * data(e).rho
        else:
            if isfield(data,'mu'):
                me01 = getElementValue(data,e,'mu') * le
            else:
                me01 = getElementValue(data,e,'me')
        me0 = me01(1)
        me1 = me01(2)
        C3[e] = cell(3,3)
        C3[e][1,1] = np.array([[np.array([(me1 + 3 * me0) / 12,0,0,0,0,0,(me1 + me0) / 12,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([(me1 + me0) / 12,0,0,0,0,0,(3 * me1 + me0) / 12,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])]])
        C3[e][1,2] = np.array([[np.array([0,(5 * me1 + 16 * me0) / 60,0,0,0,(le * me1 + 2 * le * me0) / 60,0,(5 * me1 + 4 * me0) / 60,0,0,0,- (le * me1 + le * me0) / 60])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,(4 * me1 + 5 * me0) / 60,0,0,0,(le * me1 + le * me0) / 60,0,(16 * me1 + 5 * me0) / 60,0,0,0,- (2 * le * me1 + le * me0) / 60])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])]])
        C3[e][1,3] = np.array([[np.array([0,0,(5 * me1 + 16 * me0) / 60,0,- (le * me1 + 2 * le * me0) / 60,0,0,0,(5 * me1 + 4 * me0) / 60,0,(le * me1 + le * me0) / 60,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,(4 * me1 + 5 * me0) / 60,0,- (le * me1 + le * me0) / 60,0,0,0,(16 * me1 + 5 * me0) / 60,0,(2 * le * me1 + le * me0) / 60,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])]])
        C3[e][2,1] = np.array([[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([(5 * me1 + 16 * me0) / 60,0,0,0,0,0,(4 * me1 + 5 * me0) / 60,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([(le * me1 + 2 * le * me0) / 60,0,0,0,0,0,(le * me1 + le * me0) / 60,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([(5 * me1 + 4 * me0) / 60,0,0,0,0,0,(16 * me1 + 5 * me0) / 60,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([- (le * me1 + le * me0) / 60,0,0,0,0,0,- (2 * le * me1 + le * me0) / 60,0,0,0,0,0])]])
        C3[e][2,2] = np.array([[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,(3 * me1 + 10 * me0) / 35,0,0,0,(7 * le * me1 + 15 * le * me0) / 420,0,(9 * me1 + 9 * me0) / 140,0,0,0,- (6 * le * me1 + 7 * le * me0) / 420])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,(7 * le * me1 + 15 * le * me0) / 420,0,0,0,(3 * le ** 2 * me1 + 5 * le ** 2 * me0) / 840,0,(7 * le * me1 + 6 * le * me0) / 420,0,0,0,- (le ** 2 * me1 + le ** 2 * me0) / 280])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,(9 * me1 + 9 * me0) / 140,0,0,0,(7 * le * me1 + 6 * le * me0) / 420,0,(10 * me1 + 3 * me0) / 35,0,0,0,- (15 * le * me1 + 7 * le * me0) / 420])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,- (6 * le * me1 + 7 * le * me0) / 420,0,0,0,- (le ** 2 * me1 + le ** 2 * me0) / 280,0,- (15 * le * me1 + 7 * le * me0) / 420,0,0,0,(5 * le ** 2 * me1 + 3 * le ** 2 * me0) / 840])]])
        C3[e][2,3] = np.array([[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,(3 * me1 + 10 * me0) / 35,0,- (7 * le * me1 + 15 * le * me0) / 420,0,0,0,(9 * me1 + 9 * me0) / 140,0,(6 * le * me1 + 7 * le * me0) / 420,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,(7 * le * me1 + 15 * le * me0) / 420,0,- (3 * le ** 2 * me1 + 5 * le ** 2 * me0) / 840,0,0,0,(7 * le * me1 + 6 * le * me0) / 420,0,(le ** 2 * me1 + le ** 2 * me0) / 280,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,(9 * me1 + 9 * me0) / 140,0,- (7 * le * me1 + 6 * le * me0) / 420,0,0,0,(10 * me1 + 3 * me0) / 35,0,(15 * le * me1 + 7 * le * me0) / 420,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,- (6 * le * me1 + 7 * le * me0) / 420,0,(le ** 2 * me1 + le ** 2 * me0) / 280,0,0,0,- (15 * le * me1 + 7 * le * me0) / 420,0,- (5 * le ** 2 * me1 + 3 * le ** 2 * me0) / 840,0])]])
        C3[e][3,1] = np.array([[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([(5 * me1 + 16 * me0) / 60,0,0,0,0,0,(4 * me1 + 5 * me0) / 60,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([- (le * me1 + 2 * le * me0) / 60,0,0,0,0,0,- (le * me1 + le * me0) / 60,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([(5 * me1 + 4 * me0) / 60,0,0,0,0,0,(16 * me1 + 5 * me0) / 60,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([(le * me1 + le * me0) / 60,0,0,0,0,0,(2 * le * me1 + le * me0) / 60,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])]])
        C3[e][3,2] = np.array([[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,(3 * me1 + 10 * me0) / 35,0,0,0,(7 * le * me1 + 15 * le * me0) / 420,0,(9 * me1 + 9 * me0) / 140,0,0,0,- (6 * le * me1 + 7 * le * me0) / 420])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,- (7 * le * me1 + 15 * le * me0) / 420,0,0,0,- (3 * le ** 2 * me1 + 5 * le ** 2 * me0) / 840,0,- (7 * le * me1 + 6 * le * me0) / 420,0,0,0,(le ** 2 * me1 + le ** 2 * me0) / 280])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,(9 * me1 + 9 * me0) / 140,0,0,0,(7 * le * me1 + 6 * le * me0) / 420,0,(10 * me1 + 3 * me0) / 35,0,0,0,- (15 * le * me1 + 7 * le * me0) / 420])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,(6 * le * me1 + 7 * le * me0) / 420,0,0,0,(le ** 2 * me1 + le ** 2 * me0) / 280,0,(15 * le * me1 + 7 * le * me0) / 420,0,0,0,- (5 * le ** 2 * me1 + 3 * le ** 2 * me0) / 840])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])]])
        C3[e][3,3] = np.array([[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,(3 * me1 + 10 * me0) / 35,0,- (7 * le * me1 + 15 * le * me0) / 420,0,0,0,(9 * me1 + 9 * me0) / 140,0,(6 * le * me1 + 7 * le * me0) / 420,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,- (7 * le * me1 + 15 * le * me0) / 420,0,(3 * le ** 2 * me1 + 5 * le ** 2 * me0) / 840,0,0,0,- (7 * le * me1 + 6 * le * me0) / 420,0,- (le ** 2 * me1 + le ** 2 * me0) / 280,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,(9 * me1 + 9 * me0) / 140,0,- (7 * le * me1 + 6 * le * me0) / 420,0,0,0,(10 * me1 + 3 * me0) / 35,0,(15 * le * me1 + 7 * le * me0) / 420,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,(6 * le * me1 + 7 * le * me0) / 420,0,- (le ** 2 * me1 + le ** 2 * me0) / 280,0,0,0,(15 * le * me1 + 7 * le * me0) / 420,0,(5 * le ** 2 * me1 + 3 * le ** 2 * me0) / 840,0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])]])
        # not 100# sure if this is correct
        if isfield(data,'Mlumped'):
            C3[e][1,1][1,1] = C3[e][1,1](1,1) + data(e).Mlumped
            C3[e][2,2][2,2] = C3[e][2,2](2,2) + data(e).Mlumped
            C3[e][3,3][3,3] = C3[e][3,3](3,3) + data(e).Mlumped
            if e == ne:
                C3[e][1,1][1 + 6,1 + 6] = C3[e][1,1](1 + 6,1 + 6) + data(e + 1).Mlumped
                C3[e][2,2][2 + 6,2 + 6] = C3[e][2,2](2 + 6,2 + 6) + data(e + 1).Mlumped
                C3[e][3,3][3 + 6,3 + 6] = C3[e][3,3](3 + 6,3 + 6) + data(e + 1).Mlumped
    
    # (5.252) S. 233, (6.401) S. 338
    KFr = cell(3,1)
    Kr = cell(3,1)
    for a in np.arange(1,3+1).reshape(-1):
        KFr[a] = np.zeros((nF,nF))
        for e in np.arange(1,ne+1).reshape(-1):
            lmn = np.arange(1,3+1)
            for l in np.arange(1,3+1).reshape(-1):
                m = lmn(2)
                n = lmn(3)
                KFr[a] = KFr[a] + np.transpose(T[e]) * (- C3[e][m,n] + C3[e][n,m]) * T[e] * Gamma[e](l,a)
                lmn = circshift(lmn,np.array([0,- 1]))
        # (6.483) S. 367
        Kr[a] = np.transpose(Se) * KFr[a] * Se
    
    ZF0 = np.zeros((nF,1))
    for k in np.arange(1,nk+1).reshape(-1):
        ZF0[np.arange[[nqk * [k - 1] + 1],[nqk * [k - 1] + 3]+1],1] = data(k).x
    
    # alternative Formulation for Cr0
#  CFr0= [KFr{1}*ZF0 KFr{2}*ZF0 KFr{3}*ZF0];
    
    # (5.268) S. 237
    KFom_ab = cell(3,3)
    
    for a in np.arange(1,3+1).reshape(-1):
        for b in np.arange(1,3+1).reshape(-1):
            KFom_ab[a,b] = np.zeros((nF,nF))
            for l in np.arange(1,3+1).reshape(-1):
                for m in np.arange(1,3+1).reshape(-1):
                    for e in np.arange(1,ne+1).reshape(-1):
                        if l == m:
                            m_ = l + 1
                            if m_ > 3:
                                m_ = 1
                            n_ = m_ + 1
                            if n_ > 3:
                                n_ = 1
                            # (5.266) S. 236
                            Xi = - (C3[e][m_,m_] + C3[e][n_,n_])
                        else:
                            Xi = C3[e][m,l]
                        KFom_ab[a,b] = KFom_ab[a,b] + np.transpose(T[e]) * Gamma[e](l,a) * Xi * Gamma[e](m,b) * T[e]
    
    # (5.271) S. 237
    KFom = cell(6,1)
    Kom = cell(6,1)
    Kom0 = np.zeros((nq,6))
    Kom0_ = np.zeros((nq_,6))
    for i in np.arange(1,6+1).reshape(-1):
        if i < 4:
            KFom[i] = KFom_ab[i,i]
        else:
            a = i - 3
            b = a + 1
            if b > 3:
                b = 1
            KFom[i] = KFom_ab[a,b] + np.transpose(KFom_ab[a,b])
        Kom[i] = np.transpose(Se) * KFom[i] * Se
        Kom0[:,i] = np.transpose(Se) * KFom[i] * ZF0
        Kom0_[:,i] = np.transpose(T__) * KFom[i] * ZF0
    
    # (6.490) S. 368; (6.531) S. 379 or (6.515) S. 375
    C4 = np.zeros((3,3,nq))
    for l in np.arange(1,nq+1).reshape(-1):
        for a in np.arange(1,3+1).reshape(-1):
            for b in np.arange(1,3+1).reshape(-1):
                C4[a,b,l] = - np.transpose(Sr(:,a)) * KFr[b] * Se(:,l)
    
    Kinv = T__ * KF__ ** - 1 * np.transpose(T__)
    # only axial stiffening
# 6.330 S. 319
    Fend_ax = np.zeros((nF,1))
    Fend_ax[end() - nqk + extentIdx,1] = 1
    
    K0Fend_ax = np.transpose(Se) * geo_stiff(ne,nF,nqk,data,T,- Kinv * Fend_ax) * Se
    K0t_ax = np.transpose(Se) * geo_stiff(ne,nF,nqk,data,T,- Kinv * T__ * Ct0_(:,extentIdx)) * Se
    K0omxx = np.transpose(Se) * geo_stiff(ne,nF,nqk,data,T,- Kinv * T__ * Kom0_(:,1)) * Se
    K0omyy = np.transpose(Se) * geo_stiff(ne,nF,nqk,data,T,- Kinv * T__ * Kom0_(:,2)) * Se
    K0omzz = np.transpose(Se) * geo_stiff(ne,nF,nqk,data,T,- Kinv * T__ * Kom0_(:,3)) * Se
    K0omxy = np.transpose(Se) * geo_stiff(ne,nF,nqk,data,T,- Kinv * T__ * Kom0_(:,4)) * Se
    K0omxz = np.transpose(Se) * geo_stiff(ne,nF,nqk,data,T,- Kinv * T__ * Kom0_(:,5)) * Se
    K0omyz = np.transpose(Se) * geo_stiff(ne,nF,nqk,data,T,- Kinv * T__ * Kom0_(:,6)) * Se
    # idx_t= [ones(3, ne); zeros(3, ne)];
# idx_t= logical(idx_t(:));
# idx_r= [zeros(3, ne); ones(3, ne)];
# idx_r= logical(idx_r(:));
    
    if isunix:
        __,user_name = system('whoami')
        # on my mac, isunix == 1
    else:
        if ispc:
            __,user_name = system('echo %USERDOMAIN%\%USERNAME%')
            # found it on the net elsewhere, you might want to verify
    
    user_name = user_name.replace(char(10),'')
    if ('modes' is not None):
        sid.comment = sprintf('%d nodes, %d modes, generated by FEMBeam2SID MATLAB script on %s by %s',nk,nq,datestr(now),user_name)
    else:
        sid.comment = sprintf('%d nodes, %d coordinates, generated by FEMBeam2SID MATLAB script on %s by %s',nk,nq,datestr(now),user_name)
    
    # Tabelle 6.9 S. 346
#  sid.refmod # Masse und Name der Koordinaten q_i
    sid.refmod.mass = mE(1)
    
    sid.refmod.nelastq = nq
    
    coord_name = np.array(['ux','uy','uz','rx','ry','rz'])
    if ('modes' is not None):
        for i in np.arange(1,nq+1).reshape(-1):
            sid.refmod.ielastq[i] = sprintf('Eigen Mode %4d : %13f Hz',modes(i),EF(i))
    else:
        for i in np.arange(1,nq+1).reshape(-1):
            iq = find(T__(:,i),1)
            in_ = np.ceil(iq / 6)
            ic = iq - (in_ - 1) * 6
            sid.refmod.ielastq[i] = sprintf('Node %4d, %s',in_,coord_name[ic])
    
    # sid.frame # Daten zur Berechnung der Bewegung von
    for i in np.arange(1,nk+1).reshape(-1):
        sid.frame(i).node = num2str(i)
        sid.frame(i).rframe = 'body ref'
        Phi = np.zeros((3,nF))
        Phi[:,[i - 1] * nqk + [np.arange[1,3+1]]] = np.eye(3)
        Psi = np.zeros((3,nF))
        Psi[:,[i - 1] * nqk + [np.arange[4,6+1]]] = np.eye(3)
        sid.frame(i).origin = emptyTaylor(1,3,1,nq,0,3)
        sid.frame(i).origin.M0 = data(i).x
        for j in np.arange(1,nq+1).reshape(-1):
            sid.frame[i].origin.M1[:,1,j] = Phi * Se(:,j)
        sid.frame(i).Phi = emptyTaylor(0,3,nq,nq,0,3)
        sid.frame(i).Phi.M0 = Phi * Se
        if i == nk:
            sid.frame(i).Phi.order = 1
            sid.frame[i].Phi.M1[1,:,:] = 0 * K0Fend_ax
            sid.frame[i].Phi.M1[2,:,:] = 0 * K0Fend_ax
            sid.frame[i].Phi.M1[3,:,:] = 0 * K0Fend_ax
            sid.frame[i].Phi.M1[extentIdx,:,:] = K0Fend_ax
        sid.frame(i).Psi = emptyTaylor(0,3,nq,nq,0,3)
        sid.frame(i).Psi.M0 = Psi * Se
        #      sid.frame(i).Psi.M1= 0; # no geometric stiffening due to moments for now
        sid.frame(i).AP = emptyTaylor(1,3,3,nq,0,3)
        if i == nk:
            sid.frame(i).AP.M0 = data(i - 1).D
        else:
            sid.frame(i).AP.M0 = data(i).D
        for j in np.arange(1,nq+1).reshape(-1):
            sid.frame[i].AP.M1[:,:,j] = crossmat(sid.frame(i).Psi.M0(:,j))
        sid.frame(i).sigma = emptyTaylor(1,6,1,nq,0,3)
        sid.frame(i).sigma.M0 = np.zeros((6,1))
        if i < nk:
            e = i
        else:
            e = i - 1
        Ke = np.transpose(T[e]) * K[e] * T[e]
        if i < nk:
            Ke = - Ke
        for j in np.arange(1,nq+1).reshape(-1):
            sid.frame[i].sigma.M1[:,1,j] = Ke((i - 1) * nqk + (np.arange(1,6+1)),:) * Se(:,j)
    
    # sid.mdCM
    sid.md = emptyTaylor(1,3,1,nq,0,3)
    sid.md.M0 = np.transpose(np.array([sum(sum(np.multiply(crossmat(np.array([0.5,0,0])),mc0))),sum(sum(np.multiply(crossmat(np.array([0,0.5,0])),mc0))),sum(sum(np.multiply(crossmat(np.array([0,0,0.5])),mc0)))]))
    for j in np.arange(1,nq+1).reshape(-1):
        sid.md.M1[:,1,j] = np.transpose(Ct0(j,:))
    
    # sid.J
    sid.I = emptyTaylor(1,3,3,nq,0,2)
    sid.I.M0 = I0
    for i in np.arange(1,nq+1).reshape(-1):
        sid.I.M1[:,:,i] = - C4(:,:,i) - np.transpose(C4(:,:,i))
    
    # sid.Ct
    sid.Ct = emptyTaylor(1,nq,3,nq,0,3)
    sid.Ct.M0 = Ct0
    sid.Ct.M1[:,1,:] = 0 * K0t_ax
    sid.Ct.M1[:,2,:] = 0 * K0t_ax
    sid.Ct.M1[:,3,:] = 0 * K0t_ax
    sid.Ct.M1[:,extentIdx,:] = K0t_ax
    # sid.Cr
    sid.Cr = emptyTaylor(1,nq,3,nq,0,3)
    sid.Cr.M0 = Cr0
    sid.Cr.M1[:,1,:] = Kr[0]
    
    sid.Cr.M1[:,2,:] = Kr[2]
    
    sid.Cr.M1[:,3,:] = Kr[3]
    
    # sid.Me
    sid.Me = emptyTaylor(0,nq,nq,0,0,2)
    sid.Me.M0 = Me
    # sid.Gr
    sid.Gr = emptyTaylor(0,3,3 * nq,nq,0,3)
    sid.Gr.M0 = - 2 * reshape(C4,3,3 * nq)
    
    #  sid.Gr.M1
# sid.Ge
    sid.Ge = emptyTaylor(0,nq,3 * nq,0,0,3)
    for i in np.arange(1,nq+1).reshape(-1):
        sid.Ge.M0[:,3 * [i - 1] + [np.arange[1,3+1]]] = 2 * np.array([Kr[0](:,i),Kr[2](:,i),Kr[3](:,i)])
    
    #  sid.Oe (6.407)
    sid.Oe = emptyTaylor(1,nq,6,nq,0,3)
    sid.Oe.M0 = Kom0
    sid.Oe.M1[:,1,:] = Kom[0] + K0omxx
    sid.Oe.M1[:,2,:] = Kom[2] + K0omyy
    sid.Oe.M1[:,3,:] = Kom[3] + K0omzz
    sid.Oe.M1[:,4,:] = Kom[4] + K0omxy
    sid.Oe.M1[:,5,:] = Kom[5] + K0omxz
    sid.Oe.M1[:,6,:] = Kom[6] + K0omyz
    #  sid.ksigma
#  sid.ksigma.M0= zeros(size(V, 2), 1); # no pretension for now
#  sid.ksigma.M1= zeros(size(V, 2));
    
    #  sid.Ke
    sid.Ke = emptyTaylor(0,nq,nq,0,0,2)
    sid.Ke.M0 = np.transpose(Se) * KF * Se
    # sid.Ke.M1
    sid.ksigma = emptyTaylor(0,nq,1,nq,0,0)
    sid.ksigma.M0 = []
    sid.De = emptyTaylor(0,nq,nq,0,0,0)
    sid.De.M0 = []
    sid.EF = EF
    
def geo_stiff(ne = None,nF = None,nqk = None,data = None,T = None,zF = None): 
    # Spannung: 5.220 S. 226,  Beispiel: 5.287 S. 241
# E*BL : Spannung, (6.311) S. 312 [(6.259) S. 301, (6.300) S. 309]
# K^-1 : Verformung aus (Einheits-)Kraft
# z.B. C4(:, 3) : Einheitskraft
# E bzw. H macht aus Dehnung Spannung
# BL macht aus Knotenkoordinaten Dehnung (eps_xx)
# E bzw. H und BL sind schon in K_G1_ux1 + K_G1_ux2 enthalten
    
    KFsigma_sharp = np.zeros((nF,nF))
    for e in np.arange(1,ne+1).reshape(-1):
        le = data(e).l
        if isfield(data,'E'):
            E = data(e).E
        else:
            E = 214000000000.0
        if isfield(data,'A'):
            A01 = getElementValue(data,e,'A')
        else:
            if isfield(data,'EA'):
                A01 = getElementValue(data,e,'EA') / E
            else:
                A01 = np.array([100,100])
        A0 = A01(1)
        A1 = A01(2)
        K_Ge_ux1_lin = np.array([[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,- ((3 * A1 + 3 * A0) * E) / (5 * le ** 2),0,0,0,- (A1 * E) / (10 * le),0,((3 * A1 + 3 * A0) * E) / (5 * le ** 2),0,0,0,- (A0 * E) / (10 * le)])],[np.array([0,0,- ((3 * A1 + 3 * A0) * E) / (5 * le ** 2),0,(A1 * E) / (10 * le),0,0,0,((3 * A1 + 3 * A0) * E) / (5 * le ** 2),0,(A0 * E) / (10 * le),0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,(A1 * E) / (10 * le),0,- ((A1 + 3 * A0) * E) / 30,0,0,0,- (A1 * E) / (10 * le),0,((A1 + A0) * E) / 60,0])],[np.array([0,- (A1 * E) / (10 * le),0,0,0,- ((A1 + 3 * A0) * E) / 30,0,(A1 * E) / (10 * le),0,0,0,((A1 + A0) * E) / 60])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,((3 * A1 + 3 * A0) * E) / (5 * le ** 2),0,0,0,(A1 * E) / (10 * le),0,- ((3 * A1 + 3 * A0) * E) / (5 * le ** 2),0,0,0,(A0 * E) / (10 * le)])],[np.array([0,0,((3 * A1 + 3 * A0) * E) / (5 * le ** 2),0,- (A1 * E) / (10 * le),0,0,0,- ((3 * A1 + 3 * A0) * E) / (5 * le ** 2),0,- (A0 * E) / (10 * le),0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,(A0 * E) / (10 * le),0,((A1 + A0) * E) / 60,0,0,0,- (A0 * E) / (10 * le),0,- ((3 * A1 + A0) * E) / 30,0])],[np.array([0,- (A0 * E) / (10 * le),0,0,0,((A1 + A0) * E) / 60,0,(A0 * E) / (10 * le),0,0,0,- ((3 * A1 + A0) * E) / 30])]])
        K_Ge_ux2_lin = np.array([[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,((3 * A1 + 3 * A0) * E) / (5 * le ** 2),0,0,0,(A1 * E) / (10 * le),0,- ((3 * A1 + 3 * A0) * E) / (5 * le ** 2),0,0,0,(A0 * E) / (10 * le)])],[np.array([0,0,((3 * A1 + 3 * A0) * E) / (5 * le ** 2),0,- (A1 * E) / (10 * le),0,0,0,- ((3 * A1 + 3 * A0) * E) / (5 * le ** 2),0,- (A0 * E) / (10 * le),0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,- (A1 * E) / (10 * le),0,((A1 + 3 * A0) * E) / 30,0,0,0,(A1 * E) / (10 * le),0,- ((A1 + A0) * E) / 60,0])],[np.array([0,(A1 * E) / (10 * le),0,0,0,((A1 + 3 * A0) * E) / 30,0,- (A1 * E) / (10 * le),0,0,0,- ((A1 + A0) * E) / 60])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,- ((3 * A1 + 3 * A0) * E) / (5 * le ** 2),0,0,0,- (A1 * E) / (10 * le),0,((3 * A1 + 3 * A0) * E) / (5 * le ** 2),0,0,0,- (A0 * E) / (10 * le)])],[np.array([0,0,- ((3 * A1 + 3 * A0) * E) / (5 * le ** 2),0,(A1 * E) / (10 * le),0,0,0,((3 * A1 + 3 * A0) * E) / (5 * le ** 2),0,(A0 * E) / (10 * le),0])],[np.array([0,0,0,0,0,0,0,0,0,0,0,0])],[np.array([0,0,- (A0 * E) / (10 * le),0,- ((A1 + A0) * E) / 60,0,0,0,(A0 * E) / (10 * le),0,((3 * A1 + A0) * E) / 30,0])],[np.array([0,(A0 * E) / (10 * le),0,0,0,- ((A1 + A0) * E) / 60,0,- (A0 * E) / (10 * le),0,0,0,((3 * A1 + A0) * E) / 30])]])
        ux = T[e] * zF
        KFsigma_sharp_e = K_Ge_ux1_lin * ux(1) + K_Ge_ux2_lin * ux(1 + 6)
        # 5.208 S. 222
        KFsigma_sharp = KFsigma_sharp + np.transpose(T[e]) * KFsigma_sharp_e * T[e]
    
    
def emptyTaylor(order = None,nrow = None,ncol = None,nq = None,nqn = None,str = None): 
    t.order = order
    t.nrow = nrow
    t.ncol = ncol
    t.nq = nq
    t.nqn = nqn
    t.structure = str
