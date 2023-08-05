import numpy as np
def to_np_array(data):
    nparray = np.array(data)
    print("type:{}, transformed_data:{}".format(type(nparray), nparray))
    return nparray