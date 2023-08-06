

#########################################################################################
#########################################################################################
def getInduction(ngrid, sWT, Format, U0,meta,):
    """Function that compute the axial induction distribution for subsequent use in the Ainslie wake flow model

        Inputs
        ----------
        ngrid (int): number of grid point per radius in BEM
        sWT (string): turbine name
        Format (string) : input file format (HAWC2)
        U0: mean hub height velocity
        meta (instance of class): Instance of class Meta holding DWM core variables

        Outputs
        ----------
        BEM (instnce of class) : refer to class description for details
    """


    # Initialization
    # if Format is
    PcDataAll, AeData, Rotor, Env, Spec, Algo, Misc = fInitWT(sWT, Format, meta.path_to_wt)
    Rotor = fSetRotorGrid(ngrid, Rotor)

    Pd=meta.WTG_spec.P_rated *1000.
    RPM=np.interp(U0,Spec.WS,Spec.RPM)
    Pitch=np.interp(U0,Spec.WS,Spec.Pitch)

    #print '***', Pitch
    Sim = InitSim()
    parSim = {'Name': sWT,
          'WT': sWT,
          'WS': U0,
          'RPM': RPM,
          'PITCH': Pitch}
    Sim.Set(**parSim)
    # print Spec.RPM



    Wind = InitWind()
    parWind = {'V0': np.array([0., 0., U0])}
    Wind.Set(**parWind)


    if U0 >= 0.80 * meta.WTG_spec.u_rated:
        x0 = np.interp(U0, Spec.WS, Spec.Pitch) * 1.5  # init the init pitch vector
        # x0 = Pitch*1.5 # init the init pitch vector
        # print x0
        # x=fmin_cobyla(objective , x0,cons=[constr1,], args=(WT, Sim, Wind, Algo, Rotor, PcDataAll, Env, Spec, State, Misc,Pd),consargs=(derating,), rhobeg=0.05, rhoend=0.000001, iprint=1, maxfun=1000, disp=1, catol=0.002)
        x = fmin_cobyla(objective, x0, cons=[], args=(Sim, Wind, Algo, Rotor, PcDataAll, Env, Spec, Misc, Pd),
                        consargs=None, rhobeg=0.5, rhoend=0.001, iprint=0, maxfun=1000, disp=0, catol=0.002)
        # x=fFindPitch(WT, Sim, Wind, Algo, Rotor, PcDataAll, Env, Spec, State, Misc,Pd)
        # print 'Python Pitch from cobyla is', x
        # print 'Interpolated pitch is', Pitch
        Sim.PITCH = x


    Algo = InitAlgo()
    BEM = fBEMsteady( Sim, Wind, Algo, Rotor, PcDataAll, Env, Spec, Misc)

    ################################################################
    ################################################################
    return BEM
#########################################################################################
#########################################################################################

def objective(x, Sim, Wind, Algo, Rotor, PcDataAll, Env, Spec, Misc,Pd):
    Sim.PITCH=x
    BEM=fBEMsteady( Sim, Wind, Algo, Rotor, PcDataAll, Env, Spec,  Misc)
    #print 'BEM.Power-Pd',BEM.Power-Pd
    #print 'SIM.PITCH', Sim.PITCH
    return abs(BEM.Power-Pd)
    # return abs(Ptot-Prated) # maximize power by derating

def constr1(x,derating):
    return x
#
# def constr2(x,*args):
#     return np.min(x - 0.05*np.ones_like(x))

#########################################################################################
#########################################################################################
def getTorqueFromBlade(r0, Pt0, R):
    """Function that estimates the aerodynamic torque

        Inputs
        ----------
        r0: discrete radial position of blade [m]
        Pt0: tangential load in N
        R: blade radius [m]

        Outputs
        ----------
        Q: aerodynamic torque [Nm]
    """
    n = len(r0)
    r = np.zeros((n + 1))
    Pt = np.zeros((n + 1))
    r[0:n] = r0
    r[-1] = R
    Pt[0:n] = Pt0
    Q = np.trapz(r * Pt,r )
    return Q
#########################################################################################
#########################################################################################
def getThrustFromBlade(r0, Pn0, R):
    """Function that estimates the thrust force

        Inputs
        ----------
        r0: discrete radial position of blade [m]
        Pn0: normal load in N
        R: blade radius [m]

        Outputs
        ----------
        T: aerodynamic thrust [N]
    """
    n = len(r0)
    r = np.zeros((n + 1))
    Pn = np.zeros((n + 1))
    r[0:n] = r0
    r[-1] = R
    Pn[0:n] = Pn0
    T = np.trapz(Pn,r)
    return T
#########################################################################################
#########################################################################################
def fInductionCoefficients(a_last, Vrel_norm, Un, Ut, V0_in3, V0_in4, nW_in4, omega, chord, F, Ftip, CnForAI, CtForTI,
                           lambda_r, sigma, phi, Algo):
    """Function that compute the induction coefficients while applying swirl

        Inputs
        ----------
        a_last (float) : last iteration axial induction factor
        Vrel_norm (float): normed relative velocity
        Un (float): normal velocity
        Ut (float): tangential velocity
        V0_in3 (float): [0., 0., V0]
        V0_in4 (float): [0., 0., V0]
        nW_in4 (float): [0., 0., -a_last * V0]
        omega (float): rotor rotational speed rad/s
        chord (float): rotor chord length distribution
        F (float): total loss
        Ftip (float): tip loss
        CnForAI (float): normal force coefficient
        CtForTI (float): tangential force coefficient
        lambda_r (float): speed ratio distribution
        sigma (float): blade solidity
        phi (float): flow angle
        Algo (instance of class): holds algorith BEM related parameters

        Outputs
        ----------
        a: axial induction factor
        aprime: tangential induction factor
        CT_loc: local thrust coefficient
    """
    a = 1. / ((4. * F * sin(phi * pi / 180.) ** 2) / (sigma * CnForAI) + 1.)
    # Thrust coefficient from the momentum theory => alast
    # CT=(1-a_last).^2.*sigma.*CnForAI./((sind(phi)).^2)
    CT_loc = np.linalg.norm(Vrel_norm) ** 2 * sigma * CnForAI / (np.linalg.norm(V0_in3) ** 2)  # that's a CT loc
    # --------------------------------------------------------------------------------
    # --- Hight thrust correction
    # --------------------------------------------------------------------------------
    a, CT_loc = fCorrectionHighThrust(Algo.CTcorrection, a, CnForAI, phi, a_last, sigma, F, Ftip, CT_loc)
    a = a * Algo.relaxation + (1. - Algo.relaxation) * a_last

    if Algo.bSwirl is True:
        aprime = 1. / ((4. * F * sin(phi * pi / 180.) * cos(phi * pi / 180.)) / (sigma * CtForTI) - 1.)
        if Algo.SwirlMethod == 'HAWC':
            aprime = (np.linalg.norm(Vrel_norm) ** 2 * CtForTI * sigma) / (
                4. * (1. - a) * np.linalg.norm(V0_in4) ** 2 * lambda_r)
        else:
            raise Exception('Method not implemented')
    else:
        aprime = a * 0.

    return a, aprime, CT_loc
#########################################################################################
#########################################################################################
def fCorrectionHighThrust(CTcorrection, a, CnForAI, phi, a_last, sigma, F, Ftip, CT_loc):
    """Function that applying high thrust coefficient correction

        Inputs
        ----------
        CTcorrection (string) : type of high thrust coefficient
        a (float): axial induction coefficient
        CnForAI: normal force coefficient
        phi: flow angle
        a_last: last iteration axial induction
        sigma: blade solidity
        F: total losses
        Ftip: tip losses
        CT_loc: local thrust coefficient

        Outputs
        ----------
        a: axial induction factor
        CT_loc: local thrust coefficient
    """
    if CTcorrection == 'GlauertCT':
        ac = 0.3
        if (a > ac):
            fg = 0.25 * (5. - 3. * a)
            a = CT_loc / (4. * F * (1. - fg * a))
    elif CTcorrection == False:
        pass
    else:
        raise Exception('CT correction not implemented')
    return a, CT_loc
#########################################################################################
#########################################################################################
def fAeroCoeffWrap(Rotor, PcDataAll, e, alpha, phi, chord, Vrel_norm, Re, Fperf, Algo, Misc):
    """Tabulated airfoil data interpolation

        Inputs
        ----------
        Rotor (instance of class) holds rotor related parameter
        PcDataAll (array of float) holds the profile coefficient Cm, Cl, Cd and AoA
        e : element index in BEM loop
        alpha: Angle Of Attack
        phi: flow angle
        chord: chord length
        Vrel_norm: normed relative velocity
        Re: Reynolds number
        Fperf: performance losses (not implemented)
        Algo (instance of class) holds alogrithm BEM related parameter
        Misc (instance of class) holds I/O parameters

        Outputs
        ----------
        Cl: lift coefficient
        Cd: drag coefficient
        Cn: normal coefficient
        Ct: tangential coefficient
        CnForAI: normal coefficient for correction
        CtForTI: tangential coefficient for correction
    """
    ne = 1
    Cl = [];    Cd = []

    if Misc.Format == 'flex':
        ee = int(Rotor.ProfileSet[1, e])
        # print ee
        Cd = np.interp(alpha, PcDataAll[ee - 1][:, 0], PcDataAll[ee - 1][:, 2])
        if Algo.bDynaStall == True:
            raise Exception('Not implemented')
        else:
            Cl = np.interp(alpha, PcDataAll[ee - 1][:, 0], PcDataAll[ee - 1][:, 1])
    else:
        ClCdCm = fAeroCoeff(alpha, PcDataAll, Rotor.ProfileSet[:, e], Rotor.Profile_thickness_rel,
                            Rotor.thickness_rel[e], Re, Algo.bReInterp, Algo.bThicknessInterp, Algo.bRoughProfiles)
        Cl = ClCdCm[0]
        Cd = ClCdCm[1]
        # print ClCdCm
    # Normal and tangential
    CnNoDrag = Cl * cos(phi * pi / 180.)
    CtNoDrag = Cl * sin(phi * pi / 180.)
    Cn = Cl * cos(phi * pi / 180.) + Cd * sin(phi * pi / 180.)
    Ct = Cl * sin(phi * pi / 180.) - Cd * cos(phi * pi / 180.)
    # performance correction on Cn Ct
    Cn = Fperf * Cn
    Ct = Fperf * Ct
    if (Algo.bAIDrag):
        CnForAI = Cn
    else:
        CnForAI = Fperf * CnNoDrag

    if (Algo.bTIDrag):
        CtForTI = Ct
    else:
        CtForTI = CtNoDrag
    return Cl, Cd, Cn, Ct, CnForAI, CtForTI

def fAeroCoeff(alpha, PcDataAll, ProfileSet, Profile_thickness_rel, rel_thickness, Re, bReInterp, bThicknessInterp,
               bRough):
    """Function that interpolates in the profile coefficients tabulated airfoil data

        Inputs
        ----------
        alpha: angle of attack deg
        PcDataAll: array holding all profile coefficients
        ProfileSet: index of profile set coefficients for interpolation
        Profile_thickness_rel: relative thickness of each of the profile coeff sets
        rel_thickness: rel thickness at the point of interpolation
        Re: Reynolds number
        bReInterp: Reynolds number interpolation flag
        bThicknessInterp: Thickness interpolation flag
        bRoughs: Roughness profile interpolation flag

        Outputs
        ----------
        ClCdCm (float): vector containing the Cl, Cd and Cm values at interpolation point
    """

    if bRough:
        raise Exception('Rough profile are not implemented yet')
    else:
        Data = PcDataAll
    ClCdCm = np.zeros((3))
    temp = np.zeros((3, 3))
    ii1 = int(ProfileSet[1])
    ii2 = int(ProfileSet[2])
    if bReInterp:
        raise Exception('Reynolds interpolation not implemented yet')
    else:
        if ProfileSet[0] == 1:
            for j in np.arange(1, 4, 1):
                ClCdCm[j - 1] = np.interp(alpha, PcDataAll[ii1 - 1][:, 0], PcDataAll[ii1 - 1][:, j])
        else:
            # first profile
            for j in np.arange(1, 4, 1):
                temp[2, j - 1] = np.interp(alpha, PcDataAll[ii1 - 1][:, 0], PcDataAll[ii1 - 1][:, j])
            if bThicknessInterp is False:
                ClCdCm = temp[2, 0:2]
            else:
                # second profile
                for j in np.arange(1, 4, 1):
                    temp[1, j - 1] = np.interp(alpha, PcDataAll[ii2 - 1][:, 0], PcDataAll[ii2 - 1][:, j])
                for j in np.arange(1, 4, 1):
                    ClCdCm[j - 1] = np.interp(rel_thickness, Profile_thickness_rel[ii1 - 1:ii2], temp[2:0:-1, j - 1])
    return ClCdCm
#########################################################################################
#########################################################################################
def fSetRotorGrid(ngrid, Rotor):
    """Function that discretizes the blade in elements

        Inputs
        ----------
        ngrid (int): numnber of blade elements-1
        Rotor (instance of class) holds rotor related geometrical parameters
        Outputs
        ----------
        Rotor (instance of class): updated instance of class Rotor
    """
    if (ngrid == 0) == 1:
        print('You didn''t specify a ngrid parameter')
    else:
        rfull = np.linspace(Rotor.rhub, Rotor.R, ngrid + 1)
        r_mid = (rfull[0:-1] + rfull[1:]) / 2.
        Rotor = fInterpRotor(r_mid, Rotor)
    return Rotor
#########################################################################################
#########################################################################################
def fInterpRotor(r_mid, Rotor):
    """Function that interpolate the blade geometry at the blade element center

        Inputs
        ----------
        r_mid float): blade element center
        Rotor (instance of class) holds rotor related geometrical parameters
        Outputs
        ----------
    Rotor (instance of class): updated instance of class Rotor
    """
    #print 'r_mid is', r_mid
    #print 'Rotor.r is ', Rotor.r
    #print Rotor.chord
    #print Rotor.thickness_rel_prof
    Rotor.chord = np.interp(r_mid, Rotor.r, Rotor.chord)
    Rotor.thickness_rel = np.interp(r_mid, Rotor.r, Rotor.thickness_rel_prof)
    Rotor.twist = np.interp(r_mid, Rotor.r, Rotor.twist)
    Rotor.r = r_mid

    Rotor.ProfileSet = np.zeros((3, len(r_mid)))
    #print 'Rotor.Profile_thickness_rel', Rotor.Profile_thickness_rel
    for i in np.arange(len(r_mid)):
        profilesup = np.where(Rotor.Profile_thickness_rel >= Rotor.thickness_rel[i])
        profileinf = np.max(np.where(Rotor.Profile_thickness_rel <= Rotor.thickness_rel[i]))

        if not profilesup:
            profilesup = profileinf
        elif not profileinf:
            profileinf = 0.
        profilesup = profilesup[0][0]
        cp = int(profileinf != profilesup)
        # b=np.array([cp+1, profileinf, profilesup])
        Rotor.ProfileSet[:, i] = np.array([cp + 1, profileinf + 1, profilesup + 1])

    Rotor.e_ref_for_khi = np.min(np.where(Rotor.r > 0.7 * Rotor.R))
    Rotor.ne = len(Rotor.r)
    ## Rotor dr if needed
    Rotor.dr = Rotor.r * 0.
    Rotor.dr[0] = 2.0 * (Rotor.r[0] - Rotor.rhub)
    for i in np.arange(1, len(Rotor.r)):
        Rotor.dr[i] = 2.0 * (Rotor.r[i] - Rotor.r[i - 1] - Rotor.dr[i - 1] * 0.5)
    return Rotor
#########################################################################################
#########################################################################################
def fInitWT(sWT, Format, pathtowt):
    """Function that initializes the input reader
    """
    if Format == 'hawc':
        PcDataAll, AeData, Rotor, Env,  Spec, Algo, Misc=fInitWTHawc(sWT, Format, pathtowt)
    else:
        print('The turbine file input format is mispelled or unspecified: hawc implemented so far')
    return PcDataAll, AeData, Rotor, Env,  Spec, Algo, Misc


## HAWC2
def fInitWTHawc(sWT, Format, pathtowt):
    Rotor = InitRotor()
    Env = InitEnv()
     # = InitTurbine()
    Spec = InitSpec(Env, Rotor)
    #    Controller=InitController()
    #  = InitState()
    Algo = InitAlgo()
    Misc = InitMisc()
    parMisc = {'WTname': sWT, 'Format': Format}
    Misc.Set(**parMisc)

    HtcFile = glob(pathtowt + sWT + '/*.htc')
    #    AeFile= glob(pathtowt+sWT+'/data/*ae*')
    #    PcFile= glob(pathtowt+sWT+'/data/*pc*')
    SpecFile = glob(pathtowt + sWT + '/*Spec*')


    Rotor, Spec, Algo = fReadSpec(SpecFile,  Rotor, Spec, Algo)
    AeSet, PcFileName, AeFileName, Nb, PitchAxis = fReadHtcFile(HtcFile, 'blade1')
    AeData = fReadAeFile(AeFileName, pathtowt, sWT, AeSet, 4)
    PcSet = AeData[0, 3]
    PcDataAll, thickness_rel_prof, ndata = fReadPcFile(PcFileName, pathtowt, sWT, PcSet)

    Rotor.r = AeData[:, 0] + Rotor.rhub
    Rotor.chord = AeData[:, 1]
    Rotor.thickness_rel_prof = AeData[:, 2]
    Rotor.Profile_thickness_rel = thickness_rel_prof
    if Format == 'hawc':
        Stations = PitchAxis
        twist = Stations[:, 3]
        rtwist = Stations[:, 2] + Rotor.rhub
    # Dealing with sign
    if (np.mean(twist) < 0) == 1:
        sign = -1;
    else:
        sign = 1
    # Dealing with problem of interpolation
    if (max(rtwist) < max(Rotor.r)) == 1:
        print('! For twist interpolation, last blade section in htc file should be at bigger the last of the ae file. Im replacing it....')
        rtwist[-1] = max(Rotor.r)

    if (min(rtwist) > min(Rotor.r)) == 1:
        print('! For twist interpolation, first blade section in htc file should be at smaller (usually 0) than the one in the ae file. Im replacing it....')
        rtwist[0] = Rotor.r[0]

    # Interpolating twist
    Rotor.twist = np.interp(Rotor.r, rtwist, twist) * sign

    Rotor.R_coned = Rotor.R * cos(Rotor.cone * pi / 180.)  # Rotor coned radius [m]
    Rotor.SweptArea = pi * (Rotor.R * cos(Rotor.cone * pi / 180.)) ** 2
    Spec.TSR_rated = Spec.Omega_rated * Rotor.R * cos(Rotor.cone * pi / 180.) / Spec.V_rated
    return PcDataAll, AeData, Rotor, Env,  Spec, Algo, Misc
#########################################################################################
#########################################################################################
def fReadPcFile(PcFileName, pathtowt, sWT, PcSet):
    """Function that loads HAWC2 profile coefficients file
    """
    fd = open(pathtowt + sWT + PcFileName[1:], 'r')
    line = fd.readline()
    n = line.split(" ");
    n = filter(None, n)
    #    NrSet = float(n[0])
    for i in np.arange(0, PcSet - 1, 1):
        line = fd.readline()
    line = fd.readline()
    n = line.split(" ");
    n = filter(None, n)
    NrSubSet = int(n[0])
    PcData = np.zeros((NrSubSet, 4))
    PcDataAll = [i for i in range(NrSubSet)]
    thickness_rel_prof = np.zeros((NrSubSet))
    ndata = np.zeros((NrSubSet))
    for i in np.arange(0, NrSubSet, 1):
        line = fd.readline()
        n = line.split(" ");
        n = filter(None, n)
        Tempvec = n[2:0:-1]
        Tempvec = [float(l) for l in Tempvec]
        PcData = np.zeros((len(np.arange(0, Tempvec[1], 1)), 4))
        thickness_rel_prof[i] = Tempvec[0]
        ndata[i] = Tempvec[1]
        for j in np.arange(0, Tempvec[1], 1):
            line = fd.readline()
            n = line.split(" ");
            n = filter(None, n)
            PcData[j, :] = n[0:4]
        PcDataAll[i] = PcData
    #print PcDataAll
    fd.close()
    return PcDataAll, thickness_rel_prof, ndata
#########################################################################################
#########################################################################################
def fReadAeFile(AeFileName, pathtowt, sWT, AeSet, ncol):
    """Function that loads HAWC2 aerodynamic coefficients file
    """
    fd = open(pathtowt + sWT + AeFileName[1:], 'r')
    line = fd.readline()
    n = line.split(" ");
    n = filter(None, n)
    NrSet = float(n[0])
    for i in np.arange(0, AeSet[0] - 1, 1):
        line = fd.readline()
    line = fd.readline()
    n = line.split(" ");
    n = filter(None, n)
    Label = n[-1]
    Nr = float(n[1])
    AeData = np.zeros((Nr, ncol))
    if len(Label) == 0:
        Label = None
    for i in np.arange(0, Nr, 1):
        line = fd.readline()
        n = line.split("\t"); n = [w.replace('\n', '') for w in n]
        n = filter(None, n)
        AeData[i, :] = [float(k) for k in n]
    return AeData
#########################################################################################
#########################################################################################
def fReadHtcFile(HtcFile, BladeBodyName, ):
    """Function that loads HAWC2 HTC file
    """
    fd = open(HtcFile[0], 'r')
    while 1:
        line = fd.readline()
        if not line:
            break
        pass
        ## READ PITCH AXIS DATA
        if 'name' in line and BladeBodyName in line:
            while 1:
                line = fd.readline()
                if 'begin' in line and 'c2_def' in line:
                    break
            line = fd.readline()
            line=line.replace('\t', ' ')
            n = line.split(" ");
            n = filter(None, n)
            nsec = float(n[n.index('nsec') + 1])
            PitchAxis = np.zeros((nsec, 4))
            for i in np.arange(0, float(nsec), 1):
                line = fd.readline()
                line=line.replace('\t', ' ')
                n = line.split(' ')
                n = filter(None, n)
                nn = [float(j) for j in n[2:6]]
                PitchAxis[i] = nn
                ## READ AERODYNAMIC FILE
        if 'begin' in line and 'aero ' in line:
            while not 'end aero' in line:
                line = fd.readline()
                if 'nblades' in line:
                    n = line.split(" ");
                    n = filter(None, n)
                    n = [w.replace('\t', '') for w in n]
                    Nb = float(n[n.index('nblades') + 1][0])
                if 'ae_filename' in line:
                    n = line.split(" ");
                    n = filter(None, n)
                    n = [w.replace('\t', '') for w in n]
                    AeFileName = n[n.index('ae_filename') + 1]
                if 'pc_filename' in line:
                    n = line.split(" ");
                    n = filter(None, n)
                    n = [w.replace('\t', '') for w in n]
                    PcFileName = n[n.index('pc_filename') + 1]
                if 'ae_sets' in line:
                    n = line.split(" ");
                    n = filter(None, n)
                    n = [w.replace('\t', '') for w in n]
                    AeSet = n[n.index('ae_sets') + 1:-1]
                    AeSet = [float(i) for i in AeSet]
    fd.close()
    return AeSet, PcFileName, AeFileName, Nb, PitchAxis
#########################################################################################
#########################################################################################
def fReadSpec(SpecFile,  Rotor, Spec, Algo):
    """Function that loads the turbine spec file
    """
    fd = open(SpecFile[0], 'r')
    WsRpmPitch=[]
    A=[]
    while 1:
        line = fd.readline()
        if not line:
            break
        pass
        if 'SPECS' in line:
            # Read RPM and Pitch curve
            while 1:
                line = fd.readline()
                if not line:
                    break
                else:
                    n = line.split(" ");
                    n = filter(None, n)
                    nn = [float(j) for j in n[0:3]]
                    WsRpmPitch.append(nn)
        else: # read other specs
            n = line.split(" ");
            n = filter(None, n)
            A.append(n[0])
    fd.close()
    WsRpmPitch=np.array(WsRpmPitch).T
    A=np.array(A)
    A = [float(j) for j in A]
    parRotor = {'nB': A[0],
                'BladeLength':A[1],
                'rhub': A[2],
                'cone':A[3],
                'R': A[1] + A[2]}
    Rotor.Set(**parRotor)

    parWT = {'tilt': A[4],
             'yaw': A[5],
             'H': A[6]}
    # WT.Set(**parWT)

    Algo.Ngrid = A[7]
    parAlgo = {'Ngrid': A[7]}
    Algo.Set(**parAlgo)

    parSpec = {'Omega_rated': A[8] * 2. * pi / 60.,
               'P_rated': A[9],
               'Pitch': WsRpmPitch[2,:],
               'RPM': WsRpmPitch[1,:],
               'WS': WsRpmPitch[0,:]}
    Spec.Set(**parSpec)

    parRotor = {'Omega': Spec.Omega_rated}
    Rotor.Set(**parRotor)
    return Rotor, Spec, Algo
#########################################################################################
#########################################################################################



class InitRotor:
    """ This class holds rotor related parameters
    """
    def __init__(self):
        # Required Params
        self.nB = -1.0  # number of blades
        self.R = -1.0  # Rotor radius [m]
        self.BladeLength = -1.0  # Rotor radius [m]
        self.rhub = 0.0  # Hub  length [m]
        self.cone = 0.0  # cone angle [deg]
        self.ne = -1.0 # number of blade elements in BEL
        self.HubHeight = 60.0 # hub height im m
        self.Omega = -1.  # Nominal Rotational speed [rad/s]

    def Set(self, **parRotor):
        """Parsing data ."""
        for key, value in parRotor.iteritems():
            setattr(self, key, value)


class InitEnv:
    """ This class holds ambient conditions parameters
    """
    def __init__(self):
        self.rho = 1.225  # air density [kg/m^3]
        self.g = 9.81  # gravity [m/s^2]
        self.KinVisc = 15.68 * 10 ** -6  # Knematic viscosity nu [m^2/s]
    def Set(self, **parEnv):
        """Parsing data ."""
        for key, value in parEnv.iteritems():
            setattr(self, key, value)

class InitSpec:
    """ This class holds turbine operating specifications
    """
    def __init__(self, Env, Rotor):
        # Required Params
        self.Cp_rated = -1.0  # estimation of Cp_max at mean wind speed from 31784
        self.P_rated = -1.0  # 500kW
        # self.V_rated_thumbs = gamma(1. + 1. / Env.k) * Env.A + 6.  # rule of thumb mean WS + 6m/s
        self.V_rated = (self.P_rated / (self.Cp_rated * 0.5 * Env.rho * Rotor.R ** 2. * pi)) ** (1. / 3.)
        self.Omega_rated = 0.
        self.TSR_rated = 0. # tip speed ratio at rated
        self.RPM = [] # rotational speed in RPM
        self.Pitch = [] # pitch angle in deg
        self.WS = [] # mean hub height wind speed

    def Set(self, **parSpec):
        """Parsing data ."""
        for key, value in parSpec.iteritems():
            setattr(self, key, value)

class InitMisc:
    """ This class holds turbine operating initial states
    """
    def __init__(self):
        # Required Params
        self.Profiles = -1. # profile sets  in AE HAWC2 file
        self.Format = 'hawc' # format of turbine files
        self.WTname = 'NREL5MW' # turbine name for input files

    def Set(self, **parMisc):
        """Parsing data ."""
        for key, value in parMisc.iteritems():
            setattr(self, key, value)


class InitAlgo:
    """ This class holds BEM algorithm flags and parameters
    """
    def __init__(self):
        self.nbIt = 200  # maximum number of iterations in BEM
        self.aTol = 10 ** -6 # tolerance for axial induction factor convergence
        self.relaxation = 0.5  # relaxation factor in axial induction factor
        self.CTcorrection = 'GlauertCT'  #  type of CT correction more model implementated in the future like 'spera'
        self.Ngrid = 1.0
        self.bSwirl = True  # swirl flow model enabled / disabled
        self.SwirlMethod = 'HAWC' # type of swirl model
        self.bTipLoss = True # enable / disable tip loss model
        self.bHubLoss = False # enable / disable hub loss model
        self.bTipLossCl = False # enable / disable Cl loss model
        self.TipLossMethod = 'Glauert'  # type of tip loss model
        self.bDynaStall = 0 # dynamic stall model
        self.bAIDrag = True # influence on drag coefficient on normal force coefficient
        self.bTIDrag = True # influence on drag coefficient on tangential force coefficient
        self.bReInterp = False # interpolate the input tabulated airfoil data for Reynolds variation
        self.bThicknessInterp = True # interpolate the input tabulated airfoil data for thickness variation
        self.bRoughProfiles = False # use rough profiles for input airfoil data

    def Set(self, **parAlgo):
        """Parsing data ."""
        for key, value in parAlgo.iteritems():
            setattr(self, key, value)


class InitSim:
    """ This class holds further simulation parameters
    """
    def __init__(self):
        self.WT = '' # turbine name
        self.Name = '' # turbine name, redundant to Name, adaptation from Matlab library
        self.rho = 1.225 # air density
        self.KinVisc = 15.68 * 10 ** -6 # kinematic viscosity
        self.WS = 0. # wind speed m/s
        self.RPM = 0. # rotational speed RPM
        self.PITCH = 0. # pitch angle [deg]
        self.YAW = 0. # yaw angle [deg]
        self.Omega = 0. # rotational speed rad/s

    def Set(self, **parSim):
        """Parsing data ."""
        for key, value in parSim.iteritems():
            setattr(self, key, value)


class InitWind:
    """ This class holds inflow wind model. Further implementation will include non symmetric inflow
    (shear and veer) as well as inflow turbulence
    """
    def __init__(self):
        self.V0 = 0. # free stream velocity at hub height

    def Set(self, **parWind):
        """Parsing data ."""
        for key, value in parWind.iteritems():
            setattr(self, key, value)

class InitBEM:
    """ This class holds outputs from the BEM simulations
    """
    def __init__(self, ne):
        """ Initializing the data ."""
        self.phi = np.zeros((ne)) # flow angle in deg
        self.alpha = np.zeros((ne)) # angle of attack in deg
        self.a = np.zeros((ne)) # axial induction
        self.a_last = np.zeros((ne)) # last iteration axial induction for iterative loop
        self.aprime = np.zeros((ne)) # tangential induction
        self.aprime_last = np.zeros((ne)) # last iteration tangential induction
        self.Cd = np.zeros((ne)) # drag coefficient
        self.Cl = np.zeros((ne)) # lift coefficient
        self.Cn = np.zeros((ne)) # normal force coefficient
        self.Ct = np.zeros((ne)) # tangential force coefficient
        self.CT = np.zeros((ne)) # thrust coefficient
        self.Vrel = np.zeros((ne)) # relative velocity in m/s
        self.Re = np.zeros((ne)) # Reynolds number based on chord
        self.F = np.zeros((ne)) # loss corrections
        self.Fperf = np.zeros((ne))
        self.Fshen = [] # Shen's model loss corrections
        self.Un = np.zeros((ne)) # normal velocity
        self.Ut = np.zeros((ne)) # tangential velocity
        self.nIt = np.zeros((ne)) # number of iterations
        self.omega = [] # rotational speed in rad/s
        self.r= np.zeros((ne))
    def Set(self, **parBEM):
        """Parsing data ."""
        for key, value in parBEM.iteritems():
            setattr(self, key, value)

