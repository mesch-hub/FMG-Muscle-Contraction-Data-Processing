import pandas as pd
import matplotlib.pyplot as plt
import os

import numpy as np
from scipy.signal import argrelextrema

def process_values(column):
    threshold = 100
    max_consecutive = int(0.01 * len(column))
    current_consecutive = 0
    in_sequence = False
    above_500 = False
    
    for i, value in enumerate(column):
        if value > threshold and not in_sequence:
            in_sequence = True
            current_consecutive = 1
            above_500 = False
            continue
        elif value > threshold and in_sequence:
            current_consecutive += 1
            if value > 500:
                above_500 = True
        elif value <= threshold and in_sequence:
            if above_500:
                in_sequence = False
                above_500 = False
            else:
                if current_consecutive <= max_consecutive:
                    column[i - current_consecutive:i] = 1
                in_sequence = False
                current_consecutive = 0
            
    if above_500:
        column[i - current_consecutive + 1:i + 1] = 1
    
    return column

def plot_cycles(file, muscle_names):
    # Iterate through the cycle intervals
    for interval in cycles:
        # Filter rows within the current interval and append them to the filtered_rows list
        current_intervall = file.loc[interval[0]:interval[1]]
        plt.clf()
        plt.plot(current_intervall)
        plt.title(muscle_names)
        plt.xlabel(x_achse)
        plt.ylabel(y_achse)
        #plt.show()

def intervall_from_cycles(file, cycles):
    intervall_values = []
    for interval in cycles:
            # Filter rows within the current interval and append them to the filtered_rows list
            current_intervall = file.loc[interval[0]:interval[1]]
            intervall_values.append(current_intervall)
    return intervall_values

def normalize(values, start, end) -> float:
    values_np = values.to_numpy()
    norm = 0
    for i in range(end-start):
        norm += values_np[i] 
    return norm / (end-start)

def norm_mean(file, first_index, last_index):
    norm_dev = normalize(file, first_index, last_index)

    file = file - norm_dev

    file['row_sum'] = file.sum(axis=1)
    file = file[['row_sum']] / 5
    return file

def normalizeValues(file_filtered):
    df = file_filtered.iloc[int(0.1 * len(file_filtered)):]
    # Find index of first value=1
    first_one_index = df[df == 1].index[0]
    # Extract every value before first_one_index
    subset = df.loc[:first_one_index]
    # Cut 20% at beginning and end of recording period (stabilization period)
    subset_length = len(subset)
    subset = subset.iloc[int(subset_length * 0.1):int(subset_length * 0.8)]

    first_index = subset.index[0]
    last_index = subset.index[-1]
    return first_index, last_index

def calculateMaxValues(given_intervall, device):
    # Find occurence and height of maximum
    span = 0
    for intervall in given_intervall:
        intervall = intervall.to_numpy()
        # Find the index of the maximum value
        pos_max = np.argmax(intervall)

        #calculate span of cycle
        span += np.abs(np.min(intervall)) + np.abs(np.max(intervall))

        # Calculate the position percentage
        position_percentage = ((pos_max) / len(intervall)) * 100

        # Calculate the number of values constituting 1% of the array
        one_percent = len(intervall) * 0.07

        # Determine the start and end indices for slicing
        start_index = int(pos_max - one_percent)
        end_index = int(pos_max + one_percent) + 1

        # Slice the array to cut 1% of the values to the left and right of the largest value
        mask = np.logical_or(np.arange(len(intervall)) < start_index, np.arange(len(intervall)) >= end_index)

        cut_array = intervall[mask]
        pos_max_cut = np.argmax(cut_array)
        position_percentage = ((pos_max_cut) / len(intervall)) * 100

    print(f"span device {device}: {span / len(given_intervall)}")

def interpolate_cycles(arrays):
    # Ensure all arrays are numpy arrays
    arrays = [np.array(array) for array in arrays]
    
    num_points=max(len(arr) for arr in arrays)
    # Determine the number of arrays and the length of each array
    num_arrays = len(arrays)
    array_lengths = [len(array) for array in arrays]
    max_length = max(array_lengths)
    
    # Initialize the interpolated arrays
    interpolated_arrays = []
    
    # Perform linear interpolation for each array
    for i in range(num_arrays):
        # Interpolate the current array
        interpolated_array = []
        for j in range(num_points):
            # Calculate the interpolation step for the current array
            step = (array_lengths[i] - 1) / (num_points - 1)
            
            # Calculate the index in the current array
            index = j * step
            
            # Split the index into the integer part and fractional part
            idx_floor = int(index)
            idx_ceil = min(idx_floor + 1, array_lengths[i] - 1)
            frac = index - idx_floor
            
            # Perform linear interpolation
            if idx_ceil < array_lengths[i]:
                interpolated_value = (1 - frac) * arrays[i][idx_floor] + frac * arrays[i][idx_ceil]
            else:
                interpolated_value = arrays[i][idx_floor]  # Handles edge case when idx_ceil is out of bounds
                
            interpolated_array.append(interpolated_value)
        
        # Append the interpolated array to the list of interpolated arrays
        interpolated_arrays.append(np.array(interpolated_array))
    
    return interpolated_arrays
 
#0001_walking_tights_06_1715765872457_device_  0001_walking_jeans_tib_02_1715763684901_device_
tib = False
if tib:
     muscle_names = ['m. gastrocnemius lateralis ', 'm. tibialis anterior']
else:
     muscle_names = ['m. gastrocnemius lateralis ', 'm. gastrocnemius medialis']
current_fileName = '0001_walking_tights_07_1715765903670_device_'
minus_1_filename = current_fileName + '-1.csv'
one_filename = current_fileName + '1.csv'
two_filename = current_fileName + '2.csv'
movement = 'Measures/walking'#'stairs'
x_achse = 'timesteps'
y_achse = 'hPa'
currentDire = os.getcwd()
savePathFolder = os.path.join(currentDire, 'graphs')
if not os.path.exists(savePathFolder):
    os.makedirs(savePathFolder)
savePath = os.path.join(savePathFolder ,current_fileName)
filePath_min1 = os.path.join(currentDire, os.path.join(movement, minus_1_filename))
filePath_1 = os.path.join(currentDire, os.path.join(movement, one_filename))
filePath_2 = os.path.join(currentDire, os.path.join(movement, two_filename))

file_min1 = pd.read_csv(filePath_min1, sep=',', header=None)
#Drop first two lines 1 always device number 2 time
file_min1 = file_min1.iloc[:, 2:]
file_min1 = file_min1.astype(float)

file_1 = pd.read_csv(filePath_1, sep=',', header=None)
#Drop first two lines 1 always device number 2 time
file_1 = file_1.iloc[:, 2:]
file_1 = file_1.astype(float)

file_2 = pd.read_csv(filePath_2, sep=',', header=None)
#Drop first two lines 1 always device number 2 time
file_2 = file_2.iloc[:, 2:]
file_2 = file_2.astype(float)

plt.plot(file_min1)
plt.title('heelswitch')
plt.xlabel(x_achse)
plt.ylabel(y_achse)
#plt.show()

#For -1 sensor
file_min1[file_min1 <= 100] = 1

file_filtered = process_values(file_min1.squeeze())
plt.plot(file_filtered)
plt.title('heelswitch filtered')
plt.xlabel(x_achse)
plt.ylabel(y_achse)
#plt.show()

indices = file_filtered.index[(file_filtered == 1) & (file_filtered.shift(-1) != 1)]
indices = indices[1:-1]

cycles = []
for i in range(len(indices)-1):
    # Construct [,] value pair
    pair = [indices[i], indices[i+1]-1]
    # Append the pair to the cycles array
    cycles.append(pair)

print(cycles)

first_index, last_index = normalizeValues(file_filtered)

file_1 = norm_mean(file_1, first_index, last_index)
file_2 = norm_mean(file_2, first_index, last_index)

plot_cycles(file_1, muscle_names[0])
plot_cycles(file_2, muscle_names[1])

intervall_1 = intervall_from_cycles(file_1, cycles)
intervall_2 = intervall_from_cycles(file_2, cycles)

calculateMaxValues(intervall_1, device="1")
calculateMaxValues(intervall_2, device="2")

plt.clf()

###MEAN CYCLE COMPUTATION

# Function to interpolate the array to length 100
def interpolate_array(array, target_length):
    original_indices = np.linspace(0, len(array) - 1, num=len(array))
    target_indices = np.linspace(0, len(array) - 1, num=target_length)
    interpolated_array = np.interp(target_indices, original_indices, array)
    return interpolated_array

def interpolate_to_percent_gait_cycle(time_step_cycle):
    # Interpolate to length 100
    interpolated_array = interpolate_array(time_step_cycle.flatten(), target_length=300)

    return interpolated_array


def gait_cycles_to_numpy(gait_cycles):
    gait_cycles_np = []
    for cycle in gait_cycles:
        gait_cycles_np.append(cycle.to_numpy())
    return gait_cycles_np


#calculate mean gait cycle
def compute_mean_cycle(interpolated_cycles):
    values_per_cycle = len(interpolated_cycles[0])
    sums = [0] * values_per_cycle
    for cycle in interpolated_cycles:
        for i, value in enumerate(cycle):
            sums[i] += value
    return [s / len(interpolated_cycles) for s in sums]


#calculate std dev of all gait cycles
def compute_std_cycle(interpolated_cycles, mean_cycle):
    values_per_cycle = len(interpolated_cycles[0])
    std = [0] * values_per_cycle
    for cycle in interpolated_cycles:
        for i,value in enumerate(cycle):
            std[i] += (value - mean_cycle[i])**2
    for i in range(values_per_cycle):
        std[i] = np.sqrt(std[i] / (len(interpolated_cycles) - 1))
    return std

#plot mean and std
def plot_mean_std_cycle(mean_cycle, std, current_muscle_name):
    plt.plot(mean_cycle, linewidth=2.5, color='red', label='Mean')

    pos_std = [(s + t) for s, t in zip(mean_cycle, std)]
    neg_std = [(s - t) for s, t in zip(mean_cycle, std)]
    plt.plot(pos_std, linewidth=0.5, color='red')
    plt.plot(neg_std, linewidth=0.5, color='red')
    #flattened_pos_std =[item for sublist in pos_std for item in sublist]
    #flattened_neg_std =[item for sublist in neg_std for item in sublist]
    x_list = np.arange(0, len(pos_std))##
    plt.fill_between(x_list,pos_std, neg_std, facecolor='red', alpha=0.2)
    plt.xlabel(x_achse)
    plt.ylabel(y_achse)
    plt.title(current_muscle_name)
    plt.legend(fontsize='7')
    cleaned_muscle_name = current_muscle_name.replace(" ", "_")
    cleaned_muscle_name = cleaned_muscle_name[3:]
    plt.savefig(savePath + cleaned_muscle_name)
    #plt.show()




#interpolate gait cycles of one measurement
gait_cycles_np = gait_cycles_to_numpy(intervall_1)
interpolated_cycles = interpolate_cycles(gait_cycles_np)
interpolated_cycles_percent = []
for cycle in interpolated_cycles:
    interpolated_cycles_percent.append(interpolate_to_percent_gait_cycle(cycle))

#plot curves for every gait cycle
i = 0
for cycle in interpolated_cycles_percent:
    i += 1
    plt.plot(cycle, linewidth=1, linestyle='--', label=f'Gait Cycle {i}')

mean_cycle = compute_mean_cycle(interpolated_cycles_percent)
std = compute_std_cycle(interpolated_cycles_percent, mean_cycle)
plot_mean_std_cycle(mean_cycle, std, muscle_names[0])
plt.clf()

mean_std = np.mean(std)
print(f"mean device 1: {mean_std}")



#interpolate gait cycles of one measurement
gait_cycles_np = gait_cycles_to_numpy(intervall_2)
interpolated_cycles = interpolate_cycles(gait_cycles_np)
interpolated_cycles_percent = []
for cycle in interpolated_cycles:
    interpolated_cycles_percent.append(interpolate_to_percent_gait_cycle(cycle))

#plot curves for every gait cycle
i = 0
for cycle in interpolated_cycles_percent:
    i += 1
    plt.plot(cycle, linewidth=1, linestyle='--', label=f'Gait Cycle {i}')

mean_cycle = compute_mean_cycle(interpolated_cycles_percent)
std = compute_std_cycle(interpolated_cycles_percent, mean_cycle)
plot_mean_std_cycle(mean_cycle, std, muscle_names[1])

mean_std = np.mean(std)
print(f"mean device 2: {mean_std}")