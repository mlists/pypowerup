from magicbot import StateMachine, state, timed_state
from components.intake import Intake
from automations.lifter import LifterAutomation


class IntakeAutomation(StateMachine):
    """Importing objects from other files"""
    intake: Intake
    lifter_automation: LifterAutomation

    @state(first=True, must_finish=True)
    def intake_cube(self):
        """Starts the intake motors while waiting for the cube be seen by the
        infrared sensor"""

        if self.intake.cube_inside():
            print("Cube inside")
            self.intake.rotate_intake(0.0)
            self.intake.extension(False)
            self.intake.intake_clamp(False)
            self.intake.intake_push(False)
            self.intake.extension(True)
            self.done()
        else:
            print("Cube not inside")
            self.intake.rotate_intake(1)
            self.intake.extension(True)

    @state(must_finish=True)
    def clamp(self):
        """Grabs cube and starts lifter state machine"""
        print("Closing containment area")
        self.intake.intake_clamp(True)
        self.intake.intake_push(False)
        self.lifter_automation.engage(initial_state="eject")
        self.done()

    @state(must_finish=True)
    def deposit(self):
        """Deposit cube."""
        print("Depositing cube")
        self.intake.rotate_intake(-1)
        self.done()

    @state(must_finish=True)
    def stop(self):
        """Stop moving motor."""
        self.intake.rotate(0)
        self.done()

    @timed_state(must_finish=True, duration=1, next_state="holding")
    def start(self, state_tm):
        if state_tm < 0.5:
            self.intake.extension(True)
            self.intake.rotate(1)
            self.intake.arms_out = True
        else:
            self.intake.extension(False)

    @timed_state(must_finish=True, duration=1, next_state="stop")
    def pulling_in_cube(self):
        self.intake.extension(False)
        self.intake.rotate(-1)

    @timed_state(must_finish=True, duration=1, next_state="stop")
    def push_out_cube(self):
        self.intake.rotate(1)
        self.intake.intake_clamp(False)
        self.intake.extension(False)

    @timed_state(must_finish=True, duration=0.3, next_state="reset_containment")
    def eject_cube(self):
        self.intake.clamp_on(False)
        self.intake.intake_push(True)

    @state(must_finish=True)
    def reset_containment(self):
        self.intake.clamp_on(False)
        self.intake.intake_push(False)
        print("Stopping")
        self.intake.rotate_intake(0.0)
        self.done()
