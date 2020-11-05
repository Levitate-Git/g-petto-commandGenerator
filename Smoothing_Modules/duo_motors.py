import numpy as np
from scipy import interpolate
from Smoothing_Modules import d2_smoothing, d1_smoothing, time_calculation
from CustomModules import global_vars
import main_smoothing 
import rope_parameter_preparation
import motor_parameters_preperation

def main(mot_coords,stopped_frames, usage, np_paths, delta_ts, num_of_frames, max_x, max_z, duo_duo = False, first_motor_number = None):
    """
        Main function to calculate motor parameters for DUAL motors and write parameters to txt files.
        
        Parameters
        ----------
        motor_coord : user inputted motor coordinates 
        
        stopped_frames : frames that are inputted as stop frame by user for solo motor

        usage : The usage mode of motors which could be DUO-DUO / SOLO-SOLO-SOLO / DUO-SOLO-SOLO / SOLO-DUO-SOLO / SOLO-SOLO-DUO

        np_paths : the path that end effector's pass


        delta_ts : times that have been entered by user for each frames

        num_of_frames : total number of frames inputted by user

        max_x :  maximum x value among all paths

        max_z : maximum z value among all paths

        duo_duo : controling whether the usage is DUO-DUO or not. False by default.
        
        first_motor_number : name that is using for generating txt file
    """
    error_occured = False

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
        if usage == "1001":
            path_spline = np_paths[1]
        elif usage == "1100":
            path_spline = np_paths[2]
        elif usage == "0011":
            path_spline = np_paths[0]
        if duo_duo:
            path_spline = np_paths
        tck, u = d2_smoothing.make_spline(path_spline)
    except Exception as e:
        error_occured = e
        print("make_spline function FAILED in duo_motor")
        print(e)
        return error_occured
    
    # Second, match user given times with calculated u parameters at the spline
    try:
        time_vs_u = d2_smoothing.t_wrt_u(delta_ts,u,stopped_frames)
    except Exception as e:
        error_occured = e
        print("project_t_on_u function FAILED in duo_motor")
        print(e)
        return error_occured
      
    # Third, to get more samples from constructed spline, divide spline by global_vars.DELTA_LENGTH into pieces.
    try:
        x_points, z_points, u_values = d2_smoothing.populate_spline(tck,u)
    except Exception as e:
        error_occured = e
        print("populate_spline function FAILED in duo_motor")
        print(e)
        return error_occured

    # Fourth, in order to calculate rope lengths, transform x-z cartesian coordinates to configuration coordinates by: 
        # calculating step by step rope lengths at every u value after populated spline.
    try:
        motor_coordinates = []
        if usage == "1001":
            motor_coordinates.append(mot_coords[1])
            motor_coordinates.append(mot_coords[2])
        elif usage == "1100":
            motor_coordinates.append(mot_coords[2])
            motor_coordinates.append(mot_coords[3])
        elif usage == "0011":
            motor_coordinates.append(mot_coords[0])
            motor_coordinates.append(mot_coords[1])
        
        if duo_duo:
            if first_motor_number == 0:
                motor_coordinates.append(mot_coords[0])
                motor_coordinates.append(mot_coords[1])
            else:
                motor_coordinates.append(mot_coords[2])
                motor_coordinates.append(mot_coords[3])
                
        rope_1, rope_2 = d2_smoothing.conv_cart_to_conf(x_points, z_points, motor_coordinates)
    except Exception as e:
        error_occured = e
        print("conv_cart_to_conf function FAILED in duo_motor")
        print(e)
        return error_occured
   
    # Fifth, by thinking spline as a straigth line and by using given time at every frame:
        # Calculate the velocity for end-effector at every u value by using clasic Newton formulas.
        # According to velocities and locations calculate the time passed at every u values.
        # Then, u values automatically become the time values that will be used in rope velocity calculations.
    try:
        times_and_velocities_for_end_effector = d2_smoothing.project_t_on_populated_u(delta_ts,stopped_frames,rope_1, rope_2, time_vs_u,u_values,x_points,z_points)

    except Exception as e:
        error_occured = e
        print("project_t_on_populated_u function FAILED in duo_motor")
        print(e)
        return error_occured   
    
    # Sixth, by using time and velocities of end effector draw graph of it.
    try:
        max_time = 0
        end_effector_vel_vs_time = []
        for time , vel in times_and_velocities_for_end_effector:
            if vel == "stop":
                vel = 0
            end_effector_vel_vs_time.append((vel,time))
            max_time = (max(max_time, time))
        
        d2_smoothing.draw_plot(end_effector_vel_vs_time, max_time, 0.2, -0.2, "End Effector Velocity", "Velocity")
    except Exception as e:
        error_occured = e
        print("draw_plot for rope1 function FAILED in duo_motor")
        print(e)
        return error_occured

    # Seventh, use calculated time values to understand the time based rope length.
    try:
        rope_1_point_vs_t, max_t_1, max_length_1, min_length_1 = d2_smoothing.project_time_and_velocities_on_rope(rope_1, time_vs_u, u_values, times_and_velocities_for_end_effector)
    except Exception as e:
        error_occured = e
        print("project_t_on_rope for rope1 function FAILED in duo_motor")
        print(e)
        return error_occured
    try:
        d2_smoothing.draw_plot(rope_1_point_vs_t, max_t_1, max_length_1, min_length_1, "Rope 1")
    except Exception as e:
        error_occured = e
        print("draw_plot for rope_1_point_vs_t function FAILED in duo_motor")
        print(e)
        return error_occured
    try:
        rope_2_point_vs_t, max_t_2, max_length_2, min_length_2 = d2_smoothing.project_time_and_velocities_on_rope(rope_2, time_vs_u, u_values,times_and_velocities_for_end_effector)
    except Exception as e:
        error_occured = e
        print("project_t_on_rope for rope2 function FAILED in duo_motor")
        print(e)
        return error_occured
    try:
        d2_smoothing.draw_plot(rope_2_point_vs_t, max_t_2, max_length_2, min_length_2, "Rope 2")
    except Exception as e:
        error_occured = e
        print("draw_plot for rope_2_point_vs_t function FAILED in duo_motor")
        print(e)
        return error_occured 
    
    # Eighth, from time based rope length calculate the rope velocities at every time value. 
        # TODO: They include own draw graph functions change it
    try:
        rope_1_velocities_vs_times = d2_smoothing.rope_velocity_from_length_vs_time(rope_1_point_vs_t)
    except Exception as e:
        error_occured = e
        print("rope_velocity_from_length_vs_time for rope1 function FAILED in duo_motor")
        print(e)
        return error_occured
    try:
        rope_2_velocities_vs_times = d2_smoothing.rope_velocity_from_length_vs_time(rope_2_point_vs_t)
    except Exception as e:
        error_occured = e
        print("rope_velocity_from_length_vs_time for rope2 function FAILED in duo_motor")
        print(e)
        return error_occured   

    # Ninth, calculate average velocities values from velocity values.
    try:
        average_rope_1_velocities = rope_parameter_preparation.average_velocity_calculation(rope_1_velocities_vs_times)
    except Exception as e:
        error_occured = e
        print("average_velocity_calculation for rope1 function FAILED in duo_motor")
        print(e)
        return error_occured
    
    try:
        average_rope_2_velocities = rope_parameter_preparation.average_velocity_calculation(rope_2_velocities_vs_times)
    except Exception as e:
        error_occured = e
        print("average_velocity_calculation for rope2 function FAILED in duo_motor")
        print(e)
        return error_occured
    # Tenth, combine location and average velocity for dual working motors to use them as motor parameters.
    try:
        rope_1_lengths = []
        for point, time in rope_1_point_vs_t:
            rope_1_lengths.append(point)
        rope_1_parameters = rope_parameter_preparation.rope_parametes_in_meters_and_seconds(average_rope_1_velocities,rope_1_lengths)
    except Exception as e:
        error_occured = e
        print("rope_parametes_in_meters_and_seconds for rope1 function FAILED in duo_motor")
        print(e)
        return error_occured
    
    try:
        rope_2_lengths = []
        for point, time in rope_2_point_vs_t:
            rope_2_lengths.append(point)
        rope_2_parameters = rope_parameter_preparation.rope_parametes_in_meters_and_seconds(average_rope_2_velocities,rope_2_lengths)
    except Exception as e:
        error_occured = e
        print("rope_parametes_in_meters_and_seconds for rope2 function FAILED in duo_motor")
        print(e)
        return error_occured
    # Eleventh, preparing motor parameters for each motor
    try:
        time = []
        for i in range(len(rope_1_velocities_vs_times)):
            time.append(rope_1_velocities_vs_times[i][1])
        motor_parameters_for_motor_1 = motor_parameters_preperation.motor_parameters_preperation(rope_1_parameters,time)
    except Exception as e:
        error_occured = e
        print("motor_parameters_preperation for rope1 function FAILED in duo_motor")
        print(e)
        return error_occured
    
    try:
        time = []
        for i in range(len(rope_2_velocities_vs_times)):
            time.append(rope_2_velocities_vs_times[i][1])
        motor_parameters_for_motor_2 = motor_parameters_preperation.motor_parameters_preperation(rope_2_parameters,time)
    except Exception as e:
        error_occured = e
        print("motor_parameters_preperation for rope2 function FAILED in duo_motor")
        print(e)
        return error_occured

    
    # Twelfth, writing motor parameters to files named as MotorX.txt 
    try:
        if usage == "0011":
            motorname = "Motor0.txt"
        elif usage == "1001":
            motorname = "Motor1.txt"
        elif usage == "1100":
            motorname = "Motor2.txt"

        if duo_duo:
            motorname = "Motor" + str(int(first_motor_number)) + ".txt"

        motor_parameters_preperation.writing_motor_params(usage,motor_parameters_for_motor_1, file_name = (input_path + rev_Id + "-" + motorname))
    except Exception as e:
        error_occured = e
        print("writing_motor_params for rope1 function FAILED in duo_motor")
        print(e)
        return error_occured
    
    try:
        if usage == "0011":
            motorname = "Motor1.txt"
        elif usage == "1001":
            motorname = "Motor2.txt"
        elif usage == "1100":
            motorname = "Motor3.txt"
        
        if duo_duo:
            motorname = "Motor" + str(int(first_motor_number+1)) + ".txt"

        motor_parameters_preperation.writing_motor_params(usage,motor_parameters_for_motor_2, file_name = (input_path + rev_Id + "-" + motorname))
    except Exception as e:
        error_occured = e
        print("writing_motor_params for rope2 function FAILED in duo_motor")
        print(e)
        return error_occured


    

if __name__ == "__main__":
    np_paths, delta_ts, num_of_frames, max_x, max_z  = main_smoothing.read_user_input()
    mot_coords, usage = main_smoothing.get_motor_coords()
    main(mot_coords, usage, np_paths, delta_ts, num_of_frames, max_x, max_z)