import math

def calculate_scale_factor(original_width, original_length, current_width, current_length):
    """
    Calculate the scale factor between original and current PCB dimensions.
    """
    scale_x = current_width / original_width
    scale_y = current_length / original_length
    return scale_x, scale_y

def scale_component_position(x, y, scale_x, scale_y):
    """
    Scale component position based on the scale factors.
    """
    new_x = round(x * scale_x, 4)
    new_y = round(y * scale_y, 4)
    return new_x, new_y

def get_pcb_dimensions(pcb_outline):
    """
    Calculate PCB dimensions from outline coordinates.
    """
    width = round(pcb_outline[2] - pcb_outline[0], 4)
    length = round(pcb_outline[3] - pcb_outline[1], 4)
    return width, length