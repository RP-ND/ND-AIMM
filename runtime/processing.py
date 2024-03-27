import math

def calculate_distance(x, y, z):
    try:
        return math.sqrt(float(x)**2 + float(y)**2 + float(z)**2)
    except (ValueError, TypeError):
        return float('inf')  # Return infinity if the values are not numeric or nan

def process_result(result):
    # Extract class name and spatial coordinates from the result
    class_name = result['class_name']
    spatials = result['spatials']
    
    # Extract individual spatial coordinates
    x = spatials.get('x')
    y = spatials.get('y')
    z = spatials.get('z')
    
    # Calculate distance based on class name
    if class_name == 'green_buoy':
        green_distance = calculate_distance(x, y, z)
        red_distance = float('inf')  # Set to a large value if red buoy not detected
    elif class_name == 'red_buoy':
        red_distance = calculate_distance(x, y, z)
        green_distance = float('inf')  # Set to a large value if green buoy not detected
    else:
        # Handle the case when neither green nor red buoy is detected
        green_distance = float('inf')
        red_distance = float('inf')
    
    # Check if red and green distances are equal
    if abs(green_distance - red_distance) < 1e-6:  # Adjust the tolerance as needed
        multiplier1 = 1.0
        multiplier2 = 1.0
    else:
        # Determine multipliers based on distances
        max_multiplier = 1.7  # Maximum multiplier value
        min_multiplier = 1.0  # Minimum multiplier value
        distance_threshold = 1000  # Adjust this threshold as needed
        
        if green_distance < distance_threshold:
            multiplier1 = max_multiplier - (max_multiplier - min_multiplier) * (green_distance / distance_threshold)
            multiplier2 = 1.0
        elif red_distance < distance_threshold:
            multiplier1 = 1.0
            multiplier2 = max_multiplier - (max_multiplier - min_multiplier) * (red_distance / distance_threshold)
        else:
            multiplier1 = 1.0
            multiplier2 = 1.0
    
    return multiplier1, multiplier2