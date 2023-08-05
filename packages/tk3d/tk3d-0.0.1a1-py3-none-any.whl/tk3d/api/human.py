import pyglet
import ctypes
import os
from pyglet.gl import *
from time import time
from pywavefront import visualization

t0 = time()
rotation=0
def show_3d(meshes):
    global rotation
    window = pyglet.window.Window(1024, 720, caption='Demo')
    lightfv = ctypes.c_float * 4
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60., float(1024)/720, 1., 500.)
    glMatrixMode(GL_MODELVIEW)

    @window.event
    def on_resize(width, height):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60., float(width)/height, 1., 500.)
        glMatrixMode(GL_MODELVIEW)
        return True

    @window.event
    def on_draw():
        window.clear()
        glLoadIdentity()

        glLightfv(GL_LIGHT0, GL_POSITION, lightfv(-1.0, 1.0, 1.0, 0.0))
        glEnable(GL_LIGHT0)

        glTranslated(0, -10, -20)

        glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        glCullFace(GL_FRONT_AND_BACK)
        glRotatef(rotation, 0, 1, 0)

        glEnable(GL_LIGHTING)
        # meshes.draw()

        visualization.draw(meshes)
        # visualization.draw_materials(meshes.materials)

        # test
        #import pywavefront.material
        #root_path="tests/fixtures"
        #parser = MaterialParser(root_path+'/simple.mtl', strict=True)

        #visualization.draw_materials(parser.materials,textures_enabled=True)

    def update(dt):
        global rotation
        global t0

        dt = time()-t0
        t0 = time()
        rotation += 60*dt

    pyglet.clock.schedule(update)
    pyglet.app.run()


def show_object_human(object_file):
    global rotation
    rotation = 0
    from pywavefront import Wavefront
    scene = Wavefront(object_file,create_materials=True,collect_faces=True)
    scene.parse()
    # Iterate vertex data collected in each material
    for name, material in scene.materials.items():
        # Contains the vertex format (string) such as "T2F_N3F_V3F"
        # T2F, C3F, N3F and V3F may appear in this string
        print(name,material.vertex_format)
        # Contains the vertex list of floats in the format described above
        print(name,material.vertices)
        # Material properties
        print(name,material.diffuse)
        print(name,material.ambient)
        # print(name,material.texture.name)
        print()

    for face in scene.mesh_list:
        '''
        The first vertex list is the raw vertices from the obj file. 
        The second vertex list represents the interleaved vertex data with the format specified in the material. Faces will always be triangulized (no quads)
        '''
        print("Faces:", scene.mesh_list[0].faces)
        print("Vertices:", scene.vertices)
        print("Format:", scene.mesh_list[0].materials[0].vertex_format)
        print("Vertices:", scene.mesh_list[0].materials[0].vertices)

    print()
    for vertice in scene.vertices:
        print(vertice)
    # set

    # material.diffuse("hill.jpg")

    show_3d(scene)  # awesome 3D animation
    # some stuff
    # show_3d(mesh)  # awesome 3D animation