import numpy as np





Period = 16
def sin_move(ti, para):
    assert len(para) == 10, "Action para should be a vector of length 10"
    # print(para)
    s_action = np.zeros(12)
    # print(ti)
    s_action[0] = para[0] * np.sin(ti / Period * 2 * np.pi + para[2]) # right   hind
    s_action[3] = para[1] * np.sin(ti / Period * 2 * np.pi + para[3]) # right  front
    s_action[6] = para[1] * np.sin(ti / Period * 2 * np.pi + para[4]) # left  front
    s_action[9] = para[0] * np.sin(ti / Period * 2 * np.pi + para[5]) # left  hind

    s_action[1] = para[6] * np.sin(ti / Period * 2 * np.pi + para[2]) # right   hind
    s_action[4] = para[7] * np.sin(ti / Period * 2 * np.pi + para[3]) # right   front
    s_action[7] = para[7] * np.sin(ti / Period * 2 * np.pi + para[4]) # left  front
    s_action[10]= para[6] * np.sin(ti / Period * 2 * np.pi + para[5])  # left  hind

    s_action[2] = para[8] * np.sin(ti / Period * 2 * np.pi + para[2]) # right   hind
    s_action[5] = para[9] * np.sin(ti / Period * 2 * np.pi + para[3]) # right   front
    s_action[8] = para[9] * np.sin(ti / Period * 2 * np.pi + para[4]) # left  front
    s_action[11]= para[8] * np.sin(ti / Period * 2 * np.pi + para[5])  # left  hind

    return s_action