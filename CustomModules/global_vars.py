"""
some of the global variables used by app
"""

PI = 3.14159265359
MAKARA_RADIUS = 0.009*(100.0041/100) # metre -the number in paranthesis is for helix correction
ONE_TURN_STEPS = 400

X_LOC = 500
Y_LOC = 200
WIDTH = 800
DELTA_W = 200
HEIGHT = 600
RECT_DIM = 8
POINT_R = 0.06 #determining if a frame is a stopped frame or not. In meters
MAX_LEN_IN_M = 0.5

NUM_OF_MOTORS = [] 
HOME_POS_ROPE_LEN = [0, 0, 0, 0]
HOME_TO_P0_TIME = 0

MIN_SPEED = 60
MAX_SPEED = 4000
MAX_WEIGHT = 1
#TODO: change this when ready
WEIGHT = 0.5


MAX_ROPE_LENGTH_CHANGE = 0.05 #meters
MIN_DELTA_T = 0.005 #seconds
MAX_DELTA_T = 10 #seconds
MAX_ACCLERATION = 0.27 #m/s^2
MIN_ACCLERATION = -0.27 #m/s^2
DELTA_LENGTH = 0.02 #m
MAX_SPEED_IN_METERS = 0.45 #m/s
MIN_SPEED_IN_METERS = -0.45 #m/s

OFFLINE_ONLINE = 1 # 1: ONLINE 0: OFFLINE

"""
class webApp:
  def __init__(self):
    self._board_id = ""                    
    self._rev_id = ""                       
    self._input_path = ""                
    self._output_path = ""
    self.Ids=[] 
  def define_paths(self, board_ID,rev_Id, input_path, output_path):
    self._board_id = board_ID      
    self._rev_id = rev_Id
    self._input_path = input_path
    self._output_path = output_path
  def back(self):
    self.Ids.append(self._board_id)
    self.Ids.append(self._rev_id)
    self.Ids.append(self._input_path)
    self.Ids.append(self._output_path)
    return self.Ids
"""
