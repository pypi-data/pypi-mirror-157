# Installation
Installation of `instancelib` requires `Python 3.8` or higher.

### 1. Python installation
Install Python on your operating system using the [Python Setup and Usage](https://docs.python.org/3/using/index.html) guide.

### 2. Installing `instancelib`
`instancelib` can be installed:

* _using_ `pip`: `pip3 install` (released on [PyPI](https://pypi.org/project/instancelib/))
* _locally_: cloning the repository and using `python setup.py install` (NB. On Ubuntu, you may need to use python3 if python is not available or refers to Python 2.x).

#### Using `pip`
1. Open up a `terminal` (Linux / macOS) or `cmd.exe`/`powershell.exe` (Windows)
2. Run the command:
    - `pip install instancelib`, or
    - `pip install instancelib`.

```console
user@terminal:~$ pip3 install instancelib
Collecting instancelib
...
Installing collected packages: instancelib
Successfully installed instancelib
```

#### Locally
1. Download the folder from `GitLab/GitHub`:
    - Clone this repository, or 
    - Download it as a `.zip` file and extract it.
2. Open up a `terminal` (Linux / macOS) or `cmd.exe`/`powershell.exe` (Windows) and navigate to the folder you downloaded `instancelib` in.
3. In the main folder (containing the `setup.py` file) run:
    - `python3 setup.py install`, or
    - `python setup.py install`.

```console
user@terminal:~$ cd ~/instancelib
user@terminal:~/instanceliby$ python3 setup.py install
running install
running bdist_egg
running egg_info
...
Finished processing dependencies for instancelib
```
