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
from typing import Union, Tuple
import os


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
    text_offset: int = 6,
    line_offset: int = 20,
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
    for i, p in enumerate(config[location][street]["points"]):
        x, y = p[0], p[1]
        x_end, y_end = x - line_offset, y + line_offset
        ax.plot([x, x_end], [y, y_end], color="k", linewidth=1)
        ax.annotate(
            f"{i}",
            xy=(x_end, y_end),
            xytext=(x_end - text_offset, y_end + text_offset),
            fontsize=8,
            ha=ha_offset,
            va=va_offset,
        )
    return ax


def maximum_measure_points(config: dict) -> Tuple[int, str, str]:
    """
    Find the location and street with the maximum number of measurement points in the given configuration.

    Args:
        config (Dict[str, Dict[str, dict]]): A dictionary containing configuration information with nested structure.

    Returns:
        Tuple[int, str, str]: A tuple containing the maximum number of points, the location with the maximum points,
                             and the street with the maximum points.

    Example:
        >>> config = {
        ...     'Location1': {
        ...         'StreetA': {
        ...             'points': [(1, 2), (3, 4)]
        ...         },
        ...         'StreetB': {
        ...             'points': [(5, 6), (7, 8), (9, 10)]
        ...         }
        ...     },
        ...     'Location2': {
        ...         'StreetC': {
        ...             'points': [(11, 12)]
        ...         }
        ...     }
        ... }
        >>> max_points, max_location, max_street = maximum_measure_points(config)
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
    for location in config.keys():
        for street in config[location].keys():
            if not "points" in config[location][street]:
                continue
            number_of_points = len(config[location][street]["points"])
            if number_of_points > max_points:
                max_points = number_of_points
                max_location = location
                max_street = street
    return max_points, max_location, max_street


def get_colors_from_screenshots(
    config: dict, url_image_dir: Union[str, os.PathLike]
) -> pd.DataFrame:
    """
    Extract color information from screenshots based on the provided configuration.

    Args:
        config (dict): Configuration dictionary containing information about locations, streets, and points.
        url_image_dir (Union[str, os.PathLike]): Path to the directory containing screenshot images.

    Returns:
        pd.DataFrame: DataFrame containing extracted color data with columns including location, street, path,
                      timestamp, color information, and color-mapped traffic colors.

    Example:
        >>> config = {
        ...     'Location1': {
        ...         'StreetA': {
        ...             'points': [(100, 200), (150, 250)]
        ...         },
        ...         'StreetB': {
        ...             'points': [(50, 75)]
        ...         }
        ...     }
        ... }
        >>> url_image_dir = '/path/to/screenshots'
        >>> result_df = get_colors_from_screenshots(config, url_image_dir)

    Note:
        This function processes screenshots of traffic data based on the provided configuration.
        It extracts color information from the images, maps the colors to traffic colors,
        and returns the data in a DataFrame for further analysis and visualization.
    """
    url_image_dir = argument2path(url_image_dir)
    rows = []
    color_map = {
        "[129  31  31]": "darkred",
        "[242  60  50]": "red",
        "[255 151  77]": "orange",
        "[99 214 104]": "green",
    }
    # Loop over all screenshots and extract color at the point locations
    for location in config.keys():
        for street in config[location].keys():
            for p in url_image_dir.glob(f"{location}_{street}_*.png"):
                timestamp = datetime.strptime(
                    p.stem, f"{location}_{street}_%Y%m%d-%H%M%S"
                )
                screenshot = cv2.cvtColor(cv2.imread(p.as_posix()), cv2.COLOR_BGR2RGB)
                colors = ()
                if not "points" in config[location][street]:
                    continue
                for point in config[location][street]["points"]:
                    color = screenshot[point[1], point[0]]
                    colors += (color, color[0], color[1], color[2])
                    color_array_as_string = str(color)
                    colors += (
                        color_map.get(color_array_as_string, "grey"),
                    )  # Grey means no data
                row = (location, street, p, timestamp) + colors
                rows.append(row)
    # Create a dataframe from the list of detected colors
    all_columns = ["location", "street", "path", "timestamp"]
    max_points, max_location, max_street = maximum_measure_points(config)
    for i in range(max_points):
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
