# fonticon-fontawesome6

[![License](https://img.shields.io/pypi/l/fonticon-fontawesome6.svg?color=green)](https://github.com/tlambert03/fonticon-fontawesome6/raw/master/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/fonticon-fontawesome6.svg?color=green)](https://pypi.org/project/fonticon-fontawesome6)
[![Python Version](https://img.shields.io/pypi/pyversions/fonticon-fontawesome6.svg?color=green)](https://python.org)

FontAwesome 6 extension for superqt font icons

```sh
pip install superqt fonticon-fontawesome6
```

```python

from fonticon_fa6 import FA6S
from qtpy.QtCore import QSize
from qtpy.QtWidgets import QApplication, QPushButton
from superqt.fonticon import icon, pulse

app = QApplication([])

btn2 = QPushButton()
btn2.setIcon(icon(FA6S.spinner, animation=pulse(btn2)))
btn2.setIconSize(QSize(225, 225))
btn2.show()

app.exec_()
```
