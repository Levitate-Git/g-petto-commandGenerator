
import numpy as np
from scipy import interpolate
from CustomModules import global_vars
from Smoothing_Modules import duo_motors, solo_motor
import sys

board_ID = sys.argv[1]
rev_Id = sys.argv[2]
input_path = ("/tmp/boards/" + board_ID + "/inputs/")
output_path = ("/tmp/boards/" + board_ID + "/outputs/")


def read_user_input():
    """
    Reading the txt file which contains user inputs that have been created by using Gepetto GUI.

    Returns
    ------ 
    np_paths : list of paths that end effectors pass.

    delta_ts :  times that have been entered by user for each frames

    num_of_frames : total number of frames inputted by user

    max_x :  maximum x value among all paths

    max_z : maximum z value among all paths

    """
    
    paths = []
    path1 = []
    path2 = []
    path3 = []
    path4 = []
    delta_ts = []
    with open(input_path + rev_Id + "-frame_points.txt", "r") as file:
        i = 0
        for line in file:
            #remove trailing new lines and split words
            words_in_line = line.strip().split(" ")
            #first line has configuration data formatted like
            # usage num_of_frames rth_enabled motor1_coord ...
            if i == 0:
                num_of_frames = int (words_in_line[1])
                #last two words are the motor4 coords,
                #which is fartest from origin so take their values to plot graph limits
                max_x = float(words_in_line[-2])
                max_z = float(words_in_line[-1])
            #first path
            elif i < num_of_frames+1:
                path1.append((float(words_in_line[0]), float(words_in_line[1])))
                delta_ts.append(float(words_in_line[2]))

            elif i < 2 * num_of_frames +1:
                path2.append((float(words_in_line[0]), float(words_in_line[1])))

            elif i < 3 * num_of_frames +1:
                path3.append((float(words_in_line[0]), float(words_in_line[1])))

            else:
                path4.append((float(words_in_line[0]), float(words_in_line[1])))

            i += 1

    paths = [path1, path2]
    del path1, path2
    #we can have at min 2 paths if duo-duo, so check for others
    if path3:
        paths.append(path3)
        del path3
        if path4:
            paths.append(path4)
            del path4
    np_paths = []
    
    for path in paths:
        np_paths.append(path)
    del paths
    return np_paths, delta_ts, num_of_frames, max_x, max_z 

def get_motor_coords():
    """
    Getting motor coordinates and usage info from text file created by Gepetto GUI by using user inputs.

    Returns
    -------
    mot_coords : x and z coordinates for each motors.

    usage : The usage mode of motors which could be DUO-DUO / SOLO-SOLO-SOLO / DUO-SOLO-SOLO / SOLO-DUO-SOLO / SOLO-SOLO-DUO
    """
    with open(input_path + rev_Id +"-frame_points.txt", "r") as file1:
        line0 = file1.readline().strip().split(" ")
        print(line0)
        usage = line0[0]
        mot_coords = []
        for i in range(global_vars.NUM_OF_MOTORS):
            temp1 = float(line0[i*2 + 2])
            temp2 = float(line0[i*2 + 3])
            mot_coords.append((temp1,temp2))
        
        del temp1
        del temp2
        return mot_coords, usage

def manupulating_user_input(np_paths):
    """
    Taking out the stopped frames that have been inputted by user.
    
    Parameters
    ---------
    np_paths : list of paths that end effectors pass.

    Returns
    -------
    new_paths : end effectors' paths which's stopped frames are extracted 

    all_stopped_frames : frames that are inputted as stop frame by user for all motors.
    """
    all_stopped_frames = []
    popped_frames = []
    new_paths = []
    path_num = 1
    stopped_increment_in_meters = global_vars.POINT_R
    j = 0
    for path in np_paths:   
        i = 0
        for i in range(len(path)):
            if ((path[i][0] - path[i-1][0])**2 + (path[i][1] - path[i-1][1])**2)**0.5 < stopped_increment_in_meters and i != 0:
                all_stopped_frames.append((path_num,i-1))
                popped_frames.append(i)    
            i +=1
        while abs(j) < len(popped_frames):
            j -= 1
            frame = popped_frames[j]
            length = len(path) - 1

            if frame == length:
                path.pop(frame-1)
            else:
                path.pop(frame) 

        j = 0    
        popped_frames.clear()
        new_paths.append(path)
        path_num += 1
    
    return new_paths , all_stopped_frames

def main():
    """
    This is the main function that calculates motor paramaters for all usage cases
    """
    error_occured = False
    try:
        paths, delta_ts, num_of_frames, max_x, max_z = read_user_input()
    except Exception as e:
        error_occured = e
        print("read_user_input function FAILED")
        print(e)
        return error_occured
    
    try:
        new_paths, all_stopped_frames = manupulating_user_input(paths)
    except Exception as e:
        error_occured = e
        print("manupulating_user_input function FAILED")
        print(e)
        return error_occured
    
    try:
        mot_coords, usage = get_motor_coords()
        print(usage)
    except Exception as e:
        error_occured = e
        print("get_motor_coords function FAILED")
        print(e)
        return error_occured
    
    try:
        stopped_frames = []
        if usage == "1001":
            stopped_frames.clear()
            for path_num,frame in all_stopped_frames:
                if path_num == 2:
                    stopped_frames.append(frame)
            duo_motors.main(mot_coords,stopped_frames, usage, new_paths, delta_ts, num_of_frames, max_x, max_z)
            stopped_frames.clear()
            
            for path_num,frame in all_stopped_frames:
                if path_num == 1:
                    stopped_frames.append(frame)
            path = new_paths[0]
            motor_coord = mot_coords[0][1] # We need z value of motor
            motorname = input_path + rev_Id +"-Motor0.txt"
            solo_motor.main(motor_coord,stopped_frames, usage, path, delta_ts, num_of_frames, max_x, max_z,motorname)
            stopped_frames.clear()
            
            for path_num,frame in all_stopped_frames:
                if path_num == 3:
                    stopped_frames.append(frame)
            path = new_paths[2]
            motor_coord = mot_coords[3][1]
            motorname = input_path + rev_Id +"-Motor3.txt"
            solo_motor.main(motor_coord,stopped_frames, usage, path, delta_ts, num_of_frames, max_x, max_z,motorname)
            stopped_frames.clear()

        elif usage == "1100":
            for path_num,frame in all_stopped_frames:
                if path_num == 3:
                    stopped_frames.append(frame)

            duo_motors.main(mot_coords,stopped_frames, usage, new_paths, delta_ts, num_of_frames, max_x, max_z)
            stopped_frames.clear()
            
            for path_num,frame in all_stopped_frames:
                if path_num == 1:
                    stopped_frames.append(frame)
            path = new_paths[0]
            motorname = input_path + rev_Id +"-Motor0.txt"
            motor_coord = mot_coords[0][1]
            solo_motor.main(motor_coord,stopped_frames, usage, path, delta_ts, num_of_frames, max_x, max_z,motorname)
            stopped_frames.clear()

            for path_num,frame in all_stopped_frames:
                if path_num == 2:
                    stopped_frames.append(frame)            
            path = new_paths[1]
            motor_coord = mot_coords[1][1]
            motorname = input_path + rev_Id +"-Motor1.txt"
            solo_motor.main(motor_coord,stopped_frames, usage, path, delta_ts, num_of_frames, max_x, max_z,motorname)
            stopped_frames.clear()

        elif usage == "0011":
            stopped_frames.clear()
            for path_num,frame in all_stopped_frames:
                if path_num == 1:
                    stopped_frames.append(frame)
            duo_motors.main(mot_coords,stopped_frames, usage, new_paths, delta_ts, num_of_frames, max_x, max_z)
            stopped_frames.clear()
                      
            for path_num,frame in all_stopped_frames:
                if path_num == 2:
                    stopped_frames.append(frame)
            path = new_paths[1]
            motor_coord = mot_coords[2][1]
            motorname = input_path + rev_Id +"-Motor2.txt"
            solo_motor.main(motor_coord,stopped_frames, usage, path, delta_ts, num_of_frames, max_x, max_z,motorname)
            stopped_frames.clear()

            for path_num,frame in all_stopped_frames:
                if path_num == 3:
                    stopped_frames.append(frame)
            path = new_paths[2]
            motor_coord = mot_coords[3][1]
            motorname = input_path + rev_Id +"-Motor3.txt"
            solo_motor.main(motor_coord,stopped_frames, usage, path, delta_ts, num_of_frames, max_x, max_z,motorname)

        elif usage == "0000":
            for i in range(2):
                if i == 0:
                    motor_number = 0
                else:
                    motor_number = 2
                stopped_frames.clear()
                for path_num,frame in all_stopped_frames:
                    if path_num == i+1:
                        stopped_frames.append(frame)
                duo_motors.main(mot_coords,stopped_frames, usage, new_paths[i], delta_ts, num_of_frames, max_x, max_z,duo_duo = True,first_motor_number = motor_number)
                stopped_frames.clear()

        elif usage == "1111":
            motornum = 0
            for path in new_paths:
                stopped_frames.clear()
                for path_num,frame in all_stopped_frames:
                    if path_num == motornum+1:
                        stopped_frames.append(frame)

                motor_coord = mot_coords[motornum][1]
                motorname = input_path + rev_Id +"-Motor" + str(motornum) +".txt"
                solo_motor.main(motor_coord,stopped_frames, usage, path, delta_ts, num_of_frames, max_x, max_z,motorname)
                motornum += 1
                stopped_frames.clear()
                
    except Exception as e:
        error_occured = e
        print("Getting Move Parameters FAILED in main_smoothing")
        print(e)
        return error_occured

if __name__ == "__main__":
    main()
