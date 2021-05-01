#=============================================================================
# Author: Apurv Kulkarni
#-----------------------------------------------------------------------------
# OHT Analysis Geometry
#-----------------------------------------------------------------------------
# Creating OHT geometry using gmsh api. The first layer is created using gmsh 
# api. The subsequent plies and cohesive layers are created using python loops. 
# The cohesive elements are zero thickness elements with 8 nodes. 4-nodes from 
# bottom and top are shared with plies respectively
#=============================================================================
# Geometry and Mesh controls|
#----------------------------
#                       <numMainbodyXElem>    <numMainbodyXElem>  
#     <numClampXElem>    ←---------→          ←---------→
#     ----------------------------------------------------------------------
#  ↑  |                  |         |\        /|         |                  |
#  |  |                  |         | \      / |         |                  |
#  |  |                  |         |  \____/--|-→ <numCSElem>              |
#  |  |                  |         |  /    \  |         |                  |
# Ly  |                  |         |  \____/  |         |                  |
#  |  |                  |         |  /  | \  |         |                  |
#  |  |                  |         | /   ↓  \ |         |                  |
#  |  |                  |         |<numCurveElem>      |                  |
#  ↓  ---------------------------------------------------------------------- 
#     ←-------clp-------→                               ←-------clp-------→
#     ←----------------------------- Lx ----------------------------------→
#
#=============================================================================

def create_geo(Rx=0.0024,file_dst="D:\\",filename='sample_temp',
                onlypreview=0, save_mesh=0,meshname='mymesh',
                preview_geom_mesh=0,log_flag=0, numCurveElem=25,
                numClampXElem =4, numMainbodyXElem= 10, numCSElem = 15):
    """
   Args:
        Rx (float, optional): Longitudinal radius of elliptical hole. 
        Defaults to 0.0024.
        
        file_dst (str, optional): Destination path of generated geometry file. 
        Defaults to "D:\".
        
        filename (str, optional): Filename of generated geometry file.
        Defaults to 'sample_temp'.
        
        onlypreview (int, optional): Only previews the geometry in GMSH 
        application no saving. Defaults to 0.
        
        save_mesh (int, optional): Flag to save the mesh (different from the 
        LS-Dyna geometry and mesh). Defaults to 0.
        
        meshname (str, optional): Mesh name. Defaults to 'mymesh'.
        
        preview_geom_mesh (int, optional): Previews the gemetry (and mesh) then
        saves it. User needs to close preview window manually to proceed.
        Defaults to 0.
        
        log_flag (int, optional): Whethre to generate GMSH log or not.
        Defaults to 0.
        
        numCurveElem (int, optional): Mesh control- Number of elements on the 
        hole circumference (in each of the 4 sectors). Defaults to 25.
        
        numClampXElem (int, optional): Mesh control- Number of element on 
        clamping area in x-direction. Defaults to 4.
        
        numMainbodyXElem (int, optional): Mesh control- Number of element on 
        mainbody area in x-direction. Defaults to 10.
        
        numCSElem (int, optional): Mesh control- Number of elements in cross 
        sectional part of notch mesh. Defaults to 15.
    """    
    # Importing utilities
    import gmsh                # install the api using => "pip install gmsh"
    import numpy as np
    np.set_printoptions(precision=20)
    from time import process_time
    
    try:from mt_x_mainKeywordString import mainFile
    except:from utilities.mt_x_mainKeywordString import mainFile
    
    import subprocess
    import os
    import time

    start =  process_time()
    
    # Model geometry details
    Lx = 0.240               # Length of geometry in x-direction
    Ly = 0.0288              # Width of geometry in y-direction
    Lz = 0.0019              # Thickness of geometry in z-direction
    clp = 0.05               # Claming distance
    numPly=12                # Number of composite material layers(plies)
    LzPly = Lz/numPly        # Thickness of each ply      
    numCohElem = numPly-1    # Number of cohesive element layers (numPly-1)
    Rx=Rx                    # Radius of elliptical notch in x-direction
    Ry=0.0024                # Radius of elliptical notch in y-direction
    MeshSizeFactor = 1       # Resulatant = MeshSize * meshSizeFactor
    
    os.makedirs(file_dst, exist_ok=True)
    
    # lsprepost application location (if not in path)
    lspp_loc = "C:\Program Files\LSTC\LS-PrePost 4.8\lsprepost4.8_x64.exe"      
    
    # starting gmsh
    gmsh.initialize()
    # logging gmsh geometry and mesh creation process
    if log_flag:
        gmsh.logger.start()
    
    gmsh.model.add("mymodel")
    gmsh.option.setNumber('Geometry.CopyMeshingMethod',1);
    
    #=====================================================================
    #  Geometry creation
    #=====================================================================
    
    # Finding intersection point of a line passing through ellipse center and 
    # ellipse
    a = Rx
    b = Ry
    if Rx>Ry:
        m = Ry/Rx*(0.8)  # slope of the line
    if Rx==Ry:
        m = 1
    else:
        # m = 1
        m = Ry/Rx*2     # slope of the line
        
    c = Ly/2 - (m * Lx/2)
    h = Lx/2
    k = Ly/2
    phi = c - k
    
    e1x1 = (((b*b*h)-a*a*m*phi+ 
            a*b*np.sqrt((b*b)+(a*a*m*m)-(2*m*phi*h)-(phi*phi)-(m*m*h*h)))/
            (a*a*m*m + b*b))
    
    e1y1 = m*e1x1 + c
    e1x2 = (((b*b*h) - a*a*m*phi -
             a*b*np.sqrt(b*b + a*a*m*m - 2*m*phi*h - phi*phi - m*m*h*h))/
            (a*a*m*m + b*b))
    
    e1y2 = m*e1x2 + c
    
    e2x1 = 0 + (Lx/2-Ly/2)
    e2y1 = 0
    e2x2 = Ly+(Lx/2-Ly/2)
    e2y2 = Ly
    
    # Creating points in the space
    gmsh.model.occ.addPoint(0,  0, 0, 1.0)          #1
    gmsh.model.occ.addPoint(clp,  0, 0, 1.0)        #2
    gmsh.model.occ.addPoint(Lx-clp,  0, 0, 1.0)     #3
    gmsh.model.occ.addPoint(Lx,  0, 0, 1.0)         #4
    gmsh.model.occ.addPoint(0, Ly, 0, 1.0)          #5
    gmsh.model.occ.addPoint(clp, Ly, 0, 1.0)        #6
    gmsh.model.occ.addPoint(Lx-clp, Ly, 0, 1.0)     #7
    gmsh.model.occ.addPoint(Lx, Ly, 0, 1.0)         #8
    gmsh.model.occ.addPoint(e1x2, e1y2, 0, 1.0)     #9    
    gmsh.model.occ.addPoint(e1x1, e1y2, 0, 1.0)     #10
    gmsh.model.occ.addPoint(e1x1, e1y1, 0, 1.0)     #11
    gmsh.model.occ.addPoint(e1x2, e1y1, 0, 1.0)     #12
    gmsh.model.occ.addPoint(e2x2, e2y2, 0, 1.0)     #13
    gmsh.model.occ.addPoint(e2x1, e2y2, 0, 1.0)     #14
    gmsh.model.occ.addPoint(e2x1, e2y1, 0, 1.0)     #15
    gmsh.model.occ.addPoint(e2x2, e2y1, 0, 1.0)     #16
    
    
    if Rx>=Ry:
        gmsh.model.occ.addPoint(Lx/2, Ly, 0, 1.0)   #17
    else:
        gmsh.model.occ.addPoint(0, Ly/2, 0, 1.0)    #18
        gmsh.model.occ.addPoint(clp, Ly/2, 0, 1.0)  #19
        gmsh.model.occ.addPoint(e2x1, Ly/2, 0, 1.0) #20
   
    ClampXElem = []
    MainbodyXElem = []
    CSElem = []    
    CurveElem =  []    
    Curve2 = []
    
    # Creating lines by joining points
    if Rx>=Ry:
        CurveElem.append(gmsh.model.occ.addLine(1,5))
        CurveElem.append(gmsh.model.occ.addLine(2,6))
        CurveElem.append(gmsh.model.occ.addLine(3,7))
        CurveElem.append(gmsh.model.occ.addLine(4,8))
        CurveElem.append(gmsh.model.occ.addLine(14,15))
        CurveElem.append(gmsh.model.occ.addLine(13,16))
        CurveElem.append(gmsh.model.occ.addLine(15,16))
        
        ClampXElem.append(gmsh.model.occ.addLine(1,2))
        ClampXElem.append(gmsh.model.occ.addLine(3,4))
        ClampXElem.append(gmsh.model.occ.addLine(5,6))
        ClampXElem.append(gmsh.model.occ.addLine(7,8))
        
        MainbodyXElem.append(gmsh.model.occ.addLine(2,15))
        MainbodyXElem.append(gmsh.model.occ.addLine(16,3))
        MainbodyXElem.append(gmsh.model.occ.addLine(6,14))
        MainbodyXElem.append(gmsh.model.occ.addLine(13,7))
        
        CSElem.append(gmsh.model.occ.addLine(12,14))
        CSElem.append(gmsh.model.occ.addLine(9,15))
        CSElem.append(gmsh.model.occ.addLine(10,16))
        CSElem.append(gmsh.model.occ.addLine(11,13))
            
        Curve2.append(gmsh.model.occ.addLine(14,17))
        Curve2.append(gmsh.model.occ.addLine(17,13))
        
    if Rx<Ry:
        ClampXElem.append(gmsh.model.occ.addLine(1,2))
        ClampXElem.append(gmsh.model.occ.addLine(3,4))
        ClampXElem.append(gmsh.model.occ.addLine(5,6))
        ClampXElem.append(gmsh.model.occ.addLine(7,8))
        
        MainbodyXElem.append(gmsh.model.occ.addLine(2,15))
        MainbodyXElem.append(gmsh.model.occ.addLine(16,3))
        MainbodyXElem.append(gmsh.model.occ.addLine(6,14))
        MainbodyXElem.append(gmsh.model.occ.addLine(13,7))
    
        CSElem.append(gmsh.model.occ.addLine(12,14))
        CSElem.append(gmsh.model.occ.addLine(9,15))
        CSElem.append(gmsh.model.occ.addLine(10,16))
        CSElem.append(gmsh.model.occ.addLine(11,13))
        
        CurveElem.append(gmsh.model.occ.addLine(3,7))
        CurveElem.append(gmsh.model.occ.addLine(4,8))
        CurveElem.append(gmsh.model.occ.addLine(13,16))
        CurveElem.append(gmsh.model.occ.addLine(13,14))
        CurveElem.append(gmsh.model.occ.addLine(15,16))
        
        Curve2.append(gmsh.model.occ.addLine(1,17))
        Curve2.append(gmsh.model.occ.addLine(17,5))
        Curve2.append(gmsh.model.occ.addLine(2,18))              
        Curve2.append(gmsh.model.occ.addLine(18,6))
        Curve2.append(gmsh.model.occ.addLine(15,19))
        Curve2.append(gmsh.model.occ.addLine(19,14))
    
    gmsh.model.occ.synchronize()
    
    # Creating ellipse
    mellipse = np.pi/2
    if Rx>=Ry:
        ellipse = gmsh.model.occ.addEllipse(Lx/2,Ly/2,0,Rx,Ry,angle1=mellipse,
                                            angle2=2*np.pi+mellipse)  
    else:   
        ellipse = gmsh.model.occ.addEllipse(Lx/2,Ly/2,0,Ry,Rx,angle1=mellipse,
                                            angle2=2*np.pi+mellipse)  
        gmsh.model.occ.rotate([(1,ellipse)], Lx/2, Ly/2, 0, 0, 0, 1, np.pi/2)
    gmsh.model.occ.synchronize()
    
    # Splitting ellipse using lines across ellipse
    cutOut = gmsh.model.occ.cut([(1,ellipse)], 
                                [(1,CSElem[0]),(1,CSElem[1]),(1,CSElem[2]),
                                 (1,CSElem[3])],removeTool=(False))
    
    for i in range(1,len(cutOut[0])-1):
        CurveElem.append(cutOut[0][i][1])    
    Curve2.append(cutOut[0][0][1])
    Curve2.append(cutOut[0][-1][1])
          
    gmsh.model.occ.synchronize()
  
    # Surface groups : Grouping different lines to form closed surface 
    # boundaries.
    sTag_list = []
    
    if Rx>=Ry:
        linegroup = [
            [1,8,2,10],[14,2,12,5],[6,13,3,15],[3,9,4,11],
            [17,7,18,24],[25,18,6,19],[16,5,17,23]
            ]
    else:
        linegroup = [
            [6,13,8,15],[13,2,14,4],
            [17,11,25,10],[11,15,12,26],[12,16,9,27]
            ]
    for surface in linegroup:
        lTag = gmsh.model.occ.add_wire(surface)
        sTag = gmsh.model.occ.add_plane_surface([lTag])
        sTag_list.append(sTag)
        gmsh.model.occ.synchronize()    
    
    # Setting transfinite curves for structured mesh
    for i in ClampXElem:
        gmsh.model.mesh.setTransfiniteCurve(i,numClampXElem)       
        gmsh.model.occ.synchronize()
    
    for i in MainbodyXElem:                             
        gmsh.model.mesh.setTransfiniteCurve(i,numMainbodyXElem)
        gmsh.model.occ.synchronize()
    
    
    for i in CSElem:                                      
        gmsh.model.mesh.setTransfiniteCurve(i,numCSElem)
        gmsh.model.occ.synchronize()
    
    for i in CurveElem:      
        gmsh.model.mesh.setTransfiniteCurve(i,numCurveElem)
        gmsh.model.occ.synchronize()
    
    for i in Curve2:
        gmsh.model.mesh.setTransfiniteCurve(i,int(numCurveElem/2)) 
        gmsh.model.occ.synchronize()
    
    # Setting tranfinite surfaces for structured mesh
    for i in sTag_list:
        gmsh.model.mesh.setTransfiniteSurface(i)
        gmsh.model.occ.synchronize()

    # surface groups : Grouping different lines to form closed surface 
    # boundaries (with more than 4 points/lines) 
    if Rx>=Ry:
        lTag = gmsh.model.occ.add_wire([19,21,20,16,22,26])
        gmsh.model.occ.synchronize()    
        sTag = gmsh.model.occ.add_plane_surface([lTag])
        gmsh.model.occ.synchronize()    
        gmsh.model.mesh.setTransfiniteSurface(tag=sTag,cornerTags=[13,14,12,11])
        gmsh.model.occ.synchronize()
        
    elif Rx<Ry:
        lTag = gmsh.model.occ.add_wire([1,20,21,3,19,18])
        sTag = gmsh.model.occ.add_plane_surface([lTag])
        gmsh.model.occ.synchronize()    
        gmsh.model.mesh.setTransfiniteSurface(tag=sTag,cornerTags=[1,2,6,5])
        gmsh.model.occ.synchronize()
        
        lTag = gmsh.model.occ.add_wire([5,22,23,7,21,20])
        sTag = gmsh.model.occ.add_plane_surface([lTag])
        gmsh.model.occ.synchronize()    
        gmsh.model.mesh.setTransfiniteSurface(tag=sTag,cornerTags=[2,15,14,6])
        gmsh.model.occ.synchronize()
        
        lTag = gmsh.model.occ.add_wire([9,23,22,10,24,28])
        sTag = gmsh.model.occ.add_plane_surface([lTag])
        gmsh.model.occ.synchronize()    
        gmsh.model.mesh.setTransfiniteSurface(tag=sTag,cornerTags=[15,9,12,14])
        gmsh.model.occ.synchronize()
        
    gmsh.model.mesh.recombine()
    
    # Extrude: Adding thickness to create a singly ply.
    # Number of elements in thickness direction
    numElemThickness = 3                                                        
    model_ = gmsh.model.getEntities(2)
    gmsh.model.occ.synchronize()
    gmsh.model.occ.extrude(model_,0,0,LzPly,numElements=[numElemThickness],
                            heights=[1],recombine=True)
    gmsh.model.occ.synchronize()
    
    #=====================================================================
    # Meshing
    #=====================================================================
    # Mesh options
    
    gmsh.option.setNumber("Mesh.Smoothing", 100)
    
    # 2D mesh algorithm (1: MeshAdapt, 2: Automatic, 3: Initial mesh only, 
    # 5: Delaunay, 6: Frontal-Delaunay, 7: BAMG, 8: Frontal-Delaunay for Quads, 
    # 9: Packing of Parallelograms)
    meshalgo2d = 8                                                              
    gmsh.option.setNumber("Mesh.Algorithm",meshalgo2d)
    
    # Recombine all triangular meshes? (yes:1, no:0)
    RecombineTriMesh = 1                                                        
    gmsh.option.setNumber("Mesh.RecombineAll",RecombineTriMesh)
    gmsh.option.setNumber("Mesh.MeshSizeFactor",MeshSizeFactor)
    
    # Generating mesh
    gmsh.model.mesh.clear()
    # Meshing 2D
    gmsh.model.mesh.generate(2)
    # Meshing 3D
    gmsh.model.mesh.generate(3)
    
    # gmsh mesh name without extension # save mesh (yes-1,no-0)
    if save_mesh: 
        gmsh.write(f"{meshname}.msh")
    
    if onlypreview==0:
        # Get nodes and their coordinates
        nodeTags, nodeCoords, _ = gmsh.model.mesh.getNodes()                        
        # Type,number of elements,
        elementTypes, elementTags, elementNodeTags = gmsh.model.mesh.getElements(3)
        elementTypes = elementTypes[0]
        elementTags = elementTags[0]
        elementNodeTags = elementNodeTags[0]
    
    # Launch the GUI to to preview geometry and mesh using gmsh applications.
    # Script pauses untill gmsh application is closed manually
    if preview_geom_mesh:                                                       
        gmsh.fltk.run()
    
    if log_flag:
        log = gmsh.logger.get()
        gmsh.logger.stop()
    
    # close gmsh
    gmsh.finalize()                                                             
    
    if onlypreview == 0:
        #=====================================================================
        # Data Extraction: processing data collected from gmsh
        #=====================================================================
        numElem = len(elementTags)
        if meshalgo2d==8 or RecombineTriMesh==1:                                    # processing based on shape of solid elements in mesh
            elemtonodes = np.reshape(elementNodeTags,(-1,8))                        # quad/hex elements -> 8 unique coordinates
        else:
            elemtonodes = np.reshape(elementNodeTags,(-1,4))                        # tetra hedral elements -> 4 unique coordinates
            last4nodes = np.transpose(np.asarray([elemtonodes[:,3]]))               # when represented in terms of hexahedral coordinates, the last node is repeated 4 times -> resulting in 8 nodes
            last4nodes = np.repeat(last4nodes,4,axis=1)
            elemtonodes = np.concatenate([elemtonodes,last4nodes],axis=1)
        
        node_coord = np.round(np.transpose(np.vstack([nodeCoords[0::3],nodeCoords[1::3],nodeCoords[2::3]])),16)
        numNode = len(node_coord)
        assert(len(node_coord) == len(nodeTags))
        assert(len(elemtonodes) == numElem)
        print('Total number of elements in 1st ply:\t',numElem)    
        print('Total number of nodes in 1st ply:\t',numNode)
        print('Mesh generation of 1st ply complete...')
        
        #=====================================================================
        # Building full model
        #=====================================================================
        # Add 1st layer mesh data to the database dictionary 'mesh_data'
        #---------------------------------------------------------------------
        mesh_data = {}
        mesh_data[1]={}
        mesh_data[1]['nodeCoord'] = np.copy(node_coord)
        mesh_data[1]['elemNode'] = np.copy(elemtonodes)
        mesh_data[1]['elemidx'] = np.array(list(range(1,numElem+1))).astype('int64')
        mesh_data[1]['nodeidx'] = np.copy(nodeTags.astype('int64'))
        
        # To assert that there no duplicate elements sharing same nodes
        assert(len(mesh_data[1]['elemNode']) == 
               len(np.unique(mesh_data[1]['elemNode'],axis=0)))
        
        # Adding other layer mesh data to the database dictionary 'mesh_data'
        #---------------------------------------------------------------------
        for ply in range(2,numPly+1):
            mesh_data[ply]={}
            # Adding thickness to all z coordinates
            new_z = mesh_data[ply-1]['nodeCoord'][:,2] + LzPly 
            mesh_data[ply]['nodeCoord'] = np.transpose(np.vstack([mesh_data[ply-1]['nodeCoord'][:,0],mesh_data[ply-1]['nodeCoord'][:,1],new_z]))
            mesh_data[ply]['nodeCoord'] = np.round(mesh_data[ply]['nodeCoord'],16)
            mesh_data[ply]['elemidx'] = np.arange( max(mesh_data[ply-1]['elemidx'])+1, max(mesh_data[ply-1]['elemidx'])+1+numElem )
            mesh_data[ply]['nodeidx'] = np.arange( max(mesh_data[ply-1]['nodeidx'])+1, max(mesh_data[ply-1]['nodeidx'])+1+numNode )
            mesh_data[ply]['elemNode'] = np.copy(mesh_data[ply-1]['elemNode'] + numNode)
            
            # To assert that there no duplicate elements sharing same nodes
            assert(len(mesh_data[ply]['elemNode']) == len(np.unique(mesh_data[ply]['elemNode'],axis=0))) 
        print('Mesh generation ply complete...')   
        
        # Adding cohesive layers mesh data to the database dictionary 'mesh_data'
        #---------------------------------------------------------------------
        mesh_data[numPly+1] = {}
        elemnode_map = {}
        for layer in range(1,numCohElem+1):
            lower_ply = layer
            upper_ply = layer+1
            
            # nodes on upper surface of lower ply
            lower_nodes_lidx = np.where(mesh_data[lower_ply]['nodeCoord'][:,2] == max(mesh_data[lower_ply]['nodeCoord'][:,2]))[0]
            # Elemetonode uses global node index. Hence converting them back
            lower_node_gidx = mesh_data[lower_ply]['nodeidx'][lower_nodes_lidx]
            LowerPlyElements_lidx = []
            
            temp1 = np.in1d(mesh_data[lower_ply]['elemNode'][:,4],lower_node_gidx)            
            temp2 = np.in1d(mesh_data[lower_ply]['elemNode'][:,5],lower_node_gidx)
            temp3 = np.in1d(mesh_data[lower_ply]['elemNode'][:,6],lower_node_gidx)            
            temp4 = np.in1d(mesh_data[lower_ply]['elemNode'][:,7],lower_node_gidx)
            temp = temp1*temp2*temp3*temp4
            LowerPlyElements_lidx = np.where(temp)
            lowerply_node_gidx = mesh_data[lower_ply]['elemNode'][LowerPlyElements_lidx,4:][0]

            vround = 10
            if layer==1:
                upperply_elemnode_list = [] 
                for nodecoord_i in lowerply_node_gidx:
                    for nodei in nodecoord_i:
                        nodei_lidx = np.where(mesh_data[lower_ply]['nodeidx']==nodei)[0][0] # in local idx
                        
                        # getting node with similar coordinate as "nodei" in local index            
                        node_x = np.where(np.round(mesh_data[upper_ply]['nodeCoord'][:,0],vround)== np.round(mesh_data[lower_ply]['nodeCoord'][nodei_lidx][0],vround))[0]
                        node_y = node_x[np.where(np.round(mesh_data[upper_ply]['nodeCoord'][node_x,1],vround)== np.round(mesh_data[lower_ply]['nodeCoord'][nodei_lidx][1],vround))[0]]
                        node_z = node_y[np.where(np.round(mesh_data[upper_ply]['nodeCoord'][node_y,2],vround)== np.round(mesh_data[lower_ply]['nodeCoord'][nodei_lidx,2],vround))[0]]
                        
                        # getting global indices 
                        element_gidx = mesh_data[upper_ply]['nodeidx'][node_z][0]                       
                        upperply_elemnode_list.append(element_gidx)
                        
                # 4 nodes of upper layer element for hex elements  
                upperply_node_gidx = np.reshape(upperply_elemnode_list,(-1,4))
                
                # Creating map to be used for other layers
                node_map = np.vstack((upperply_node_gidx[:,0] - lowerply_node_gidx[:,0],               
                                      upperply_node_gidx[:,1] - lowerply_node_gidx[:,1],
                                      upperply_node_gidx[:,2] - lowerply_node_gidx[:,2],
                                      upperply_node_gidx[:,3] - lowerply_node_gidx[:,3],
                                      )).transpose()
            else:
                # Using map to get nodes of eleemnts of other layers
                upperply_node_gidx = lowerply_node_gidx + node_map                                      
                        
            new_layer_elemnode = np.hstack((lowerply_node_gidx,upperply_node_gidx))
            new_layer_elemnode = np.unique(new_layer_elemnode, axis=0)
            elemnode_map[layer] = new_layer_elemnode
            
            if layer == 1:
                new_layer_elemidx = np.arange( max(mesh_data[numPly]['elemidx'])+1, max(mesh_data[numPly]['elemidx'])+1+len(new_layer_elemnode) )
                mesh_data[numPly+1]['elemidx'] = new_layer_elemidx
                mesh_data[numPly+1]['elemNode'] = new_layer_elemnode
            else:
                new_layer_elemidx = np.arange( max(mesh_data[numPly+1]['elemidx'])+1, max(mesh_data[numPly+1]['elemidx'])+1+len(new_layer_elemnode) )
                mesh_data[numPly+1]['elemidx'] = np.hstack((mesh_data[numPly+1]['elemidx'],new_layer_elemidx))
                mesh_data[numPly+1]['elemNode'] = np.vstack((mesh_data[numPly+1]['elemNode'],new_layer_elemnode))
        
        # To ensure that there are no duplicate elements sharing same nodes
        assert(len(mesh_data[numPly+1]['elemNode']) == len(np.unique(mesh_data[numPly+1]['elemNode'],axis=0))) 
        print('Mesh generation cohesive layer complete...')
                
        #=====================================================================
        # Node Set: Creating node set for boundary conditions
        #=====================================================================
        node_list = {}
        # all nodes with x-coord <= 0.05
        kx1 = np.where(np.round(mesh_data[numPly]['nodeCoord'][:,0],15) <= clp)[0]
        # all nodes with z-coord == Lz
        kz1 = np.where(np.round(mesh_data[numPly]['nodeCoord'][:,2],15) >= round(Lz,16))[0] 
        clamp_set_1_local_idx = np.intersect1d(kx1,kz1)
        node_list[1] = mesh_data[numPly]['nodeidx'][clamp_set_1_local_idx]
        
        # all nodes with x-coord <= 0.05
        kx2 = np.where(np.round(mesh_data[1]['nodeCoord'][:,0],15) <= clp)[0]
        # all nodes with z-coord == 0
        kz2 = np.where(np.round(mesh_data[1]['nodeCoord'][:,2],15) <= 0)[0]
        clamp_set_2_local_idx= np.intersect1d(kx2,kz2)
        node_list[2] = mesh_data[1]['nodeidx'][clamp_set_2_local_idx]
        
        # all nodes with x-coord >= Ly-0.05
        kx3 = np.where(np.round(mesh_data[numPly]['nodeCoord'][:,0],15) >= Lx-clp)[0]
        # all nodes with z-coord = Lz
        kz3 = np.where(np.round(mesh_data[numPly]['nodeCoord'][:,2],15) >= round(Lz,15))[0]
        clamp_set_3_local_idx = np.intersect1d(kx3,kz3)
        node_list[3] = mesh_data[numPly]['nodeidx'][clamp_set_3_local_idx]
        
        # all nodes with x-coord >= Ly-0.05
        kx4 = np.where(np.round(mesh_data[1]['nodeCoord'][:,0],15) >= Lx-clp)[0]
        # all nodes with z-coord == 0
        kz4 = np.where(np.round(mesh_data[1]['nodeCoord'][:,2],15) <= 0)[0]
        clamp_set_4_local_idx = np.intersect1d(kx4,kz4)
        node_list[4] = mesh_data[1]['nodeidx'][clamp_set_4_local_idx]
        
        print("Node set complete ..")
        
        #=====================================================================
        # LS-Dyna file generation: creating database, in the form of string, 
        # to be added in the LS-Dyna keyword file
        #=====================================================================
    
        node_str = '*NODE\n'
        elem_str = """*ELEMENT_SOLID
        """
        numEntities = len(mesh_data)
        for ply in range(1,numEntities+1):
            # Node data
            if ply != numPly+1:
                node_data = np.hstack((np.reshape(mesh_data[ply]['nodeidx'],(-1,1)),
                                       mesh_data[ply]['nodeCoord']))
                node_str += '\n'.join(', '.join(str(cell) for cell in row) 
                                      for row in node_data)
                node_str += '\n'
                
            # solid elements
            elem_id = np.reshape(mesh_data[ply]['elemidx'],(-1,1))
            part_id = np.reshape(np.repeat(ply,len(elem_id)),(-1,1))
            node_coord =  mesh_data[ply]['elemNode']
            elem_data = np.hstack((elem_id,part_id,node_coord))
            elem_data.astype('int64')
            elem_str += '\n'.join(', '.join(str(int(cell)) for cell in row) 
                                  for row in elem_data)
            elem_str += "\n"
            
        # Node set 
        node_list_str_all = ''
        for node_list_id in node_list:
            node_list_str = f"""*SET_NODE_LIST
        {node_list_id}, 0.0, 0.0, 0.0, 0.0, 0.0, MECH
        """
            for i,node_i in enumerate(node_list[node_list_id]):
                node_list_str += str(node_i)
                if node_i != node_list[4][-1]:
                    if ((i+1)%8 == 0 or node_i==node_list[node_list_id][-1]):
                        node_list_str += "\n"
                    else:
                        node_list_str += ", "
                        
            node_list_str_all += node_list_str
            
        geo_str = node_str + '$#\n' + elem_str + '$#\n' + node_list_str_all
        
        # Adding generated string to the LS-Dyna keyword files and getting 
        # final string
        main_str = mainFile(geo_str)            # *END inserted here
        
        print("String generation complete...")    
        
        # Writing LS-Dyna keyword file
        with open(f'{file_dst}{filename}.k','w+') as mygeo:        
            mygeo.write(main_str)
        print("Writing file complete...")    
        
        # creating macro for keyword style conversion to new keyword style
        geo_macro_str = f"""*lsprepost macro command file
*macro begin macro_post
openc keyword "{file_dst}{filename}.k"

$# Deleteing unreferenced nodes
elemedit createnode accept
genselect target node
elemedit delenode delete
elemedit delenode accept 1
Build Rendering data
genselect clear

$# Saving keyword files as per new format
save keywordabsolute 0
save keywordbylongfmt 0
save keywordbyi10fmt 0
save outversion 10
save keyword specialsubsystem "{file_dst}{filename}.k" 1
*macro end
"""
        macro_filename = f"{filename}"
        print("Writing macro to location: ",file_dst)
        with open(f"{file_dst}{macro_filename}.cfile","w+") as my_geo_macro:
            my_geo_macro.write(geo_macro_str)
        
        # Converting the old keyword style to new keyword style using lsprepost
        print("Saving newly fomatted keyword to location: ",file_dst)
        cmd=f'"{lspp_loc}" -nographics c="{file_dst}{macro_filename}.cfile"'
        
        subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, 
                         stdout=subprocess.PIPE)
        
        time.sleep(20) 
    print('elapsed time', process_time() - start)

#%% Example
# loc = "D:\\Academics\\MasterThesisData\\DataAnalysis\\"
# create_geo(Rx              = 0.0024,
#             filename        = 'geo',
#             file_dst        = loc,
#             numCurveElem    = 10,#35,
#             numClampXElem   = 1,#4,
#             numMainbodyXElem= 5,#12,
#             numCSElem       = 10,#20,
#             )

