from vispy import scene, io

def show_object(model_file):
    canvas = scene.SceneCanvas(keys='interactive', show=True)
    view = canvas.central_widget.add_view()

    # model_file = "data/Chess set.obj"

    verts, faces, normals, nothing = io.read_mesh(model_file)

    mesh = scene.visuals.Mesh(vertices=verts, faces=faces, shading='smooth')

    view.add(mesh)

    view.camera = scene.TurntableCamera()
    view.camera.depth_value = 10

    canvas.app.run()