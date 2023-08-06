

    UF=[]
    UF.append(weio.read('FlexFlap1.csv').toDataFrame())
    UF.append(weio.read('FlexFlap2.csv').toDataFrame())
    UF.append(weio.read('FlexEdge1.csv').toDataFrame())
    # for j in np.arange(nShapes):
    #     iAxis = ShapeDir[j]
    #     plt.figure()
    #     plt.title('Blade shape function {} - direction {}'.format(j+1,DirNames[iAxis]))
    #     plt.plot(s_span,U[j][iAxis,:]  ,label = 'Shape'  )
    #     plt.plot(s_span,dU[j][iAxis,:] ,label = 'Slope'   )
    #     plt.plot(s_span,ddU[j][iAxis,:]*100,label = 'Curvature*100')

    #     if iAxis==2:
    #         plt.plot(UF[j]['x'],UF[j]['Uz'],'--', label = 'Shape Flex'  )
    #         plt.plot(UF[j]['x'],UF[j]['Vz'],'--', label = 'Slope Flex'  )
    #         plt.plot(UF[j]['x'],UF[j]['Kz']*100,'--', label = 'Curvature*100 Flex'  )
    #     elif iAxis==1:
    #         plt.plot(UF[j]['x'],UF[j]['Uy'],'--', label = 'Shape Flex'  )
    #         plt.plot(UF[j]['x'],UF[j]['Vy'],'--', label = 'Slope Flex'  )
    #         plt.plot(UF[j]['x'],UF[j]['Ky']*100,'--', label = 'Curvature*100 Flex'  )
    #     plt.legend()
    # plt.show()

    if body_type=='tower':
        UF=[]
        UF.append(weio.read('ShapeTower1.csv').toDataFrame())
        UF.append(weio.read('ShapeTower2.csv').toDataFrame())
        for j in np.arange(nShapes):
            iAxis = ShapeDir[j]
            plt.figure()
            plt.title('Shape function {} - direction {}'.format(j+1,DirNames[iAxis]))
            plt.plot(s_span,U[j][iAxis,:]  ,label = 'Shape'  )
            plt.plot(s_span,dU[j][iAxis,:] ,label = 'Slope'   )
            plt.plot(s_span,ddU[j][iAxis,:]*100,label = 'Curvature*100')

            if iAxis==2:
                plt.plot(UF[j]['H'],UF[j]['U'],'--', label = 'Shape Flex'  )
                plt.plot(UF[j]['H'],UF[j]['V'],'--', label = 'Slope Flex'  )
                plt.plot(UF[j]['H'],UF[j]['K']*100,'--', label = 'Curvature*100 Flex'  )
            elif iAxis==1:
                plt.plot(UF[j]['H'],UF[j]['U'],'--', label = 'Shape Flex'  )
                plt.plot(UF[j]['H'],UF[j]['V'],'--', label = 'Slope Flex'  )
                plt.plot(UF[j]['H'],UF[j]['K']*100,'--', label = 'Curvature*100 Flex'  )
            plt.legend()
        plt.show()

# 
# Twr.MM=np.array([[ 3.08E+05,  0.00E+00,  0.00E+00,  0.00E+00,  0.00E+00,  0.00E+00,  0.00E+00,  0.00E+00 ],
#                  [ 0.00E+00,  3.08E+05,  0.00E+00,  0.00E+00,  0.00E+00, -1.04E+07,  0.00E+00,  0.00E+00 ],
#                  [ 0.00E+00,  0.00E+00,  3.08E+05,  0.00E+00,  1.04E+07,  0.00E+00,  8.47E+04, -1.94E+05 ],
#                  [ 0.00E+00,  0.00E+00,  0.00E+00,  0.00E+00,  0.00E+00,  0.00E+00,  0.00E+00,  0.00E+00 ],
#                  [ 0.00E+00,  0.00E+00,  1.04E+07,  0.00E+00,  4.99E+08,  0.00E+00,  4.66E+06, -7.41E+06 ],
#                  [ 0.00E+00, -1.04E+07,  0.00E+00,  0.00E+00,  0.00E+00,  4.99E+08,  0.00E+00,  0.00E+00 ],
#                  [ 0.00E+00,  0.00E+00,  8.47E+04,  0.00E+00,  4.66E+06,  0.00E+00,  4.88E+04, -5.27E+04 ],
#                  [ 0.00E+00,  0.00E+00, -1.94E+05,  0.00E+00, -7.41E+06,  0.00E+00, -5.27E+04,  2.10E+05 ]])
# 
# 
# if nB==2:
#     Twr.MM=np.array([
#                     [ 3.08E+05,  0.00E+00,  0.00E+00,  0.00E+00,  0.00E+00,  0.00E+00,  0.00E+00,  0.00E+00],
#                     [ 0.00E+00,  3.08E+05,  0.00E+00,  0.00E+00,  0.00E+00, -1.04E+07,  0.00E+00,  0.00E+00],
#                     [ 0.00E+00,  0.00E+00,  3.08E+05,  0.00E+00,  1.04E+07,  0.00E+00,  8.55E+04, -1.46E+05],
#                     [ 0.00E+00,  0.00E+00,  0.00E+00,  0.00E+00,  0.00E+00,  0.00E+00,  0.00E+00,  0.00E+00],
#                     [ 0.00E+00,  0.00E+00,  1.04E+07,  0.00E+00,  4.99E+08,  0.00E+00,  4.70E+06, -5.28E+06],
#                     [ 0.00E+00, -1.04E+07,  0.00E+00,  0.00E+00,  0.00E+00,  4.99E+08,  0.00E+00,  0.00E+00],
#                     [ 0.00E+00,  0.00E+00,  8.55E+04,  0.00E+00,  4.70E+06,  0.00E+00,  4.94E+04, -3.51E+04],
#                     [ 0.00E+00,  0.00E+00, -1.46E+05,  0.00E+00, -5.28E+06,  0.00E+00, -3.51E+04,  1.30E+05]])
#     if bHubMass:
#         Twr.MM[6,6:]= np.array([4.80E+04 , -9.19E+04])
#         Twr.MM[7,6:]= np.array([-9.19E+04,  4.72E+05 ])
# 
# 
# if nB==3:
#     if bHubMass:
#         Twr.MM[6,6:]= np.array([4.78E+04, -1.09E+05]);
#         Twr.MM[7,6:]= np.array([-1.09E+05 , 6.28E+05]);
# Twr.MM[6,6:]= np.array([ 4.67E+04, -3.49E+05]);
# Twr.MM[7,6:]= np.array([ -3.49E+05,  5.09E+06]) 


if nShapes_bld==0:
    Bld1.MM=np.array([
                     [  1.7552E+04,  0.0000E+00,  0.0000E+00,  0.0000E+00, -0.0000E+00,  0.0000E+00],
                     [  0.0000E+00,  1.7552E+04,  0.0000E+00,  0.0000E+00,  0.0000E+00,  3.8652E+05],
                     [  0.0000E+00,  0.0000E+00,  1.7552E+04,  0.0000E+00, -3.8652E+05,  0.0000E+00],
                     [  0.0000E+00,  0.0000E+00,  0.0000E+00,  0.0000E+00,  0.0000E+00,  0.0000E+00],
                     [ -0.0000E+00,  0.0000E+00, -3.8652E+05,  0.0000E+00,  1.2770E+07,  0.0000E+00],
                     [  0.0000E+00,  3.8652E+05,  0.0000E+00,  0.0000E+00,  0.0000E+00,  1.2770E+07]])

else:
    Bld1.MM=np.array([
 [ 1.7552E+04 ,0.0000E+00, 0.0000E+00, 0.0000E+00, 0.0000E+00, 0.0000E+00, 0.0000E+00, 0.0000E+00, 0.0000E+00],
 [ 0.0000E+00 ,1.7552E+04, 0.0000E+00, 0.0000E+00, 0.0000E+00, 3.8652E+05, 0.0000E+00, 0.0000E+00, 3.0397E+03],
 [ 0.0000E+00 ,0.0000E+00, 1.7552E+04, 0.0000E+00,-3.8652E+05, 0.0000E+00, 2.0591E+03,-1.3596E+03, 0.0000E+00],
 [ 0.0000E+00 ,0.0000E+00, 0.0000E+00, 0.0000E+00, 0.0000E+00, 0.0000E+00, 0.0000E+00, 0.0000E+00, 0.0000E+00],
 [ 0.0000E+00 ,0.0000E+00,-3.8652E+05, 0.0000E+00, 1.2770E+07, 0.0000E+00,-9.1037E+04, 3.5088E+04,-0.0000E+00],
 [ 0.0000E+00 ,3.8652E+05, 0.0000E+00, 0.0000E+00, 0.0000E+00, 1.2770E+07, 0.0000E+00, 0.0000E+00, 1.2511E+05],
 [ 0.0000E+00 ,0.0000E+00, 2.0591E+03, 0.0000E+00,-9.1037E+04, 0.0000E+00, 8.7062E+02, 0.0000E+00, 0.0000E+00],
 [ 0.0000E+00 ,0.0000E+00,-1.3596E+03, 0.0000E+00, 3.5088E+04, 0.0000E+00, 0.0000E+00, 5.6256E+02, 0.0000E+00],
 [ 0.0000E+00 ,3.0397E+03, 0.0000E+00, 0.0000E+00,-0.0000E+00, 1.2511E+05, 0.0000E+00, 0.0000E+00, 1.4080E+03]]);





        # TODO HACK
        rho = 7850
        E   = 2.10e+11                 # Young modulus [Pa] [N/m^2]
        M = np.array([[00.00, 5.771803, 0.03955],
                     [07.76, 5.566965, 0.03838],
                     [15.52, 5.362056, 0.03721],
                     [23.28, 5.157188, 0.03603],
                     [31.04, 4.952343, 0.03486],
                     [38.80, 4.747473, 0.03369],
                     [46.56, 4.542617, 0.03252],
                     [54.32, 4.337742, 0.03135],
                     [62.08, 4.132880, 0.03017],
                     [69.84, 3.928017, 0.02900],
                     [77.60, 3.723150, 0.02783]])
        H=M[:,0]
        s_bar=H/H[-1]
        D=M[:,1]
        t=M[:,2]
        A  = np.pi*( (D/2)**2 -(D/2-t)**2 ) # [m^2]
        Iy = np.pi/64*(D**4-(D-2*t)**4)     # [m^4]
        m  = rho*A                          # [kg/m]
        EI = E*Iy                           # [Nm^2]
        EIFlp=EI
        EIEdg=EI

    print('Span max:',span_max)
