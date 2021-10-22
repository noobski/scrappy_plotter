# TODO
# - reduce resolution from 1mm downwards
# - be able to use interleave, single and double (bug in double)
# - see the initiation of MotorKit() in https://github.com/adafruit/Adafruit_CircuitPython_MotorKit/blob/main/adafruit_motorkit.py, 
#   to be able to maybe drive the motor faster or slower there

import time
import math
import RPi.GPIO as GPIO
from adafruit_motor import stepper
from adafruit_motorkit import MotorKit # sets mode to BCM
from ADCDevice import *
from pen import Pen
from ../ofer_libs/lib_vector import * 

class Plotter:
    def __init__(self):
        # GPIO globals
        self.led_pin = 17 
        self.pen_servo_pin = 21
        # start up a2d
        self.adc = ADCDevice() # todo: one of these should be removed? 
        self.adc = ADS7830()
        # motor definitions
        self.kit = MotorKit()
        self.m1, self.m2 = self.kit.stepper1, self.kit.stepper2
        self.pen = Pen(pen_servo_pin) 
        # motor spin style definitions:
        self.M = {"style": stepper.MICROSTEP, "steps": 1}
        self.I = {"style": stepper.INTERLEAVE, "steps": 8}
        self.S = {"style": stepper.SINGLE, "steps": 16}
        self.D = {"style": stepper.DOUBLE, "steps": 32}
        self.fwd, self.back = stepper.FORWARD, stepper.BACKWARD
        # 3,000 steps are 98mm (on m1) and 99mm (on m2) so using 
        self.one_step_in_mm = 98/3000 # 1 step =~ 1/30mm. single (16 steps) =~ 0.5mm
        # Starting position (top left of the paper) 
        self.loc = Vector(0,0) # initial location in mm
        self.page_w, self.page_h = 210, 297 # A4 page is 210mm * 297mm
        self.from_m1_page_topleft, self.from_m2_page_topleft = Vector(-300, 85), Vector(66, 85)
        self.string_lengths = self.loc_to_string_lengths(311.8, 107.6) # top left of page
        # Resolution, scale and speed
        self.resolution = 1 # (in mm) resolution of segments within the line. TODO: Change to less later
        self.drawing_speed = S # M, I, S, D
        self.plotter_global_scale=1
        # LED setup (turn it on to show motors running with current)
        GPIO.setup(led_pin, GPIO.OUT, initial=GPIO.HIGH)
    # breaks line into smaller segments and draws each of them
    def line_to(self, new_x, new_y, pen_down=True):
        # limit x,y values to page size
        new_x, new_y = limit(new_x, 0, page_w), limit(new_y, 0, page_h)
        new_loc = Vector(new_x, new_y).mult(plotter_global_scale)
        # pen down/up
        pen.down(pen_down)
        # create midpoints (break each long line to short lines of 'resolution' length)
        midpoints = get_midpoints(loc, new_loc, resolution)
        # draw all of the midpoint segments to form the whole line
        for new_loc in midpoints:
            if new_loc == midpoints[0]: continue
            req_change_in_strings = self.loc_to_string_lengths(new_loc).sub(self.string_lengths)
            req_motor_steps = self.get_motor_steps(req_change_in_strings)
            actual_motor_steps = self.spin_motors_parallel(req_motor_steps)
            actual_change_in_strings = Vector(\
                actual_motor_steps.x*one_step_in_mm*(-1), actual_motor_steps.y*one_step_in_mm)
            self.string_lengths.add(actual_change_in_strings)
            loc.copy(new_loc) # NO! -- the new location should figure out where it is based on the actual change in the strings
    def draw_test_helicopter(self):
        helicopter = [[170,104, 170,88 ,162,80 ,146,80 ,138,88 ,138,104 ,154,96 ,154,104 ,146,112] ,[98,72, 170,72 ,170,56 ,98,64], [66,96, 74,88 ,90,88 ,90,72],[10,176, 10,168 ,26,176 ,50,176 ,58,160 ,42,160 ,26,144 ,26,120 ,42,104],[138, 104,122, 112 ,114,104 ,114,88 ,98,88 ,98,56 ,90,56 ,90,64 ,18,56],[34,152, 66,128 ,66,112 ,42,104 ,50,96 ,106,96 ,114,104],[74,112, 74,128 ,90,128 ,90,112 ,74,112],[18,56, 18,72 ,90,72 ,90,64],[10,176, 26,184 ,130,184 ,130,176 ,106,176 ,98,160],[170,104, 162,112 ,146,112 ,106,144 ,98,160 ,58,160],[66,160, 58,176 ,98,176 ,90,160],[170,200, 200,300]]
        self.draw_pic(helicopter)
    def draw_pic(self, coords):
        for line in coords:
            for c in range(0, len(line), 2):
                line_to(line[c], line[c+1], False if c==0 else True)
    # returns string vector (string_length_m1, string_length_m2) at location v 
    def loc_to_string_lengths(self, loc):
        m1_string_length = loc.dup().add(from_m1_page_topleft).mag()
        m2_string_length = loc.dup().add(from_m2_page_topleft).mag()
        return Vector(m1_string_length, m2_string_length)
    # returns steps each motor needs to make to get to new string vector
    def get_motor_steps(self, change_in_strings):
        m1_steps = math.floor(change_in_strings.x/one_step_in_mm) * (-1) # fwd is counter-clockwise
        m2_steps = math.floor(change_in_strings.y/one_step_in_mm) 
        return Vector(m1_steps, m2_steps)
    # create a linear line of the steps needed to be spun, and spin both motors towards that slope
    def spin_motors_parallel(self, steps):
        m1_steps, m2_steps = steps.x, steps.y
        # direction of each motor
        m1_dir = back if m1_steps < 0 else fwd
        m2_dir = back if m2_steps < 0 else fwd
        # steps in single spin of style
        steps_per_spin, style = self.drawing_speed["steps"], self.drawing_speed["style"]
        m1_spins = m1_spins_init = abs(m1_steps//self.steps_per_spin)
        m2_spins = m2_spins_init = abs(m2_steps//self.steps_per_spin)
        # create the slant (spin both motors in parallel) with midpoints
        midpoints = get_midpoints(Vector(0,0), Vector(m1_spins, m2_spins), 1) 
        for i in range (len(midpoints)-1, -1, -1): #.. until -1 because range excludes upper (lower in this case) bound
            if m1_spins > midpoints[i].x: 
                motor_spin(self.m1, m1_dir, 1, style)
                m1_spins -= 1
            if m2_spins > midpoints[i].y: 
                motor_spin(self.m2, m2_dir, 1, style)
                m2_spins -= 1 
        m1_actual_spins = m1_spins_init*steps_per_spin*sign(steps.x)
        m2_actual_spins = m2_spins_init*steps_per_spin*sign(steps.y)
        return Vector(m1_actual_spins, m2_actual_spins)
    def motor_spin(self, motor, motor_direction, steps, step_style):
        for i in range(steps):
            motor.onestep(direction = motor_direction, style = step_style)
            time.sleep(0.015) # should sleep different amounts for different type style of steps? (e.g. more for double than for single)
                              # also can work with timestamp here, so that the time spent out of the function is counted as rest for the motor
    def plotter_finishup(self):
        # release motors and lift the pen
        self.m1.release() 
        self.m2.release() 
        self.pen.down(False)
        # turn led off, to show current is shut off
        GPIO.output(led_pin, GPIO.LOW)
        # clean up
        GPIO.cleanup()
        self.adc.close()
        self.pen.finishup()

if __name__ == "__main__":
    try:
        plotter = new Plotter()
        plotter.draw_test_helicopter()
        plotter.finishup()
    except KeyboardInterrupt: # Press ctrl-c to end the program.
        plotter.finishup()
// 143