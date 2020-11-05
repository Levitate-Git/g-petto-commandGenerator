"""
helper functions
"""

from CustomModules import global_vars

def get_intersections(x0, y0, r0, x1, y1, r1):
    # circle 1: (x0, y0), radius r0
    # circle 2: (x1, y1), radius r1

    d = ((x1-x0)**2 + (y1-y0)**2)**0.5

    # non intersecting
    if d > r0 + r1:
        return None
    # One circle within other
    if d < abs(r0-r1):
        return None
    # coincident circles
    if d == 0 and r0 == r1:
        return None
    else:
        a=(r0**2-r1**2+d**2)/(2*d)
        h=(r0**2-a**2)**0.5
        x2=x0+a*(x1-x0)/d
        y2=y0+a*(y1-y0)/d
        x3=x2+h*(y1-y0)/d
        y3=y2-h*(x1-x0)/d

        x4=x2-h*(y1-y0)/d
        y4=y2+h*(x1-x0)/d
        # print(y3, y4)
        if(y3 < y0):
            return(x3, y3)
        else:
            return (x4, y4)

def step_to_meters(step):
    """
    distance in steps converted to meters
    number_of_turns * circumference = length in meters
    """
    return (step / global_vars.ONE_TURN_STEPS) * 2 *global_vars.PI * global_vars.MAKARA_R


def meter_to_steps(meter):
    """
    distance in meter converted to steps
    """
    num_of_turns = meter /(2 * global_vars.PI * global_vars.MAKARA_R)
    return num_of_turns * global_vars.ONE_TURN_STEPS


def import_json_from_url():
    import json
    import urllib.request
    with urllib.request.urlopen("http://levitate.com.tr/nodemcu_output.json") as frame_json:
        first_data = json.loads(frame_json.read().decode())
    i = 0
    num_of_frames = first_data["Number of Frames"]
    frames = []
    for frame in first_data["Frames"]:
        temp_frame = []
        for pos in frame["Frame"+" "+str(i)]:
            temp_frame.append(pos)
        frames.append(temp_frame)
        i += 1
    print(num_of_frames, " frames imported")
    for frame in frames:
        print(frame)
    return num_of_frames, frames


def imported_points_transform(motorxs, m_height, usage):
    """
    positions read from json converted to pixel values
    """
    num_of_frames, frames_in_steps = import_json_from_url()
    print("Frame in steps", frames_in_steps)
    frames_in_meters = []
    for frame in frames_in_steps:
        temp_frame = []
        for pos in frame:
            temp_frame.append(step_to_meters(pos))
        frames_in_meters.append(temp_frame)
    print("frame in meters", frames_in_meters)
    print("usage: ", usage)
    frames_in_coords = []
    for frame in frames_in_meters:
        temp_frame = []
        j = 0
        while j < len(usage):
            print(j)
            if usage[j] == 1:
                temp_frame.append((motorxs[j], m_height - frame[j]))
            else:
                temp_frame.append(get_intersections(motorxs[j], m_height, frame[j], motorxs[j+1], m_height, frame[j+1]))
                j += 1
            j += 1
        print(" temp: ", temp_frame)
        frames_in_coords.append(temp_frame)
    for coord in frames_in_coords:
        print(coord)
    return frames_in_coords
    """ if usage == "1111":
        for frame in frames_in_meters:
            temp_frame = []
            j = 0
            for dist in frame:
                temp_frame.append((motorxs[j], m_height - dist))
                j += 1
            frames_in_coords.append(temp_frame)
    elif usage == "1100":
        for i in range(2):
            points.append((motorxs[i], m_height - positions[i]))
        points.append(get_intersections(motorxs[2], m_height, positions[2], motorxs[3], m_height, positions[3]))
    elif usage == "1001":
        points.append((motorxs[0], m_height - positions[0]))
        points.append(get_intersections(motorxs[1], m_height, positions[1], motorxs[2], m_height, positions[2]))
        points.append((motorxs[3], m_height - positions[3]))
    elif usage == "0011":
        points.append(get_intersections(motorxs[0], m_height, positions[0], motorxs[1], m_height, positions[1]))
        for i in range(2,4):
            points.append((motorxs[i], m_height - positions[i]))
    elif usage == "0000":
        points.append(get_intersections(motorxs[0], m_height, positions[0], motorxs[1], m_height, positions[1]))
        points.append(get_intersections(motorxs[2], m_height, positions[2], motorxs[3], m_height, positions[3]))
    return points """

# def point_to_motor_meters(point, motor_pos, max_len, m_height, is_duo=False):
#     if is_duo:
#         dists_in_pixel = [((point[0] - motor_pos[0][0])**2 + (point[1] - motor_pos[0][1])**2) ** 0.5, ((point[0] - motor_pos[1][0])**2 + (point[1] - motor_pos[1][1])**2) ** 0.5]
#     else:
#         dist_in_pixel = ((point[0] - motor_pos[0])**2 + (point[1] - motor_pos[1])**2) ** 0.5
#         return(dist_in_pixel/global_vars.)

def meters_to_pixels(frames_in_coords, m_height, m_width):
    frames_in_pixels = []
    for frame in frames_in_coords:
        temp_frame = []
        for point in frame:
            temp_frame.append(( int((point[0] / m_width) * (global_vars.WIDTH - global_vars.DELTA_W)), int((global_vars.HEIGHT - (point[1] / m_height)*global_vars.HEIGHT))))
        frames_in_pixels.append(temp_frame)
    return frames_in_pixels

def point_to_current_motor_in_cm(point, motor1_posx=None, motor2_posx=None, max_len=600, m_height=600, point2=None, solo=False):
    point_in_cm = ((point[0]*max_len)/((global_vars.WIDTH - global_vars.DELTA_W)), ((global_vars.HEIGHT - point[1]) * m_height) / (global_vars.HEIGHT))
    if point2 is not None:
        if solo:
            point2_in_cm = ((point2[0]*max_len)/((global_vars.WIDTH - global_vars.DELTA_W)), ((global_vars.HEIGHT - point2[1]) * m_height) / (global_vars.HEIGHT))
            return ((point2_in_cm[0] - motor1_posx)**2 + (point2_in_cm[1] - point_in_cm[1])**2)**0.5
        else:
            point2_in_cm = ((point2[0]*max_len)/((global_vars.WIDTH - global_vars.DELTA_W)), ((global_vars.HEIGHT - point2[1]) * m_height) / (global_vars.HEIGHT))
            return ((point2_in_cm[0] - point_in_cm[0])**2 + (point2_in_cm[1] - point_in_cm[1])**2)**0.5
    # print(point_in_cm)
    if motor2_posx is None:
        dist_in_cm = abs(point_in_cm[1] - m_height)
        return dist_in_cm
    else:
        dist1_in_cm = ((point_in_cm[0] - motor1_posx)**2 + (point_in_cm[1] - m_height)**2)**0.5
        dist2_in_cm = ((point_in_cm[0] - motor2_posx)**2 + (point_in_cm[1] - m_height)**2)**0.5
        return [dist1_in_cm, dist2_in_cm]

def constrain_speed(speed):
    if abs(speed) < global_vars.MIN_SPEED:
        if speed == 0:
            return global_vars.MIN_SPEED
        return (speed / abs(speed)) * global_vars.MIN_SPEED
    else:
        return speed
