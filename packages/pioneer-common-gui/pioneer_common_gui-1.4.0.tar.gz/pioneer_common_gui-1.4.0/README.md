# pioneer.common.gui

pioneer.common.ui is a python gui library regrouping all graphical utilities needed by pioneer.das.view and other applications.


## Installation

Use the package manager to install pioneer.common.gui

```bash
pip install pioneer-common-gui
```
** Prerequisites **
To setup pioneer.common.gui in develop mode, you need to have installed **cmake** beforehand.

**Eigen3** and **tbb** are also required
```bash
sudo apt install libeigen3-dev
sudo apt install libtbb-dev
```

When developing, you can link the repository to your python site-packages and enable hot-reloading of the package
```bash
pip3 install -r requirements.txt 
python3 setup.py develop --user
```

If you don't want to install all the dependencies on your computer, you can run it in a virtual environment as well.
```bash
pipenv install --skip-lock

pipenv shell
```

## Usage

To run the dasview in the virtual environment, you can use the run command
```python
from pioneer.common.gui import Actors

```
