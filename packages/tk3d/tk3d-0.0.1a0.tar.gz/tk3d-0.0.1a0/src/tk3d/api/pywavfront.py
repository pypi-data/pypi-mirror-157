import ratcave as rc
import pyglet
from pyglet.window import key
import ctypes
import os
from pyglet.gl import *

from pywavefront import visualization
import pywavefront

def get_object_keys(obj_filename):
    '''
        get object keys from an object file
    '''
    # obj_filename="objects/Bulldozer.obj"
    obj_reader = rc.WavefrontReader(obj_filename)

    list_object_keys=obj_reader.bodies.keys()
    return list_object_keys

def show_object(obj_filename,object_key="Object.1",xyz=(0,1,-2)):
    '''
        show 3d object in window
    '''
    # obj_filename = "objects/Bulldozer.obj"
    # Create Window
    window = pyglet.window.Window()

    def update(dt):
        pass

    pyglet.clock.schedule(update)

    # Insert filename into WavefrontReader.
    # obj_filename = rc.resources.obj_primitives
    obj_reader = rc.WavefrontReader(obj_filename)
    print(obj_reader.bodies.keys())

    # Create Mesh
    monkey = obj_reader.get_mesh(object_key)
    monkey.position.xyz = xyz

    # Create Scene
    scene = rc.Scene(meshes=[monkey])

    @window.event
    def on_draw():
        with rc.default_shader:
            scene.draw()

    pyglet.app.run()


def show_object_window(obj_filename,list_obj_key,list_position,scale=0.1,bgcolor=(0.5,0.5,0.5)):
    '''
        show object in pyglet.window
    '''
    # obj_filename = "objects/Bulldozer.obj"

    # Create Window and Add Keyboard State Handler to it's Event Loop
    window = pyglet.window.Window()
    keys = key.KeyStateHandler()
    window.push_handlers(keys)

    # Insert filename into WavefrontReader.
    # obj_filename = rc.resources.obj_primitives
    obj_reader = rc.WavefrontReader(obj_filename)
    print(obj_reader.bodies.keys())
    # Create Mesh
    list_object=[]
    for idx,k in enumerate(list_object):
        list_object.append(obj_reader.get_mesh(list_obj_key[idx], position=list_position[idx], scale=scale))


    # Create Scene
    scene = rc.Scene(meshes=list_object)
    scene.bgColor = bgcolor

    # scene.camera=rc.Camera(position=(1, 1,0), rotation=(-90, 0, 0), z_far=6)

    # Functions to Run in Event Loop
    def rotate_meshes(dt):
        for obj in list_object:
            obj.rotation. x += 80 * dt
            obj.rotation.y += 15 * dt
        # monkey.rotation.y += 15 * dt  # dt is the time between frames
        # torus.rotation.x += 80 * dt

    pyglet.clock.schedule(rotate_meshes)

    @window.event
    def on_resize(width, height):
        scene.camera.aspect = width / float(height)

    def move_camera(dt):
        camera_speed = 1
        if keys[key.LEFT]:
            scene.camera.position.x -= camera_speed * dt
        if keys[key.RIGHT]:
            scene.camera.position.x += camera_speed * dt

    pyglet.clock.schedule(move_camera)

    @window.event
    def on_draw():
        with rc.default_shader:
            scene.draw()

    pyglet.app.run()

rotation=0


def show_object_window_gl(obj_filename):
    '''
        show 3d object in rotation view
    '''
    global rotation

    # Create absolute path from this module


    rotation = 0
    meshes = pywavefront.Wavefront(obj_filename)
    window = pyglet.window.Window(resizable=True)
    lightfv = ctypes.c_float * 4

    @window.event
    def on_resize(width, height):
        viewport_width, viewport_height = window.get_size()
        glViewport(0, 0, viewport_width, viewport_height)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60., float(width) / height, 1., 100.)
        glMatrixMode(GL_MODELVIEW)
        return True

    @window.event
    def on_draw():
        window.clear()
        glLoadIdentity()

        glLightfv(GL_LIGHT0, GL_POSITION, lightfv(-1.0, 1.0, 1.0, 0.0))
        glEnable(GL_LIGHT0)

        glTranslated(0.0, 0.0, -100)
        glRotatef(rotation, 0.0, 1.0, 0.0)
        # glRotatef(-25.0, 1.0, 0.0, 0.0)
        glRotatef(45.0, 0.0, 0.0, 1.0)

        glEnable(GL_LIGHTING)

        visualization.draw(meshes)

    def update(dt):
        global rotation
        print("rotation = ",rotation)
        rotation += 90.0 * dt

        if rotation > 720.0:
            rotation = 0.0


    pyglet.clock.schedule(update)
    pyglet.app.run()