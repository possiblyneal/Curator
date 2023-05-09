from rich.table import Table
from rich.console import Console
from rich.text import Text

import styles
from joy_ways import joystick_ways
from genre_questions import genre

console = Console()

def control(mame_tree, mame_root, rebuilder_exe, roms_folder, chds_folder, samples_folder):

    unique_control_types = {}

    def update_unique_control_types(mame_root):
        unique_control_types = {}
        control_elements = mame_root.findall('.//control')
        
        for control in control_elements:
            control_type = control.get('type')
            if control_type in unique_control_types:
                unique_control_types[control_type] += 1
            else:
                unique_control_types[control_type] = 1
        
        return unique_control_types

    def print_table():
     
        # Sort the control types alphabetically
        sorted_control_types = sorted(unique_control_types.items())

        # Control type descriptions
        control_type_descriptions = {
            'keypad': "A numeric or alphanumeric keypad with multiple buttons for entering digits or characters.",
            'joy': "A digital joystick, usually 8-way, with a limited number of discrete positions for detecting distinct directions.",
            'pedal': "A foot-operated controller for controlling in-game actions like acceleration, braking, or movement.",
            'only_buttons': "A control setup that includes only buttons, without any other types of controllers like joysticks or trackballs.",
            'mahjong': "A specific controller setup for playing Mahjong games, featuring multiple buttons to represent the various Mahjong tiles.",
            'triplejoy': "A rare control setup featuring three joysticks, used for specialized arcade games or systems.",
            'gambling': "Controls specifically designed for gambling or casino-style games, such as slot machines or poker games.",
            'trackball': "A ball-shaped controller that can be rolled in any direction for precise movement or aiming in games.",
            'keyboard': "A full or partial keyboard used for input, typically found in computer-based systems or games.",
            'dial': "A rotating controller that can be turned clockwise or counterclockwise continuously for controlling in-game actions or movement.",
            'positional': "An digial joystick with a number of discrete positions rather than true analog measurement, providing more precise control than a standard digital joystick, but less than an analog joystick",
            'lightgun': "A gun-shaped controller that detects the position of the gun on the screen, typically used in shooting games.",
            'stick': "An analog joystick with a continuous range of positions, providing more precise control than a digital joystick.",
            'hanafuda': "A specific controller setup for playing Hanafuda card games, featuring buttons to represent the various cards.",
            'paddle': "A rotating controller, similar to a dial but typically larger, used for controlling in-game movement or actions in a limited range (such as Pong-style games).",
            'doublejoy': "A control setup featuring two joysticks, often used for games that require simultaneous control of movement and aiming.",
            'mouse': "A computer mouse, used for controlling in-game actions or movement with high precision."
        }

        # Create a table using the rich library
        console = Console()
        table = Table(show_header=True, title="Controller Types in Current List", title_style=styles.info, header_style=None)
        table.add_column("Number")
        table.add_column("Control Type")
        table.add_column("# of Games")
        table.add_column("Description")

        valid_types = list(unique_control_types.keys())
        for index, (control_type, count) in enumerate(sorted_control_types, start=1):
            description = control_type_descriptions.get(control_type) if control_type in valid_types else "Unknown control type"
            table.add_row(str(index), control_type, str(count), description)

        console.print(table)


    def remove_machines_by_control_type(mame_root, control_types_to_remove):
        removed_count = 0
        for machine in mame_root.findall('machine'):
            for control in machine.findall('.//control'):
                control_type = control.get('type')
                if control_type in control_types_to_remove:
                    mame_root.remove(machine)
                    removed_count += 1
                    break
        return mame_root, removed_count

    # Find all the 'control' elements
    control_elements = mame_root.findall('.//control')

    # Extract the unique control types and store them in a dictionary
    unique_control_types = {}
    for control in control_elements:
        control_type = control.get('type')
        if control_type in unique_control_types:
            unique_control_types[control_type] += 1
        else:
            unique_control_types[control_type] = 1

    unique_control_types = update_unique_control_types(mame_root)

    while True:
        print_table()
        control_type_prompt = Text("What control type(s) would you like to remove from your collection? Enter the number in the left column to eliminate the corresponding games from your list. You may enter multiple numbers separated by a comma. Type 'done' to continue:", style=styles.prompt)
        user_input = console.input(control_type_prompt).strip()

        if user_input.lower() == 'done':
            console.print("Ok\n", style=styles.success)
            break

        control_types_indices = user_input.split(',')
        valid_types = list(unique_control_types.keys())
        sorted_control_types = sorted(valid_types)

        control_types_to_remove = []
        invalid_indices = []

        for t in control_types_indices:
            try:
                index = int(t.strip())
                if 1 <= index <= len(sorted_control_types):
                    control_types_to_remove.append(sorted_control_types[index - 1])
                else:
                    invalid_indices.append(t.strip())
                    print(f"Invalid index {t.strip()} detected. Valid range: 1-{len(sorted_control_types)}")
            except ValueError:
                console.print("Error: Please enter only valid numbers separated by a comma.", style=styles.error)
                break

        if invalid_indices:
            console.print("Error: The following control type numbers are invalid:", ', '.join(invalid_indices), style=styles.error)

        if control_types_to_remove:
            mame_root, removed_count = remove_machines_by_control_type(mame_root, control_types_to_remove)
            update_text = Text(f"Success! {removed_count} games have been filtered out of your collection. You now have {len(mame_root)} games.\n", style=styles.success)
            console.print(update_text)

            # Update the unique_control_types dictionary after removing machines
            unique_control_types = update_unique_control_types(mame_root)

    #Check if there are any joysticks left and launch joy_ways if there are
    joy_controls = ['joy', 'doublejoy', 'triplejoy']

    found_joy_control = False
    for machine in mame_root.findall('machine'):
        if found_joy_control:
            break

        for control in machine.findall('.//control'):
            control_type = control.get('type')
            if control_type in joy_controls:
                mame_root = joystick_ways(mame_root)
                found_joy_control = True
                break

    genre(mame_tree, mame_root, rebuilder_exe, roms_folder, chds_folder, samples_folder)




