# forfiles

forfiles has useful tools for files and images.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install forfiles.

```bash
python3 -m pip install --upgrade forfiles
```

## Usage

```python
from forfiles import file, image

# file tools
file.filter("C:/Users/example/Downloads/files-to-filter/", [".png", ".txt", "md"])

# image tools
image.scale("C:/Users/example/Downloads/b.png", 1, 1.5)
image.resize("C:/Users/example/Downloads/car.jpg", 1000, 1000)
```