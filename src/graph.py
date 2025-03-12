import py_trees
from robot_behavior import create_tree

def main(args=None):
    root = create_tree()
    
    # Create and setup the tree
    behavior_tree = py_trees.trees.BehaviourTree(root)
    
    # Render the tree to a dot file
    py_trees.display.render_dot_tree(root, name='robot_behavior_tree', with_blackboard_variables=True)
    return

if __name__ == '__main__':
    main()