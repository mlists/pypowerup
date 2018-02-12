from magicbot.state_machine import AutonomousStateMachine, state
from pyswervedrive.swervechassis import SwerveChassis


class CrossBaseline(AutonomousStateMachine):

    chassis: SwerveChassis
    MODE_NAME = 'Default'
    DEFAULT = True

    @state(first=True)
    def go_forward(self, initial_call):
        if initial_call:
            self.chassis.set_inputs(3, 0, 0)
        if self.chassis.odometry_x >= 3:  # get the actual value
            self.next_state('stopping')

    @state
    def stopping(self):
        self.chassis.set_inputs(0, 0, 0)
        print("Statemachine execution completed")
        self.done()
