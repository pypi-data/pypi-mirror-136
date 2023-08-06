"""
Obserware
Copyright (C) 2021-2022 Akashdeep Dhar

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


from PyQt5.QtWidgets import QWidget

from obserware.sources.widgets.phptwdgt.interface import Ui_phptwdgt


class PhPtWdgt(QWidget, Ui_phptwdgt):
    def __init__(
        self,
        parent=None,
        phptdevc="Unavailable",
        phptfutl={
            "free": "000.00XB",
            "used": "000.00XB",
            "comp": "000.00XB",
            "perc": 0.0,
        },
        phptfsys={"mtpt": "Unavailable", "fsys": "Unavailable"},
    ):
        super(PhPtWdgt, self).__init__(parent)
        self.setupUi(self)
        self.handle_elements(phptdevc, phptfutl, phptfsys)

    def handle_elements(self, phptdevc, phptfutl, phptfsys):
        self.phptdvce.setText(str(phptdevc))
        self.phptfrtx.setText(phptfutl["free"])
        self.phptustx.setText(phptfutl["used"])
        self.phptsmtx.setText(phptfutl["comp"])
        self.phptpgbr.setValue(int(phptfutl["perc"]))
        self.phptfsys.setText("<b>%s</b> (%s)" % (phptfsys["mtpt"], phptfsys["fsys"]))
