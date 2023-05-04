import re
from collections import defaultdict
from rich.table import Table
from rich.console import Console
from rich.text import Text

import styles
from language_questions import language

def genre(mame_tree, mame_root, rebuilder_exe, roms_folder, chds_folder, samples_folder):

    # Function to create table for displaying genres and sub-genres
    def create_table(unique_genres):
        table = Table(show_header=True, header_style=None, title="All Genres in Collection", title_style=styles.info)
        table.add_column("Row")
        table.add_column("Genre")
        table.add_column("Sub-Genres")

        for idx, (main_genre, sub_genres) in enumerate(sorted(unique_genres.items()), start=1):
            table.add_row(str(idx), main_genre, ", ".join(sorted(sub_genres)))
        return table

    # Parse genres and sub-genres from XML file
    unique_genres = defaultdict(set)
    for genre in mame_root.findall('.//category'):
        cleaned_genre = re.sub(r'\*.*\*', '', genre.text)  # Remove text between asterisks
        cleaned_genre = cleaned_genre.strip()  # Remove leading and trailing spaces
        main_genre, sub_genre = cleaned_genre.split(' / ', 1)
        unique_genres[main_genre].add(sub_genre)

    console = Console()

    while True:
        console.print(create_table(unique_genres))
        input_text = Text("Which genre(s) would you like to remove from your collection? "
                            "Enter the row number to remove the associated genre and all associated sub-genres "
                            "(you'll be able to eliminate specific sub-genres in the next step). "
                            "You may enter multiple numbers separated by a comma. Enter 'done' to continue: ", style=styles.prompt)    
        user_input = console.input(input_text)
        if user_input.lower() == 'done':
            console.print("Ok\n", style=styles.success)
            break

        genre_indices = [int(idx.strip()) - 1 for idx in user_input.split(',') if idx.strip().isdigit()]
        genres_to_remove = [genre for idx, (genre, _) in enumerate(sorted(unique_genres.items())) if idx in genre_indices]

        if not genres_to_remove:
            error_text = Text("Error: Invalid input. Please enter a valid number or 'done' to continue.\n", style=styles.error)
            console.print(error_text)
            continue

        removed_machines = 0
        for genre_to_remove in genres_to_remove:
            for machine in mame_root.findall('.//machine'):
                genre = machine.find('category')
                if genre is not None:
                    cleaned_genre = re.sub(r'\*.*\*', '', genre.text).strip()
                    main_genre, _ = cleaned_genre.split(' / ', 1)
                    if main_genre == genre_to_remove:
                        mame_root.remove(machine)
                        removed_machines += 1
            unique_genres.pop(genre_to_remove)

        success_text = Text(f"Success! {removed_machines} games have been filtered out of your collection. You now have {len(mame_root)} games.\n", style=styles.success)
        console.print(success_text)

    # Function to display genres table
    def display_genres_table(unique_genres):
        table = Table(show_header=False, show_lines=False, title="All Sub-genres in Collection", title_style=styles.info)
        table.add_column("Row", justify="right")
        table.add_column("Genre", justify="left")

        for index, genre in enumerate(sorted(unique_genres), start=1):
            table.add_row(str(index), genre)

        console.print(table)
        return {str(index): genre for index, genre in enumerate(sorted(unique_genres), start=1)}

    console = Console()

    # Parse unique genres from XML file
    unique_genres = set()
    for genre in mame_root.findall('.//category'):
        cleaned_genre = re.sub(r'\*.*\*', '', genre.text) # Remove text between asterisks
        cleaned_genre = cleaned_genre.strip() # Remove leading and trailing spaces
        unique_genres.add(cleaned_genre)

    genre_mapping = display_genres_table(unique_genres)

    while True:
        input_text = Text("Which genre(s) would you like to remove from your collection? "
        "Enter the row number to remove the associated genre. "
        "You may enter multiple numbers separated by a comma. Enter 'done' to continue: ", style=styles.prompt)
        response = console.input(input_text)

        if response.lower() == "done":
            console.print("Ok\n", style=styles.success)
            break

        selected_genres = [genre_mapping[num.strip()] for num in response.split(',') if num.strip() in genre_mapping]

        if not selected_genres:
            error_text = Text("Error: Invalid input. Please enter a valid number or 'done' to continue.\n", style=styles.error)
            console.print(error_text)
            continue


        machines_removed = 0
        for machine in mame_root.findall('.//machine'):
            for genre in machine.findall('.//category'):
                cleaned_genre = re.sub(r'\*.*\*', '', genre.text).strip()
                if cleaned_genre in selected_genres:
                    mame_root.remove(machine)
                    machines_removed += 1
                    break

        success_text = Text(f"Success! {removed_machines} games have been filtered out of your collection. You now have {len(mame_root)} games.\n", style=styles.success)
        console.print(success_text)

        # Update unique genres
        unique_genres = set()
        for genre in mame_root.findall('.//category'):
            cleaned_genre = re.sub(r'\*.*\*', '', genre.text)  # Remove text between asterisks
            cleaned_genre = cleaned_genre.strip()  # Remove leading and trailing spaces
            unique_genres.add(cleaned_genre)

        genre_mapping = display_genres_table(unique_genres)

    language(mame_tree, mame_root, rebuilder_exe, roms_folder, chds_folder, samples_folder)
