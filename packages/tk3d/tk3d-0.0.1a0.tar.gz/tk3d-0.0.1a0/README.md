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

### License

The `tk3d` toolkit is provided by [Donghua Chen](https://github.com/dhchenx) with MIT License.

