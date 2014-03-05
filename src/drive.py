import common

try:
    import wpilib
except ImportError:
    from pyfrc import wpilib

__all__ = ['Drive']


class Drive(common.ComponentBase):

    START = 'start'
    DRIVE_FORWARD = 'drive_forward'
    STOP = 'stop'

    def __init__(self, config):
        self.robot_drive = config.robot_drive

        self.left_motors = config.left_motors
        self.right_motors = config.right_motors

        self.joy = config.drive_joy

        self.squared_drive_button = config.squared_drive_button

        self.shift_button = config.shift_button
        self.left_shifter = config.left_shifter
        self.right_shifter = config.right_shifter
        self.low = config.forward
        self.high = config.reverse
        self.align_button = config.align_button

        self.front_left_photo_switch = config.front_left_photo_switch
        self.front_right_photo_switch = config.front_right_photo_switch
        self.back_left_photo_switch = config.back_left_photo_switch
        self.back_right_photo_switch = config.back_right_photo_switch

        self.auto_state = self.START
        self.auto_drive_start_time = 0


    def op_init(self):
        self.robot_drive.StopMotor()

    def op_tick(self, bs):
        speed = self.joy.GetY()
        rot = self.joy.GetX()

        squared = False
        if self.squared_drive_button.get():
            squared = True
        self.robot_drive.ArcadeDrive(speed, rot, squared)

        if self.shift_button.get():
            self.shift(self.low) 
        else:
            self.shift(self.high)

        if self.align_button.get():
            self.align()

    def auto_init(self, auto_config):
        self.auto_state = self.START
        self.auto_config = auto_config

    def auto_drive_forward_tick(self, time):

        speed = 0

        if self.auto_state == self.START:
            self.auto_drive_start_time = time
            self.auto_state = self.DRIVE_FORWARD

        elif self.auto_state == self.DRIVE_FORWARD:
            speed = 1
            elapsed_time = time - self.auto_drive_start_time
            if elapsed_time > self.auto_config.drive_forward_time:
                self.auto_state = self.STOP

        elif self.auto_state == self.STOP:
            speed = 0
        
        self.left_motors.Set(speed)
        self.right_motors.Set(-speed)

        wpilib.SmartDashboard.PutString('auto drive state', self.auto_state)

    def is_auto_drive_done(self):
        return self.auto_state == self.STOP

    def shift(self, gear):
        self.left_shifter.Set(gear)
        self.right_shifter.Set(gear)

    def downshift(self):
        self.shift(self.low)

    def align(self):

        motor_speed = .25
        reverse_speed = -.1
        left = 0
        right = 0
        
        if self.back_left_photo_switch.Get():
            left = reverse_speed
        elif self.front_left_photo_switch.Get():
            left = 0
        else:
            left = motor_speed

        if self.back_right_photo_switch.Get():
            right = reverse_speed
        elif self.front_right_photo_switch.Get():
            right = 0
        else:
            right = motor_speed 

        # DANGER! Right and left are inverted here. This is because morgan flipped
        # forward and back
        self.robot_drive.SetLeftRightMotorOutputs(right, left)



            
            
       



            


            