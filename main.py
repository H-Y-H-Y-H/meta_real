from controller import *
from LX16A import *
import time 
import os 
import pyrealsense2.pyrealsense2 as rs
import math as m


lx16_control = LX16A()
# Declare RealSense pipeline, encapsulating the actual device and sensors
pipe = rs.pipeline()

# Build config object and request pose data
cfg = rs.config()
cfg.enable_stream(rs.stream.pose)

# Start streaming with requested config
pipe.start(cfg)


def get_state_data(cam_data):
    w = cam_data.rotation.w
    x = -cam_data.rotation.z
    y = cam_data.rotation.x
    z = -cam_data.rotation.y

    pitch =  -m.asin(2.0 * (x*z - w*y)) * 180.0 / m.pi;
    roll  =  m.atan2(2.0 * (w*x + y*z), w*w - x*x - y*y + z*z) * 180.0 / m.pi;
    yaw   =  m.atan2(2.0 * (w*z + x*y), w*w + x*x - y*y - z*z) * 180.0 / m.pi;
    # yaw: right +
    # roll: right +
    # pitch: upper + 
    return [cam_data.translation.x,cam_data.translation.z,cam_data.translation.y, roll, pitch, yaw]


def norm_act(cmds):
    cmds = np.asarray(cmds)
    assert ( cmds <= 1. ).all() and ( cmds >= -1. ).all(),'ERROR: cmds wrong, should between -1 and 1'


    cmds[7:9],cmds[10:13] = -cmds[7:9], -cmds[10:13]

    # cmds = cmds*((870-130)/2) + 500 # +-90
    cmds = cmds*((870-130)/3) + 500 # +-60  

    return cmds.astype(int)


def act_cmds(cmds):
    cmds = norm_act(cmds)
    for i in range(12):
        lx16_control.moveServo(i+10,cmds[i],rate=150)

def read_pos():
    pos = []
    for i in range(12):
        pos.append(lx16_control.readPosition(i+10))
    return pos

if __name__ == '__main__':

    para_config = np.loadtxt('para_config.csv')
    log_path = 'log/'
    os.makedirs(log_path,exist_ok = True)


    initial_para = para_config[:,0]
    para_range = para_config[:,1:]

    initial_moving_joints_angle = [0]*12
    # cmds[1],cmds[4],cmds[7],cmds[10] = [-1]*4
    # cmds[2],cmds[5],cmds[8],cmds[11] = [-1]*4
    act_cmds(initial_moving_joints_angle)
    time.sleep(1)
    init_pos = read_pos()


    step_num = 2
    query_state_after_N_step = 1
    log_pos = []
    log_action = []
    log_state = []
    try:
        for step_i in range(step_num):
            norm_space = np.random.sample(len(initial_para))
            a_para = norm_space * (para_range[:,1]-para_range[:,0]) + para_range[:,0]
            time0 = time.time()
            for ti in range(1,17):
                a_add = sin_move(ti, a_para)
                a = initial_moving_joints_angle + a_add
                a = np.clip(a, -1, 1)
                act_cmds(a)

                # time

                time1 = time.time()
                time.sleep(0.125-(time1-time0))
                print('time_used',time1-time0)
                time0 = time.time()

                # log pos action
                log_pos.append(read_pos())
                log_action.append(a)
                
                #imu:
                pose = pipe.wait_for_frames().get_pose_frame()
                data = pose.get_pose_data()
                state_data = get_state_data(data)
                log_state.append(state_data)

    finally:
        pipe.stop()
        
    np.savetxt(log_path+'joint_pos.csv',np.asarray(log_pos))
    np.savetxt(log_path+'a.csv',np.asarray(a))
    np.savetxt(log_path+'state.csv',np.asarray(log_state))


                