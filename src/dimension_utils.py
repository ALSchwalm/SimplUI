import math

def calculate_dimensions(aspect_ratio_str, pixel_count_m):
    """
    Calculates width and height from an aspect ratio string (e.g. "16:9")
    and pixel count in millions. 
    1M is specifically mapped to 1024 * 1024.
    Results are rounded to the nearest multiple of 64.
    """
    # 1M pixels = 1024 * 1024
    total_pixels = pixel_count_m * 1024 * 1024
    
    # Parse aspect ratio
    try:
        w_part, h_part = map(float, aspect_ratio_str.split(":"))
        ratio = w_part / h_part
    except (ValueError, ZeroDivisionError):
        ratio = 1.0
        
    # Height = sqrt(P / R)
    # Width = Height * R
    height = math.sqrt(total_pixels / ratio)
    width = height * ratio
    
    # Round to nearest multiple of 64
    def round_to_64(val):
        return int(round(val / 64.0) * 64)
    
    final_width = round_to_64(width)
    final_height = round_to_64(height)
    
    # Ensure minimum of 64
    final_width = max(64, final_width)
    final_height = max(64, final_height)
    
    return final_width, final_height
