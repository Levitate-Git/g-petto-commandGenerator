import json
from CustomModules import global_vars


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

def writing_json_file(total_frame_amount,combination, frame_amount, all_motor_parameters, file_name="levitate"):
    if total_frame_amount % 100 != 0:
        json_file_amount = int(total_frame_amount /100) + 1
    else:
        json_file_amount = int(total_frame_amount /100)
    remaining_frame_amount = total_frame_amount
    counter = 0
    json_num = 0
    k = 0
    for j in range(json_file_amount):
        
        if remaining_frame_amount > 100:
            file_frames = 100
        else:
            file_frames = remaining_frame_amount
        
        if remaining_frame_amount % 100  != 0:
            next_file_amount = int(remaining_frame_amount / 100)

        else:
            next_file_amount = int(remaining_frame_amount / 100) -1 

        with open(file_name + "_" +str(json_num) + ".json", "w") as file:
            file.write ("{" + "\n" \
                        '"combination": ' + str(combination) + "," +"\n" \
                        '"total_frames_0": ' + str(frame_amount[0][1]) + "," +"\n" \
                        '"total_frames_1": ' + str(frame_amount[1][1]) + "," +"\n" \
                        '"total_frames_2": ' + str(frame_amount[2][1]) + "," +"\n" \
                        '"total_frames_3": ' + str(frame_amount[3][1]) + "," +"\n" \
                            +"\n" \
                        '"file_frames": ' + str(int(file_frames)) + "," +"\n" \
                        '"next_file": ' + str(int(next_file_amount)) + "," +"\n"   
                        '"frame_2d": ' + "[" + "\n")     

            counter += file_frames                
            
            while k <= counter-1:
                step = all_motor_parameters[k][0]
                vel = all_motor_parameters[k][1]
                direct = all_motor_parameters[k][2]
                if k == counter-1:
                    file.write("\t" + "\t" + str(step) + "," + "\n" \
                                "\t" + "\t" + str(vel) + "," + "\n"  
                                "\t" + "\t" + str(direct) + "\n" )
                else:
                    file.write("\t" + "\t" + str(step) + "," + "\n" \
                                "\t" + "\t" + str(vel) + "," + "\n"  
                                "\t" + "\t" + str(direct) + "," + "\n" + "\n" )
                k += 1
                remaining_frame_amount -= 1
            file.write("\t"+"]" + "\n" + "}")
            file.close()
        json_num += 1


def reading_motor_params():
    all_motor_params = []
    frame_amount = []
    total_frame_amount = 0

    for num in range(4):
        name = input_path + rev_Id + "-Motor" + str(num) + ".txt"
        with open(name, "r") as file:
            line_num = 0
            for line in file:
                #remove trailing new lines and split words
                words_in_line = line.strip().split(",")
                if line_num == 0:
                    combination = words_in_line[1]
                else:
                    all_motor_params.append((words_in_line[0],words_in_line[1],words_in_line[2]))
                line_num += 1
        total_frame_amount += line_num - 1
        frame_amount.append((name,line_num-1))

    return all_motor_params, frame_amount, combination, total_frame_amount

def main():
    error_occured = False
    
    try:
        all_motor_parameters, frame_amount, combination, total_frame_amount = reading_motor_params()
    except Exception as e:
        error_occured = e
        print("reading_motor_params function FAILED in json_preperation")
        print(e)
        return error_occured
    
        
    try:
        writing_json_file(total_frame_amount,combination, frame_amount, all_motor_parameters, output_path + rev_Id + "-levitate")
    except Exception as e:
        error_occured = e
        print("writing_json_file function FAILED in json_preperation")
        print(e)
        return error_occured
    
if __name__ == "__main__":
    main()
    