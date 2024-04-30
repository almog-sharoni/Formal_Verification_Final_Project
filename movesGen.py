def file_to_states(file):
    # Open the file
    # Open the file
    with open(file, 'r') as file:
        # Read lines from the file
        lines = file.readlines()

        # Initialize variables
        states = []
        current_state = {}
        previous_action = None

        # Iterate through each line
        for line in lines:
            # If line starts with '-> State:', it indicates a new state
            if line.startswith('  -> State:'):
                # If current_state is not empty, append it to states list
                if current_state:
                    states.append(current_state)
                # Initialize a new state
                current_state = {}
                # Set the action for the current state
                if previous_action:
                    current_state['action'] = previous_action
                else:
                    current_state['action'] = None
            # If line starts with 'action =', extract the action
            elif line.startswith('    action = '):
                action = line.split('=')[1].strip()
                current_state['action'] = action
                # Update the previous_action for the next state
                previous_action = action

        # Append the last state
        states.append(current_state)

    # Print the actions from each state
    for state in states:
        print("Action:", state['action'])


if __name__ == '__main__':
    file_to_states('moves.txt')