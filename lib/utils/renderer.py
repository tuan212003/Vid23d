import math
import trimesh
import pyrender
import numpy as np
from pyrender.constants import RenderFlags
from lib.models.smpl import get_smpl_faces


class WeakPerspectiveCamera(pyrender.Camera):
    def __init__(self,
                 scale,
                 translation,
                 znear=pyrender.camera.DEFAULT_Z_NEAR,
                 zfar=None,
                 name=None):
        super(WeakPerspectiveCamera, self).__init__(
            znear=znear,
            zfar=zfar,
            name=name,
        )
        self.scale = scale
        self.translation = translation

    def get_projection_matrix(self, width=None, height=None):
        P = np.eye(4)
        P[0, 0] = self.scale[0]
        P[1, 1] = self.scale[1]
        P[0, 3] = self.translation[0] * self.scale[0]
        P[1, 3] = -self.translation[1] * self.scale[1]
        P[2, 2] = -1
        return P


class Renderer:
    def __init__(self, resolution=(224,224), orig_img=False, wireframe=False):
        self.resolution = resolution

        self.faces = get_smpl_faces()
        self.orig_img = orig_img
        self.wireframe = wireframe
        self.renderer = pyrender.OffscreenRenderer(
            viewport_width=self.resolution[0],
            viewport_height=self.resolution[1],
            point_size=1.0
        )

        # set the scene
        self.scene = pyrender.Scene(bg_color=[0.0, 0.0, 0.0, 0.0], ambient_light=(0.3, 0.3, 0.3))

        light = pyrender.PointLight(color=[1.0, 1.0, 1.0], intensity=1)

        light_pose = np.eye(4)
        light_pose[:3, 3] = [0, -1, 1]
        self.scene.add(light, pose=light_pose)

        light_pose[:3, 3] = [0, 1, 1]
        self.scene.add(light, pose=light_pose)

        light_pose[:3, 3] = [1, 1, 2]
        self.scene.add(light, pose=light_pose)

    def render(self, img, verts, cam, angle=None, axis=None, mesh_filename=None, color=[1.0, 1.0, 0.9]):

        mesh = trimesh.Trimesh(vertices=verts, faces=self.faces, process=False)

        Rx = trimesh.transformations.rotation_matrix(math.radians(180), [1, 0, 0])
        mesh.apply_transform(Rx)

        if mesh_filename is not None:
            mesh.export(mesh_filename)

        if angle and axis:
            R = trimesh.transformations.rotation_matrix(math.radians(angle), axis)
            mesh.apply_transform(R)

        sx, sy, tx, ty = cam

        camera = WeakPerspectiveCamera(
            scale=[sx, sy],
            translation=[tx, ty],
            zfar=1000.
        )

        material = pyrender.MetallicRoughnessMaterial(
            metallicFactor=0.0,
            alphaMode='OPAQUE',
            baseColorFactor=(color[0], color[1], color[2], 1.0)
        )

        mesh = pyrender.Mesh.from_trimesh(mesh, material=material)

        mesh_node = self.scene.add(mesh, 'mesh')

        camera_pose = np.eye(4)
        cam_node = self.scene.add(camera, pose=camera_pose)

        if self.wireframe:
            render_flags = RenderFlags.RGBA | RenderFlags.ALL_WIREFRAME
        else:
            render_flags = RenderFlags.RGBA

        rgb, _ = self.renderer.render(self.scene, flags=render_flags)
        valid_mask = (rgb[:, :, -1] > 0)[:, :, np.newaxis]
        output_img = rgb[:, :, :-1] * valid_mask + (1 - valid_mask) * img
        image = output_img.astype(np.uint8)

        self.scene.remove_node(mesh_node)
        self.scene.remove_node(cam_node)

        return image
    
# import numpy as np
# import trimesh
# import math
# from pythreejs import *
# from IPython.display import display
# from lib.models.smpl import get_smpl_faces
# import matplotlib.pyplot as plt
# from PIL import Image
# import io

# class WeakPerspectiveCamera(PerspectiveCamera):
#     def __init__(self, scale, translation, **kwargs):
#         super(WeakPerspectiveCamera, self).__init__(**kwargs)
#         self.scale = scale
#         self.translation = translation

#     def get_projection_matrix(self):
#         P = np.eye(4)
#         P[0, 0] = self.scale[0]
#         P[1, 1] = self.scale[1]
#         P[0, 3] = self.translation[0] * self.scale[0]
#         P[1, 3] = -self.translation[1] * self.scale[1]
#         P[2, 2] = -1
#         return P

# class Renderer:
#     def __init__(self, resolution=(224, 224), orig_img=False, wireframe=False):
#         self.resolution = resolution
#         self.faces = get_smpl_faces()
#         self.orig_img = orig_img
#         self.wireframe = wireframe

#         self.scene = Scene(children=[], background=None)

#         light1 = PointLight(color='white', intensity=1, position=[0, -1, 1])
#         light2 = PointLight(color='white', intensity=1, position=[0, 1, 1])
#         light3 = PointLight(color='white', intensity=1, position=[1, 1, 2])
#         self.scene.add(light1)
#         self.scene.add(light2)
#         self.scene.add(light3)

#     def render(self, img, verts, cam, angle=None, axis=None, mesh_filename=None, color=[1.0, 1.0, 0.9]):
#         mesh = trimesh.Trimesh(vertices=verts, faces=self.faces, process=False)

#         Rx = trimesh.transformations.rotation_matrix(math.radians(180), [1, 0, 0])
#         mesh.apply_transform(Rx)

#         if mesh_filename is not None:
#             mesh.export(mesh_filename)

#         if angle and axis:
#             R = trimesh.transformations.rotation_matrix(math.radians(angle), axis)
#             mesh.apply_transform(R)

#         vertices = mesh.vertices
#         faces = mesh.faces

#         geometry = BufferGeometry(attributes={
#             'position': BufferAttribute(vertices, normalized=False),
#             'index': BufferAttribute(faces.flatten(), normalized=False)
#         })

#         material = MeshStandardMaterial(color=color, wireframe=self.wireframe)
#         mesh = Mesh(geometry=geometry, material=material)
#         self.scene.add(mesh)

#         sx, sy, tx, ty = cam
#         camera = WeakPerspectiveCamera(scale=[sx, sy], translation=[tx, ty], fov=50, aspect=self.resolution[0]/self.resolution[1], near=0.1, far=1000)
#         camera.position = [0, 0, 2]

#         controls = OrbitControls(controlling=camera)
#         renderer = Renderer(camera=camera, scene=self.scene, controls=[controls], width=self.resolution[0], height=self.resolution[1])

#         display(renderer)
#         # Render ra canvas để lấy ảnh
#         canvas = renderer.to_image()

#         # Chuyển canvas thành numpy array
#         buf = io.BytesIO()
#         canvas.save(buf, format='PNG')
#         buf.seek(0)
#         img_arr = np.array(Image.open(buf))

#         # Xóa mesh để tránh xung đột trong lần render tiếp theo
#         self.scene.remove(mesh)

#         return img_arr








