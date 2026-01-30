import math

ASPECT_RATIOS = [
    "1:1",
    "4:3",
    "3:4",
    "16:9",
    "9:16",
    "3:2",
    "2:3",
    "7:9",
    "9:7",
    "1:2",
    "2:1",
]
PIXEL_COUNTS = ["0.25M", "0.5M", "1M", "1.5M", "2M"]


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
    except ValueError, ZeroDivisionError:
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


def find_matching_preset(width, height):
    """
    Checks if the given width/height exactly matches a known preset.
    Returns (aspect_ratio, pixel_count) or None.
    """
    for ar in ASPECT_RATIOS:
        for pc in PIXEL_COUNTS:
            pc_val = float(pc.replace("M", ""))
            w, h = calculate_dimensions(ar, pc_val)
            if w == width and h == height:
                return ar, pc
    return None


def find_nearest_preset(width, height):
    """
    Finds the preset combination that produces dimensions closest to the input.
    Returns (aspect_ratio, pixel_count).
    """
    best_dist = float("inf")
    best_match = ("1:1", "1M")

    for ar in ASPECT_RATIOS:
        for pc in PIXEL_COUNTS:
            pc_val = float(pc.replace("M", ""))
            w, h = calculate_dimensions(ar, pc_val)

            # Euclidean distance in dimension space
            dist = math.sqrt((w - width) ** 2 + (h - height) ** 2)

            if dist < best_dist:
                best_dist = dist
                best_match = (ar, pc)

    return best_match
