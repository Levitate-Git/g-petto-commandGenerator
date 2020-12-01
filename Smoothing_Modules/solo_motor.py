import numpy as np
from scipy import interpolate
from Smoothing_Modules import d2_smoothing, d1_smoothing, time_calculation
from CustomModules import global_vars
import main_smoothing 
import rope_parameter_preparation
import motor_parameters_preperation

def main(motor_coord,stopped_frames, usage, path, delta_ts, num_of_frames, max_x, max_z,motorname):
    """
        Main function to calculate motor parameters for SOLO Motors and write parameters to txt files.

        Parameters
        ----------
        motor_coord : user inputted motor coordinates 
        
        stopped_frames : frames that are inputted as stop frame by user for solo motor

        usage : The usage mode of motors which could be DUO-DUO / SOLO-SOLO-SOLO / DUO-SOLO-SOLO / SOLO-DUO-SOLO / SOLO-SOLO-DUO

        path : the path that end effector's pass

        delta_ts : times that have been entered by user for each frames

        num_of_frames : total number of frames inputted by user

        max_x :  maximum x value among all paths

        max_z : maximum z value among all paths

        motorname : name that is using for generating txt file
    """
    on_off = global_vars.OFFLINE_ONLINE 
    if on_off:
        import sys
        board_ID = sys.argv[1]
        rev_Id = sys.argv[2]
        input_path = ("/tmp/boards/" + board_ID + "/inputs/")
        output_path = ("/tmp/boards/" + board_ID + "/outputs/")
    else:
        board_ID = ""
        rev_Id = "1"
        input_path = ""
        output_path = ""
    
    # First, determine the paths according to the usage and than make a spline from 2D Path
    try:
        x_point_1d , z_point_1d , list_positions = d1_smoothing.populate_path(path,motor_coord)
    except Exception as e:
        error_occured = e
        print("popolate_path function FAILED in solo_motor")
        print(e)
        return error_occured

    # Second, determine the frames that will have zero velocity at the end.
    try:
        zero_end_velocity_frames = d1_smoothing.zero_end_velocities(z_point_1d)
    except Exception as e:
        error_occured = e
        print("zero_end_velocities function FAILED in solo_motor")
        print(e)
        return error_occured
    
    # Third, making delta_ts values appropriate for TimeCalculations class.
    try:
        t_vs_u = d1_smoothing.time_vs_u(delta_ts)
    except Exception as e:
        error_occured = e
        print("time_vs_u function FAILED in solo_motor")
        print(e)
        return error_occured

    # Fourth, calculating, time and velocity values for sub-frames.
    try:
        times_and_velocities_for_end_effector = d1_smoothing.time_calculations(x_point_1d,z_point_1d, zero_end_velocity_frames,list_positions, t_vs_u,stopped_frames)
    except Exception as e:
        error_occured = e
        print("time_calculations function FAILED in solo_motor")
        print(e)
        return error_occured

    # Fifth, interchanging the locations of velocity and time in the times_and_velocities_for_end_effector to use in average velocity calculations
    try:
        rope_vel_vs_time = d1_smoothing.changing_location_of_time_and_velocity_in_list(times_and_velocities_for_end_effector)
    except Exception as e:
        error_occured = e
        print("changing_location_of_time_and_velocity_in_list function FAILED in solo_motor")
        print(e)
        return error_occured
    
    # Sixth, calculating average velocities for each sub-frame
    try:
        average_rope_velocities = rope_parameter_preparation.average_velocity_calculation(rope_vel_vs_time)
    except Exception as e:
        error_occured = e
        print("average_velocity_calculation function FAILED in solo_motor")
        print(e)
        return error_occured
    
    # Seventh, creating rope parameters in meters and seconds.
    try:
        rope_parameters = rope_parameter_preparation.rope_parametes_in_meters_and_seconds(average_rope_velocities,z_point_1d)
    except Exception as e:
        error_occured = e
        print("rope_parametes_in_meters_and_seconds function FAILED in solo_motor")
        print(e)
        return error_occured

    # Ninth, generating motor parameters from rope parameters.
    try:
        time = []
        for i in range(len(rope_vel_vs_time)):
            time.append(rope_vel_vs_time[i][1])
        motor_parameters_for_motor_1 = motor_parameters_preperation.motor_parameters_preperation(rope_parameters,time)
    except Exception as e:
        error_occured = e
        print("motor_parameters_preperation function FAILED in solo_motor")
        print(e)
        return error_occured
    
    # Tenth, writing motor parameters to txt files.
    try:
        motor_parameters_preperation.writing_motor_params(usage,motor_parameters_for_motor_1, file_name = motorname)
    except Exception as e:
        error_occured = e
        print("writing_motor_params for rope1 function FAILED in solo_motor")
        print(e)
        return error_occured