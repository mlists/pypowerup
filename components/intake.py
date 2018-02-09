from ctre import WPI_TalonSRX
import wpilib
from robotpy_ext.common_drivers.distance_sensors import SharpIRGP2Y0A41SK0F


class Intake:
    intake_left: WPI_TalonSRX
    intake_right: WPI_TalonSRX
    clamp_arm: wpilib.Solenoid
    intake_kicker: wpilib.Solenoid
    extension_arm_left: wpilib.Solenoid
    extension_arm_right: wpilib.Solenoid
    infrared: SharpIRGP2Y0A41SK0F
    cube_switch: wpilib.DigitalInput

    def setup(self):
        """This is called after variables are injected by magicbot."""
        self.intake_right.follow(self.intake_left)
        self.intake_right.setInverted(True)

    def on_enable(self):
        """This is called whenever the robot transitions to being enabled."""
        pass

    def on_disable(self):
        """This is called whenever the robot transitions to disabled mode."""
        pass

    def execute(self):
        """Run at the end of every control loop iteration."""
        pass

    def rotate_intake(self, value):
        """Turns intake mechanism on."""
        self.intake_left.set(value)
        # self.intake_right.set(value)

    def intake_disable(self):
        """Turns intake mechanism off."""
        self.intake_left.stopMotor()
        self.intake_right.stopMotor()

    def intake_clamp(self, value):
        """Turns intake arm on or off"""
        self.clamp_arm.set(value)

    def intake_push(self, value):
        """Turns the pushing pneumatic on or off"""
        self.intake_kicker.set(value)

    def extension(self, value):
        """Turns both pneumatic extensions on or off"""
        self.extension_arm_left.set(value)
        self.extension_arm_right.set(value)

    def infrared_distance(self):
        self.cube_distance = self.infrared.getDistance()
        self.cube_distance * 10

    def cube_inside(self):
        """Run when the limit switch is pressed and when the current
        output is above a threshold, which stops the motors."""
        # if not self.cube_switch.get():
        # print("limit switch pressed")
        # return True
        if 10 <= self.cube_distance <= 15:
            return True
        print("limit switch not pressed")
        return False
