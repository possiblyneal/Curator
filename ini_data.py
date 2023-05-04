import xml.etree.ElementTree as ET

def ini_data(mame_root, catver_file, languages_file):

    """
    Section 1. Language Dictionary
    """

    # Read the .ini file as text
    with open(languages_file, 'r') as f:
        ini_text = f.read()

    # Split the .ini file into sections
    sections = ini_text.split('\n\n')

    # Create a dictionary to map filenames to languages
    filename_to_language = {}
    for section in sections:
        lines = section.strip().split('\n')
        if len(lines) > 1:
            language = lines[0].strip('[]')
            
            # Skip "FOLDER_SETTINGS" and "ROOT_FOLDER" sections
            if language in ["FOLDER_SETTINGS", "ROOT_FOLDER"]:
                continue
                
            for filename in lines[1:]:
                filename = filename.strip()
                filename_to_language[filename] = language

    """
    Section 2. Catergory Dictionary
    """

    def parse_ini_file(file_path):
        filename_to_cat = {}
        with open(file_path, 'r') as file:
            category_section = False
            for line in file:
                line = line.strip()
                if not category_section and line == '[Category]':
                    category_section = True
                    continue
                if category_section and line.startswith('['):
                    break
                if category_section and '=' in line:
                    key, value = line.split('=', 1)
                    filename_to_cat[key] = value
        return filename_to_cat

    ini_file_path = catver_file
    filename_to_cat_dict = parse_ini_file(ini_file_path)

    """
    Section 3. Incorporating dictionary data as elements in xml
    """

    # Iterate through the machine elements in the XML
    for machine in mame_root.findall('machine'):
        filename = machine.get('name')

        # Add the "language" element if the filename is in the filename_to_language dictionary
        if filename in filename_to_language:
            language = filename_to_language[filename]
            language_element = ET.SubElement(machine, 'language')
            language_element.text = language

        # Add the "category" element if the filename is in the filename_to_cat_dict dictionary
        if filename in filename_to_cat_dict:
            category = filename_to_cat_dict[filename]
            category_element = ET.SubElement(machine, 'category')
            category_element.text = category

    return mame_root