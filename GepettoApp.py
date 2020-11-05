from PyQt5.QtCore import QSize, QRect, Qt
from PyQt5.QtGui import QPixmap, QPen, QBrush, QPainter, QFont
#from PyQt5.QtWidgets import * #QSize, QWidget, QLineEdit, QComboBox, QLabel
from PyQt5.QtWidgets import QWidget, QLineEdit, QComboBox, QLabel, QApplication
from buttons import *
import numpy as np
from CustomModules import global_vars, helpers, file_writing
import math

#in programs 0,0 point is the top left, we want bottom left as origin
#also points are in pixel value, we want in terms of meter
def transform_frames(frames, max_len, m_height):
    temp_frames = []
    for frame in frames:
        temp_frame = []
        for point in frame:  #(pixel/max_pixel)*max_in_cm / 100 for meters
            temp_frame.append(((point[0]*max_len)/((global_vars.WIDTH - global_vars.DELTA_W)*100), ((global_vars.HEIGHT - point[1]) * m_height) / (global_vars.HEIGHT*100) ) )
        temp_frames.append(temp_frame)
    return temp_frames

#we have only xs, ys = 0 in pixel format
#change it to coord points in meters
def transform_motorxs(motorxs, max_len, m_height):
    motor_coords = []
    for x in motorxs:
        motor_coords.append(((x*max_len)/((global_vars.WIDTH - global_vars.DELTA_W)*100), m_height/100))
    return motor_coords



class GepettoApp(QWidget):
    """
    app class
    """
    def __init__(self):
        super().__init__()
        self.ui = Ui_buttons()
        self.ui.setupUi(self)
        self.setGeometry(global_vars.X_LOC, global_vars.Y_LOC, global_vars.WIDTH, global_vars.HEIGHT)
        self.size = QSize(global_vars.WIDTH, global_vars.HEIGHT)
        self.setFixedSize(self.size)
        self.setMouseTracking(True)
        self.output_points = []
        self.import_press_times = 0

        self.mouse_x = 200 #mouse coord in pixel
        self.mouse_y = 200
        #LineEdit Objects, need to use findChild because QtDesigner used
        self.frame_dur_line = self.findChild(QLineEdit, "frame_dur_line")
        self.mot2 = self.findChild(QLineEdit, "mot2_line")
        self.mot3 = self.findChild(QLineEdit, "mot3_line")
        self.mot4 = self.findChild(QLineEdit, "mot4_line")
        self.mot_h = self.findChild(QLineEdit, "height_line")

        #Solo Duo Combobox
        self.solo_duo_box = self.findChild(QComboBox, "solo_duo_box")
        #Label Objects
        self.stat_label = self.findChild(QLabel, "status_label")
        self.warn_label = self.findChild(QLabel, "warn_label")
        self.stat_text = "0 Frames Added"
        self.warn_text = "Inputs Needed"
        self.status_warning_update()
        #flags
        self.rth = False
        self.rth_frame_time_recieved = False
        self.h_updated = False #global_vars.HEIGHT input updated
        self.delta_t_updated = False
        self.motorxs_updated = [False, False, False] #motor distance inputs updated
        self.background_inputs_recieved = False # frame backround is ready for drawing points

        self.delta_ts = []
        self.delta_t_current = 0
        #drawing parameters
        self.counter = 0 #to count solo or duo point
        self.usage = [1, 1, 1, 1] #solo duo info, 1=solo, 0=duo
        self.frame_max_point = 4 #usage determines max point for a frame
        self.motorxs = [0, 0, 0, 0] #motor x positions in cm
        self.motorxs_in_pixels = [0, 0, 0, 0] #motor x positions in pixels
        self.motor_height = 0
        self.radius = 8
        self.imported_frames = []
        self.cur_point = (0, 0)
        self.cur_frame = []
        self.point_colors = []
        self.prev_frames = []
        self.image = QPixmap("draw_board.png")
        self.image_rect = QRect(0, 0, global_vars.WIDTH-global_vars.DELTA_W, global_vars.HEIGHT)
        print("Press Twice To Import Frames From Web")
    #where we draw everthing
    def paintEvent(self, event):
        painter = QPainter(self)
        self.draw_background(painter)
        self.draw_motors_and_lines(painter)
        self.draw_imported_frames(painter)
        self.draw_prev_frames(painter)
        self.draw_frame_points(painter)
        self.drawMotorDistText(painter)

    # when mouse is pressed, add a point to frame if it is not full
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.background_inputs_recieved:
                if self.frame_max_point > len(self.cur_frame):
                    if self.usage[self.counter]:
                        self.cur_point = (self.motorxs_in_pixels[self.counter], event.y())
                        self.cur_frame.append(self.cur_point)
                        self.counter +=1
                        self.warn_text = f"{len(self.cur_frame)} Points"
                    else:
                        self.cur_point = (event.x(), event.y())
                        if self.point_validation():
                            self.cur_frame.append(self.cur_point)
                            self.counter +=2
                            self.warn_text = f"{len(self.cur_frame)} Points"
                    self.stat_text = f"{len(self.prev_frames)} Frames Added"
                    self.status_warning_update()
                    self.update()
                else:
                    self.warn_text = f"Max {self.frame_max_point} Points"
                    self.status_warning_update()
            else:
                self.warn_text = "Frame is not Ready"
                self.status_warning_update()
        else:
            self.stat_text = f"{len(self.prev_frames)} Frames Added"
            self.warn_text = "Press Left Button"
            self.status_warning_update()

    def mouseMoveEvent(self, event):
        self.mouse_x = event.x()
        self.mouse_y = event.y()
        self.update()

    def drawMotorDistText(self, painter):
        if self.background_inputs_recieved and self.counter < len(self.usage):
            #if it is first frame, show dist from motors
            if not self.prev_frames:
                #if it is solo only 1 motor distance
                if self.usage[self.counter]:
                    dist = helpers.point_to_current_motor_in_cm((self.mouse_x, self.mouse_y), self.motorxs[self.counter], max_len=self.biggest, m_height=self.motor_height)
                    painter.drawText(self.mouse_x, self.mouse_y, str(dist))
                else:
                    dists = helpers.point_to_current_motor_in_cm((self.mouse_x, self.mouse_y), self.motorxs[self.counter], motor2_posx=self.motorxs[self.counter+1], max_len=self.biggest, m_height=self.motor_height)
                    painter.drawText(self.mouse_x, self.mouse_y, str(dists))
            #else show dist from last point from prev frame
            else:
                if self.usage[self.counter]:
                    dist = helpers.point_to_current_motor_in_cm((self.mouse_x, self.mouse_y), motor1_posx=self.motorxs[self.counter], max_len=self.biggest, m_height=self.motor_height, point2=self.prev_frames[-1][len(self.cur_frame)], solo=True)
                    painter.drawText(self.mouse_x, self.mouse_y, str(dist))                    
                else:
                    dist = helpers.point_to_current_motor_in_cm((self.mouse_x, self.mouse_y), max_len=self.biggest, m_height=self.motor_height, point2=self.prev_frames[-1][len(self.cur_frame)])
                    painter.drawText(self.mouse_x, self.mouse_y, str(dist))
    #draw background image to the screen
    def draw_background(self, painter):
        painter.drawPixmap(self.image_rect, self.image)

    #draw motors and vertical lines from them according to inputs
    def draw_motors_and_lines(self, painter):
        if self.background_inputs_recieved:
            for i in self.motorxs_in_pixels:
                painter.setPen(QPen(Qt.black))
                painter.drawLine(i,0, i, global_vars.HEIGHT)
                painter.setPen(QPen(Qt.red))
                painter.setBrush(QBrush(Qt.red, 3))
                painter.drawRect(i, 0, global_vars.RECT_DIM, global_vars.RECT_DIM)

    def draw_imported_frames(self, painter):
        for frame in self.imported_frames:
            for point in frame:
                painter.setPen(QPen(Qt.red))
                painter.setBrush(QBrush(Qt.black, 3))
                painter.drawEllipse(point[0] - self.radius/2, point[1] - self.radius/2 , self.radius*2, self.radius*2)
                #painter.setFont(QFont("Times", 12))
                painter.drawText(point[0] - self.radius/2 -20, point[1] - self.radius/2 +30, "("+str(point[0])+","+ str(point[1])+")")

    #frame points are loop through, also a line with it is drawn to see its level, easy to coordinate Y values
    def draw_frame_points(self, painter):
        #if backround is ready, draw points
        if self.background_inputs_recieved:
            num_p = 0
            for point in self.cur_frame:
                painter.setPen(QPen(Qt.blue))
                painter.setBrush(QBrush(Qt.blue, 3))
                painter.drawEllipse(point[0] - self.radius/2, point[1] - self.radius/2, self.radius, self.radius)
                pen = QPen(Qt.blue)
                pen.setStyle(Qt.DashDotLine)
                painter.setPen(pen)
                painter.drawLine(0,point[1], global_vars.WIDTH - global_vars.DELTA_W, point[1])
                num_p +=1

    #Previous frame points should be different color to see its path when drawing
    def draw_prev_frames(self, painter):
        if self.background_inputs_recieved:
            for frame in self.prev_frames:
                num_p = 0 # count colors
                for point in frame:
                    painter.setPen(QPen(self.point_colors[num_p]))
                    painter.setBrush(QBrush(self.point_colors[num_p], 3))
                    painter.drawEllipse(point[0] - self.radius/2, point[1] - self.radius/2, self.radius, self.radius)
                    num_p +=1

    #when draw button is pressed, add inputs to drawable inputs
    def draw_frame_background(self):
        if(self.motorxs_updated[0] and self.motorxs_updated[1] and self.motorxs_updated[2] and self.h_updated):
            self.solo_duo_edit()
            self.background_inputs_recieved = True

            #here motorxs are in cm, scale and turn it into pixels 600-600 wide
            #biggest distances corresponds to 600 pixels, and biggest is assumed to be the last motor
            self.biggest = self.motorxs[-1]
            for i in range(len(self.motorxs)):
                self.motorxs_in_pixels[i] = (self.motorxs[i] / self.biggest ) * 600

            with open("config.txt", "w") as file:
                for x in self.motorxs:
                    file.write(str(x)+"\n")
                file.write(str(self.motor_height) + "\n")
                file.write("".join(str(i) for i in self.usage))

            #new background drawing should also clear all frame info
            self.cur_frame = []
            self.prev_frames = []
            self.counter = 0
            self.stat_text = "0 Frames Added"
            self.warn_text = "0 Points"
            self.status_warning_update()
            self.update()

#------------------------BUTTONS -----------------------------------------------
    #TODO: Add same points button for waiting on the same points
    # when a frame is done go to next one, store it and reset frame points
    def next_frame(self):
        if not self.background_inputs_recieved:
            self.warn_text = f"Inputs Needed!"
        #see if all of the points placed on
        elif len(self.cur_frame) < self.frame_max_point:
            self.warn_text = f"Add {self.frame_max_point -len(self.cur_frame)} more Points"
            pass
        else:
            if not self.delta_t_updated:
                self.warn_text = "Frame Time Needed!"
            else:
                self.prev_frames.append(self.cur_frame)
                self.delta_ts.append(self.delta_t_current)
                self.cur_frame = []
                self.counter = 0
                self.update()
                self.stat_text = f"{len(self.prev_frames)} Frames Added"
                self.warn_text = "0 Points"

        self.status_warning_update()

    #clear only the current frame
    def clear_frame(self):
        if not self.background_inputs_recieved:
            self.stat_text = f"{len(self.prev_frames)} Frames Added"
            self.warn_text = "Inputs Needed!"
        else:
            self.cur_frame = []
            self.update()
            self.counter = 0
            self.stat_text = f"{len(self.prev_frames)} Frames Added"
            self.warn_text = "0 Points"
        self.status_warning_update()

    #clear all frames, resets everything
    def clear_all(self):
        if not self.background_inputs_recieved:
            self.stat_text = "0 Frames Added"
            self.warn_text = "Inputs Needed!"
        else:
            self.cur_frame = []
            self.prev_frames = []
            self.counter = 0
            self.update()
            self.stat_text = "0 Frames Added"
            self.warn_text = "0 Points"
        self.status_warning_update()

    def rth_func(self):
        self.stat_text = "Rth Enabled"
        self.warn_text = "Don't Add More"
        self.rth = True
        self.status_warning_update()

    def done_func(self):

        if not self.prev_frames:
            self.close()
        else:
            if self.rth:
                if (self.rth_frame_time_recieved):
                    self.delta_ts.append(self.delta_t_current)
                    self.prev_frames.append(self.prev_frames[0])
                else:
                    self.warn_text = "Need RTH Frame Time"
                    #self.rth_frame_time_enabled = True
                    self.status_warning_update()
                    return
            #transform_frames pixel valued points to meters
            in_m_frames = transform_frames(self.prev_frames, self.biggest, self.motor_height)
            motor_coords = transform_motorxs(self.motorxs_in_pixels, self.biggest, self.motor_height)
            file_writing.write_points_to_file(in_m_frames, self.usage, len(self.prev_frames), motor_coords, self.delta_ts)
            self.close()

    def import_last_values(self):
        self.import_press_times += 1
        if self.import_press_times == 1:
            #config.txt has the info already, format is known, take the values
            with open("config.txt", "r") as file:
                lines = file.readlines()
                xs = [float (line.strip()) for line in lines[:-1]]
                usage = [int(letter) for letter in lines[-1].strip()]
            #last element global_vars.HEIGHT, others xs
            self.motorxs = xs[:-1]
            self.motor_height = xs[-1]
            self.usage = usage

            #we updated inputs through import so set flags
            self.motorxs_updated = [True, True, True]
            self.h_updated = True
            self.not_from_but = True

            #show the imported values of screen
            self.mot2.setText(str(self.motorxs[1]))
            self.mot3.setText(str(self.motorxs[2]))
            self.mot4.setText(str(self.motorxs[3]))
            self.mot_h.setText(str(self.motor_height))
            #quick and dirty way to set current text, instead of huge if elses
            txt = ""
            i = 0
            while i < len(self.usage):
                if self.usage[i]:
                    txt += "Solo-"
                    i += 1
                else:
                    txt += "Duo-"
                    i += 2
            txt = txt[:-1]
            self.solo_duo_box.setCurrentText(txt)
        elif self.import_press_times == 2:
            motorxs_in_meter = [x/100 for x in self.motorxs]
            motor_height = self.motor_height / 100
            frames_in_coords = helpers.imported_points_transform(motorxs_in_meter, motor_height, self.usage)
            frames_in_pixels = helpers.meters_to_pixels(frames_in_coords, motor_height, motorxs_in_meter[-1])
            self.imported_frames = frames_in_pixels
            print(self.imported_frames)


#-------------------------------------- TEXT INPUTS --------------------------------------------
    def frame_dur_line_edit(self):
        frame_time = self.frame_dur_line.text()
        try:
            self.delta_t_current = (float(frame_time))
        except:
            self.warn_text = "Number inputs!"
            self.status_warning_update()
            return
        self.delta_t_updated = True
        #if at the end, rth is pushed, we also need that last duration to return home
        if self.rth:
            self.rth_frame_time_recieved = True

    def motor2_text_edit(self):
        try:
            mot2_dist = float(self.mot2.text())
        except:
            self.warn_text = "Number inputs!"
            self.status_warning_update()
            return
        self.motorxs[1] = mot2_dist
        self.motorxs_updated[0] = True

    def motor3_text_edit(self):
        try:
            mot3_dist = float(self.mot3.text())
        except:
            self.warn_text = "Number inputs!"
            self.status_warning_update()
            return
        self.motorxs[2] = mot3_dist
        self.motorxs_updated[1] = True

    def motor4_text_edit(self):
        try:
            mot4_dist = float(self.mot4.text())
        except:
            self.warn_text = "Number inputs!"
            self.status_warning_update()
            return
        self.motorxs[3] = mot4_dist
        self.motorxs_updated[2] = True

    def height_text_edit(self):
        try:
            self.motor_height = float(self.mot_h.text())
        except:
            self.warn_text = "Number inputs!"
            self.status_warning_update()
            return
        self.h_updated = True

#-------------------------------SOLO DUO------------------------------------
    def solo_duo_edit(self):
        if self.solo_duo_box.currentText() == "Solo-Solo-Solo-Solo":
            self.frame_max_point = 4
            self.usage = [1, 1, 1, 1]
            self.point_colors = [Qt.gray, Qt.yellow, Qt.magenta, Qt.green]
        elif self.solo_duo_box.currentText() == "Solo-Solo-Duo":
            self.frame_max_point = 3
            self.usage = [1, 1, 0, 0]
            self.point_colors = [Qt.gray, Qt.yellow, Qt.magenta]
        elif self.solo_duo_box.currentText() == "Solo-Duo-Solo":
            self.frame_max_point = 3
            self.usage = [1, 0, 0, 1]
            self.point_colors = [Qt.gray, Qt.yellow, Qt.magenta]
        elif self.solo_duo_box.currentText() == "Duo-Solo-Solo":
            self.frame_max_point = 3
            self.usage = [0, 0, 1, 1]
            self.point_colors = [Qt.gray, Qt.yellow, Qt.magenta]
        elif self.solo_duo_box.currentText() == "Duo-Duo":
            self.frame_max_point = 2
            self.usage = [0,0,0,0]
            self.point_colors = [Qt.gray, Qt.yellow]

    def status_warning_update(self):
        self.stat_label.setText(self.stat_text)
        self.warn_label.setText(self.warn_text)

    def point_validation(self):
        cursorx = (self.motorxs[3] / self.motorxs_in_pixels[3]) * self.cur_point[0]
        ydist = (self.motor_height / global_vars.HEIGHT) * self.cur_point[1]
        if self.solo_duo_box.currentText() == "Solo-Solo-Solo_solo":
            return True
        elif self.solo_duo_box.currentText() == "Solo-Solo-Duo":
            if len(self.cur_frame) == 2:
                xdist1 = cursorx - self.motorxs[2]
                xdist2 = self.motorxs[3] - cursorx
                if(xdist1 == 0 or xdist2 == 0):
                    return True
                else:
                    hypotenus1 = math.sqrt((xdist1**2) + (ydist**2))
                    hypotenus2 = math.sqrt((xdist2**2) + (ydist**2))
                    sina = ydist / hypotenus1
                    cosa = xdist1 / hypotenus1
                    sinb = ydist / hypotenus2
                    cosb = xdist2 / hypotenus2
                    T1 = global_vars.WEIGHT / (sina + ((cosa*sinb)/cosb))
                    T2 = global_vars.WEIGHT / (sinb + ((cosb*sina)/cosa))
                    if(xdist1 < 0):
                        self.warn_text = "Not Between The Motors"
                        return False
                    elif(T1 > global_vars.MAX_WEIGHT or T2 > global_vars.MAX_WEIGHT):
                        self.warn_text = "Torque Is Not Enough"
                        return False
                    else:
                        return True
            else:
                return True
        elif self.solo_duo_box.currentText() == "Solo-Duo-Solo":
            if len(self.cur_frame) == 1:
                xdist1 = cursorx - self.motorxs[1]
                xdist2 = self.motorxs[2] - cursorx
                if(xdist1 == 0 or xdist2 == 0):
                    return True
                else:
                    hypotenus1 = math.sqrt((xdist1**2) + (ydist**2))
                    hypotenus2 = math.sqrt((xdist2**2) + (ydist**2))
                    sina = ydist / hypotenus1
                    cosa = xdist1 / hypotenus1
                    sinb = ydist / hypotenus2
                    cosb = xdist2 / hypotenus2
                    T1 = global_vars.WEIGHT / (sina + ((cosa*sinb)/cosb))
                    T2 = global_vars.WEIGHT / (sinb + ((cosb*sina)/cosa))
                    if(xdist1 < 0 or xdist2 < 0):
                        self.warn_text = "Not Between The Motors"
                        return False
                    elif(T1 > global_vars.MAX_WEIGHT or T2 > global_vars.MAX_WEIGHT):
                        self.warn_text = "Torque Is Not Enough"
                        return False
                    else:
                        return True
            else:
                return True

        elif self.solo_duo_box.currentText() == "Duo-Solo-Solo":
            if len(self.cur_frame) == 0:
                xdist1 = cursorx - self.motorxs[0]
                xdist2 = self.motorxs[1] - cursorx
                if(xdist1 == 0 or xdist2 == 0):
                    return True
                else:
                    hypotenus1 = math.sqrt((xdist1**2) + (ydist**2))
                    hypotenus2 = math.sqrt((xdist2**2) + (ydist**2))
                    sina = ydist / hypotenus1
                    cosa = xdist1 / hypotenus1
                    sinb = ydist / hypotenus2
                    cosb = xdist2 / hypotenus2
                    T1 = global_vars.WEIGHT / (sina + ((cosa*sinb)/cosb))
                    T2 = global_vars.WEIGHT / (sinb + ((cosb*sina)/cosa))
                    if(xdist2 < 0):
                        self.warn_text = "Not Between The Motors"
                        return False
                    elif(T1 > global_vars.MAX_WEIGHT or T2 > global_vars.MAX_WEIGHT):
                        self.warn_text = "Torque Is Not Enough"
                        return False
                    else:
                        return True
            else:
                return True

        elif self.solo_duo_box.currentText() == "Duo-Duo":
            if len(self.cur_frame) == 0:
                xdist1 = cursorx - self.motorxs[0]
                xdist2 = self.motorxs[1] - cursorx
                if(xdist1 == 0 or xdist2 == 0):
                    return True
                else:
                    hypotenus1 = math.sqrt((xdist1**2) + (ydist**2))
                    hypotenus2 = math.sqrt((xdist2**2) + (ydist**2))
                    sina = ydist / hypotenus1
                    cosa = xdist1 / hypotenus1
                    sinb = ydist / hypotenus2
                    cosb = xdist2 / hypotenus2
                    T1 = global_vars.WEIGHT / (sina + ((cosa*sinb)/cosb))
                    T2 = global_vars.WEIGHT / (sinb + ((cosb*sina)/cosa))
                    if(xdist2 < 0):
                        self.warn_text = "Not Between The Motors"
                        return False
                    elif(T1 > global_vars.MAX_WEIGHT or T2 > global_vars.MAX_WEIGHT):
                        self.warn_text = "Torque Is Not Enough"
                        return False
                    else:
                        return True
            elif len(self.cur_frame) == 1:
                xdist1 = cursorx - self.motorxs[2]
                xdist2 = self.motorxs[3] - cursorx
                if(xdist1 == 0 or xdist2 == 0):
                    return True
                else:
                    hypotenus1 = math.sqrt((xdist1**2) + (ydist**2))
                    hypotenus2 = math.sqrt((xdist2**2) + (ydist**2))
                    sina = ydist / hypotenus1
                    cosa = xdist1 / hypotenus1
                    sinb = ydist / hypotenus2
                    cosb = xdist2 / hypotenus2
                    T1 = global_vars.WEIGHT / (sina + ((cosa*sinb)/cosb))
                    T2 = global_vars.WEIGHT / (sinb + ((cosb*sina)/cosa))
                    if(xdist1 < 0):
                        self.warn_text = "Not Between The Motors"
                        return False
                    elif(T1 > global_vars.MAX_WEIGHT or T2 > global_vars.MAX_WEIGHT):
                        self.warn_text = "Torque Is Not Enough"
                        return False
                    else:
                        return True


def main():
    """
    main function
    """
    import sys
    app = QApplication(sys.argv)
    widget = GepettoApp()
    widget.show()
    return(app.exec())

if __name__ == "__main__":
    main()
