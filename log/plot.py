import matplotlib.pyplot as plt
import numpy as np
test_id = 1
for joint in range(6):
    # test1_a = np.loadtxt('test%d/a.csv'%test_id) [:,joint]
    test1_jp = np.loadtxt('test%d/state.csv'%1)[:,joint]
    test3_jp = np.loadtxt('test%d/state.csv'%3)[:,joint]
    test4_jp = np.loadtxt('test%d/state.csv'%4)[:,joint]

    test1_jp = np.array(test1_jp[1:]) - np.array(test1_jp[:-1])
    test3_jp = np.array(test3_jp[1:]) - np.array(test3_jp[:-1])
    test4_jp = np.array(test4_jp[1:]) - np.array(test4_jp[:-1])

    if joint >2:
         test1_jp = test1_jp/180 * np.pi
         test3_jp = test3_jp/180 * np.pi
         test4_jp = test4_jp/180 * np.pi

    # test1_jp = (test1_jp-500)/370 * 1.57

    sim_state = np.load('../data/robot_sign_data_2/10_9_9_6_11_9_9_6_13_3_3_6_14_3_3_6/sans_100_0_V2.npy')
    print(sim_state.shape)
    sim_jp = sim_state[:10,:,12+joint]
    sim_jp = sim_jp.flatten()

    x = list(range(len(sim_jp)))

    plt.plot(x,sim_jp,label='sim_j')

    # plt.plot(list(range(len(test1_jp))),test1_jp,label='real1',alpha= 0.5)
    # plt.plot(list(range(len(test3_jp))),test3_jp,label='real3')
    plt.plot(x,test4_jp,label='real4')

    plt.legend()
    plt.show()

