import numpy as np
from scipy import interpolate
from CustomModules import global_vars
import math
import main_smoothing
from Smoothing_Modules import time_calculation

def make_spline(path):
    """
        Producing a cubic spline by using splprep method from scipy interpolate.
        
        Parameters
        ----------
        path : list type
            Points on path that end effectors passed.

        Returns
        -------
        tck : tuple type
            A tuple contains parameter of created spline.

        u : list type
            values between 0-1, corresponding to the user inputted frames. u value at zeroth frame is zero. u value at last frame is one.
    """
    np_path = np.asarray(path)
    tck, u = interpolate.splprep([np_path[:, 0], np_path[:, 1]], s=0)  # making a spline from given coordinates(x=path[:,0] and z=path[:,0]) by using splprep

    return tck, u

def t_wrt_u(delta_t, u,stopped_frames):
    """
        Projecting t values on u values (before populated) of spline helps us to divide spline into time intervals as user input.

        Parameters
        ----------

        delta_t : list type
            Times that have been entered by user for each frames.

        u : list type
            List of values between 0-1, corresponding to the user inputted frames. u value at zeroth frame is zero. u value at last frame is one.

        stopped_frames: list type
            The frames that are stopped afterwards.
        Returns
        -------
        time vs_u : list type
            Time values corresponding u values as user inputted.
    """
    st_frames=[]
    s_frames = []
    if len(stopped_frames) > 0:
        for frame in stopped_frames:
            st_frames.append(frame)

        for j in range(len(stopped_frames)):
            s_frames.append(stopped_frames[j])

    temp = 0
    i = 0 # u counter
    s = 0 # delta_t counter
    time_vs_u = []
    while s < len(delta_t):
        if s == 0:
            temp = 0
            time_vs_u.append((temp,u[i]))
            s += 1
            if len(s_frames)>0 :
                while s_frames[0] == s-1:
                    temp += delta_t[s]
                    time_vs_u.append((temp,u[0]))
                    s_frames.pop(0)
                    s_frames.append(0)
                    s += 1
                    if not len(s_frames) > 0:
                        break
                 
                
        else:
            if len(s_frames)>0:
                if s_frames[0] == s:
                    temp += delta_t[s]
                    time_vs_u.append((temp,u[i]))
                    s+=1
                    while s_frames[0] == s-1:
                        temp += delta_t[s]
                        time_vs_u.append((temp,u[i]))
                        s_frames.pop(0)
                        s_frames.append(0)
                        s += 1

                        if not len(s_frames) > 0:
                            break
                else:
                    temp += delta_t[s]
                    time_vs_u.append((temp,u[i]))
                    s += 1
                                    
            else:
                temp += delta_t[s]
                time_vs_u.append((temp,u[i]))
                s += 1 
        i += 1


    return time_vs_u

def populate_spline(tck, u):
    """
        In order to populate the spline inputted by user.

        Parameters
        ----------
        tck : tuple type
            A tuple contains parameter of created spline.

        u : list type
            Values between 0-1, corresponding to the user inputted frames. u value at zeroth frame is zero. u value at last frame is one.
        
        Returns
        -------
        xs : list type
            List of x values which are on the constructed splined path of end effector.

        zs : list type
            List of z values which are on the constructed splined path of end effector.

        u_values : list type
            List of u values which refer a sub_frame point on the constructed splined path of end effector. u values are between 0 and 1.

    """
    xs = []
    zs = []
    u_values = []

    k = 0
    l = 0
    m = 0

    for i in range(len(u)-1): # Number of points taken from user -1 = number of intervals in spline.
      
        # Spline length approximation by calculating very small increments.
        spl_leng_pnt = np.linspace(u[i], u[i+1], 10000, endpoint=True)
        x, z = interpolate.splev(spl_leng_pnt, tck)
        total_length_of_spline_part = 0

        
        for j in range(len(x)-1):
            length_of_small_piece = ( (x[j+1]-x[j])**2 + (z[j+1]-z[j])**2 )**0.5
            total_length_of_spline_part += length_of_small_piece      

        frame_div_factor = int(total_length_of_spline_part / global_vars.DELTA_LENGTH)  # Dividing spline into approximately DELTA_LENGTH pieces.

        # Get samples from divided path
        temp = np.linspace(u[i], u[i+1], frame_div_factor + 1, endpoint=True)
        xs_spline, zs_spline = interpolate.splev(temp, tck)
        
        last_element_x = xs_spline[-1]
        last_element_z = zs_spline[-1]
        for u_temp in temp:
            if k == 0:
                u_values.append(u_temp)
   
            elif u_values[-1] != u_temp:
                u_values.append(u_temp)
            k +=1

        # Remove last element when adding, to avoid duplicates.
        # Unless it is the last element, we need end point.
        l = 0
        for x in xs_spline:
            if l == (len(xs_spline)-1):
                pass
            else:
                xs.append(x)
            l +=1
        
        m = 0
        for z in zs_spline:
            if m == (len(xs_spline)-1):
                pass
            else:
                zs.append(z)
            m +=1
    xs.append(last_element_x) # adding last elements
    zs.append(last_element_z) # adding last elements
    
    del temp
    del xs_spline
    del zs_spline 

    
    return xs, zs, u_values

def conv_cart_to_conf(x_points, z_points, motor_coordinates):
    """
        Converting cartesian coordinates to rope1(length of 1. motor) and rope2(length of 2. motor) configuration space coordinates. 
        This method assumes that there is two motors in the system.
        Using basic hypotenuse formulation rope_i = ( ( x-Px(i) )^2 - ( z-Pz(i) )^2 )**0.5 where: 
            
            rope_i  : is the cable length of ith motor
            Px(i)   : is the x value of ith motor.
            PZ(i)   : is the z value of ith motor.
        
        Parameters
        ----------
        x_points : list type
            List of x values corresponding to the divided path values values

        z_points : list type
            List of z values corresponding to the divided path values values

        motor_coordinates : list type
            List of lists of motor coordinates that will be used in 2D motion
        
        Return
        ------
        configuration_coordinates : list type
            List of coordinates in configuration space
    """
    rope_1=[]
    rope_2=[]
    temp = 0 
    horizontal_dist = 0 #for experimenting purpose /horizontal distance between rope connection points to center point

    # Configuration space coordinates for rope        
    for i in range(len(x_points)) :

        temp1 = ( (x_points[i] - horizontal_dist - motor_coordinates[0][0] )**2 + (z_points[i] - motor_coordinates[0][1])**2 )**0.5
        rope_1.append(temp1)
        temp1 = 0
    
    
    for i in range(len(x_points)) :
        temp2 = ( (x_points[i] + horizontal_dist - motor_coordinates[1][0] )**2 + (z_points[i] - motor_coordinates[1][1])**2 )**0.5 
        rope_2.append(temp2)
        temp2 = 0  
    

    del temp

    return rope_1, rope_2



def project_t_on_populated_u(delta_ts,stopped_frames,rope_1_length_values,rope_2_length_values,time_vs_u, u_values, xs,zs):
    """
        We need to find a relationship between u and t according to the movement of end-effectors equations.
        Doing this task involves velocity and time manupulations for every frame in a movement configuration
    """
    time_calculate = time_calculation.TimeCalculations()
    # First we find the u values correponding to the t values that a user inputted
    list_position =[]
    
    for t_vs_u in time_vs_u:
        for i in range(len(u_values)):
            if t_vs_u[1] == u_values[i]:
                list_position.append(i)
    del i
    
    


    # To define the time intervals in a frame we do the steps below:
    average_speed_of_frames = time_calculate.calculating_average_end_effector_speed(list_position, time_vs_u,xs,zs)  
    j = -1 #average velocity counter
    s = 0 #real frame counter including stop frames
    for pos in list_position: 
        enter = True
        # If it is the zero numbered frame we just add a "0" to start time_of_intervals list
        if s == 0:
            time_calculate.zeroth_frame()
            enter = False
        elif average_speed_of_frames[j] == 0:
            times_and_velocities_for_end_effector = time_calculate.stopped_frame(time_vs_u)
            enter = False
        elif s+1 != len(list_position) and pos == list_position[-1]:
            # It means we have stopped frames at the end of the movement.
            if average_speed_of_frames[j] != 0:
                end_velocity = float(0)
                times_and_velocities_for_end_effector = time_calculate.solving_with_jerk_control(pos,list_position, end_velocity,time_vs_u,xs,zs)
            else:
                times_and_velocities_for_end_effector = time_calculate.stopped_frame(time_vs_u)  
            enter = False
        elif s+1 == len(list_position):
            # It means we are at the last frame
            if average_speed_of_frames[j] == 0:
                times_and_velocities_for_end_effector = time_calculate.stopped_frame(time_vs_u)  
            else:
                end_velocity = float(0)
                times_and_velocities_for_end_effector = time_calculate.solving_with_jerk_control(pos,list_position, end_velocity,time_vs_u,xs,zs)
            enter = False                     
        
        if enter:
            end_velocity = average_speed_of_frames[j]
            if abs((zs[pos]-zs[pos-1])/(xs[pos]-xs[pos-1]) - (zs[pos+1]-zs[pos])/(xs[pos+1]-xs[pos]))>1:
                end_velocity = float(0)
            if average_speed_of_frames[j+1] == 0:
                end_velocity = float(0)
            
            times_and_velocities_for_end_effector = time_calculate.solving_with_jerk_control(pos,list_position, end_velocity,time_vs_u,xs,zs)
        s += 1
        j += 1
    print("DUO_MODE FINISHED")    
    
    return times_and_velocities_for_end_effector

def project_time_and_velocities_on_rope(rope_point, time_vs_u, u_values, times_and_velocities_for_end_effector):
    
    time_of_intervals = []
    velocities_of_end_effector = []
    angles_of_end_effector = []
    rope_point_vs_t =[]
    list_position =[]
    
    for i in range(len(times_and_velocities_for_end_effector)):
        time_of_intervals.append(times_and_velocities_for_end_effector[i][0])
        velocities_of_end_effector.append(times_and_velocities_for_end_effector[i][1])

    first_frame_control = True
    if velocities_of_end_effector[0] == "stop":
        for v in range(len(time_of_intervals)):
            if velocities_of_end_effector[v] == "stop":
                if v==0:
                    time_of_intervals.insert(0,0)
                    rope_point.insert(v,rope_point[v])
                else:
                    rope_point.insert(v,rope_point[v])
    else:
        for v in range(len(time_of_intervals)):
            if velocities_of_end_effector[v] == "stop":
                if v==0:
                    time_of_intervals.insert(0,0)
                    rope_point.insert(v,rope_point[v])
                else:
                    rope_point.insert(v-1,rope_point[v-1])
    
    for i in range(len(time_of_intervals)):
        rope_point_vs_t.append((rope_point[i],time_of_intervals[i]))
    
    
    max_t = max(time_of_intervals)
    max_length = max(rope_point)
    min_length = min(rope_point)

    return rope_point_vs_t, max_t, max_length ,min_length


def rope_velocity_from_length_vs_time(rope_point_vs_t):
    #TODO: en son hız olarak neden 0 basmadığını bulmamız gerekiyor
    for_graph_rope_vel_vs_t =[(0,0)]
    for i in range(1,len(rope_point_vs_t)):
        rope_vel = (rope_point_vs_t[i][0] - rope_point_vs_t[i-1][0])/(rope_point_vs_t[i][1] - rope_point_vs_t[i-1][1])
        for_graph_rope_vel_vs_t.append((rope_vel,rope_point_vs_t[i][1]))
    for_graph_rope_vel_vs_t
    draw_plot(for_graph_rope_vel_vs_t,200,0.4,-0.4,"Rope Velocity","Velocity")
    
    rope_vel_vs_t =[]
    for i in range(len(for_graph_rope_vel_vs_t)):
        if i==0:
            if for_graph_rope_vel_vs_t[i+1][0] == 0:
                pass
            else:
                temp = for_graph_rope_vel_vs_t[i]
                rope_vel_vs_t.append(temp)
        else:
            if for_graph_rope_vel_vs_t[i][0]==0:
                rope_vel_vs_t.append(("stop",for_graph_rope_vel_vs_t[i][1]))
            else:
                rope_vel_vs_t.append((for_graph_rope_vel_vs_t[i][0],for_graph_rope_vel_vs_t[i][1]))

    return rope_vel_vs_t
       
def draw_plot(splined_paths, lim_x, lim_y, min_length = -0.1, title="title", y_label="Rope Length"):
    """
    rope_list = []
    time_list = []
    for i in range(len(splined_paths)):
        rope_list.append(splined_paths[i][1])
        time_list.append(splined_paths[i][0])
    fig, ax = plt.subplots()

    ax.plot(rope_list, time_list, 'r-')
    plt.title(title)
    plt.xlabel("T")
    plt.ylabel(y_label)
    plt.xlim(min_length, lim_x+0.5)
    plt.ylim(min_length, lim_y+0.5)
    plt.show()
    """