$# LS-DYNA Keyword file created by LS-PrePost(R) V4.5.7
$# Created by Apurv Kulkarni
*KEYWORD
*CONTROL_TIMESTEP
$#  dtinit    tssfac      isdo    tslimt     dt2ms      lctm     erode     ms1st
      0.00      0.90         0      0.00-1.000E-08         0         0         0
$#  dt2msf   dt2mslc     imscl    unused    unused     rmscl
       0.0         0         0                           0.0
$#
*MAT_LAMINATED_FRACTURE_DAIMLER_PINHO
$#     mid        ro        ea        eb        ec      prba      prca      prcb
         11.5305E+031.2100E+119.2400E+099.2400E+091.5000E-021.5000E-023.7000E-01
$#     gab       gbc       gca      aopt       daf       dkf       dmf       efs
1.3500E+102.9200E+091.3500E+10         2       0.0       1.0       1.0-2.000E-01
$#      xp        yp        zp        a1        a2        a3
       0.0       0.0       0.0       1.0       0.0       0.0
$#      v1        v2        v3        d1        d2        d3    mangle
       0.0       0.0       0.0       0.0       1.0       0.0
$#  enkink       ena       enb       ent       enl
4.0000E+074.5000E+072.5000E+034.0000E+034.0000E+03
$#      xc        xt        yc        yt        sl
6.5000E+091.7900E+091.3000E+084.2000E+077.4000E+07
$#     fio      sigy      lcss      beta       pfl      puck      soft
5.3000E+017.5000E+05         2     0.000   100.000     0.000     0.000
$#
*MAT_LAMINATED_FRACTURE_DAIMLER_PINHO
$#     mid        ro        ea        eb        ec      prba      prca      prcb
         21.5305E+031.2100E+119.2400E+099.2400E+091.5000E-021.5000E-023.7000E-01
$#     gab       gbc       gca      aopt       daf       dkf       dmf       efs
1.3500E+102.9200E+091.3500E+10         2       0.0       1.0       1.0-2.000E-01
$#      xp        yp        zp        a1        a2        a3
       0.0       0.0       0.0       0.0       1.0       0.0
$#      v1        v2        v3        d1        d2        d3    mangle
       0.0       0.0       0.0       1.0       0.0       0.0
$#  enkink       ena       enb       ent       enl
4.0000E+074.5000E+072.5000E+034.0000E+034.0000E+03
$#      xc        xt        yc        yt        sl
6.5000E+091.7900E+091.3000E+084.2000E+077.4000E+07
$#     fio      sigy      lcss      beta       pfl      puck      soft
5.3000E+017.5000E+05         2     0.000   100.000     0.000     0.000
$#
*MAT_COHESIVE_GENERAL
$#     mid        ro     roflg   intfall       tes      tslc       gic      giic
         36.5000E+00         1       1.0       1.0         35.0000E+028.0000E+02
$#     xmu         t         s     stfsf     tslc2
       1.03.9900E+071.3700E+08       1.0       4.0
$#
*DEFINE_CURVE_TITLE
shear
$#    lcid      sidr       sfa       sfo      offa      offo    dattyp     lcint
         2         0     1.400     0.900       0.0       0.0         0         0
$#                a1                  o1
                   0               0e+08
              0.0007          0.0533e+08
              0.0016          0.1277e+08
              0.0028          0.1949e+08
              0.0044          0.2788e+08
              0.0067          0.3638e+08
              0.0102          0.4440e+08
              0.0137          0.5136e+08
              0.0185          0.5670e+08
              0.0243          0.6050e+08
              0.0284          0.6311e+08
              0.0328          0.6482e+08
              0.0374          0.6595e+08
              0.0423          0.6677e+08
              0.0472          0.6758e+08
              0.0522          0.6869e+08
              0.0571          0.7038e+08
              0.0621          0.7229e+08
              0.0673          0.7422e+08
              0.0727          0.7620e+08
              0.0808          0.7942e+08
              0.0946          0.8574e+08
              0.1058          0.9060e+08
              0.1179          0.9688e+08
              0.1297          1.0325e+08
              0.1426          1.0972e+08
              0.1695          1.2442e+08
$#
*DEFINE_CURVE_TITLE
fail_cohesive
$#    lcid      sidr       sfa       sfo      offa      offo    dattyp     lcint
         3         0       1.0       1.0       0.0       0.0         0         0
$#                a1                  o1
                 0.0                 0.0
                 0.2                 1.0
                 1.0                 0.0
$#
*DEFINE_CURVE_TITLE
fail_cohesive
$#    lcid      sidr       sfa       sfo      offa      offo    dattyp     lcint
         4         0       1.0       1.0       0.0       0.0         0         0
$#                a1                  o1
                 0.0                 0.0
                 0.2                 1.0
                 0.4                 0.9
                 0.7                 0.6
                 1.0                 0.0
$#