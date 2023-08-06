import numpy as np
import cv2
from multiprocessing.pool import ThreadPool
from .JSONBinaryEncoder import JSONBinaryEncoder
import os
from glob import glob
from pathlib import Path
from pyquaternion import Quaternion
from scale_lidar_io import Transform
from scale_lidar_io.helper import (
    format_lidar_point,
    format_point,
    format_quaternion,
    parse_xyz,
    parse_quaternion,
    )

encoder = JSONBinaryEncoder()
WORKERS = 4
FPS = 10

###########################
# From Scene to BS4
###########################

def get_points(scene, path):
    points = []
    intensities = []
    frame_offset = 0
    frame_offsets = []
    poses = []
    for frame_idx in range(0, len( scene.frames )):
        scene.get_frame(frame_idx).get_world_points()

        world_points = scene.get_frame(frame_idx).get_world_points()
        frame_points = np.float32(world_points[:, :3])
        point_intensities = np.float32(world_points[:, 3:4])
        assert len(frame_points) == len(point_intensities)
        print(f'Found {len(frame_points)} points for frame {frame_idx}')
        points.append(frame_points)
        intensities.append(point_intensities)
        frame_offsets.append(frame_offset)
        frame_offset += len(frame_points)

        device_pose = scene.get_frame(frame_idx).transform
        poses.append({
            'position': {
                'x': device_pose.translation[0],
                'y': device_pose.translation[1],
                'z': device_pose.translation[2]
            },
            'heading': {
                'x': device_pose.quaternion.x,
                'y': device_pose.quaternion.y,
                'z': device_pose.quaternion.z,
                'w': device_pose.quaternion.w
            }
        })

    encoder.write_file(f"{path}/scene_points.bs4", {
        'version': '4.0',
        'sensors': [{
            'type': 'lidar',
            'poses': poses,
            'points': {
                'positions': np.concatenate(points),
                'intensities': np.concatenate(intensities),
            },
            'frame_offsets': frame_offsets
        }]
    })


def process_video(output, frames, camera):
    print(f'Processing camera {camera.id}...')
    files = []
    width = frames[0].images[camera.id].get_image().width
    height = frames[0].images[camera.id].get_image().height
    for frame in frames:
        files.append(frame.images[camera.id].image_path)

    video_file = f'{output}/video_{camera.id}.mp4'
    fourcc = cv2.VideoWriter_fourcc(*'avc1')

    size = (width, height)

    out = cv2.VideoWriter(video_file, fourcc, FPS, size)

    for image_file in files:
        frame = cv2.imread(image_file)
        frame = cv2.resize(frame, size)
        out.write(frame)

    out.release()

    return video_file


def process_camera(scene, camera_name, path):
    camera_poses = []
    camera = scene.get_camera(camera_name)

    image_width = scene.frames[0].images[camera.id].get_image().width
    image_height = scene.frames[0].images[camera.id].get_image().height

    for frame_idx, frame in enumerate(scene.frames):
        if camera.world_poses:
            wct = camera.world_poses[frame.id]
        else:
            wct = frame.transform @ camera.pose

        camera_poses.append({
            'position': format_point(wct.position),
            'heading': format_quaternion(wct.quaternion)
        })

    video_file = process_video(path, scene.frames, camera)

    D = camera.D

    distortion = dict(
        model=camera.model,
        skew=camera.skew,
        k1=float(D[0]),
        k2=float(D[1]),
        p1=float(D[2]),
        p2=float(D[3]),
        k3=float(D[4]),
        k4=float(D[5]),
        k5=float(D[6]) if len(D) >= 7 else 0,
        k6=float(D[7]) if len(D) >= 8 else 0,
        scale_factor=camera.scale_factor,
    )
    cam_sensor = dict(
        type='camera',
        name=camera_name,
        fps=FPS,
        imageSize=dict(
            width=image_width,
            height=image_height
        ),
        poses=camera_poses,
        video=np.frombuffer(open(video_file, 'rb').read(), dtype=np.uint8),
        distortion=distortion,
        fx=int(camera.fx),
        fy=int(camera.fy),
        cx=int(camera.cx),
        cy=int(camera.cy)
    )

    return cam_sensor


def get_cameras(scene, path, camera_name="all"):
    if camera_name == "all":
        pool = ThreadPool(WORKERS)
        pool_input = [(scene, camera.id, path) for camera in scene.cameras]
        camera_sensors = pool.starmap(process_camera, pool_input)
    else:
        camera_sensors = [process_camera(scene, camera_name, path)]

    encoder.write_file(f'{ path }/scene_camera_{camera_name}.bs4', {
        'version': '4.0',
        'sensors': camera_sensors,
    })

    video_files = glob(f'{ path }/video_*.mp4')
    for video in video_files:
        os.remove(video)


def combine_scenes(camera_name, path, filename):
    cameras_scene = encoder.read_file(f'{ path }/scene_camera_{camera_name}.bs4')
    os.remove(f'{ path }/scene_camera_{camera_name}.bs4')

    points_scene = encoder.read_file(f"{ path }/scene_points.bs4")
    os.remove(f"{ path }/scene_points.bs4")

    out_file = f'{ path }/{filename}.bs4'
    encoder.write_file(out_file, {
        'version': '4.0',
        'sensors': cameras_scene['sensors'] + points_scene['sensors']
    })

###########################
# From BS4 to Scene
###########################

def load_bs4(scene, file):
    ''' Load point cloud / lidar sensor data '''
    f = open(file, 'rb')
    file_data = encoder.loads(f.read())
    path = os.path.dirname(f.name)
    scene_name = os.path.basename(f.name)
    for sensor in file_data['sensors']:
        if sensor['type'] == 'lidar':
            print('Loading poses')
            for idx, frame in enumerate(sensor['frame_offsets']):
                scene.get_frame(idx).apply_transform(Transform().from_Rt(
                    R=Quaternion(np.array(parse_quaternion(sensor['poses'][idx]['heading']))),
                    t=np.array(parse_xyz(sensor['poses'][idx]['position']))
                ))
                if 'points' in sensor:
                    range_frames = sensor['frame_offsets'][idx+1] if len(sensor['frame_offsets']) > idx+1 else len( sensor['points']['positions'] )
                    print(f'Loading points for frame {idx}')
                    points = np.array(sensor['points']['positions'][frame:range_frames])
                    if 'intensities' in sensor['points']:
                        points = np.c_[points, sensor['points']['intensities'][frame:range_frames]]
                    if 'device_ids' in sensor['points']:
                        points = np.c_[points, sensor['points']['device_ids'][frame:range_frames]]
                    # if 'colors' in sensor['points']: #TODO: implement color support
                    #     scene.get_frame(idx).add_colors()
                    scene.get_frame(idx).add_points(points, transform = scene.get_frame(idx).transform.inverse)

        if sensor['type'] == 'camera':
            print(f'Loading camera {sensor["name"]}')
            scene.get_camera(sensor['name']).calibrate(
                pose=Transform().from_Rt(
                    R=Quaternion(np.array(parse_quaternion(sensor['poses'][0]['heading']))),
                    t=np.array(parse_xyz( sensor['poses'][0]['position'] ))
                ),
                K=np.array([
                    [sensor['fx'], 0, sensor['cx']],
                    [0,sensor['fy'], sensor['cy']],
                    [0,0,1],
                ]),
                model=sensor['model'] if 'model' in sensor else 'brown_conrady',
                skew=sensor['distortion']['skew'],
                D= [
                    sensor['distortion']['k1'],
                    sensor['distortion']['k2'],
                    sensor['distortion']['p1'],
                    sensor['distortion']['p2'],
                    sensor['distortion']['k3'],
                    sensor['distortion']['k4'],
                    sensor['distortion']['k5'],
                    sensor['distortion']['k6']
                    ],
                )
            # first store the data as video
            f = open(f'{ path }/video_{sensor["name"]}.mp4', "wb")
            f.write(sensor['video'].tobytes())
            f.close()
            # then conver the video in images per frame
            vidcap = cv2.VideoCapture(f'{ path }/video_{sensor["name"]}.mp4')
            success,image = vidcap.read()
            count = 0
            Path(f"{ path }/images-{scene_name}/video_{sensor['name']}").mkdir(parents=True, exist_ok=True)
            while success:
                cv2.imwrite(f"{ path }/images-{scene_name}/video_{sensor['name']}/{count}.jpg", image)
                success,image = vidcap.read()
                scene.get_frame(count).get_image(sensor['name']).load_file(f"{ path }/images-{scene_name}/video_{sensor['name']}/{count}.jpg") # store the images
                count += 1
            os.remove(f'{ path }/video_{sensor["name"]}.mp4') # delete the video
        # if sensor['type'] == 'annotation':
            # TODO: load annotations
