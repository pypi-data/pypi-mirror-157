from mayavi import mlab
from plyfile import PlyData
import numpy as np
import open3d as o3d

def plot(ply):
    '''
    Plot vertices and triangles from a PlyData instance. Assumptions:
        `ply' has a 'vertex' element with 'x', 'y', and 'z'
            properties;
        `ply' has a 'face' element with an integral list property
            'vertex_indices', all of whose elements have length 3.
    '''
    vertex = ply['vertex']

    (x, y, z) = (vertex[t] for t in ('x', 'y', 'z'))

    mlab.points3d(x, y, z, color=(1, 1, 1), mode='point')

    if 'face' in ply:
        tri_idx = ply['face']['vertex_indices']
        triangles = np.vstack(tri_idx)
        mlab.triangular_mesh(x, y, z, triangles,
                             color=(1, 0, 0.4), opacity=0.5)

def show_ply(ply_filename):
    '''
    Example script illustrating plotting of PLY data using Mayavi.  Mayavi
    is not a dependency of plyfile, but you will need to install it in order
    to run this script.  Failing to do so will immediately result in
    ImportError.
    '''
    # ply_filename = "data/tet.ply"
    mlab.figure(bgcolor=(0, 0, 0))
    plot(PlyData.read(ply_filename))
    mlab.show()

def show_pointcloud(ply_filename):
    '''
    show the point cloud of 3d model
    :param ply_filename:
    :return:
    '''
    mesh = o3d.io.read_point_cloud(ply_filename)
    vis = o3d.visualization.Visualizer()
    vis.create_window()
    vis.add_geometry(mesh)
    vis.run()
    vis.destroy_window()

def paint_points_knn(ply_filename,uniform_color=[0.5,0.5,0.5],point_id=1,point_num=200,target_color=[0,0,1],window_name="TK3D"):
    '''
    paint some points with KNN given point_id
    :param ply_filename:
    :param uniform_color:
    :param point_id:
    :param point_num:
    :param target_color:
    :param window_name:
    :return:
    '''
    # print("Testing IO for point cloud ...")
    # pcd = o3d.io.read_point_cloud(ply_filename)
    # print(pcd)  # 可以打印这个点云的点数
    # o3d.io.write_point_cloud("data/Hand.pcd", pcd)

    print("Load a ply point cloud, print it, and render it")
    pcd = o3d.io.read_point_cloud(ply_filename)
    print(pcd)
    print(np.asarray(pcd.points))

    print("Find its 200 nearest neighbors, paint blue.")
    pcd.paint_uniform_color(uniform_color)
    pcd_tree = o3d.geometry.KDTreeFlann(pcd)
    [k, idx, _] = pcd_tree.search_knn_vector_3d(pcd.points[point_id], point_num)
    np.asarray(pcd.colors)[idx[1:], :] = target_color

    o3d.visualization.draw_geometries([pcd],window_name=window_name)

def paint_points_radius(ply_filename,uniform_color=[0.5,0.5,0.5],point_id=1,radius=10,target_color=[0,1,0],window_name="TK3D"):
    '''
    paint points in radius of the selected point id
    :param ply_filename:
    :param uniform_color:
    :param point_id:
    :param radius:
    :param target_color:
    :param window_name:
    :return:
    '''
    print("Load a ply point cloud, print it, and render it")
    pcd = o3d.io.read_point_cloud(ply_filename)
    print(pcd)
    print(np.asarray(pcd.points))

    pcd.paint_uniform_color(uniform_color)
    pcd_tree = o3d.geometry.KDTreeFlann(pcd)

    print("Find its neighbors with distance less than 0.2, paint green.")
    [k, idx, _] = pcd_tree.search_radius_vector_3d(pcd.points[point_id], radius)
    np.asarray(pcd.colors)[idx[1:], :] = target_color

    print("Visualize the point cloud.")
    o3d.visualization.draw_geometries([pcd],window_name=window_name)
    print("")

def paint_point(ply_filename,uniform_color=[0.5,0.5,0.5],point_id=0,target_color=[1,0,0],window_name="TK3D"):
    '''
    paint one point given point_id
    :param ply_filename:
    :param uniform_color:
    :param point_id:
    :param target_color:
    :param window_name:
    :return:
    '''
    pcd = o3d.io.read_point_cloud(ply_filename)
    print(pcd)
    print(np.asarray(pcd.points))

    print("Find its 200 nearest neighbors, paint blue.")
    pcd.paint_uniform_color(uniform_color)

    print("Paint the 1500th point red.")
    pcd.colors[point_id] = target_color

    o3d.visualization.draw_geometries([pcd],window_name=window_name)

def paint_points(ply_filename,list_point_id,list_target_color,uniform_color=[0.5,0.5,0.5],window_name="TK3D"):
    '''
    paint a series of points given a series of point ids
    :param ply_filename:
    :param list_point_id:
    :param list_target_color:
    :param uniform_color:
    :param window_name:
    :return:
    '''
    pcd = o3d.io.read_point_cloud(ply_filename)
    print(pcd)
    print(np.asarray(pcd.points))

    print("Find its 200 nearest neighbors, paint blue.")
    pcd.paint_uniform_color(uniform_color)

    print("Paint the 1500th point red.")
    for idx,point_id in enumerate(list_point_id):
        pcd.colors[point_id] = list_target_color[idx]

    o3d.visualization.draw_geometries([pcd],window_name=window_name)


