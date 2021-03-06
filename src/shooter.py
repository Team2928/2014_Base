import common

try:
    import wpilib
except ImportError:
    from pyfrc import wpilib


__all__ = ['Shooter']


class Shooter(common.ComponentBase):

    SHOOTING = 'shooting'
    RESET = 'reset'
    RESETTING = 'resetting'
    AUTO_SHOOT_DONE = 'auto_shoot_done'
    CATCHING = 'catching'

    def __init__(self, config):
        self.motors = config.motors

        self.shoot_button = config.shoot_button
        self.manual_reset_button = config.manual_reset_button
        self.e_reset_button = config.e_reset_button

        self.low_shot_preset_button = config.low_shot_preset_button
        self.high_shot_preset_button = config.high_shot_preset_button
        self.catch_preset_button = config.catch_preset_button
        
        self.low_shot_hall_effect_counter = config.low_shot_hall_effect_counter
        self.high_shot_hall_effect_counter = config.high_shot_hall_effect_counter

        self.reset_hall_effect_counter = config.reset_hall_effect_counter
        self.catch_hall_effect_counter = config.catch_hall_effect_counter

        self.ds = wpilib.DriverStation.GetInstance()

        self.pickup = config.pickup
    
        self.op_state = self.RESETTING

        self.auto_state = self.RESET

        self.resetting_speed = -.2

        self.shooting_speed = .85

        self.shoot_start_time = 0

    def robot_init(self):
        wpilib.SmartDashboard.PutNumber("shooting_speed", self.shooting_speed)
        wpilib.SmartDashboard.PutNumber("resetting_speed", self.resetting_speed)

    def update_smartdashboard_vars(self):
        self.shooting_speed = wpilib.SmartDashboard.GetNumber("shooting_speed")
        self.resetting_speed = wpilib.SmartDashboard.GetNumber("resetting_speed")

    def op_init(self):
        self.low_shot_hall_effect_counter.Reset()
        self.high_shot_hall_effect_counter.Reset()
        self.reset_hall_effect_counter.Reset()

        self.op_state = self.RESET

    def op_tick(self, time):
        # TODO - Make sure catch is properly implemented
        #    Talk to Elaine and make sure the switches do what she wants

        if self.op_state == self.RESET:
            speed = 0
            # if self.shoot_button.get():
            if self.shoot_button.get() and self.pickup.is_extended():
                self.op_state = self.SHOOTING
                print("SHOOTING")
                self.shoot_start_time = time
                self.low_shot_hall_effect_counter.Reset()
                self.high_shot_hall_effect_counter.Reset()
                self.reset_hall_effect_counter.Reset()
                self.catch_hall_effect_counter.Reset()

        if self.op_state == self.SHOOTING:
            speed = self.shooting_speed
            if self.should_stop():
                speed = 0
                

                # Logging code
                # voltage = self.ds.Battery.GetVoltage()
                # shoot_seconds = time - self.shoot_start_time
                # preset = "low" if self.low_shot_preset_button.get() else "high"
                # print("SHOOTER_LOGGER,%s,%s,%s,%s" % (voltage, preset, shoot_seconds, self.shooting_speed))

                self.reset_hall_effect_counter.Reset()
                if self.catch_preset_button.get():
                    print("CATCHING")
                    self.op_state = self.CATCHING
                else:
                    print("RESETTING")
                    self.op_state = self.RESETTING

        if self.op_state == self.CATCHING:
            speed = 0
            if self.reset_hall_effect_counter.Get():
                print("RESET FROM CATCH")
                self.reset_hall_effect_counter.Reset()
                self.op_state = self.RESET

        if self.op_state == self.RESETTING:
            speed = self.resetting_speed
            if self.reset_hall_effect_counter.Get():
                print("RESET")
                speed = 0
                self.reset_hall_effect_counter.Reset()
                self.op_state = self.RESET
        
        #This is not part of the normal state machine,
        #this is for manual reset.
        if self.op_state != self.RESET and self.manual_reset_button.get() and self.shoot_button.get():
            self.op_state = self.RESETTING

        # This sets the state to RESET regardless of where the arm thinks it is.
        # This should only be used to recover from a missed reset hall effect or similar
        if self.e_reset_button.get() and self.shoot_button.get():
            self.op_state = self.RESET
            print("***************** EMERGENCY RESET *****************")

        wpilib.SmartDashboard.PutString("Shooter Op State", self.op_state)

        self.motors.Set(speed)

    def auto_init(self, auto_config):
        self.auto_state = self.RESET
        self.low_shot_hall_effect_counter.Reset()
        self.high_shot_hall_effect_counter.Reset()
        self.reset_hall_effect_counter.Reset()
        self.catch_hall_effect_counter.Reset()

        wpilib.SmartDashboard.PutString('auto shooter state', self.auto_state)

    def auto_shoot_tick(self, time):
        speed = 0
        if self.auto_state == self.RESET:
            self.auto_state = self.SHOOTING

        elif self.auto_state == self.SHOOTING:
            speed = self.shooting_speed

            if self.low_shot_hall_effect_counter.Get():
                self.reset_hall_effect_counter.Reset()
                self.auto_state = self.RESETTING
                # wpilib.Wait(3)

        elif self.auto_state == self.RESETTING:
            speed = self.resetting_speed
            if self.reset_hall_effect_counter.Get():
                speed = 0
                self.auto_state = self.AUTO_SHOOT_DONE
                # wpilib.Wait(3)

        elif self.auto_state == self.AUTO_SHOOT_DONE:
            speed = 0

        self.motors.Set(speed)
        
        wpilib.SmartDashboard.PutString('auto shooter state', self.auto_state)

    def is_auto_shoot_done(self):
        return self.auto_state == self.AUTO_SHOOT_DONE

    def reset(self):
        self.auto_state = self.RESET
        self.low_shot_hall_effect_counter.Reset()
        self.high_shot_hall_effect_counter.Reset()
        self.reset_hall_effect_counter.Reset()
        self.catch_hall_effect_counter.Reset()

    def should_stop(self):
        # This could be compacted down, but it's understandable as is
        if self.catch_preset_button.get() and self.catch_hall_effect_counter.Get():
            return True
        if self.low_shot_preset_button.get() and self.low_shot_hall_effect_counter.Get():
            return True
        # Always stop if the high shot hall effect is triggered
        elif self.high_shot_hall_effect_counter.Get(): 
            return True

        return False
