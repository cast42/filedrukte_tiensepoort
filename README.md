# Take screenshots to monitor traffic

Take screenshots from a list of urls using [playright](https://github.com/Microsoft/playwright-python) and checks them into the repo using github actions. Based on Simon Willison's [shotscraper](https://github.com/simonw/shot-scraper)

## Schedule a Python script with GitHub Actions to take screenshots from URLS

**Watch the video tutorial:**

[![Alt text](https://img.youtube.com/vi/PaGp7Vi5gfM/hqdefault.jpg)](https://youtu.be/PaGp7Vi5gfM)

This example shows how to run a Python script as cron job with GitHub Actions. It calls an API once a week (could be any schedule you want), logs the response in `status.log`, and automatically pushes the changes to this repo.

- The code to automatically take a screenshot with [playright](https://github.com/Microsoft/playwright-python) is implemented in `main.py`
- Inspect and configure cron job in GitHub Action `.github/workflows/actions.yml`
- It installs and use third party packages from `requirements.txt`
- Secret environment variables can be used. Set secrets in Settings/Secrets/Actions -> 'New repository secret'. Use the same secret name inside `actions.yml` and `main.py`

## Configuration

### For the screenshots

The configuration is done via a TOML file called [config.toml](https://github.com/cast42/filedrukte_tiensepoort/blob/main/config.toml) It contains
a list of locations. Each location can have several streets. Every location/street must have an URL.
Example:

```ascii
>>> config = {
...     'Location1': {
...         'StreetA': {
...             'url': '<https://www.google.com/maps/>...'
...         },
...         'StreetB': {
...             'url': '<https://www.google.com/maps/>...'
...         }
...     },
...     'Location2': {
...         'StreetC': {
...             'url': '<https://www.google.com/maps/>...'
...         }
...     }
... }
```

### Configuration of the colors that represent traffic

First, a GUI must be started to click on a map at what position the colors must be sampled.

```bash
python measure_points_gui.py shots/leuven_geldenaaksevest_20231017-114230.png -direction from
```

A visualisation of the screenshot of the argument will appear. It's handy to use the magnifier glass on osx:
Press option-command 8

Next click in the position were colors must be sampled.

Press q.

In this case, the following will be added to the config.yml file:

```ascii
"point_from": [ [ 887, 78,], ..., [ 418, 712,],]
```

## Analysis of the screenshot

Open notebook [get_traffic_info_from_screenshot.ipynb](https://github.com/cast42/filedrukte_tiensepoort/blob/main/get_traffic_info_from_screenshot.ipynb).

Adapt the global variables LOCATION, STREET and DIRECTION in the third cell:

```ascii
# Which street to analyse and in what direction
LOCATION = "leuven"
STREET = "tiensestraat"
DIRECTION = "to" # must be "to" the crossing or away "from" the crossing
```

Run the notebook until the end. The results are in the figs directory.

## Installation

To locally test main.py python script follow these steps:

### 1. Prerequisites

Make sure you have Python 3.11 or later installed on your system.

### 2. Install Poetry

To install Poetry, you can use the [official installer](https://python-poetry.org/docs/#installing-with-the-official-installer)  provided by Poetry. Do not use pip.

### 3. Clone the Repository

Clone the repo `filedrukte_tiensepoort` repository from GitHub:

```bash
git clone hhttps://github.com/cast42/filedrukte_tiensepoort
```

### 4. Install Dependencies

Use Poetry to install the package and its dependencies:

```bash
poetry install
```

or you can create a virtualenv with poetry and install the dependencies

```bash
poetry shell
poetry install
```
