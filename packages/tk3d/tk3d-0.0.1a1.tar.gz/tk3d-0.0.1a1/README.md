## 3D Modeling Toolkit
A toolkit integrating multiple 3D modeling libraries to support rapid use of 3d models

### Examples
#### Part 1: The use of `pywavefront`

First, determine an object file path: 
```python
    from tk3d.api.pywavfront import *
    object_filename="data/objects/Bulldozer.obj"
```
Example 1: get object keys from an object file
```python
    list_object_keys=get_object_keys(object_filename)
    print("List of object keys: ",list_object_keys)
```

Example 2:  show 3d object in window
```python
    show_object(object_filename,object_key="Object.1",xyz=(0,1,-2))
```

Example 3: show object in pyglet.window
```python
 show_object_window(obj_filename=object_filename,
                       list_obj_key=["Object.1","Object.2"],
                       list_position=[(0, 0, -1.5),(0, 0, -1.5)],
                       scale=0.01,
                       bgcolor=(0.5,0.5,0.5)
                       )
```

Example 4: show 3d object in rotation view
```python
    show_object_window_gl(obj_filename=object_filename)
```

#### Part 2: The use of `vispy`

```python
import tk3d.api.vispyapi as vis
vis.show_object(model_file="data/objects/Chess set.obj")
```

#### Part 3: Show human body 3d model

```python
from tk3d.api.human import *
object_filepath="data/objects/standard-male-figure.obj"
show_object_human(object_file=object_filepath)
```

#### Part 4: The use of `open3d`

```python
from tk3d.api.open3dapi import *
ply_filepath="data/ply/tet.ply"
# Example 1
show_ply(ply_filename=ply_filepath)
# Example 2
ply_filepath="data/ply/Hand.ply"
show_pointcloud(ply_filename=ply_filepath)
# Example 3
ply_filepath="data/ply/Hand.ply"
paint_points_knn(ply_filename=ply_filepath,uniform_color=[0.5,0.4,0.5],point_id=1500,point_num=200,target_color=[0.5,0,0.5])
# Example 4
ply_filepath="data/ply/Hand.ply"
paint_points_radius(ply_filename=ply_filepath,uniform_color=[0.5,0.4,0.5],point_id=1500,radius=10,target_color=[0,1,0])
# Example 5
ply_filepath="data/ply/Hand.ply"
paint_point(ply_filename=ply_filepath,point_id=1500,target_color=[0,1,0])
# Example 6
ply_filepath="data/ply/Hand.ply"
paint_points(ply_filename=ply_filepath,list_point_id=[1,2,3,4,5],list_target_color=[[0,1,0],[0,1,0],[0,1,0],[0,1,0],[0,1,0]])
```

### Credits

- [Open3D](https://github.com/isl-org/Open3D)

- [PyWaveFront](https://github.com/pywavefront/PyWavefront)

- [vispy](https://github.com/vispy/vispy)

### License

The `tk3d` toolkit is provided by [Donghua Chen](https://github.com/dhchenx) with MIT License.

