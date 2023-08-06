from superqt.fonticon import icon
from fonticon_fa6 import FA6S, FA6B, FA6R
from qtpy.QtWidgets import QPushButton


def test_FA6S(qtbot):
    btn = QPushButton()
    qtbot.addWidget(btn)
    btn.setIcon(icon(FA6S.spinner))
    btn.show()

def test_FA6B(qtbot):
    btn = QPushButton()
    qtbot.addWidget(btn)
    btn.setIcon(icon(FA6B.accusoft))
    btn.show()

def test_FA6R(qtbot):
    btn = QPushButton()
    qtbot.addWidget(btn)
    btn.setIcon(icon(FA6R.address_book))
    btn.show()
