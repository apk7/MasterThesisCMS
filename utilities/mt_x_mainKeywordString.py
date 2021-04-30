def mainFile(geo_data):
	return f"""$# LS-DYNA Keyword file created by LS-PrePost(R) V4.5.7
$# Created by Apurv Kulkarni
*TITLE
$#                                                                         title
LS-DYNA keyword deck by LS-PrePost
*CONTROL_ACCURACY
$#     osu       inn    pidosu      iacc    
         1         4         0         0
*CONTROL_ENERGY
$#    hgen      rwen    slnten     rylen     irgen     
         2         1         2         2         2
*CONTROL_HOURGLASS
$#     ihq        qh  
         4      0.05
*CONTROL_TERMINATION
$#  endtim    endcyc     dtmin    endeng    endmas     nosol     
    0.0035         0         0      0.01         0         0
*DATABASE_ELOUT
$#      dt    binary      lcur     ioopt   option1   option2   option3   option4
       0.0         3         7         1         0         0         0         0
*DATABASE_GLSTAT
$#      dt    binary      lcur     ioopt     
       0.0         3         7         1
$#*DATABASE_GLSTAT_MASS_PROPERTIES
$#      dt    binary      lcur     ioopt     
$#       0.0         3         7         1
*DATABASE_MATSUM
$#      dt    binary      lcur     ioopt     
       0.0         3         7         1
$#*DATABASE_NODFOR
$#      dt    binary      lcur     ioopt     
$#       0.0         3         7         1
$#*DATABASE_NODOUT
$#      dt    binary      lcur     ioopt   option1   option2       
$#       0.0         3         7         1       0.0         0
*DATABASE_RBDOUT
$#      dt    binary      lcur     ioopt     
       0.0         3         7         1
$#*DATABASE_RCFORC
$#      dt    binary      lcur     ioopt     
$#       0.0         3         7         1
$#*DATABASE_SECFORC
$#      dt    binary      lcur     ioopt     
$#     0.0         3         7         1
$#*DATABASE_SPCFORC
$#      dt    binary      lcur     ioopt     
$#       0.0         3         7         1
*DATABASE_BINARY_D3PLOT
$#      dt      lcdt      beam     npltc    psetid      
       0.0         7         0         0         0
$#   ioopt      rate    cutoff    window      type      pset    
         1       0.0       0.0       0.0         0         0
*DATABASE_EXTENT_BINARY
$#   neiph     neips    maxint    strflg    sigflg    epsflg    rltflg    engflg
        12         0         3         1         1         1         1         1
$#  cmpflg    ieverp    beamip     dcomp      shge     stssz    n3thdt   ialemat
         0         0         0         1         2         1         2         1
$# nintsld   pkp_sen      sclp     hydro     msscl     therm    intout    nodout
         0         0       1.0         0         0         0ALL       ALL
$#    dtdt    resplt     neipb     quadr     cubic     
         0         0         0         0         0
*BOUNDARY_PRESCRIBED_MOTION_SET
$#    nsid       dof       vad      lcid        sf       vid     death     birth
         3         1         1         1       1.3         01.00000E28       0.0
$#    nsid       dof       vad      lcid        sf       vid     death     birth
         4         1         1         1       1.3         01.00000E28       0.0
*BOUNDARY_SPC_SET
$#    nsid       cid      dofx      dofy      dofz     dofrx     dofry     dofrz
         1         0         1         1         1         0         0         0
$#    nsid       cid      dofx      dofy      dofz     dofrx     dofry     dofrz
         2         0         1         1         1         0         0         0
*PART
$#                                                                         title
L11
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
         1         1         1         0         0         0         0         0
*SECTION_SOLID_TITLE
sec1
$#   secid    elform       aet   
         1         1         0
*PART
$#                                                                         title
L22
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
         2         2         2         0         0         0         0         0
*SECTION_SOLID_TITLE
sec1
$#   secid    elform       aet   
         2         1         0
*PART
$#                                                                         title
L31
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
         3         3         1         0         0         0         0         0
*SECTION_SOLID_TITLE
sec1
$#   secid    elform       aet   
         3         1         0
*PART
$#                                                                         title
L42
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
         4         4         2         0         0         0         0         0
*SECTION_SOLID_TITLE
sec1
$#   secid    elform       aet   
         4         1         0
*PART
$#                                                                         title
L51
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
         5         5         1         0         0         0         0         0
*SECTION_SOLID_TITLE
sec1
$#   secid    elform       aet   
         5         1         0
*PART
$#                                                                         title
L62
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
         6         6         2         0         0         0         0         0
*SECTION_SOLID_TITLE
sec1
$#   secid    elform       aet   
         6         1         0
*PART
$#                                                                         title
SL62
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
         7         7         2         0         0         0         0         0
*SECTION_SOLID_TITLE
sec1
$#   secid    elform       aet   
         7         1         0
*PART
$#                                                                         title
SL51
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
         8         8         1         0         0         0         0         0
*SECTION_SOLID_TITLE
sec1
$#   secid    elform       aet   
         8         1         0
*PART
$#                                                                         title
SL42
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
         9         9         2         0         0         0         0         0
*SECTION_SOLID_TITLE
sec1
$#   secid    elform       aet   
         9         1         0
*PART
$#                                                                         title
SL31
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        10        10         1         0         0         0         0         0
*SECTION_SOLID_TITLE
sec1
$#   secid    elform       aet   
        10         1         0
*PART
$#                                                                         title
SL22
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        11        11         2         0         0         0         0         0
*SECTION_SOLID_TITLE
sec1
$#   secid    elform       aet   
        11         1         0
*PART
$#                                                                         title
SL11
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        12        12         1         0         0         0         0         0
*SECTION_SOLID_TITLE
sec1
$#   secid    elform       aet   
        12         1         0
*PART
$#                                                                         title
Cohesive_Part
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
        13        13         3         0         0         0         0         0
*SECTION_SOLID_TITLE
sec1
$#   secid    elform       aet   
        13        19         0
*DEFINE_COORDINATE_SYSTEM
$#     cid        xo        yo        zo        xl        yl        zl      cidl
         1       0.0       0.0       0.0       1.0       0.0       0.0         0
$#      xp        yp        zp  
       0.0      -1.0       0.0
*DEFINE_CURVE_TITLE
Force
$#    lcid      sidr       sfa       sfo      offa      offo    dattyp     lcint
         1         0       1.0       1.5       0.0       0.0         0         0
$#                a1                  o1  
                 0.0                 0.0
                0.01              8000.0
                0.02              8000.0
$#
$#*BOUNDARY_SPC_SET
$#         1         0         1         1         1         0         0         0
$#*BOUNDARY_SPC_SET
$#         2         0         1         1         1         0         0         0
$#*BOUNDARY_SPC_SET
$#         2         0         1         1         1         0         0         0
*DAMPING_PART_STIFFNESS
$#     pid      coef    
         1       0.1
*DAMPING_PART_STIFFNESS
$#     pid      coef    
         2       0.1
*DAMPING_PART_STIFFNESS
$#     pid      coef    
         3       0.1
*DAMPING_PART_STIFFNESS
$#     pid      coef    
         4       0.1
*DAMPING_PART_STIFFNESS
$#     pid      coef    
         5       0.1
*DAMPING_PART_STIFFNESS
$#     pid      coef    
         6       0.1
*DAMPING_PART_STIFFNESS
$#     pid      coef    
         7       0.1
*DAMPING_PART_STIFFNESS
$#     pid      coef    
         8       0.1
*DAMPING_PART_STIFFNESS
$#     pid      coef    
         9       0.1
*DAMPING_PART_STIFFNESS
$#     pid      coef    
        10       0.1
*DAMPING_PART_STIFFNESS
$#     pid      coef    
        11       0.1
*DAMPING_PART_STIFFNESS
$#     pid      coef    
        12       0.1
*DAMPING_PART_STIFFNESS
$#     pid      coef    
        13       0.1
$#
{geo_data}
*END"""
