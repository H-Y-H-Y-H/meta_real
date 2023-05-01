import matplotlib.pyplot as plt
import numpy as np
test_id = 1
for joint in range(1):
    # test1_a = np.loadtxt('test%d/a.csv'%test_id) [:,joint]
    test1_jp = np.loadtxt('test%d/a.csv'%test_id)[:,joint]
    test2_jp = np.loadtxt('test%d/a.csv'%3)[:,joint]

    # test1_jp = (test1_jp-500)/370 * 1.57

    sim_state = np.load('../data/robot_sign_data_2/10_9_9_6_11_9_9_6_13_3_3_6_14_3_3_6/sans_100_0_V2.npy')
    print(sim_state.shape)
    sim_jp = sim_state[:10,:,joint]
    sim_jp = sim_jp.flatten()
    plt.plot(list(range(len(sim_jp))),sim_jp,label='sim_j')

    plt.plot(list(range(len(test1_jp))),test1_jp,label='joint pos',alpha= 0.5)
    plt.plot(list(range(len(test2_jp))),test2_jp,label='joint pos3',alpha= 0.5)

    plt.legend()
    plt.show()

