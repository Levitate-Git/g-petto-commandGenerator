from CustomModules import global_vars
import math

def motor_parameters_preperation(rope_parameters,time):
    makara_radius = global_vars.MAKARA_RADIUS
    pi = global_vars.PI
    one_turn_steps = global_vars.ONE_TURN_STEPS
    
    motor_parameters=[]
    velocities_in_sps = [0]
    step_values = []
    

    for i in range(len(rope_parameters)):
    # Rope Length to Step  
        length_in_meters = rope_parameters[i][0]
        step_value = int((length_in_meters / (2*pi*makara_radius))*one_turn_steps)
        step_values.append(step_value)
 
    # Rope Velocity to SPS(Step Per Second)
    if len(time) == len(step_values):
        for i in range(1,len(step_values)):
            velocity_in_sps_before = (step_values[i]-step_values[i-1])/(time[i]-time[i-1])
            velocity_in_sps = int(abs(velocity_in_sps_before) + 0.5)
            velocities_in_sps.append(velocity_in_sps)
    else:
        print("Length of time list and step list are not equal!")
        raise ValueError
    
    
    if type(rope_parameters[0][1]) == list: 
        directions=[-rope_parameters[0][1][1]]
    else :
        directions = [1]
    for i in range(1,len(step_values)):
        if step_values[i] > step_values[i-1] :
            directions.append(1) # prop going downward
        elif step_values[i] < step_values[i-1] :
            directions.append(0) # prop going upward
        else:
            if type(rope_parameters[i][1]) == list: # When user inputted a stop frame
                directions.append(-rope_parameters[i][1][1])
            else:
                directions.append(0)
    
    for i in range(len(step_values)):
        try:
            temp = int((125000/velocities_in_sps[i])-1)
        except ZeroDivisionError:
            temp = 0
            if i == 0:
                temp = int((125000)-1)
            else:
                directions[i] = -int((abs(time[i]-time[i-1]))*1000)
        if velocities_in_sps[i] <=2:
            temp = 2
            if velocities_in_sps[i] == 0:
                temp = 0
            
        motor_parameters.append((step_values[i],temp,directions[i]))
    
    if step_values[0] > step_values[-1]:
        temp = int(125000/velocities_in_sps[1]-1)
        motor_parameters.append((step_values[0],temp,1))
    elif step_values[0] < step_values[-1]:
        temp = int(125000/velocities_in_sps[1]-1)
        motor_parameters.append((step_values[0],temp,0))
    
    del temp
    
    # Adding a frame if first frame is a stopped one.
    if motor_parameters[0][2] < 0:
        temp = (motor_parameters[0][0],motor_parameters[0][1],int(motor_parameters[0][2]*1000))
        motor_parameters.insert(1,temp)
    return motor_parameters

def writing_motor_params(usage,motor_parameters, file_name="deneme.txt"):
    """
    generic list writing, write every element on a new line
    """
    with open(file_name, "w") as file:
        if usage == "1111":
            file.write("combination:," +str(0) + "\n")
        elif usage == "1100":
            file.write("combination:," +str(1) + "\n")
        elif usage == "1001":
            file.write("combination:," +str(2) + "\n")
        elif usage == "0011":
            file.write("combination:," +str(3) + "\n")	
        elif usage == "0000":
            file.write("combination:," +str(4) + "\n")

        for i in range(len(motor_parameters)):
            file.write( str(motor_parameters[i][0]) + "," + str(abs(motor_parameters[i][1])) + "," + str(motor_parameters[i][2]) + "\n")

        file.close()


