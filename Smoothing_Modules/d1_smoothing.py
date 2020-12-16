import numpy as np
from scipy import interpolate
from CustomModules import global_vars
import math
import main_smoothing 
from Smoothing_Modules import time_calculation

def populate_path(path, motor_coord):
    """
        Dividing path into pieces with a length of "global_vars.DELTA_LENGTH" and turn this length into rope lengths.

        Parameters
        ----------
        path : which is a list of user inputted points.
        
        motor_coords : user inputted motor coordinates.

        Return
        ------
        xs : To calculate time values TimeCalculation class need this value 
            So this code make a list from zeros.
        
        rope_lengths : list of rope lengths 
        
        list_positions : list of list indexes for user inputted frames after populated spline.
    """
    zs = []
    list_positions = [0] 
    j = 0
    if len(path)==1:
        zs.append(path[0][1])
    else:
        for i in range(1,len(path)):
            # Finding frame distance in order to determine how many sub-frames occurs in that user inputted frame by using "global_vars.DELTA_LENGTH" value 
                # as a divider.
            frame_distance = abs(path[i][1]-path[i-1][1])
            divide_num = int(frame_distance / global_vars.DELTA_LENGTH)
            
            if i == len(path)-1:
                # Take the last value if end of the spline.
                zs_temp = np.linspace(path[i-1][1],path[i][1], divide_num, endpoint=True)
            else:    
                # Do not take last value to avoid duplication
                zs_temp = np.linspace(path[i-1][1],path[i][1], divide_num, endpoint=False)
            for z in zs_temp:
                zs.append(z)
                j += 1
            # Determining a list of user inputted frames in populated spline
            list_positions.append(j)
        # Read just last member because j += 1 makes last member irrelevant
        last_member = list_positions.pop()
        list_positions.append(last_member-1)
    # Making a list of zeros as big as list(zs)
    xs = []
    for z in zs:
        xs.append(0)
    
    rope_lengths = []
    # Transforming zs values into rope lengths
    for z in zs:
        temp = motor_coord - z
        rope_lengths.append(temp)

    return xs,rope_lengths, list_positions

def zero_end_velocities(zs):
    """
        Determining the points where end_effector change direction in solo motor case. 
        We need this frame numbers in order to assign end velocities of previous frames to zero.

        Parameters:
        -----------
        zs : rope length values 

        Return:
        ------
        zero_end_velocity_frames : list of frames with zero end velocity.
    """
    
    directions = ["s"]
    for i in range(1,len(zs)):
        if zs[i]-zs[i-1] > 0:
            direction = "d" # Means prop is moving downward.
        elif zs[i]-zs[i-1] < 0:
            direction = "u" # Means prop is moving upward.
        else:
            direction = "s" # Means prop is stopping.
        directions.append(direction)
    
    zero_end_velocity_frames = []
    for i in range(len(directions)-1):
        # If directions does not equal it means motor is changing direction.
        if directions[i] != directions[i+1]:
            zero_end_velocity_frames.append(i)

    return zero_end_velocity_frames

def time_vs_u(delta_ts):
    """
        To use time values in TimeCalculaions class we need a list of list of 2 elements. 

        Parameters
        ----------
        delta_ts : user inputted time values for frames.

        Return
        ------
        t_vs_u : list of passed time and zeros
    """
    t_vs_u = [(0,0)]
    time = int(0)
    a = 0
    for t in delta_ts:
        if a == 0:
            a += 1
        else:    
            time += t # To create a list of time passed
            t_vs_u.append((time,0))

    return t_vs_u

def time_calculations(xs,zs, zero_end_velocity_frames,list_positions, time_vs_u,stopped_frames):
    """
        To calculate the time needed for sub-frames (which are the frames that have been constructed for populate the spline) by using the limit values for
            velocity and acceleration. This function uses TimeCalculation class which have generated in time_calculations.py.
        
        Parameters
        ----------
        xs : x values of the end effector (which is a list of zero for solo motors)
        
        zs : list of rope lengths
        
        zero_end_velocity_frames : frames that ends with velocity value of zero.

        list_positions : list of list indexes for user inputted frames after populated spline.

        time_vs_u : list of passed time and u values (which are zero for solo motors)

        stopped_frames : user inputted frames that user want to end effector stops

        Return
        ------
        times_and_velocities_for_end_effector : gives the list of time passed and velocities for end effector at each sub-frame
    
    """
    #Adding stopped_frames to list_positions
    count_list_position = 1
    temp_list_positions =[]
    for pos in list_positions:
        temp_list_positions.append(pos)
    old_st_frame = 0
    elem = temp_list_positions.pop(0)
    i = 0
    while i <len(stopped_frames):
        if i == 0 and stopped_frames[i] == 0:
            list_positions.insert(0,0)
            i += 1
            while i<len(stopped_frames) and (stopped_frames[i]-stopped_frames[i-1]) == 1:
                list_positions.insert(0,0)
                i += 1 
        else:
            if(stopped_frames[i]-stopped_frames[i-1]) != 1 and len(temp_list_positions)>0 and i >0:    
                diff = stopped_frames[i]-stopped_frames[i-1]
                for j in range(diff -1):
                    elem = temp_list_positions.pop(0)

                insert_index = list_positions.index(elem)
                list_positions.insert(insert_index,elem)     
                i += 1
                if i < len(stopped_frames):
                    while (stopped_frames[i]-stopped_frames[i-1]) == 1:
                        list_positions.insert(insert_index,elem)
                        i += 1
                        if i >= len(stopped_frames):
                            break 
            else:
                if i == 0  and stopped_frames[i]>1:
                    elem = temp_list_positions.pop(0)
                elem = temp_list_positions.pop(0)
                insert_index = list_positions.index(elem)
                list_positions.insert(insert_index,elem)   
                i += 1
                if i < len(stopped_frames):
                      while (stopped_frames[i]-stopped_frames[i-1]) == 1:
                        list_positions.insert(insert_index,elem)
                        i += 1
                        if i >= len(stopped_frames):
                            break 
    del count_list_position
   
    #Defining time calculation class
    time_calculate = time_calculation.TimeCalculations()
    # Calculating average velocities exclusively for each user inputted frame
    average_speed_of_frames = time_calculate.calculating_average_end_effector_speed(list_positions, time_vs_u,xs,zs)
       
    j = 0 #average velocity counter
    s = 0 #real frame counter including stop frames
    for pos in list_positions:
        enter = True
        # Start point of the choreography
        if s == 0:
            time_calculate.zeroth_frame()
            enter = False
            s += 1
        #if our frame is a stopped frame we determine it by using average velocities     
        elif average_speed_of_frames[j] == 0:
            times_and_velocities_for_end_effector = time_calculate.stopped_frame(time_vs_u)
            enter = False
            s += 1
            j += 1     
        else:
            #İf there is a turn, stop or finish frame we finish movement with zero velocity
            for zero_end_vel in zero_end_velocity_frames:
                if zero_end_vel == pos or pos == list_positions[-1]:
                    end_velocity = 0
                    break
                else:
                    end_velocity = average_speed_of_frames[j]
            times_and_velocities_for_end_effector = time_calculate.solving_with_jerk_control(pos,list_positions, end_velocity,time_vs_u,xs,zs)
            s += 1
            j += 1
        
    print("SOLO MODE FINISHED")
    return times_and_velocities_for_end_effector


def changing_location_of_time_and_velocity_in_list(times_and_velocities_for_end_effector):
    """
        In order to be used in rope_parameter_calculations.py we are interchanging the list location of velocity and time values.
        
        Parameters
        ----------
        times_and_velocities_for_end_effector : gives the list of time passed and velocities for end effector at each sub-frame

        Returns
        -------
        rope_vel_vs_time : interchanged list location of times_and_velocities_for_end_effector
    """
    rope_vel_vs_time = []
    for i in range(len(times_and_velocities_for_end_effector)):
        rope_vel_vs_time.append((times_and_velocities_for_end_effector[i][1],times_and_velocities_for_end_effector[i][0]))
    return rope_vel_vs_time


def main(usage,np_paths):
    # For testing purposes.
    if usage == "1001":
        path1d_1 = np_paths[0]
        path1d_2 = np_paths[2]
        path_spline = np_paths[1]
    elif usage == "1100":
        path1d_1 = np_paths[0]
        path1d_2 = np_paths[1]
        path_spline = np_paths[2]
    elif usage == "0011":
        path1d_1 = np_paths[1]
        path1d_2 = np_paths[2]
        path_spline = np_paths[0]

    x_point_1d_1 , z_point_1d_1 , list_positions = populate_path(path1d_1)
    zero_end_velocity_frames = zero_end_velocities(z_point_1d_1)
    t_vs_u = time_vs_u(delta_ts)
    times_and_velocities_for_end_effector = time_calculations(x_point_1d_1,z_point_1d_1, zero_end_velocity_frames,list_positions, t_vs_u)


if __name__ == "__main__":
    np_paths, delta_ts, num_of_frames, max_x, max_z  = main_smoothing.read_user_input()
    mot_coords, usage = main_smoothing.get_motor_coords()
    main(usage, np_paths)