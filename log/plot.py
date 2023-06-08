import matplotlib.pyplot as plt
import numpy as np

def example_plot(ax, plot_title,real_data,sim_data, fontsize=12, hide_labels=False):
    # ax.plot([1, 2])

    ax.plot(real_data, label='real')
    ax.plot(sim_data, label='sim')
    ax.locator_params(nbins=3)
    if hide_labels:
        ax.set_xticklabels([])
        ax.set_yticklabels([])
    else:
        ax.set_xlabel('Time', fontsize=fontsize)
        # ax.set_ylabel('value', fontsize=fontsize)
        ax.set_title(plot_title, fontsize=fontsize)

def compare_sim_real():

    test_id = 1
    # Sim data:
    data_pth = "../data/robot_sign_data/10_9_9_6_11_9_9_6_13_3_3_6_14_3_3_6/"

    # data_pth = "../data/robot_sign_data/10_9_3_11_6_0_1_0_9_0_11_0_14_3_9_1/"
    sim_action_ns = np.load(data_pth +'/sans_100s_0_V2.npy')[:10] # 12 a, 6 xyzrpy, 12 joints pos
    sim_joint_pos = sim_action_ns[:, :, 18:].reshape(-1,12).T
    sim_delta_state = sim_action_ns[:, :, 12:18].reshape(-1,6).T
    sim_action = sim_action_ns[:, :, :12].reshape(-1,12).T

    # # Real data:
    joint_pos = np.loadtxt('log_real_%d/joint_pos.csv' % test_id).T
    action =    np.loadtxt('log_real_%d/a.csv' % test_id).T
    state =     np.loadtxt('log_real_%d/state.csv' % test_id).T



    action_ns = np.load('log_real_%d/sans_10_0_V2.npy'%test_id)[:10] # 12 a, 6 xyzrpy, 12 joints pos
    joint_pos = action_ns[:, :, 18:].reshape(-1,12).T
    delta_state = action_ns[:, :, 12:18].reshape(-1,6).T
    action = action_ns[:, :, :12].reshape(-1,12).T


    # # # motor pos to -1 and 1
    # joint_pos =  (joint_pos - 500) / 370 * 1.57
    # joint_pos[6:] = -1*joint_pos[6:]
    # action[6:] = -1*action[6:]
    #
    # # real imu in degree --> radius
    # state[3:] = state[3:] / 180 * np.pi
    #
    # # real xyz rpy to delta
    # delta_state = state[:,1:] - state[:,:-1]
    # delta_state = np.hstack((state[:,:1],delta_state))
    #
    # # reverse the direction
    # delta_state[3:] = -delta_state[3:]
    #
    # delta_state = np.clip(delta_state,-0.2,0.5)
    #
    # # reverse_list = [1,3,4,6,7,10]
    # # for i in reverse_list:
    # #     joint_pos[i] *=-1
    # #     action[i] *=-1
    #
    #
    # action1 = action.T.reshape(-1,16,12)
    # delta_state1 = delta_state.T.reshape(-1,16,6)
    # joint_pos1 = joint_pos.T.reshape(-1,16,12)


    # csv_2_npy = np.dstack((action1, delta_state1,joint_pos1))


    # np.save('log_real_%d/sans_%d_0_V2.npy'%(test_id,len(csv_2_npy)),csv_2_npy)



    plot_list = ['a1','a2','a3','a4','a5','a6',
                 'a7','a8','a9','a10','a11','a12',
                 'dx','dy','dz','droll','dpitch','dyaw',
                 'j1', 'j2', 'j3', 'j4',  'j5',  'j6',
                 'j7', 'j8', 'j9', 'j10', 'j11', 'j12',
                 ]

    fig, axs = plt.subplots(5, 6, layout='constrained',figsize=(16,12))
    count = 0
    for ax in axs.flat:

        # action
        if count <12:
            real_data = action[count]
            sim_data = sim_action[count]
        elif count >= 12 and count < 18:
            real_data = delta_state[count-12]
            sim_data = sim_delta_state[count-12]

        else:
            real_data = joint_pos[count-18]
            sim_data = sim_joint_pos[count-18]

        example_plot(ax,
                     plot_title = plot_list[count],
                     real_data=real_data,
                     sim_data=sim_data)
        count+=1

    plt.legend()
    plt.show()



compare_sim_real()

#
# for joint in range(6):
#     # test1_a = np.loadtxt('test%d/a.csv'%test_id) [:,joint]
#     test1_jp = np.loadtxt('test%d/state.csv'%1)[:,joint]
#     test3_jp = np.loadtxt('test%d/state.csv'%3)[:,joint]
#     test4_jp = np.loadtxt('test%d/state.csv'%4)[:,joint]
#
#     test1_jp = np.array(test1_jp[1:]) - np.array(test1_jp[:-1])
#     test3_jp = np.array(test3_jp[1:]) - np.array(test3_jp[:-1])
#     test4_jp = np.array(test4_jp[1:]) - np.array(test4_jp[:-1])
#
#     if joint >2:
#          test1_jp = test1_jp/180 * np.pi
#          test3_jp = test3_jp/180 * np.pi
#          test4_jp = test4_jp/180 * np.pi
#
#     # test1_jp = (test1_jp-500)/370 * 1.57
#
#     sim_state = np.load('../data/robot_sign_data_2/10_9_9_6_11_9_9_6_13_3_3_6_14_3_3_6/sans_100_0_V2.npy')
#     print(sim_state.shape)
#     sim_jp = sim_state[:10,:,12+joint]
#     sim_jp = sim_jp.flatten()
#
#     x = list(range(len(sim_jp)))
#
#     plt.plot(x,sim_jp,label='sim_j')
#
#     # plt.plot(list(range(len(test1_jp))),test1_jp,label='real1',alpha= 0.5)
#     # plt.plot(list(range(len(test3_jp))),test3_jp,label='real3')
#     plt.plot(x,test4_jp,label='real4')
#
#     plt.legend()
#     plt.show()
#
