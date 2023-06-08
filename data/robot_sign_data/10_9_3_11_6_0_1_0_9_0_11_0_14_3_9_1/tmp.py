import numpy as np

sans_sim = np.load('sans_100s_0_V2.npy')[:10]
sans_r = np.load('sans_100r_0_V2.npy')
print(sans_r.shape,sans_r.shape)
sans_new = np.mean([sans_sim,sans_r,sans_sim,],axis=0)
print(sans_new.shape)

np.save('sans_100_0_V2.npy',sans_new)
