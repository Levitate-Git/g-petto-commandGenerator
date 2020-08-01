import numpy as np
from scipy import interpolate
from CustomModules import global_vars
import math


def average_velocity_calculation(rope_vel_vs_time):
    average_velocities = []
    enter = True
    for i in range(0,len(rope_vel_vs_time)):
        if rope_vel_vs_time[i][0] == "stop": # where user wants end effector stops for this frame.
            if i == 0:
                temp = rope_vel_vs_time[i][1]
                avg_velocity = [0,temp]
            else:
                if rope_vel_vs_time[i-1][0] == "stop":
                    temp = (rope_vel_vs_time[i][1] - rope_vel_vs_time[i-1][1])
                    avg_velocity = [0,temp]
                else:

                    temp = (rope_vel_vs_time[i][1] - rope_vel_vs_time[i-1][1])
                    avg_velocity = [0,temp] 
            enter =False
        elif enter:
            enter = False
            average_velocities.append(0.05)
            continue
        else:
            if rope_vel_vs_time[i-1][0] == "stop":
                temp = 0
            else:
                temp = rope_vel_vs_time[i-1][0]
            avg_velocity = (rope_vel_vs_time[i][0] + temp ) / 2
        average_velocities.append(avg_velocity)

    return average_velocities

def rope_parametes_in_meters_and_seconds(average_velocities,rope_length):
    rope_parameters = []
    k_values =[]
    for k in range(1,len(rope_length)):
        if rope_length[k] == rope_length[k-1]:
            k_values.append(k)

    while len(k_values)>0:
        rope_length.pop(k_values[-1])
        noUse = k_values.pop()


    j = 0
    while j < len(average_velocities):
        if len(rope_length) > j:
            
            if type(average_velocities[j]) == list: # We added stop frames as lists to average_velocities
                if j + 1  == len(rope_length):
                    rope_length.insert(j,rope_length[j])
                elif j == 0:
                    while type(average_velocities[j]) == list:
                        if j==0:
                            pass
                        else:
                            rope_length.insert(j,rope_length[j-1])
                        j += 1
                else:
                    rope_length.insert(j,rope_length[j-1]) # Adding stopped rope length to the list.
 
            j += 1    
                
        else:
            
            if type(average_velocities[j]) == list: # We added stop frames as lists to average_velocities
                rope_length.append(rope_length[-1]) # Adding stopped rope length to the list.
            j += 1    
        
    k = 0    

    for k in range(len(rope_length)):
        
        rope_parameters.append((rope_length[k],average_velocities[k]))
    
    return rope_parameters

