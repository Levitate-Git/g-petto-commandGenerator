"""
functions for writing data to files
"""
from CustomModules import global_vars
def write_a_list_to_file(the_list, file_name="deneme.txt"):
    """
    generic list writing, write every element on a new line
    """
    with open(file_name, "w") as file:
        for item in the_list:
            file.write(str(item)+ "\n")


def write_move_to_and_times_to_file(frames):
    """
    motor parameters and times written for next interpolation of STEPvsTIME graph
    """
    with open("move_to_and_dt.txt", "w") as file1:
        file1.write(str(len(frames)) + "\n")
        for motor in range(global_vars.NUM_OF_MOTORS):
            for frame in frames:
                file1.write(str(frame.move_to[motor]) + " "+ \
                            str(frame.move_time) +" "+ \
                            str(frame.max_speed[motor])+ "\n")


def write_inted_frames_to_file(paths, dts, num_of_frames):
    """
    interpolation result written to txt file
    """
    with open("inted_points.txt", "w") as file:
        file.write(str(num_of_frames) + "\n")
        i = 0
        for path in paths:
            j = 0
            for x, y in zip(path[0], path[1]):
                if i == 0:
                    file.write(str(x) + " "+ str(y)+ " "+ str(dts[j]) + "\n")
                else:
                    file.write(str(x) + " "+ str(y)+ "\n")
                j += 1
            i+= 1

def write_points_to_file(frames, usage, num_of_frames, motor_coords, delta_ts):
    """
    After Gepetto.py GUI program, we want to store saved points and other infos
    """
    import numpy as np

    if not frames:
        print("what")
        return
    np_frames = np.array(frames)
    with open("1-frame_points.txt", "w") as file:
        use_str = ""
        for number in usage:
            use_str += str(number)
        file.write(use_str + " " +str(num_of_frames))
        for point in motor_coords:
            file.write(" " +str(point[0]) + " " + str(point[1]) )
        file.write("\n")
        for i in range(len(frames[0])):
            #multi dim slice, write paths for each point not frame frame
            j = 0
            for point in np_frames[:, i]:
                file.write(str(point[0]) + " "+ str(point[1]))
                if i == 0:
                    file.write(" "+ str(delta_ts[j]) +"\n")
                else:
                    file.write("\n")
                j += 1

def write_in_json_format(params):
    import json
    json_data = {}
    json_data["number_of_frames"] = len(params)
    json_data["frame_2d"] = params
    with open("smooth_step.json", "w") as json_file:
        json.dump(json_data, json_file, indent=2)