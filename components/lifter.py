import ctre
import wpilib


class Lifter:
    motor: ctre.WPI_TalonSRX
    center_switch: wpilib.DigitalInput
    top_switch: wpilib.DigitalInput

    #  TODO find encoder values, tune height values to include robot height and cube
    COUNTS_PER_REV = 4096
    NUM_TEETH = 42
    TEETH_DISTANCE = 0.005
    COUNTS_PER_METER = COUNTS_PER_REV / (NUM_TEETH * TEETH_DISTANCE) / 2  # for height of dolly

    MOTOR_FREE_SPEED = 5310 / 600  # RPM to rotations/100ms
    GEAR_RATIO = 1 / 6
    FREE_SPEED = int(MOTOR_FREE_SPEED * GEAR_RATIO * COUNTS_PER_REV)  # counts/100ms

    THRESHOLD = 10  # in counts

    TOP_HEIGHT = 2  # in m
    BOTTOM_HEIGHT = 0

    HEIGHT_FROM_FLOOR = 0.2585  # height from floor to initial lift pos when reset in m
    CONTAINMENT_SIZE = 0  # height needed for the mechanism to work properly in m

    UPPER_SCALE = 1.8288 - HEIGHT_FROM_FLOOR + CONTAINMENT_SIZE  # in m
    BALANCED_SCALE = 1.524 - HEIGHT_FROM_FLOOR + CONTAINMENT_SIZE
    LOWER_SCALE = 1.2192 - HEIGHT_FROM_FLOOR + CONTAINMENT_SIZE
    SWITCH = 0.47625 - HEIGHT_FROM_FLOOR + CONTAINMENT_SIZE
    #  TODO find switch pos
    CENTER_SWITCH_POS = 0
    TOP_SWITCH_POS = 0

    def setup(self):
        """This is called after variables are injected by magicbot."""
        self.set_pos = None



        self.motor.setInverted(True)
        self.motor.setNeutralMode(ctre.WPI_TalonSRX.NeutralMode.Brake)

        self.motor.overrideLimitSwitchesEnable(False)
        self.motor.configReverseLimitSwitchSource(ctre.WPI_TalonSRX.LimitSwitchSource.FeedbackConnector, ctre.WPI_TalonSRX.LimitSwitchNormal.NormallyOpen, deviceID=0, timeoutMs=10)
        self.motor.configForwardLimitSwitchSource(ctre.WPI_TalonSRX.LimitSwitchSource.Deactivated, ctre.WPI_TalonSRX.LimitSwitchNormal.Disabled, deviceID=0, timeoutMs=10)

        self.motor.overrideSoftLimitsEnable(True)
        self.motor.configForwardSoftLimitEnable(True, timeoutMs=10)
        self.motor.configForwardSoftLimitThreshold(self.meters_to_counts(self.TOP_HEIGHT), timeoutMs=10)
        self.motor.configReverseSoftLimitEnable(True, timeoutMs=10)
        self.motor.configReverseSoftLimitThreshold(self.meters_to_counts(self.BOTTOM_HEIGHT), timeoutMs=10)

        self.motor.configSelectedFeedbackSensor(ctre.WPI_TalonSRX.FeedbackDevice.QuadEncoder, 0, timeoutMs=10)

        # TODO tune motion profiling
        self.motor.selectProfileSlot(0, 0)
        self.motor.config_kF(0, 1023/self.FREE_SPEED, timeoutMs=10)
        self.motor.config_kP(0, 0.7, timeoutMs=10)
        self.motor.config_kI(0, 0.01, timeoutMs=10)
        self.motor.config_kD(0, 0, timeoutMs=10)

        self.motor.configMotionAcceleration(500, timeoutMs=10)
        self.motor.configMotionCruiseVelocity(self.FREE_SPEED, timeoutMs=10)

    def on_enable(self):
        """This is called whenever the robot transitions to being enabled."""

    def on_disable(self):
        """This is called whenever the robot transitions to disabled mode."""
        self.stop()

    def execute(self):
        """Run at the end of every control loop iteration."""
        if self.set_pos is not None:
            self.motor.set(self.motor.ControlMode.MotionMagic, self.meters_to_counts(self.set_pos))

            if self.at_pos():
                self.stop()
        else:
            self.motor.stopMotor()

        if not self.center_switch.get():
            self.motor.setQuadraturePosition(self.CENTER_SWITCH_POS, timeoutMs=10)
        if not self.top_switch.get():
            self.motor.setQuadraturePosition(self.TOP_SWITCH_POS, timeoutMs=10)
        if self.motor.isRevLimitSwitchClosed():
            self.motor.setQuadraturePosition(self.BOTTOM_HEIGHT, timeoutMs=10)

    def meters_to_counts(self, meters):
        return int(meters * self.COUNTS_PER_METER)

    def stop(self):
        """Stop the lift motor"""
        self.set_pos = None
        self.motor.stopMotor()

    def reset(self):
        self.set_pos = self.BOTTOM_HEIGHT

    def move(self, input_setpos):
        """Move lift to height on encoder

        Args:
            input_setpos (int): Encoder position to move lift to in m.
        """
        self.set_pos = input_setpos

    def get_pos(self):
        """Returns encoder position on lift

       Returns:
            int: The location of the lift
        """
        return self.motor.getSelectedSensorPosition(0) / self.COUNTS_PER_METER

    def at_pos(self):
        """Finds if cube location is at setops and within threshold

        Returns:
            bool: If the encoder is at the pos
        """
        if self.set_pos is None:
            return False
        return abs(self.set_pos - self.get_pos()) < self.THRESHOLD

    def at_pos_switch_pressed(self):
        if self.set_pos == self.SWITCH_HEIGHT:
            default_switch = self.center_switch
        elif self.set_pos == self.BALANCED_SCALE:
            default_switch = self.top_switch
        else:
            return True
        return default_switch.get()
