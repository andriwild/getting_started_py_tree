import py_trees
import threading
import time
import readchar

from enum import Enum

class ProcessState(Enum):
    IDLE = 0
    SEARCH= 1
    ENGAGE = 2
    ESCORT_AGREE = 3
    ESCORT_DISAGREE = 4
    HANDOFF = 5



class Simulator(py_trees.behaviour.Behaviour):
    def __init__(self, name="Simulator"):
        super().__init__(name)
        self.blackboard = self.attach_blackboard_client(name=name)
        self.blackboard.register_key("process_state", access=py_trees.common.Access.WRITE)

    def setup(self, **kwargs):
        self.blackboard.process_state = ProcessState.IDLE
        self.listener_thread = threading.Thread(target=self.listen_for_keys, daemon=True)
        self.listener_thread.start()

    def listen_for_keys(self):
        while True:            
            key = readchar.readchar()
            if key == "s":
                self.blackboard.process_state = ProcessState.SEARCH
            elif key == "e":
                self.blackboard.process_state = ProcessState.ENGAGE
            elif key == "a":
                self.blackboard.process_state = ProcessState.ESCORT_AGREE
            elif key == "d":
                self.blackboard.process_state = ProcessState.ESCORT_DISAGREE
            elif key == "h":
                self.blackboard.process_state = ProcessState.HANDOFF

    def update(self):
        self.feedback_message = "Checking keys: ([s]earch, [e]ngage, escort[a]gree,escort[d]isagree, [h]andoff)"
        return py_trees.common.Status.RUNNING


class CheckState(py_trees.behaviour.Behaviour):
    def __init__(self, state, name="CheckState"):  
        super().__init__(name + "-" +state.name)
        self.state = state
        self.blackboard = self.attach_blackboard_client(name=name)
        self.blackboard.register_key("process_state", access=py_trees.common.Access.READ)

    def update(self):
        self.feedback_message = "Checking for " + str(self.state) + "..."
        if self.blackboard.process_state == self.state:
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE



class Search(py_trees.behaviour.Behaviour):
    def __init__(self, name="Search"):
        super().__init__(name)

    def update(self):
        self.feedback_message = "Searching..."
        return py_trees.common.Status.RUNNING

    def terminate(self, new_status):
        self.feedback_message = ""



class Engage(py_trees.behaviour.Behaviour):
    def __init__(self, name="Engage"):
        super().__init__(name)

    def update(self):
        self.feedback_message = "Engaging..."
        return py_trees.common.Status.RUNNING
    
    def terminate(self, new_status):
        self.feedback_message = ""
      

class EscortAgree(py_trees.behaviour.Behaviour):
    def __init__(self, name="EscortAgree"):
        super().__init__(name)

    def update(self):
        self.feedback_message = "Escorting..."
        return py_trees.common.Status.RUNNING
    
    def terminate(self, new_status):
        self.feedback_message = ""


class EscortDisagree(py_trees.behaviour.Behaviour):
    def __init__(self, name="EscortDisagree"):
        super().__init__(name)

    def update(self):
        self.feedback_message = "Escorting fallback..."
        return py_trees.common.Status.RUNNING
    
    def terminate(self, new_status):
        self.feedback_message = ""


class Handoff(py_trees.behaviour.Behaviour):
    def __init__(self, name="Handoff"):
        super().__init__(name)

    def update(self):
        self.feedback_message = "Handing off..."
        return py_trees.common.Status.RUNNING
    
    def terminate(self, new_status):
        self.feedback_message = ""


class Conversation(py_trees.behaviour.Behaviour):
    def __init__(self, name="Conversation"):
        super().__init__(name)
        self.blackboard = self.attach_blackboard_client(name=name)
        self.blackboard.register_key("process_state", access=py_trees.common.Access.WRITE)
        
        self.last_state = None
        self.running = True
        self.listener_thread = threading.Thread(target=self.communicate, daemon=True)
        

    def setup(self, **kwargs):
        self.listener_thread.start()
        

    def communicate(self):

        def changed_state_to(state):
            return self.last_state != current_state and current_state == state

        while self.running:
            current_state = self.blackboard.process_state
            # print("Current state: " + current_state.name)
        
            # Change to ENGAGE
            if changed_state_to(ProcessState.ENGAGE):
                self.feedback_message = "Found resident. Trying to convince resident to escort to therapy."
                resident = self.resident_information()
                print("Hi " + resident['name'] + ", are you ready for your therapy?")
                print("Resident information: " + str(resident))
                # TODO: Use LLM to ask resident for agreement and call resident_agreed_escort(agreed) function
                time.sleep(3) # API Call
                # self.resident_agreed_escort(True) # Called by LLM, or type 'a' for agree or 'd' for disagree

            if changed_state_to(ProcessState.ESCORT_AGREE):
                self.feedback_message = "Resident agreed to escort to therapy. Smalltalk."
                resident = self.resident_information()
                print("Talk me something about your " + resident['hobby'])
                # TODO: Use LLM to smalltalk
                time.sleep(3) # API Call
  
            if changed_state_to(ProcessState.ESCORT_DISAGREE):
                self.feedback_message = "Resident disagreed to escort to therapy. "
                print("Notify nurse about resident's disagreement.")
                self.blackboard.process_state = ProcessState.IDLE

            if changed_state_to(ProcessState.HANDOFF):
                self.feedback_message = "Arriving at the therapy room."

                resident = self.resident_information()
                print("Please confirm your arrival at the therapy room.")
                # TODO: Use LLM to smalltalk
                time.sleep(3) # API Call
                self.resident_confirmed_handoff() # Only happy path is supported
            
            
            time.sleep(1)
            self.last_state = current_state
        pass


    # Function call from LLM
    def resident_agreed_escort(self, agreed):
        if agreed:
            self.blackboard.process_state = ProcessState.ESCORT_AGREE
        else:
            self.blackboard.process_state = ProcessState.ESCORT_DISAGREE


    # Function call from LLM
    def resident_confirmed_handoff(self):
        self.blackboard.process_state = ProcessState.IDLE


    # From database
    def resident_information(self):
        return dict(name='Hans', age=80, sex='male', hobby='gardening')

    def update(self):
        return py_trees.common.Status.RUNNING
    
    def terminate(self, new_status):
        self.feedback_message = ""


def create_tree():
    """Create and return the behavior tree."""
    
    search = py_trees.composites.Sequence(name="SearchSeq", memory=False, children=[CheckState(ProcessState.SEARCH), Search()])
    engage = py_trees.composites.Sequence(name="EngageSeq", memory=False, children=[CheckState(ProcessState.ENGAGE), Engage()])
    escort = py_trees.composites.Selector(name="EscortBehavior", memory=False, children=[
        py_trees.composites.Sequence(name="EscortAgreeSeq", memory=False, children=[CheckState(ProcessState.ESCORT_AGREE), EscortAgree()]),
        py_trees.composites.Sequence(name="EscortDisargreeSeq", memory=False, children=[CheckState(ProcessState.ESCORT_DISAGREE), EscortDisagree()]),
    ])
    
    handoff = py_trees.composites.Sequence(name="HandoffSeq", memory=False, children=[CheckState(ProcessState.HANDOFF), Handoff()])
    robot_behaviour = py_trees.composites.Selector(name="RobotBehavior", memory=False, children=[search, engage, escort, handoff, py_trees.behaviours.Running("Idle")])
    talking_robot_behaviour = py_trees.composites.Parallel(name="TalkingRobot", policy=py_trees.common.ParallelPolicy.SuccessOnOne(), children=[robot_behaviour, Conversation()])
    root = py_trees.composites.Parallel(name="Simulation", policy=py_trees.common.ParallelPolicy.SuccessOnAll(), children=[Simulator(), talking_robot_behaviour])

    return root


def main():
    """Main function to run the behavior tree."""
    root = create_tree()
    
    # Create and setup the tree
    behavior_tree = py_trees.trees.BehaviourTree(root)
    behavior_tree.setup()

    def post_tick_handler(tree):
        print(py_trees.display.ascii_tree(tree.root, show_status=True))
        print(py_trees.display.unicode_blackboard())

    try:
        behavior_tree.tick_tock(
            period_ms=100,
            number_of_iterations=py_trees.trees.CONTINUOUS_TICK_TOCK,
            pre_tick_handler=None,
            post_tick_handler=post_tick_handler, # Comment out to remove tree print
        )

    except KeyboardInterrupt:
        behavior_tree.interrupt()

if __name__ == "__main__":
    main() 