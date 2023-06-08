import os
import math as m
import time
import pybullet_data as pd
import gym
import torch
from search_para.controller import *
import numpy as np

random.seed(2023)
np.random.seed(2023)
torch.manual_seed(2023)


class meta_sm_Env(gym.Env):
    def __init__(self, init_q, robot_camera=False, urdf_path='CAD2URDF'):

        self.stateID = None
        self.robotid = None
        self.v_p = None
        self.q = None
        self.p = None
        # self.last_q = None
        self.last_p = None
        self.obs = [0] * 18
        self.mode = p.POSITION_CONTROL

        self.sleep_time = 0  # decrease the value if it is too slow.

        self.maxVelocity = 1.5  # lx-224 0.20 sec/60degree = 5.236 rad/s
        self.force = 1.8

        # self.max_velocity = 1.8
        # self.force = 1.6

        self.n_sim_steps = 30
        self.motor_action_space = np.pi / 3
        self.urdf_path = urdf_path
        self.camera_capture = False
        self.robot_camera = robot_camera
        self.friction = 0.99
        self.robot_view_path = None
        self.sub_step_num = 16
        self.joint_moving_idx = [1, 2, 3, 6, 7, 8, 11, 12, 13, 16, 17, 18]
        self.initial_moving_joints_angle = np.asarray([3 / np.pi * init_q[idx] for idx in self.joint_moving_idx])

        self.action_space = gym.spaces.Box(low=-np.ones(16, dtype=np.float32), high=np.ones(16, dtype=np.float32))
        self.observation_space = gym.spaces.Box(low=-np.ones(18, dtype=np.float32) * np.inf,
                                                high=np.ones(18, dtype=np.float32) * np.inf)

        self.log_obs = []
        self.log_action = []
        self.log_sub_state = []
        self.count = 0

        p.setAdditionalSearchPath(pd.getDataPath())

    def World2Local(self, pos_base, ori_base, pos_new):
        psi, theta, phi = ori_base
        R = np.array([[m.cos(phi), -m.sin(phi), 0],
                      [m.sin(phi), m.cos(phi), 0]])
        R_in = R.T
        pos = np.asarray([pos_base[:2]]).T
        R = np.hstack((R_in, np.dot(-R_in, pos)))
        pos2 = list(pos_new[:2]) + [1]
        vec = np.asarray(pos2).T
        local_coo = np.dot(R, vec)
        return local_coo

    def get_obs(self):
        self.last_p = self.p
        self.last_q = self.q
        self.p, self.q = p.getBasePositionAndOrientation(self.robotid)
        self.q = p.getEulerFromQuaternion(self.q)
        self.p, self.q = np.array(self.p), np.array(self.q)

        # Change robot world-XY_coordinates to robot-XY_coordinates
        self.v_p = self.World2Local(self.last_p, self.last_q, self.p)
        self.v_p[2] = self.p[2] - self.last_p[2]

        self.v_q = self.q - self.last_q

        # correct the values if over 180 to -180.
        if self.v_q[2] > 1.57:
            self.v_q[2] = self.q[2] - self.last_q[2] - 2 * np.pi
        elif self.v_q[2] < -1.57:
            self.v_q[2] = (2 * np.pi + self.q[2]) - self.last_q[2]

        jointInfo = [p.getJointState(self.robotid, i) for i in self.joint_moving_idx]
        jointVals = np.array([[joint[0]] for joint in jointInfo]).flatten()
        self.obs = np.concatenate([self.v_p, self.v_q, jointVals])

        return self.obs

    def act(self, a):
        if dyna_force_joints:
            for j in range(12):
                pos_value = a[j]
                # if j in [1,2,10,11]:
                #     self.maxVelocity = 0.9
                # else:
                #     self.maxVelocity = 0.8

                p.setJointMotorControl2(self.robotid, self.joint_moving_idx[j], controlMode=self.mode,
                                        targetPosition=pos_value,
                                        force=self.force,
                                        maxVelocity=self.maxVelocity)
        else:
            for j in range(12):
                pos_value = a[j]
                p.setJointMotorControl2(self.robotid, self.joint_moving_idx[j], controlMode=self.mode,
                                        targetPosition=pos_value,
                                        force=self.force,
                                        maxVelocity=self.maxVelocity)

        for _ in range(self.n_sim_steps):
            p.stepSimulation()

            # if self.render:
            #     # Capture Camera
            #     if self.camera_capture == True:
            #         basePos, baseOrn = p.getBasePositionAndOrientation(self.robotid)  # Get model position
            #         basePos_list = [basePos[0], basePos[1], 0.3]
            #         p.resetDebugVisualizerCamera(cameraDistance=1, cameraYaw=75, cameraPitch=-20,
            #                                      cameraTargetPosition=basePos_list)  # fix camera onto model
            time.sleep(self.sleep_time)
            # self.log_sub_state.append(self.get_obs())

    def reset(self):
        p.resetSimulation()
        p.setGravity(0, 0, -10)
        p.setAdditionalSearchPath(pd.getDataPath())
        planeId = p.loadURDF("plane.urdf")
        p.changeDynamics(planeId, -1, lateralFriction=self.friction)

        robotStartPos = [0, 0, 0.3]
        robotStartOrientation = p.getQuaternionFromEuler([0, 0, 0])

        self.robotid = p.loadURDF(self.urdf_path, robotStartPos, robotStartOrientation, flags=p.URDF_USE_SELF_COLLISION,
                                  useFixedBase=0)

        p.changeDynamics(self.robotid, 2, lateralFriction=self.friction)
        p.changeDynamics(self.robotid, 5, lateralFriction=self.friction)
        p.changeDynamics(self.robotid, 8, lateralFriction=self.friction)
        p.changeDynamics(self.robotid, 11, lateralFriction=self.friction)

        for j in range(12):
            pos_value = self.initial_moving_joints_angle[j]
            p.setJointMotorControl2(self.robotid, self.joint_moving_idx[j], controlMode=self.mode,
                                    targetPosition=pos_value, force=self.force, maxVelocity=100)

        for _ in range(100):
            p.stepSimulation()
        self.stateID = p.saveState()
        self.p, self.q = p.getBasePositionAndOrientation(self.robotid)

        self.q = p.getEulerFromQuaternion(self.q)
        self.p, self.q = np.array(self.p), np.array(self.q)

        return self.get_obs()

    def resetBase(self):
        p.restoreState(self.stateID)

        self.last_p = 0
        self.p, self.q = p.getBasePositionAndOrientation(self.robotid)

        self.q = p.getEulerFromQuaternion(self.q)
        self.p, self.q = np.array(self.p), np.array(self.q)

        return self.get_obs()

    def step(self, sin_para):

        step_action_list = []
        step_obs_list = []
        r = 0
        step_done = False
        # range 1 to step_num +1 so that the robot can achieve the original pos after current action.
        for a_i in range(1, self.sub_step_num+1):
            a_i_add = sin_move(a_i, sin_para)
            norm_a = self.initial_moving_joints_angle + a_i_add
            norm_a = np.clip(norm_a, -1, 1)
            a = norm_a * self.motor_action_space
            self.act(a)
            step_obs = self.get_obs()
            step_obs_list.append(step_obs)
            step_action_list.append(norm_a)  # from -1 to 1
            r += (3 * step_obs[1] - abs(step_obs[5]) - 0.5 * abs(step_obs[0]) + 1)
            step_done = self.check()
            if step_done:
                break

        self.count += 1
        obs_combine = np.hstack((step_action_list, step_obs_list))
        return obs_combine, r, step_done, {}

    def robot_location(self):
        position, orientation = p.getBasePositionAndOrientation(self.robotid)
        orientation = p.getEulerFromQuaternion(orientation)

        return position, orientation

    def check(self):
        pos, ori = self.robot_location()
        # if abs(pos[0]) > 0.5:
        #     abort_flag = True
        if (abs(ori[0]) > np.pi / 6) or (abs(ori[1]) > np.pi / 6):  # or abs(ori[2]) > np.pi / 6:
            abort_flag = True
        # elif pos[1] < -0.04:
        #     abort_flag = True
        # elif abs(pos[0]) > 0.2:
        #     abort_flag = True
        else:
            abort_flag = False
        return abort_flag


def call_max_reward_action(train_data, test_data):
    action_rewards = torch.stack((train_data.R, test_data.R))
    a_id = torch.argmax(action_rewards)
    a_choose = torch.stack((train_data.A, test_data.A))[a_id]
    return a_choose


data_root = "/home/ubuntu/Documents/data_4_meta_self_modeling_id/data/"
data_save_root = "/home/ubuntu/Documents/data_4_meta_self_modeling_id/data_V2/"
URDF_PTH = data_root + "robot_urdf_210k/"

if __name__ == "__main__":

    # Data collection
    mode = 0
    dyna_force_joints = True

    # robot_name = '11_0_2_0_10_0_9_2_14_0_3_10_13_0_10_0'
    # robot_name = '10_9_3_11_6_0_1_0_9_0_11_0_14_3_9_1'
    robot_name = '10_9_9_6_11_9_9_6_13_3_3_6_14_3_3_6'
    # [1, 2, 3, 4, 9, 11, 13, 14, 15, 16, 17, 22, 30, 31, 32, 34]
    if mode == 0:

        save_flg = True
        add_sans = 0

        Train = True
        # p.connect(p.DIRECT) if Train else p.connect(p.GUI)
        p.connect(p.GUI)
        para_config = np.loadtxt('search_para/para_config.csv')

        initial_para = para_config[:, 0]
        para_range = para_config[:, 1:]

        log_pth = "data/robot_sign_data/%s/" % robot_name
        os.makedirs(log_pth, exist_ok=True)

        initial_joints_angle = np.loadtxt('robot_urdf/%s/%s.txt' % (robot_name,robot_name))
        initial_joints_angle = initial_joints_angle[0] if len(
            initial_joints_angle.shape) == 2 else initial_joints_angle

        if Train:
            meta_env = meta_sm_Env(initial_joints_angle,
                                   urdf_path='robot_urdf/%s/%s.urdf'%(robot_name,robot_name))
            max_train_step = 10
            meta_env.sleep_time = 0
            obs = meta_env.reset()
            step_times = 0
            r_record = -np.inf
            ANS_data = []  # size = 12 + 6 + 12 initial np.hstack((initial_joints_angle, obs))
            save_action = []
            done_time = 0
            done_time_killer = 3
            num_population = 5

            loop_action = np.copy(initial_para)
            mu = 0.8
            action_para_logger = []
            while 1:
                # tunning 80%
                loop_action_array = np.repeat([loop_action], int(num_population * mu), axis=0)
                # keep one of previous best one
                loop_action_array[1:] = np.random.normal(loop_action_array[1:], scale=0.1)
                # random_new 20%
                norm_space = np.random.sample((int(num_population - mu * num_population), len(initial_para)))
                num_new_random_para = int(num_population - mu * num_population)
                action_list_append = norm_space * (para_range[:, 1] - para_range[:, 0]) + np.repeat([para_range[:, 0]],
                                                                                                    num_new_random_para,
                                                                                                    axis=0)
                # All individual actions in one epoch
                action_list = np.vstack((loop_action_array, action_list_append))
                rewards = []

                for i in range(num_population):
                    # time.sleep(10000)
                    action = action_list[i]
                    action_and_next_obs, r, done, _ = meta_env.step(action)

                    ANS_data.append(action_and_next_obs)
                    obs = action_and_next_obs[-18:]
                    rewards.append(r)

                    if done:
                        obs = meta_env.resetBase()
                        done_time += 1
                        break
                    if r > r_record:
                        r_record = np.copy(r)
                        save_action = np.copy(action)

                    action_para_logger.append(action)

                if done_time == 0:
                    best_id = np.argmax(rewards)
                    loop_action = action_list[best_id]
                # pos, ori = meta_env.robot_location()

                step_times += num_population
                print(step_times)
                if step_times >= max_train_step:
                    break

            print("step count:", step_times, "r:", r_record)
            if save_flg :#and (done_time < done_time_killer):
                os.makedirs(log_pth, exist_ok=True)
                np.savetxt(log_pth + "gait_step%d_%d.csv" % (max_train_step, add_sans), np.asarray(save_action))
                ANS_data = np.asarray(ANS_data)
                print(ANS_data.shape)
                np.save(log_pth + "sans_%d_%d_V2.npy" % (max_train_step, add_sans), ANS_data)
                np.savetxt(log_pth + "action_para_list.csv", np.asarray(action_para_logger))

        else:
            meta_env = meta_sm_Env(initial_joints_angle,
                                   urdf_path=URDF_PTH + "%s/%s.urdf" % (robot_name, robot_name))
            action = np.loadtxt(log_pth + '/gait_step300.csv')

            meta_env.sleep_time = 0
            obs = meta_env.reset()

            for epoch_run in range(1):
                obs = meta_env.resetBase()
                r_log = 0
                for i in range(6):
                    next_obs, r, done, _ = meta_env.step(action)
                    r_log += r
                    if done:
                        break

    p.disconnect()
