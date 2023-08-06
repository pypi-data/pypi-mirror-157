
## VESTAS
#########################################################################################
#########################################################################################
def fReadVBladeFile(AeFileName, pathtowt, sWT):
    """Function that loads Vestas blad aerodynamic coefficients file
    """
    radial=[]; twist=[];  thick=[]; chord=[]
    fd = open(pathtowt + '/'+AeFileName, 'r')
    #### Main loop in entire file
    while 1:
        line = fd.readline()
#        print line
        if not line:
            break
        pass
        line=line.replace('\t', ' '); n = line.split(" "); n = filter(None, n)
        if 'airfoilProfile' in n:
            # print n
            nn=n[1].replace('\"', '')
            PcFileName = nn
        if 'numBlades' in n:
            numBlades=float(n[1])
        if 'coning' in n:
            coning=float(n[1])
        if 'tilt' in n:
            tilt=float(n[1])
        if 'radialStations' in n:   ### Inner loop for parsing radial positions
            fd.readline() # skip opening parentheses line
            while 1:
                line = fd.readline();line=line.replace('\t', ' '); line=line.replace('\n', ' ');n = line.split(' ')
                n = filter(None, n)
                if ');' in n:
                    break
                else:
                    radial.append(float(n[0]))
        if 'twist' in n: ### Inner loop for parsing twist positions
            fd.readline() # skip opening parentheses line
            while 1:
                line = fd.readline();line=line.replace('\t', ' '); line=line.replace('\n', ' ');n = line.split(' ')
                n = filter(None, n)
                if ');' in n:
                    break
                else:
                    twist.append(float(n[0]))
        if 'chord' in n: ### Inner loop for parsing twist positions
            fd.readline() # skip opening parentheses line
            while 1:
                line = fd.readline();line=line.replace('\t', ' '); line=line.replace('\n', ' ');n = line.split(' ')
                n = filter(None, n)
                if ');' in n:
                    break
                else:
                    chord.append(float(n[0]))
        if 'thick' in n:  ### Inner loop for parsing thick positions
            fd.readline() # skip opening parentheses line
            while 1:
                line = fd.readline();line=line.replace('\t', ' '); line=line.replace('\n', ' ');n = line.split(' ')
                n = filter(None, n)
                if ');' in n:
                    break
                else:
                    thick.append(float(n[0]))
    nrad=len(radial)

    #print 'Blade radial position: ', radial
    #print 'Blade twist angle distribution: ',twist
    #print 'Blade thickness distribution: ', thick
    #print 'Blade chord distribution: ', chord
    #print 'Turbine no blades:', numBlades
    #print 'Tilt angle is: ', tilt
    #print 'Cone angle is: ', coning
    #print 'Number of radial section is: ', nrad
    #print 'Profile coefficient filename is: ',PcFileName
    return radial, twist, thick, chord, numBlades, tilt, coning, nrad,PcFileName
#########################################################################################
#########################################################################################
def fReadVSpecFile(SpecFile, SpecTurbine, pathtowt, sWT,  Rotor, Spec, Algo):
    """Function that loads Vestas blade aerodynamic coefficients file
    """
    wind=[]; rpm=[];  pitch=[]
    # fd = open(pathtowt + sWT + '/'+SpecTurbine, 'r')
    fd = open(SpecTurbine[0], 'r')
    #### Main loop in entire file
    while 1:
        line = fd.readline()
#        print line
        if not line:
            break
        pass
        line=line.replace('\t', ' '); n = line.split(" "); n = filter(None, n)

        if 'wind' in n:   ### Inner loop for parsing radial positions
            fd.readline() # skip opening parentheses line
            while 1:
                line = fd.readline();line=line.replace('\t', ' '); line=line.replace('\n', ' ');n = line.split(' ')
                n = filter(None, n)
                if ');' in n:
                    break
                else:
                    wind.append(float(n[0]))
        if 'rpm' in n: ### Inner loop for parsing twist positions
            fd.readline() # skip opening parentheses line
            while 1:
                line = fd.readline();line=line.replace('\t', ' '); line=line.replace('\n', ' ');n = line.split(' ')
                n = filter(None, n)
                if ');' in n:
                    break
                else:
                    rpm.append(float(n[0]))
        if 'pitch' in n:  ### Inner loop for parsing thick positions
            fd.readline() # skip opening parentheses line
            while 1:
                line = fd.readline();line=line.replace('\t', ' '); line=line.replace('\n', ' ');n = line.split(' ')
                n = filter(None, n)
                if ');' in n:
                    break
                else:
                    pitch.append(float(n[0]))
    nrad=len(pitch)
    # print 'Turbine pitch: ', pitch
    # print 'Turbine rpm: ',rpm
    # print 'Wind for rpm and pitch: ', wind
    fd.close()

    fd = open(SpecFile[0], 'r')
    A=[]
    while 1:
        line = fd.readline()
        if not line:
            break
        pass
        if 'SPECS' in line:
            break
        else:
            n = line.split(" ");
            n = filter(None, n)
            A.append(n[0])

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
               'Pitch': pitch,
               'RPM': rpm,
               'WS': wind}
    Spec.Set(**parSpec)

    parRotor = {'Omega': Spec.Omega_rated}
    Rotor.Set(**parRotor)

    fd.close()
    return Rotor, Spec, Algo
#########################################################################################
#########################################################################################
def fReadVPcFile(PcFileName, pathtowt, sWT):
    """Function that loads Vestas profile coefficients file
    """
    fd = open(pathtowt + '/' +PcFileName, 'r')
    fd.readline() # skip header
    line = fd.readline()
    n = line.split(" ");
    n = filter(None, n)
    NrSubSet = int(n[0])
    # print 'NrSubSet', NrSubSet
    line = fd.readline()
    n = line.split(" ");
    #n=n.replace('\n', ' ')
    n = filter(None, n)
    thickness_rel_prof=[float(n[j]) for j in range(len(n))]
    # print 'thickness_rel_prof is', thickness_rel_prof
    line = fd.readline()
    n = line.split(" ");
    ndata=float(n[0])
    # print 'ndata is', ndata

    #PcDataAll = np.zeros((NrSubSet,ndata, 4))
    PcDataAll = [w for w in range(NrSubSet)]
    for j in np.arange(0, NrSubSet, 1):
        fd.readline() # skip profile headers
        PcData = np.zeros((ndata, 4))
        for i in np.arange(0.,ndata,1.):
            line = fd.readline(); line=line.replace('\t', ' '); line=line.replace('\n', ' ');    n = line.split(" ");
            n = filter(None, n)
            #print n
            #PcData[i,:] = [float(n[j]) for j in range(len(n))]
            PcData[i,:] = n[0:4]
            #print PcData[i,0:3]
        #print '#####################################################################'
        PcDataAll[j] =PcData

    fd.close()
    return PcDataAll, thickness_rel_prof, ndata
#########################################################################################
#########################################################################################
def fInitWTvestas(sWT, Format, pathtowt):
    # print pathtowt
    # print pathtowt+sWT+'/Spec'
    SpecFile = glob(pathtowt + '/'+sWT+'*Spec*')
    AeFileName=str(sWT)
    SpecTurbine= glob(pathtowt + '/'+sWT+'*ControlTable*')
    # print 'SpecFile is', SpecFile
    # print 'AeFilename is', AeFileName
    # print 'SpecTurbine is', SpecTurbine

    AeData=[]
    Rotor = InitRotor()
    Env = InitEnv()
     # = InitTurbine()
    Spec = InitSpec(Env, Rotor)
    Algo = InitAlgo()
    Misc = InitMisc()
    parMisc = {'WTname': sWT, 'Format': Format}
    Misc.Set(**parMisc)


    radial, twist, thick, chord, numBlades, tilt, coning, nrad,PcFileName =fReadVBladeFile(AeFileName, pathtowt, sWT)
    Rotor, Spec, Algo=fReadVSpecFile(SpecFile,SpecTurbine, pathtowt, sWT,  Rotor, Spec, Algo)
    PcDataAll, thickness_rel_prof, ndata=fReadVPcFile(PcFileName, pathtowt, sWT)


    Rotor.r = radial
    Rotor.chord = chord
    Rotor.thickness_rel_prof = thick
    Rotor.Profile_thickness_rel = thickness_rel_prof
    Rotor.cone=coning
    Rotor.tilt=tilt
    Rotor.twist=twist

    Rotor.R_coned = Rotor.R * cos(Rotor.cone * pi / 180.)  # Rotor coned radius [m]
    Rotor.SweptArea = pi * (Rotor.R * cos(Rotor.cone * pi / 180.)) ** 2
    Spec.TSR_rated = Spec.Omega_rated * Rotor.R * cos(Rotor.cone * pi / 180.) / Spec.V_rated

    return PcDataAll, AeData, Rotor, Env,  Spec, Algo, Misc
#########################################################################################
#########################################################################################
