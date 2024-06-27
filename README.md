# Angle Monitoring System

This project is designed to monitor a user's posture using points collected from an OptiTrack system. The system checks whether the user is sitting correctly in front of a computer by analyzing the appropriate angles, curvature, and desk height. It updates every second and filters out minor measurement errors to provide accurate feedback.

## Features

- **Real-time Posture Monitoring**: The system updates every second to reflect the user's posture.
- **Angle and Curvature Calculation**: Calculates various angles and curvature of the body to determine posture.
- **Measurement Error Filtering**: Ignores minor changes within a threshold to avoid displaying false alerts.
- **Visual Alerts**: Highlights points on a body image to indicate incorrect posture.
- **Tkinter Interface**: Provides a graphical interface using Tkinter.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/angle-monitoring-system.git
    cd angle-monitoring-system
    ```

2. Install the required packages:
    ```bash
    pip install numpy pandas pillow
    ```

## Usage

1. Ensure you have the `image.webp` file in the same directory as the script. This image should represent the body points that will be highlighted in case of incorrect posture.

2. Run the script:
    ```bash
    python main.py
    ```

## Code Overview

### Constants
- `ACCEPTABLE_TIME`: Time in seconds between alerts for the same issue.
- `THRESHOLD_ANGLE_CHANGE`: Minimum change in angle to consider it a valid change.
- `THRESHOLD_DISTANCE_CHANGE`: Minimum change in distance to consider it a valid change.

### Functions

- `highlight_points(image, points, color)`: Highlights specific points on the image with the given color.
- `update_image(points_of_the_body, alert_states)`: Updates the displayed image based on the alert states.
- `get_alert(value, acceptable_range, index)`: Determines if a value is outside the acceptable range and should trigger an alert.
- `calculate_alpha1(points_of_the_body)`, `calculate_alpha2(points_of_the_body)`, `calculate_alpha3(points_of_the_body)`, `calculate_alpha4(points_of_the_body)`: Calculate specific angles based on the body points.
- `calculate_curvature(points_of_the_body)`: Calculates the curvature of the spine.
- `calculate_angles(points_of_the_body)`: Calculates all relevant angles and curvatures.
- `filter_data(new_points)`: Filters out minor changes in point data to avoid false alerts.
- `visualize_table(points_used_to_calculate_angles, acceptable_ranges_of_the_points)`: Visualizes the angles, updates alerts, and refreshes the display.

### Example Points and Acceptable Ranges

- `points`: A list of coordinates representing various points on the body.
- `acceptable_ranges`: A list of acceptable ranges for each calculated angle and measurement.

## Contributing

Feel free to fork the repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

