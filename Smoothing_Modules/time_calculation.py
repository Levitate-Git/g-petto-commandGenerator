from CustomModules import global_vars
import numpy as np
import math


class TimeCalculations:
    """
        This class calculates the needed time to pass a sub frame by using user inputs and classic physics.
    """
    
    max_speed = global_vars.MAX_SPEED_IN_METERS             # Max speed that an end effector can have.
    min_speed = global_vars.MIN_SPEED_IN_METERS             # Min speed that an end effector can have.
    max_acceleration = global_vars.MAX_ACCLERATION          # Max acceleration that an end effector can have.
    min_acceleration = global_vars.MIN_ACCLERATION          # Min acceleration that an end effector can have.

    def __init__(self):
        self.start_velocity = float(0)                      # Start velocity of frame
        self.end_velocity = float(0)                        # End velocity of frame
        self.acceleration = float(0)                        # Acceleration within a frame
        self.total_length_of_spline_part = float(0)         # Total path length of frame
        self.total_time_passed = float(0)                   # Time passed till stated point
        self.delta_t = float(0)                             # Time for stated user inputted frame
        self.total_spline = float(0)                        # Total path length passed till stated point
        self.i = 1                                          # Counter for calcuations 
 
        self.k = 1                                          # Counter for calcuations 
        self.g = 0                                          # Counter for calcuations 
        self.m = 1                                          # Counter for calcuations 
        
        self.average_speeds_of_frames = []                  # Average speed within a user inputted frame
        self.times_of_intervals = []                        # Time values for sub-frames
        self.velocities = []                                # List of velocities
        self.start_velocities = []                          # List of frames' start velocities
        self.accelerations = []                             # List of accelerations within frames                 
        self.end_velocities = []                            # List of end velocities
        self.times_and_velocities_for_end_effector = []     # Returning list of calculated frame times and velocities
  
    def calculating_average_end_effector_speed(self, list_position, time_vs_u,xs,zs):
        """
            Calculating the average speed within frames. Average speed values are used in end_velocity calculations for double acceleration frames.

            Parameter
            ---------
            list_positions : list type
                List of list indexes for user inputted frames after populated spline.

            time vs_u : list type
                Time values corresponding u values as user inputted.
            
            xs : list type
                List of x values corresponding to the divided path values values

            zs : list type
                List of z values corresponding to the divided path values values

            Returns
            -------
            self.average_speeds_of_frames : list type
                Average speed within a user inputted frame
            
            Errors
            ------
            Error_Type: 101 
                Max speed limit is exceeding please increase the frame time
        """
        
        a = 0
        b = 1
        frame = -1
        for pos in list_position:
            frame += 1
            length_of_spline_part = 0
            if a == 0:
                a += 1
                pass
            else:
                while a < (pos+1) and (a-1) < list_position[-1]:
                    temp_length_of_small_piece = ( (xs[a]-xs[a-1])**2 + (zs[a]-zs[a-1])**2 )**0.5
                    length_of_spline_part += temp_length_of_small_piece
                    a += 1
                frame_time = time_vs_u[b][0] - time_vs_u[b-1][0]
                average_speed_in_frame = length_of_spline_part / frame_time
                b += 1
                if average_speed_in_frame > self.max_speed:
                    raise ValueError (f"Error_Type=101,Frame={frame}")
                    
                self.average_speeds_of_frames.append(average_speed_in_frame)
        del a
        del b
        del length_of_spline_part
        del average_speed_in_frame

        return self.average_speeds_of_frames
 
    def solving_with_jerk_control(self,pos,list_position, end_velocity,time_vs_u,xs,zs):
        """
            Calculating acceleration and velocities to solve the inputted frame by using jerk calculation method
            #TODO: jerk calculation methodun açıklama linki eklenecek.
            Parameter
            ---------
            pos : integer type
                List index corresponding to the user inputted frame within all sub frames

            list_positions : list type
                List of list indexes for user inputted frames after populated spline.

            end_velocity : float type
                End velocity of the frame which is calculating. 

            time vs_u : list type
                Time values corresponding u values as user inputted.
            
            xs : list type
                List of x values corresponding to the divided path values values.

            zs : list type
                List of z values corresponding to the divided path values values.

            Returns
            -------
            self.times_and_velocities_for_end_effector : list type
                Returning list of calculated frame times and velocities.
            
            Errors
            ------
            Error_Type: 101 
                Max speed limit is exceeding please increase the frame time
            Error_Type: 102 
                Max speed limit is exceeding please increase the frame time
            Error_Type: 103
                There are no real roots to compute this frame's velocties.
        """
        
        
        self.total_length_of_spline_part = float(0)
        # First we fing the length of spline
        while self.m < (pos+1) and (self.m-1) < list_position[-1]:
            length_of_small_piece = ( (xs[self.m]-xs[self.m-1])**2 + (zs[self.m]-zs[self.m-1])**2 )**0.5 
            self.total_length_of_spline_part += length_of_small_piece
            self.m += 1
        self.total_spline += self.total_length_of_spline_part
        self.delta_t = time_vs_u[self.i][0] - time_vs_u[self.i-1][0]
        

        # Acceleration is written as a = b * t + c
            # a = acceleration
            # b = b_element
            # c = c_element
        # Finding velocity and location by integrating acceleration
            # end_velocity = b * t^2 / 2 + c * t + start_velocity
            # location = (b * t^3)/6 +(c * t^2)/2 + start_velocity * t
        # Using the equations above we found c_element and b_element as below:
        self.end_velocity = end_velocity
        c_element = (self.total_length_of_spline_part - self.end_velocity * self.delta_t/3 - 2 * self.start_velocity * self.delta_t /3)/((self.delta_t**2)/6)
        b_element = (self.end_velocity - self.start_velocity - c_element * self.delta_t)/((self.delta_t**2) / 2)
             
 
        velocity = self.start_velocity
        time_at_sub_frame = 0
        length_of_intervals = []
        all_roots = []
        total_length = 0
        old_velocity = velocity

        while self.k < (pos + 1) and (self.k-1) < list_position[-1]:
            length_of_interval = ( (xs[self.k]-xs[self.k-1])**2 + (zs[self.k]-zs[self.k-1])**2 )**0.5
            length_of_intervals.append(length_of_interval)
            total_length += length_of_interval
            # Solving time for each length of interval means solving 3. degree equation derived from definite integral:
                # location = (b * t^3)/6 +(c * t^2)/2 + start_velocity * t

            coef1 = b_element / 6
            coef2 = c_element / 2
            coef3 = self.start_velocity
            coef4 = -total_length
            np_coefs = [coef1,coef2,coef3,coef4]
            roots = np.roots(np_coefs)
            all_roots.append(roots)
            temp =[]
            for root in roots:
                if root > 0 and abs(np.imag(root))<0.0001 :
                    temp2 = np.real(root)
                    temp.append(temp2)
            if len(temp) == 1:
                time_at_sub_frame = temp[0]
            elif len(temp) >= 2:
                if time_at_sub_frame > min(temp):
                    time_at_sub_frame = max(temp)
                else:
                    time_at_sub_frame = min(temp)
            else:
                raise ValueError (f"Error_Type=104,Frame={self.i}")
            del temp2
            np_coefs.clear()
            temp.clear()
            
            # Solving velocity as a definite integral
            velocity = self.start_velocity + b_element * (time_at_sub_frame**2) /2 + c_element * (time_at_sub_frame)
            # Controlling maximum velocity and acceleration
            control_acceleration = (velocity - old_velocity) / self.delta_t
            if abs(control_acceleration) > self.max_acceleration:
                raise ValueError (f"Error_Type=102,Frame={self.i}")
            if abs(velocity) > self.max_speed:
                raise ValueError (f"Error_Type=103,Frame={self.i}")
            
            self.times_of_intervals.append(self.total_time_passed + time_at_sub_frame)
            self.velocities.append(velocity)
            self.k += 1
            old_velocity = velocity
            
        self.total_time_passed += time_at_sub_frame

        self.start_velocity = velocity
                   
        
        
        
        if abs(velocity - self.end_velocity)<0.001:
            print("Velocities are same as calculated at the end-- double_acceleration_within_a_frame in TimeCalculations class")
        else:
            print("There is something wrong with the velocities-- double_acceleration_within_a_frame in TimeCalculations class")
        
        if len(self.velocities) == len(self.times_of_intervals):
            while self.g < len(self.velocities):
                self.times_and_velocities_for_end_effector.append((self.times_of_intervals[self.g],self.velocities[self.g]))
                self.g += 1
        else:
            print("There is something wrong with the length of time arrivals-- double_acceleration_within_a_frame in TimeCalculations class")
        self.i += 1
        
        del old_velocity
        del velocity
        del b_element
        del c_element
        del np_coefs
        del coef1
        del coef2
        del coef3
        del coef4
        del temp
        del root
        del roots
        del all_roots
        
        return self.times_and_velocities_for_end_effector    
        
    def stopped_frame(self,time_vs_u):
        """
            Importing stopped frames as frames into the list self.times_and_velocities_for_end_effector

            Parameters
            ----------
            time vs_u : list type
                Time values corresponding u values as user inputted.
            
            Returns
            -------
            self.times_and_velocities_for_end_effector : list type
                Returning list of calculated frame times and velocities

        """
        self.delta_t = time_vs_u[self.i][0] - time_vs_u[self.i-1][0]
        self.total_time_passed += self.delta_t
        self.times_of_intervals.append(self.total_time_passed)
        self.velocities.append(0)
        
        if self.g == 0:
            self.g = 2
        else:    
            self.g += 1
        self.i += 1
        self.times_and_velocities_for_end_effector.append((self.times_of_intervals[-1],"stop"))
        
        print("Stopped Frame calculated")
        return self.times_and_velocities_for_end_effector
    
    def zeroth_frame(self):
        """
            Adding needed values of time and velocities to the lists "self.times_of_intervals" and "self.velocities" for starting point
        """
        self.times_of_intervals.append(float(0))
        self.velocities.append(float(0))