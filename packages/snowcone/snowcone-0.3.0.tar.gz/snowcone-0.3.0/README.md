# 🍧 snowcone
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![Python CI](https://github.com/ismailuddin/snowcone/actions/workflows/ci.yml/badge.svg)
![PyPI - Downloads](https://img.shields.io/pypi/dm/snowcone)
![PyPi version](https://img.shields.io/pypi/v/snowcone)
> Set of useful utilities for Python inspired by other libraries and languages

## Requirements
- Python 3.6 or newer

## 🛠 Installation
To install the package, run the following command from a terminal:

```shell
$   pip install snowcone
```


## 🚀 Usage
### JavaScript style arrays
Manipulate Python lists using a more object-oriented style JavaScript array syntax:

```python
from snowcone.containers import Array

array = [
    [
        {"category": "A", "value": 0},
        {"category": "A", "value": 2},
        {"category": "A", "value": 4},
    ],
    [
        {"category": "B", "value": 7},
        {"category": "B", "value": 3},
        {"category": "B", "value": 9},
    ]
]

values = (
    Array(array)
        .flatten()
        .filter(lambda x: x["category"] == "A")
        .map(lambda x: x["value"] * 5)
        .all()
)
print(values)
>>> [0, 10, 20, 35, 15, 45]
```

## 📚 Documentation
Documentation can be built using the command `make docs`, which uses the `Makefile` and the `make` binary.
