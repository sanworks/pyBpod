# PyBpod #

**version:** 1.8.2a2

iblpybpod is a GUI application that enables interaction with the Bpod device from [Sanworks](https://sanworks.io/). Much credit 
and thanks go to the original creators of the [pybpod project](https://github.com/pybpod/pybpod).

This project is has recently been adopted by the software development team at the International Brain Lab and is very much a 'work 
in progress' at the moment.

## Steps to install ##
```bash
conda create --name iblpybpod python=3.8
conda activate iblpybpod
pip install iblpybpod
start-pybpod
```

## Steps to setup development environment ##
```bash
conda create --name iblpybpod-dev python=3.8
conda activate iblpybpod-dev
git clone https://github.com/int-brain-lab/iblpybpod
pip install --editable iblpybpod
start-pybpod
```