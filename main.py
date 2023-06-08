from controller import *
from LX16A import *
import time 
import os 
import pyrealsense2.pyrealsense2 as rs
import math as m

np.random.seed(2023)




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

    pitch =  -m.asin(2.0 * (x*z - w*y)) * 180.0 / m.pi
    roll  =  m.atan2(2.0 * (w*x + y*z), w*w - x*x - y*y + z*z) * 180.0 / m.pi
    yaw   =  m.atan2(2.0 * (w*z + x*y), w*w + x*x - y*y - z*z) * 180.0 / m.pi
    # yaw: right +
    # roll: right +
    # pitch: upper + 
    return [cam_data.translation.x,cam_data.translation.z,cam_data.translation.y, roll, pitch, yaw]


def norm_act(cmds_):
    # cmds: -1,1
    cmds = np.asarray(cmds_)
    assert ( cmds <= 1. ).all() and ( cmds >= -1. ).all(),'ERROR: cmds wrong, should between -1 and 1'

    cmds[6:13] = - cmds[6:13]

    cmds[1] *= -1
    cmds[3:5] *= -1

    cmds[6:8] *=-1
    cmds[10] *=-1


    # cmds = cmds*((870-130)/2) + 500 # +-90
    cmds = cmds*((870-130)/3) + 500 # +-60  

    return cmds.astype(int)


def act_cmds(cmds_):
    cmds = norm_act(cmds_)
    for i in range(12):
        lx16_control.moveServo(i+10,cmds[i],rate=100)
def read_pos():
    pos = []
    for i in range(12):
        pos.append(lx16_control.readPosition(i+10))
    return pos

if __name__ == '__main__':
    robot_name = "10_9_3_11_6_0_1_0_9_0_11_0_14_3_9_1"

    time_step = 0.11623673115395303
    para_config = np.loadtxt('para_config.csv')
    log_path = 'log/log_real_10/'
    os.makedirs(log_path, exist_ok = True)


    initial_para = para_config[:,0]
    para_range = para_config[:,1:]

    # initial_moving_joints_angle = [0]*12
    init_q = np.loadtxt('robot_urdf/%s/%s.txt'%(robot_name,robot_name))
    init_q = init_q[0] if len(init_q.shape) == 2 else init_q
    joint_moving_idx = [1, 2, 3, 6, 7, 8, 11, 12, 13, 16, 17, 18]
    initial_moving_joints_angle = np.asarray([3 / np.pi * init_q[idx] for idx in joint_moving_idx])
    # initial_moving_joints_angle[1] *= -1
    # initial_moving_joints_angle[3:5] *= -1

    # initial_moving_joints_angle[6:8] *=-1
    # initial_moving_joints_angle[10] *=-1

    # cmds[1],cmds[4],cmds[7],cmds[10] = [-1]*4
    # cmds[2],cmds[5],cmds[8],cmds[11] = [-1]*4
    act_cmds(initial_moving_joints_angle)
    time.sleep(2)
    init_pos = read_pos()

    POLICY = 1 
    
    #10_9_9_6_11_9_9_6_13_3_3_6_14_3_3_6
    action_para_list = np.loadtxt('data/robot_sign_data/%s/action_para_list.csv'%robot_name)

    step_num = 20
    query_state_after_N_step = 1
    log_pos = []
    log_action = []
    log_state = []

    try:
        for step_i in range(step_num):
            if POLICY == 0:
                norm_space = np.random.sample(len(initial_para))
                a_para = norm_space * (para_range[:, 1] - para_range[:, 0]) + para_range[:, 0]
            elif POLICY == 1:
                a_para = action_para_list[step_i]
            else:
                a_para = None
                quit()

            time0 = time.time()
            for ti in range(16):
                a_add = sin_move(ti, a_para)
                a = initial_moving_joints_angle + a_add

                a = np.clip(a, -1, 1)
                act_cmds(a)

                # time

                time1 = time.time()
                time.sleep(time_step-(time1-time0))
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
    np.savetxt(log_path+'a.csv',np.asarray(log_action))
    np.savetxt(log_path+'state.csv',np.asarray(log_state))


