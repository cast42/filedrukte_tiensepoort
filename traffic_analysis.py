import cv2
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.axes._axes as axes
from matplotlib.patheffects import Stroke, Normal
import numpy as np
import toml
from datetime import datetime
import pandas as pd
import re
from typing import Union, Tuple, Dict, List
import os
from pprint import pprint
import math


def argument2path(argument: Union[str, os.PathLike]) -> os.PathLike:
    """
    Convert a string or path-like object to a Path object and validate its existence.

    Args:
        argument (Union[str, os.PathLike]): A string or a path-like object representing a file or directory path.

    Returns:
        os.PathLike: A Path object representing the converted path.

    Raises:
        TypeError: If the argument is neither a string nor a path-like object.

    Example:
        >>> argument = "/path/to/some/file.txt"
        >>> path = argument2path(argument)
        >>> print(path)
        PosixPath('/path/to/some/file.txt')

    Note:
        This function is useful for converting file or directory path arguments to pathlib.Path objects
        and verifying whether the specified path exists. If the path does not exist, it returns an empty Path object.
    """
    if isinstance(argument, str):
        argument_path = Path(argument)
    elif isinstance(argument, os.PathLike):
        argument_path = argument
    else:
        raise TypeError("url must be a string or a path object")
    if not argument_path.exists():
        # logger.error(f"Argument {argument_path.as_posix()} does not exists.")
        return Path()
    return argument_path


def load_config(tomlfile: Union[str, os.PathLike]) -> dict:
    """
    Load configuration settings from a TOML file and return them as a dictionary.

    Args:
        tomlfile (Union[str, os.PathLike]): A string or a path-like object representing the path to the TOML file.

    Returns:
        dict: A dictionary containing the configuration settings loaded from the TOML file.

    Example:
        >>> tomlfile = "config.toml"
        >>> config = load_config(tomlfile)
        >>> print(config)
        {'key1': 'value1', 'key2': 'value2', ...}

    Note:
        This function reads the contents of a TOML file and converts it into a dictionary
        of key-value pairs. It is useful for loading configuration settings from external files.
    """
    toml_path = argument2path(tomlfile)

    # Open the TOML file
    with open(toml_path, "r") as f:
        # Load the contents of the file into a dictionary
        config = toml.load(f)
    return config


def display_shot(url: Union[str, os.PathLike]) -> axes.Axes:
    """
    Display an image from a given URL or file path using Matplotlib.

    Args:
        url (Union[str, os.PathLike]): A string or a path-like object representing the URL or file path of the image.

    Returns:
        matplotlib.axes.Axes: Matplotlib Axes object displaying the image.

    Example:
        >>> image_url = "https://example.com/image.jpg"
        >>> display_shot(image_url)

    Note:
        This function takes a URL or file path, loads and displays the image using Matplotlib.
        It can be used to visualize images in Jupyter notebooks or other interactive environments.
    """
    image = argument2path(url)
    im = cv2.cvtColor(cv2.imread(image.as_posix()), cv2.COLOR_BGR2RGB)
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_axis_off()
    ax.imshow(im)
    return ax


def show_points_on_screenshot(
    config: dict,
    location: str,
    street: str,
    url_image: Union[str, os.PathLike],
    points_list_name: str,
    x_text_offset: int = 6,
    y_text_offset: int = 6,
    x_line_offset: int = 20,
    y_line_offset: int = 20,
    ha_offset: str = "center",
    va_offset: str = "center",
) -> axes.Axes:
    # Read in the image on the URL
    url_image = argument2path(url_image)
    image_path = argument2path(url_image)
    im = cv2.cvtColor(cv2.imread(image_path.as_posix()), cv2.COLOR_BGR2RGB)
    # Plot the point on the screenshot
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.spines[:].set_visible(False)
    ax.yaxis.set_visible(False)
    ax.xaxis.set_visible(False)
    ax.imshow(im)
    for i, p in enumerate(config[location][street]["points"][points_list_name]):
        x, y = p[0], p[1]
        x_end, y_end = x - x_line_offset, y + y_line_offset
        ax.plot([x, x_end], [y, y_end], color="k", linewidth=1)
        ax.annotate(
            f"{i}",
            xy=(x_end, y_end),
            xytext=(x_end - x_text_offset, y_end + y_text_offset),
            fontsize=8,
            ha=ha_offset,
            va=va_offset,
        )
    return ax


def maximum_measure_points(config: dict) -> Tuple[int, str, str, str]:
    """
    Find the location and street with the maximum number of measurement points in the given configuration.

    Args:
        config (Dict[str, Dict[str, dict]]): A dictionary containing configuration information with nested structure.

    Returns:
        Tuple[int, str, str, str]: A tuple containing the maximum number of points, the location with the maximum points,
                             and the street with the maximum points.

    Example:
        >>> config = {
        ...     'Location1': {
        ...         'StreetA': {
        ...             'points': {'to': [(1, 2), (3, 4)],
        ...                         'from': [(1, 2), (3, 4)]
        ...              }
        ...         },
        ...         'StreetB': {
                        'points': {
        ...                 'to': [(5, 6), (7, 8), (9, 10)]
                         }
        ...         }
        ...     },
        ...     'Location2': {
        ...         'StreetC': {
        ...             'points': {'to': [(11, 12)]}
        ...         }
        ...     }
        ... }
        >>> max_points, max_location, max_street, max_direction = maximum_measure_points(config)
        >>> print(max_points, max_location, max_street)
        3 Location1 StreetB

    Note:
        This function iterates through the nested structure of the configuration dictionary
        to find the location and street with the maximum number of measurement points.
        It returns a tuple containing the maximum points, location, and street names.
    """
    max_points = 0
    max_location = ""
    max_street = ""
    max_direction = ""
    for location in config.keys():
        for street in config[location].keys():
            for points in config[location][street]["points"].keys():
                number_of_points = len(config[location][street]["points"][points])
                if number_of_points > max_points:
                    max_points = number_of_points
                    max_location = location
                    max_street = street
                    max_list_name = points
    return max_points, max_location, max_street, max_list_name


def get_colors_from_screenshots(
    config: dict,
    url_image_dir: Union[str, os.PathLike],
    location: str,
    street: str,
    points_list_name: str,
) -> pd.DataFrame:
    """
    Extract color information from screenshots based on the provided configuration.

    Args:
        config (dict): Configuration dictionary containing information about locations, streets, and points.
        url_image_dir (Union[str, os.PathLike]): Path to the directory containing screenshot images.
        points_list_name (str): Name of the list of points to be sampled.

    Returns:
        pd.DataFrame: DataFrame containing extracted color data with columns including location, street, path,
                      timestamp, color information, and color-mapped traffic colors.

    Example:
        >>> config = {
        ...     'Location1': {
        ...         'StreetA': {
        ...             'points': {'to': [(1, 2), (3, 4)],
        ...                         'from': [(1, 2), (3, 4)]
        ...              }
        ...         },
        ...         'StreetB': {
        ...             'points': {
        ...                 'to': [(5, 6), (7, 8), (9, 10)]
        ...              }
        ...         }
        ...     },
        ...     'Location2': {
        ...         'StreetC': {
        ...             'points': {'to': [(11, 12)]}
        ...         }
        ...     }
        ... }
        >>> url_image_dir = '/path/to/screenshots'
        >>> result_df = get_colors_from_screenshots(config, url_image_dir, points_list_name)

    Note:
        This function processes screenshots of traffic data based on the provided configuration.
        It extracts color information from the images, maps the colors to traffic colors,
        and returns the data in a DataFrame for further analysis and visualization.
    """
    url_image_dir = argument2path(url_image_dir)
    rows = []
    number_of_points, _, _, _ = maximum_measure_points(config)
    color_map = {
        "[129  31  31]": "darkred",
        "[242  60  50]": "red",
        "[255 151  77]": "orange",
        "[99 214 104]": "green",
    }
    # Loop over all screenshots and extract color at the point locations
    for p in url_image_dir.glob(f"{location}_{street}_*.png"):
        timestamp = datetime.strptime(p.stem, f"{location}_{street}_%Y%m%d-%H%M%S")
        screenshot = cv2.cvtColor(cv2.imread(p.as_posix()), cv2.COLOR_BGR2RGB)
        colors = ()
        for idx, point in enumerate(
            config[location][street]["points"][points_list_name]
        ):
            color = screenshot[point[1], point[0]]
            colors += (color, color[0], color[1], color[2])
            color_array_as_string = str(color)
            colors += (color_array_as_string,)
        # Fill the rest of the columns with grey color
        for _ in range(idx + 1, number_of_points):
            colors += ([128, 128, 128], 128, 128, 128, "[128 128 128]")
        row = (location, street, p, timestamp) + colors
        rows.append(row)

    # Create a dataframe from the list of detected colors
    all_columns = ["location", "street", "path", "timestamp"]

    for i in range(number_of_points):
        all_columns.extend(
            (
                f"color_{i}",
                f"p{i}_red",
                f"p{i}_green",
                f"p{i}_blue",
                f"traffic_color_{i}",
            )
        )

    df = pd.DataFrame(rows, columns=all_columns).sort_values(by="timestamp")

    return df


def rgb_to_xyz(r, g, b):
    # Convert RGB to [0, 1] range
    r, g, b = r / 255.0, g / 255.0, b / 255.0

    # Assuming sRGB
    r = ((r + 0.055) / 1.055) ** 2.4 if r > 0.04045 else r / 12.92
    g = ((g + 0.055) / 1.055) ** 2.4 if g > 0.04045 else g / 12.92
    b = ((b + 0.055) / 1.055) ** 2.4 if b > 0.04045 else b / 12.92

    # Convert to XYZ
    x = r * 0.4124 + g * 0.3576 + b * 0.1805
    y = r * 0.2126 + g * 0.7152 + b * 0.0722
    z = r * 0.0193 + g * 0.1192 + b * 0.9505

    return x, y, z


def xyz_to_lab(x, y, z):
    # Observer=2°, Illuminant=D65
    x = x / 95.047
    y = y / 100.000
    z = z / 108.883

    x = x ** (1 / 3) if x > 0.008856 else (7.787 * x) + (16 / 116)
    y = y ** (1 / 3) if y > 0.008856 else (7.787 * y) + (16 / 116)
    z = z ** (1 / 3) if z > 0.008856 else (7.787 * z) + (16 / 116)

    l = (116 * y) - 16
    a = 500 * (x - y)
    b = 200 * (y - z)

    return l, a, b


def rgb_to_lab(r, g, b):
    x, y, z = rgb_to_xyz(r, g, b)
    return xyz_to_lab(x, y, z)


def euclidean_distance(
    color1: Tuple[float, float, float], color2: Tuple[float, float, float]
) -> float:
    # Function to calculate Euclidean distance between two vectors
    return math.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(color1, color2)))


def map_color(
    color: str, cielab_target_colors: Dict[str, Tuple[float, float, float]]
) -> Tuple[str, float]:
    """
    Maps an RGB color to the closest color in CIELAB space from a given set of target colors.

    Args:
    color (str): The RGB color to be mapped, in the format 'rgb(r, g, b)'.
    cielab_target_colors (dict): A dictionary where keys are color names and values are colors in CIELAB space.

    Returns:
    Tuple[str, float]: The name of the closest color from the target set and the Euclidean distance to it in CIELAB space.
    """
    # Extract RGB values from the input string
    numbers = re.findall(r"\d+", color)
    assert (
        len(numbers) == 3
    ), f"Input {color} string has {len(numbers)} numbers: {numbers=}. Expected 3"

    # Convert string numbers to integers
    r, g, b = [int(num) for num in numbers]

    # Convert RGB to CIELAB
    cielab_color = rgb_to_lab(r, g, b)

    # Find the closest color
    closest_color = min(
        cielab_target_colors,
        key=lambda named_color: euclidean_distance(
            cielab_color, cielab_target_colors[named_color]
        ),
    )

    # Calculate the Euclidean distance to the closest color
    cielab_euclid_distance = euclidean_distance(
        cielab_color, cielab_target_colors[closest_color]
    )

    return closest_color, cielab_euclid_distance


def map_colors(unique_colors: List[str]) -> Dict[str, str]:
    """
    Maps each color in a list of unique RGB color strings to the closest color from a predefined set of target colors.

    The mapping is done based on the CIELAB color space. The function converts the target colors and the input colors to CIELAB space and then finds the closest target color for each input color.

    Args:
        unique_colors (List[str]): A list of color strings in the RGB format in string format.
        Each string must contain 3 integer numbers.

    Returns:
        Dict[str, str]: A dictionary mapping each color in `unique_colors` to the name of the closest color from the predefined set.

    Note:
        The function assumes the input RGB colors are in string format and need to be parsed.
        The target colors are predefined within the function in RGB.
    """
    # Predefined target colors in RGB
    target_colors = {
        "darkred": (139, 0, 0),
        "red": (255, 0, 0),
        "orange": (255, 165, 0),
        "green": (2, 128, 8),
        "grey": (128, 128, 128),
    }

    # Convert target colors to CIELAB
    cielab_target_colors = {
        color_name: rgb_to_lab(*rgb_values)
        for color_name, rgb_values in target_colors.items()
    }

    # Map each unique color to the closest target color
    mapped_colors = {
        color: map_color(color, cielab_target_colors)[0] for color in unique_colors
    }

    return mapped_colors
