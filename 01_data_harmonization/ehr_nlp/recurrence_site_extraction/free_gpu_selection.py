import pynvml
import os

def get_free_gpu():
    '''
    this functions finds the best gpu based on the memory usage
    '''
    pynvml.nvmlInit()
    device_count = pynvml.nvmlDeviceGetCount()

    best_gpu = None
    lowest_memory_usage = float('inf')

    for i in range(device_count):
        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
        mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)

        if mem_info.used < lowest_memory_usage and utilization.gpu == 0:
            lowest_memory_usage = mem_info.used
            best_gpu = i

    pynvml.nvmlShutdown()

    return best_gpu

def get_device():
    '''
    this function selects gpu core or 'cpu' based on get_free_gpu function output
    '''
    free_gpus = get_free_gpu()
    if free_gpus is not None:
        print(f"Using GPU core {free_gpus} for computation")
        device = "cuda:{}".format(free_gpus)
    else:
        print("None of the GPU cores are free. Using 'cpu' for computation")
        device = "cpu"
    return device