import numpy as np
import matplotlib.pyplot as plt
import segyio

def get_vel(file_name):
    with segyio.open(file_name, "r") as f:
        f.mmap()
        nx = f.bin[segyio.BinField.Traces]
        nz = f.bin[segyio.BinField.Samples]
        vel = np.zeros((nx, nz))
        vel_gen = f.trace[:]
        for i, v in enumerate(vel_gen):
            vel[i] = v
        return vel.T

def get_sources(file_name, idx=1):
    sources = np.fromfile(file_name, sep=" ").reshape((-1, 4))
    return sources[idx][1], sources[idx][3]

def get_receiver_depth(file_name):
    receivers = np.fromfile(file_name, sep=" ").reshape((-1, 4))
    return receivers[1][-1]

def get_observation(file_name, idx):
    with segyio.open(file_name, "r", strict=False, ignore_geometry=True) as f:
        f.mmap()
        trace_num = len(f.header)
        obs_trace = []
        for i in range(trace_num):
            if (f.header[i][segyio.TraceField.FieldRecord] == idx):
                obs_trace.append(f.trace[i])
        return np.array(obs_trace)

def plot_at_receivers(r, nx, time, bounds):
    """
    Plot displacement as receiver over time time
    Args:
        r (2d array): Wave pressure values at receiver depth over given time
        nx (int): the number of cells in horizontal direction of the model
        time (float): Time legth
        bounds (float): The maximum absolute value for pressure for plotting
    """
    plt.figure(figsize=(10,7))
    plt.imshow(r.T, cmap='RdBu', interpolation='bilinear', aspect='auto',
               vmin=-bounds, vmax=bounds,   # set bounds for colourmap data
               extent=(0,nx,time,0))  # set bounds for axes
    plt.title('Receiver Data')
    plt.colorbar()
    plt.xlabel('Receiver number')
    plt.ylabel('Time / s')
    plt.show()

def get_source(file_name, idx):
    with segyio.open(file_name, "r", ignore_geometry=True) as f:
        return f.trace[idx].astype(np.float32)


def get_loss(p, obs_file, idx):
    d = get_observation(obs_file, idx)
    p = p.flatten()
    d = d.flatten()
    a = (p.T@d+d.T@p)/(2*p.T@p)
    return np.sum(np.sqrt(np.power(d-a*p, 2)))
