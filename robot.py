try:
    import wpilib
except ImportError:
    from pyfrc import wpilib

import config


class MyRobot(wpilib.SimpleRobot):

    def __init__(self):
        super().__init__()
        
        self.dog = self.GetWatchdog()
        self.dog.SetExpiration(0.25)
        self.components = config.components()

    def RobotInit(self):
        self.smartdashboardNT = wpilib.NetworkTable.GetTable("SmartDashboard")
        for type, component in self.components.items():
            component.robot_init()

    def Disabled(self):
        self.dog.SetEnabled(True)

        for type, component in self.components.items():
            component.disabled_init()

        while wpilib.IsDisabled():
            self.dog.Feed()

            for type, component in self.components.items():
                component.disabled_tick(wpilib.Timer.GetFPGATimestamp())

            wpilib.Wait(0.01)

        self.dog.SetEnabled(False)

    def Autonomous(self):
        # TODO: add downshift to the initialization
        # TODO: does the ball fall out when there's only one?
        # TODO: add a pause state between every state
        self.dog.SetEnabled(True)
        for type, component in self.components.items():
            component.auto_init()

        START = 'start'
        SHOOTING = 'shooting'
        DRIVE_FORWARD = 'drive_forward'
        STOP = 'stop'
        EXTENDED_PICKUP_PAUSE = 'extended_pickup_pause'

        current_state = START
        start_time = wpilib.Timer.GetFPGATimestamp()

        

        while wpilib.IsAutonomous() and wpilib.IsEnabled():
            self.dog.Feed()

            wpilib.SmartDashboard.PutString('auto robot state', current_state)

            current_time = wpilib.Timer.GetFPGATimestamp()
            elapsed_seconds = current_time - start_time

            if current_state == START:
                if self.goal_is_hot() or elapsed_seconds > 5:
                    wpilib.Wait(3)
                    current_state = DRIVE_FORWARD
                    

            elif current_state == DRIVE_FORWARD:
                self.components['drive'].auto_drive_forward_tick(current_time)
                if self.components['drive'].is_auto_drive_done():
                    self.components['pickup'].extend()
                    wpilib.Wait(3)
                    current_state = SHOOTING
                    

            elif current_state == SHOOTING:
                self.components['shooter'].auto_shoot_tick(current_time)
                if self.components['shooter'].is_auto_shoot_done():
                    current_state = STOP

            # for type, component in self.components.items():
            #     component.auto_tick(wpilib.Timer.GetFPGATimestamp())

            wpilib.Wait(0.01)

        self.dog.SetEnabled(False)

    def OperatorControl(self):
        self.dog.SetEnabled(True)

        for type, component in self.components.items():
            component.op_init()

        while self.IsOperatorControl() and self.IsEnabled():
            self.dog.Feed()
            for type, component in self.components.items():
                component.op_tick(wpilib.Timer.GetFPGATimestamp())

            ## Debug & Tuning
            # ??
            wpilib.Wait(0.01)

        self.dog.SetEnabled(False)

    def Test(self):
        while self.IsTest() and self.IsEnabled():
            wpilib.LiveWindow.Run()
            wpilib.Wait(0.01)

    def goal_is_hot(self):
        return True
        # try:
        #     hot_goal = self.smartdashboardNT.GetBoolean("HOT_GOAL")
        #     return hot_goal
        # except:
        #     return False

def run():
    robot = MyRobot()
    robot.StartCompetition()
    return robot

if __name__ == '__main__':
    wpilib.run()
