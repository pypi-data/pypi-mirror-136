# Appyx

## Setting up the project for programming
Before continuing, clone the repository via the preferred method.

### Configuring IntelliJ
1. Open IntelliJ.
2. Select `File > New > Project from Existing Sources...`.
3. Choose the coned repository's base folder and press `Next`.
4. Select create project from existing sources and press `Next`.
5. Choose a name for the project ("Appyx" or similar is suggested) and press `Next`.
6. There should be only one source file. Mark it and press `Next`.
7. You will be prompted to select a project SDK.
    1. Press the _plus_ button in the upper-left corner of the window.
    2. Select `Add Python SDK...`.
    3. Select `Virtualenv Environment` to create a new Python virtual environment for installing the required Python packages and libraries.
        1. Select `New environment`.
        2. Choose the location path of the project, which should look like `(...)/appyx` and create a new folder inside, named `venv`. The resulting path should be `(...)/appyx/venv`.
        3. Choose the Python interpreter for the desired version (for example in the path `/use/bin/python3.8` for Python 3.8).
        4. Press `OK`.
    4. It is advised you now change the name of the SDK ("Appyx virtualenv" or similar is suggested).
    5. Make sure the recently created SDK is selected and press `Next`.
8. No frameworks will be detected. This is as intended. Press `Finish`.

### Installing required packages
1. Open the project in the current window or in a new one.
2. Open a terminal with `Alt + F12` or `View > Tool Windows > Terminal`.
3. Make sure the PIP package installer is upgraded with `pip install --upgrade pip`.
4. Install the required packages with `pip install -r requirements.txt`.

### Set testing configurations
1. Select `Run > Edit Configurations...`.
2. Press the _plus_ button on the upper-left corner of the window.
3. Write `Unittests` and press enter, or select `Python tests > Unittests`.
4. In the `Configuration` tab, select `Module name` as the target.
5. In the text field below, type `appyx` by hand.
6. Under `Python interpreter` select `Use specified interpreter` and choose the created Appyx virtual environment (most likely named "Appyx virtualenv" as suggested).
7. Name it "Unit Tests for Appyx" or something similar and press `Apply` and `OK`.
8. With that configuration selected, which it should now be, tests can be run with `Shoft + F10`.

### Tests and packages
Django and flask tests are executed only if the corresponding packages are installed.

## Making a new version of Appyx for PyPi
Note: [this is a good reference for updating Appyx version](https://widdowquinn.github.io/coding/update-pypi-package/)

### Preparing
Ensure you have local packages for distribution. Run these commands in your virtualenv:

```
python -m pip install --upgrade setuptools wheel
python -m pip install --upgrade twine
```

### Changing the version number
- Change the version number in setup.py
- Commit with a message like: `Update to version xxxx`

### Uploading to PiPy
First, change the version number in file setup.py

To generate the distribution:
```
python3 setup.py sdist bdist_wheel
```

To upload:
```
python3 -m twine upload dist/*
```