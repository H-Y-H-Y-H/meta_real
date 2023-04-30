#!/usr/bin/python
# -*- coding: utf-8 -*-


def get_state_data(cam_data):
    # Euler angles from pose quaternion
    # See also https://github.com/IntelRealSense/librealsense/issues/5178#issuecomment-549795232
    # and https://github.com/IntelRealSense/librealsense/issues/5178#issuecomment-550217609

    w = cam_data.rotation.w
    x = -cam_data.rotation.z
    y = cam_data.rotation.x
    z = -cam_data.rotation.y

    pitch =  -m.asin(2.0 * (x*z - w*y)) * 180.0 / m.pi;
    roll  =  m.atan2(2.0 * (w*x + y*z), w*w - x*x - y*y + z*z) * 180.0 / m.pi;
    yaw   =  m.atan2(2.0 * (w*z + x*y), w*w + x*x - y*y - z*z) * 180.0 / m.pi;
    
    # print("Frame #{}".format(pose.frame_number))
    # print("RPY [deg]: Roll: {0:.7f}, Pitch: {1:.7f}, Yaw: {2:.7f}".format(roll, pitch, yaw))
    # print(cam_data.translation)

    # yaw: right +
    # roll: right +
    # pitch: upper + 
    return [cam_data.translation.x,cam_data.translation.z,cam_data.translation.y, roll, pitch, yaw]


if __name__ == '__main__':
    import pyrealsense2.pyrealsense2 as rs
    import math as m
    import time
    # Declare RealSense pipeline, encapsulating the actual device and sensors
    pipe = rs.pipeline()

    # Build config object and request pose data
    cfg = rs.config()
    cfg.enable_stream(rs.stream.pose)

    # Start streaming with requested config
    pipe.start(cfg)


    try:
        while (True):
            time0 = time.time()
            # Wait for the next set of frames from the camera
            frames = pipe.wait_for_frames()

            # Fetch pose frame
            pose = frames.get_pose_frame()
            if pose:
                # Print some of the pose data to the terminal
                data = pose.get_pose_data()
                state_data = get_state_data(data)

                print(state_data)
            time1 = time.time()
            print(time1-time0)
            

    finally:
        pipe.stop()
