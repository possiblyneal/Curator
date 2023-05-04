from rich import print
from rich.table import Table
from rich.text import Text
from rich.console import Console
import re

from rich_pbar import loaded_pbar
import styles
from rebuilder import rebuild

console=Console()

def clone(mame_tree, mame_root, rebuilder_exe, roms_folder, chds_folder, samples_folder):

    """
    Step 1. Check for Clones
    """

    # Create a set of parent and child machines
    # First pass: collect all machines and mark if they are parents

    def parent_clone_sets():
        machines = {}
        parent_clone_dict = {}
        missing_parents = set()

        for machine in mame_root.findall('machine'):
            machine_name = machine.get('name')
            cloneof = machine.get('cloneof')

            if cloneof:
                machines[machine_name] = {
                    'is_parent': False,
                    'parent': cloneof
                }
            else:
                machines[machine_name] = {
                    'is_parent': True
                }

        # Second pass: populate parent-clone dictionary
        for machine_name, machine_data in machines.items():
            if machine_data['is_parent']:
                parent_clone_dict[machine_name] = []

        for machine_name, machine_data in machines.items():
            if not machine_data['is_parent']:
                parent_name = machine_data['parent']
                if parent_name not in parent_clone_dict:
                    parent_clone_dict[parent_name] = []
                    missing_parents.add(parent_name)
                parent_clone_dict[parent_name].append(machine_name)

        p_c_sets = [set([parent, *clones]) for parent, clones in parent_clone_dict.items()]
        filtered_p_c_sets = [s - missing_parents for s in p_c_sets]
        return filtered_p_c_sets

    output = parent_clone_sets()
    no_sets_with_multiple_items = True

    for p_c_set in output:
        if len(p_c_set) > 1:
            no_sets_with_multiple_items = False
            break

    if no_sets_with_multiple_items:
        rebuild(mame_tree, mame_root, rebuilder_exe, roms_folder, chds_folder, samples_folder)
    

    """
    Step 2. Ask user what to do with Clones. Remove all if applicable.
    """

    clone_prompt_text = f"[{styles.prompt}]Your ROMs/ CHDs are comprised of parents and clones, where clones are variations of the parent game. What would you like to do?[/{styles.prompt}]\n[not bold white]1. Choose one version based on preferences of language, and number of players (Recommended)\n2. Keep all clones\n3. Remove all clones\n(1/2/3/info):[/not bold white]"
    info_text = "Info: Clones are a version of an arcade game that is based on the same original game but has some differences. These differences can be small or significant and can include changes in gameplay, graphics, or sounds. Clones are often regional variants, bootlegs, hacks, or earlier versions of the game."
    valid_responses = ['1', '2', '3', 'info']
    while True:
        response = console.input(clone_prompt_text).lower()
        if response in valid_responses:
            if response == 'info':
                console.print(info_text + "\n", style=styles.info)
            elif response == '2':
                console.print("Ok\n", style=styles.success)
                rebuild(mame_tree, mame_root, rebuilder_exe, roms_folder, chds_folder, samples_folder)
            elif response == '3':
                total_machines = len(mame_root)
                mame_root [:] = [machine for machine in mame_root.findall('machine') if machine.get('cloneof') is None]
                removed_count = total_machines - len(mame_root)
                console.print(f"Success! {removed_count} games have been filtered out of your collection. You now have {len(mame_root)} games.\n", style=styles.success)
                rebuild(mame_tree, mame_root, rebuilder_exe, roms_folder, chds_folder, samples_folder)
            else:
                console.print("Ok\n", style=styles.success)
                break
        else:
            console.print("Please select one of the available options.\n", style=styles.error)


    """
    Step 3.	Ask user to choose their preferred language and a secondary option if applicable. Remove (silently) machines
            that do not meet the criteria.
    """

    # Get initial machine count to report removed count in final step
    total_machines = len(mame_root)

    # Display a table of all available languages in the xml file
    languages = []
    for machine in mame_tree.findall("machine"):
        language = machine.find("language")
        if language is not None and language.text not in languages:
            languages.append(language.text)

    languages = sorted(languages)

    table = Table(title="Languages in Collection", title_style=styles.info)
    table.add_column("Row", justify="right")
    table.add_column("Language")

    for index, language in enumerate(languages):
        table.add_row(str(index + 1), language)

    print(table)

    # Ask the user which language(s) they would like to prioritize

    primary_language_prompt = Text("Enter the row number of your prefered language (row number/info):", style=styles.prompt)
    info_text = "Info: Curator will prioritize your chosen primary language when selecting a rom from each set of parent/clones.\n"
    while True:
        primary_language = console.input(primary_language_prompt).lower()
        if primary_language.isdigit() and 0 <= int(primary_language) < len(languages):
            primary_language = int(primary_language) - 1
            console.print("Ok\n", style=styles.success)
            break
        elif primary_language == "info":
            console.print(info_text, style=styles.info)
        else:
            console.print("Error: Please enter a valid row number from the table.\n", style=styles.error)

    secondary_language_prompt = Text("Enter the row number of your prefered alternate language (optional) (row number/none/info):", style=styles.prompt)
    info_text = "Info: Curator will prioritize your chosen alternate language when your prefered language is not availible.\n"
    while True:
        secondary_language = console.input(secondary_language_prompt).lower()
        if secondary_language.isdigit() and 0 <= int(secondary_language) < len(languages) and secondary_language != primary_language:
            secondary_language = int(secondary_language) - 1
            console.print("Ok\n", style=styles.success)
            break
        elif secondary_language == "info":
            console.print(info_text, style=styles.info)
        elif secondary_language == "none":
            console.print("Ok\n", style=styles.success)
            break
        else:
            console.print("Error: Please enter a valid row number from the table or enter 'none'.", style=styles.error)

    #Create a list of machines that fit the selected criteria. Note: This will keep all primary languge roms from each set. 
    secondary_language_flag = secondary_language != "none"

    language_filtered = []

    with loaded_pbar() as progress:
        if secondary_language_flag:
            task = progress.add_task(f"Prioritizing {languages[int(primary_language)]} and {languages[int(secondary_language)]} languages...", total=len(parent_clone_sets()))
        else:
            task = progress.add_task(f"Prioritizing {languages[int(primary_language)]} language...", total=len(parent_clone_sets()))
        for machine_set in parent_clone_sets():

            primary_found = False
            secondary_found = False

            primary_language_matches = []
            secondary_language_matches = []
            
            for machine_name in machine_set: 
                machine_element = mame_root.find(f"machine[@name='{machine_name}']")
                language_element = machine_element.find("language") if machine_element is not None else None
                language = language_element.text if language_element is not None else None
                if language == languages[int(primary_language)]:
                    primary_language_matches.append(machine_name)
                    primary_found = True
                
            if not primary_found and secondary_language_flag:
                for machine_name in machine_set:            
                    machine_element = mame_root.find(f"machine[@name='{machine_name}']")
                    language_element = machine_element.find("language") if machine_element is not None else None
                    language = language_element.text if language_element is not None else None
                    if language == languages[int(secondary_language)]:
                        secondary_language_matches.append(machine_name)
                        secondary_found = True
            
            if primary_found:
                language_filtered.append({*primary_language_matches})  # This creates a set and appends it to the list
            elif secondary_found:
                language_filtered.append({*secondary_language_matches})  # This creates a set and appends it to the list
            else:
                language_filtered.append({*machine_set})
            progress.advance(task)


    """
    Step 4.	Ask user to choose their preferred number of players. Remove (silently) machines
            that do not meet the criteria.
    """

    two_player = False
    four_player = False
    max_player = False

    player_prompt_text = f"[{styles.prompt}]Which player variant would you like to prioritize?\n[/{styles.prompt}][white]1. 2-player\n2. 4-player\n3. Prioritize the variant with the most players!\n(1/2/3/info):[/white]"
    info_text = "Info: Many popular arcade games have 2, 4, or even 6 player variants to accomodate the number of players the cabinet is designed for. Select the most appropriate varient to prioritize for your setup."
    valid_responses = ['1', '2', '3', 'info']
    while True:
        response = console.input(player_prompt_text).lower()
        if response in valid_responses:
            if response == 'info':
                console.print(Text(info_text + "\n", style=styles.info))
            elif response == '1':
                console.print("Ok\n", style=styles.success)
                two_player = True 
                task_var = "2-player variants"
                break
            elif response == '2':
                console.print("Ok\n", style=styles.success)
                four_player = True
                task_var = "4-player variants"
                break
            else:
                console.print("Ok\n", style=styles.success)
                max_player = True
                task_var = "variants with the most players"
                break
        else:
            console.print("Please select one of the available options.\n", style=styles.error)

    player_filtered = []

    with loaded_pbar() as progress:
        task = progress.add_task(f"Prioritizing {task_var}...", total=len(language_filtered))
        for machine_set in language_filtered:
            if max_player:
                max_player_count = 0
                max_player_matches = []

                # Find the maximum player count
                for machine_name in machine_set:
                    machine_element = mame_root.find(f"machine[@name='{machine_name}']")
                    input_element = machine_element.find("input") if machine_element is not None else None
                    if input_element is not None and "players" in input_element.attrib:
                        player_count = int(input_element.attrib["players"])
                        if player_count > max_player_count:
                            max_player_count = player_count

                # Append all machine names with max player count
                for machine_name in machine_set:
                    machine_element = mame_root.find(f"machine[@name='{machine_name}']")
                    input_element = machine_element.find("input") if machine_element is not None else None
                    if input_element is not None and "players" in input_element.attrib:
                        player_count = int(input_element.attrib["players"])
                        if player_count == max_player_count:
                            max_player_matches.append(machine_name)

                player_filtered.append({*max_player_matches})

            elif four_player:
                found4player = False
                four_player_matches = []

                # Find machines with 4 players
                for machine_name in machine_set:
                    machine_element = mame_root.find(f"machine[@name='{machine_name}']")
                    input_element = machine_element.find("input") if machine_element is not None else None
                    if input_element is not None and "players" in input_element.attrib:
                        player_count = int(input_element.attrib["players"])
                        if player_count == 4:
                            four_player_matches.append(machine_name)
                            found4player = True

                if found4player:
                    player_filtered.append({*four_player_matches}) 
                else:        
                    player_filtered.append({*machine_set})

            else:
                found2player = False
                two_player_matches = []

                # Find machines with 2 players
                for machine_name in machine_set:
                    machine_element = mame_root.find(f"machine[@name='{machine_name}']")
                    input_element = machine_element.find("input") if machine_element is not None else None
                    if input_element is not None and "players" in input_element.attrib:
                        player_count = int(input_element.attrib["players"])
                        if player_count == 2:
                            two_player_matches.append(machine_name)
                            found2player = True

                if found2player:
                    player_filtered.append({*two_player_matches}) 
                else:       
                    player_filtered.append({*machine_set})  
                    
            progress.advance(task)  
 

    """
    Step 5.	 Prioritize US Releases at request if English was a selected language.
    """

    us_release = False

    us_release_prompt_text = Text("Would you like to prioritize US releases for English language games? (y/n/info):", style=styles.prompt)
    info_text = "Info: This will attempt to prioritize US releases by searching game descriptions for USA and US."
    valid_responses = ['y', 'n', 'info']
    while True:
        response = console.input(us_release_prompt_text).lower()
        if response in valid_responses:
            if response == 'info':
                console.print(info_text + "\n", style=styles.info)
            elif response == 'n':
                console.print("Ok\n", style=styles.success)
                break
            else:
                console.print("Ok\n", style=styles.success)
                us_release = True
                break
        else:
            console.print("Please select one of the available options.\n", style=styles.error)

    us_filtered = []


    if us_release:
        with loaded_pbar() as progress:
            task = progress.add_task(f"Prioritizing US releases...", total=len(player_filtered))
            for machine_set in player_filtered:
                found_us = False
                us_matches = []

                # Find if there are any descriptions matching 'us' or 'usa'
                for machine_name in machine_set:
                    machine_element = mame_root.find(f"machine[@name='{machine_name}']")
                    description_element = machine_element.find("description") if machine_element is not None else None
                    if description_element is not None:
                        pattern = re.compile(r'\(([^)]*?\b(?:us|usa)\b[^)]*?)\)', re.IGNORECASE)
                        if pattern.search(description_element.text):
                            us_matches.append(machine_name)
                            found_us = True

                if found_us:
                    us_filtered.append({*us_matches}) 

                else:       
                    us_filtered.append({*machine_set}) 

                progress.advance(task) 

    else:       
        us_filtered = player_filtered

    """
    Step 6.	For the remaining parent/clone sets, if there are more than one item per set, choose the parent. 
            If no parent availible, choose shortest name.
    """

    final_filtered = []

    with loaded_pbar() as progress:
        task = progress.add_task(f"Cleaning up...", total=len(language_filtered))
        for machine_set in us_filtered:

            parent_found = False

            for machine_name in machine_set: 
                machine_element = mame_root.find(f"machine[@name='{machine_name}']")
                if machine_element is not None and "cloneof" not in machine_element.attrib:
                    final_filtered.append(machine_name)
                    parent_found = True

            if not parent_found:
                if machine_set:  # Check if machine_set is not empty
                    shortest_item = min(machine_set, key=lambda x: len(x))
                    final_filtered.append(shortest_item)

            progress.advance(task) 

    """
    Step 7.	Update mame_root to reflect user preferences and report new total
    """

    # Iterate through the machines to be removed list and remove those machines from the root and save it
    mame_root[:] = [machine for machine in mame_root.findall('machine') if machine.get('name') in final_filtered]

    removed_count = total_machines - len(mame_root)
    console.print(f"Success! {removed_count} games have been filtered out of your collection. You now have {len(mame_root)} games.\n", style=styles.success)

    rebuild(mame_tree, mame_root, rebuilder_exe, roms_folder, chds_folder, samples_folder)