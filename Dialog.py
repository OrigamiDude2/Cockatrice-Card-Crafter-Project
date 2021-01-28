from dearpygui.core import *
from dearpygui.simple import *

def directory_picker(sender, data):
    select_directory_dialog(callback=apply_selected_directory)

def apply_selected_directory(sender, data):
    log_debug(data)  # so we can see what is inside of data
    directory = data[0]
    folder = data[1]
    set_value("directory", directory)
    set_value("folder", folder)
    set_value("folder_path", f"{directory}\\{folder}")

show_logger()

with window("Tutorial"):
    add_button("Directory Selector", callback=directory_picker)
    add_text("Directory Path: ")
    add_same_line()
    add_label_text("##dir", source="directory", color=[255, 0, 0])
    add_text("Folder: ")
    add_same_line()
    add_label_text("##folder", source="folder", color=[255, 0, 0])
    add_text("Folder Path: ")
    add_same_line()
    add_label_text("##folderpath", source="folder_path", color=[255, 0, 0])

start_dearpygui()