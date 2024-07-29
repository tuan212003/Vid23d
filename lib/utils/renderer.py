# import math
# import trimesh
# import pyrender
# import numpy as np
# from pyrender.constants import RenderFlags
# from lib.models.smpl import get_smpl_faces


# class WeakPerspectiveCamera(pyrender.Camera):
#     def __init__(self,
#                  scale,
#                  translation,
#                  znear=pyrender.camera.DEFAULT_Z_NEAR,
#                  zfar=None,
#                  name=None):
#         super(WeakPerspectiveCamera, self).__init__(
#             znear=znear,
#             zfar=zfar,
#             name=name,
#         )
#         self.scale = scale
#         self.translation = translation

#     def get_projection_matrix(self, width=None, height=None):
#         P = np.eye(4)
#         P[0, 0] = self.scale[0]
#         P[1, 1] = self.scale[1]
#         P[0, 3] = self.translation[0] * self.scale[0]
#         P[1, 3] = -self.translation[1] * self.scale[1]
#         P[2, 2] = -1
#         return P


# class Renderer:
#     def __init__(self, resolution=(224,224), orig_img=False, wireframe=False):
#         self.resolution = resolution

#         self.faces = get_smpl_faces()
#         self.orig_img = orig_img
#         self.wireframe = wireframe
#         self.renderer = pyrender.OffscreenRenderer(
#             viewport_width=self.resolution[0],
#             viewport_height=self.resolution[1],
#             point_size=1.0
#         )

#         # set the scene
#         self.scene = pyrender.Scene(bg_color=[0.0, 0.0, 0.0, 0.0], ambient_light=(0.3, 0.3, 0.3))

#         light = pyrender.PointLight(color=[1.0, 1.0, 1.0], intensity=1)

#         light_pose = np.eye(4)
#         light_pose[:3, 3] = [0, -1, 1]
#         self.scene.add(light, pose=light_pose)

#         light_pose[:3, 3] = [0, 1, 1]
#         self.scene.add(light, pose=light_pose)

#         light_pose[:3, 3] = [1, 1, 2]
#         self.scene.add(light, pose=light_pose)

#     def render(self, img, verts, cam, angle=None, axis=None, mesh_filename=None, color=[1.0, 1.0, 0.9]):

#         mesh = trimesh.Trimesh(vertices=verts, faces=self.faces, process=False)

#         Rx = trimesh.transformations.rotation_matrix(math.radians(180), [1, 0, 0])
#         mesh.apply_transform(Rx)

#         if mesh_filename is not None:
#             mesh.export(mesh_filename)

#         if angle and axis:
#             R = trimesh.transformations.rotation_matrix(math.radians(angle), axis)
#             mesh.apply_transform(R)

#         sx, sy, tx, ty = cam

#         camera = WeakPerspectiveCamera(
#             scale=[sx, sy],
#             translation=[tx, ty],
#             zfar=1000.
#         )

#         material = pyrender.MetallicRoughnessMaterial(
#             metallicFactor=0.0,
#             alphaMode='OPAQUE',
#             baseColorFactor=(color[0], color[1], color[2], 1.0)
#         )

#         mesh = pyrender.Mesh.from_trimesh(mesh, material=material)

#         mesh_node = self.scene.add(mesh, 'mesh')

#         camera_pose = np.eye(4)
#         cam_node = self.scene.add(camera, pose=camera_pose)

#         if self.wireframe:
#             render_flags = RenderFlags.RGBA | RenderFlags.ALL_WIREFRAME
#         else:
#             render_flags = RenderFlags.RGBA

#         rgb, _ = self.renderer.render(self.scene, flags=render_flags)
#         valid_mask = (rgb[:, :, -1] > 0)[:, :, np.newaxis]
#         output_img = rgb[:, :, :-1] * valid_mask + (1 - valid_mask) * img
#         image = output_img.astype(np.uint8)

#         self.scene.remove_node(mesh_node)
#         self.scene.remove_node(cam_node)

#         return image

import math
import trimesh
import open3d as o3d
import numpy as np
from lib.models.smpl import get_smpl_faces

class WeakPerspectiveCamera:
    def __init__(self, scale, translation, znear=0.1, zfar=1000.0):
        self.scale = scale
        self.translation = translation
        self.znear = znear
        self.zfar = zfar

    def get_projection_matrix(self, width=None, height=None):
        P = np.eye(4)
        P[0, 0] = self.scale[0]
        P[1, 1] = self.scale[1]
        P[0, 3] = self.translation[0] * self.scale[0]
        P[1, 3] = -self.translation[1] * self.scale[1]
        P[2, 2] = -1
        P[2, 3] = -self.znear
        return P

class Renderer:
    def __init__(self, resolution=(224, 224), orig_img=False, wireframe=False):
        self.resolution = resolution
        self.faces = get_smpl_faces()
        self.orig_img = orig_img
        self.wireframe = wireframe

    def render(self, img, verts, cam, angle=None, axis=None, mesh_filename=None, color=[1.0, 1.0, 0.9]):
        # Create trimesh object
        mesh = trimesh.Trimesh(vertices=verts, faces=self.faces, process=False)
        
        # Apply rotation if needed
        if angle and axis:
            R = trimesh.transformations.rotation_matrix(math.radians(angle), axis)
            mesh.apply_transform(R)
        
        # Apply transformation to align the mesh
        Rx = trimesh.transformations.rotation_matrix(math.radians(180), [1, 0, 0])
        mesh.apply_transform(Rx)
        
        # Save mesh if filename is provided
        if mesh_filename is not None:
            mesh.export(mesh_filename)
        
        # Convert trimesh to open3d mesh
        vertices = np.array(mesh.vertices)
        triangles = np.array(mesh.faces)
        o3d_mesh = o3d.geometry.TriangleMesh()
        o3d_mesh.vertices = o3d.utility.Vector3dVector(vertices)
        o3d_mesh.triangles = o3d.utility.Vector3iVector(triangles)
        o3d_mesh.paint_uniform_color(color)

        # Set up the camera
        camera = WeakPerspectiveCamera(scale=[cam[0], cam[1]], translation=[cam[2], cam[3]])
        intrinsics = camera.get_projection_matrix(self.resolution[0], self.resolution[1])
        intrinsics = np.linalg.inv(intrinsics[:3, :3])  # Convert to Open3D's format
        extrinsics = np.eye(4)

        # Create scene
        vis = o3d.visualization.Visualizer()
        vis.create_window(width=self.resolution[0], height=self.resolution[1])
        vis.add_geometry(o3d_mesh)
        
        # Set camera
        ctr = vis.get_view_control()
        parameters = o3d.camera.PinholeCameraParameters()
        parameters.intrinsic = o3d.camera.PinholeCameraIntrinsic(self.resolution[0], self.resolution[1], intrinsics[0, 0], intrinsics[1, 1], intrinsics[0, 2], intrinsics[1, 2])
        parameters.extrinsic = extrinsics
        ctr.convert_from_pinhole_camera_parameters(parameters)
        
        # Render image
        vis.poll_events()
        vis.update_renderer()
        image = vis.capture_screen_float_buffer(do_render=True)
        vis.destroy_window()

        # Convert image from float to uint8
        output_img = np.asarray(image) * 255.0
        output_img = output_img.astype(np.uint8)
        
        # Merge with original image
        if self.orig_img:
            valid_mask = (output_img[:, :, -1] > 0)[:, :, np.newaxis]
            output_img = output_img[:, :, :-1] * valid_mask + (1 - valid_mask) * img
        
        return output_img


