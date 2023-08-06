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

from obserware.sources.widgets.lgptwdgt.interface import Ui_lgptwdgt


class LgPtWdgt(QWidget, Ui_lgptwdgt):
    def __init__(
        self,
        parent=None,
        lgptdevc="Unavailable",
        lgptfutl={
            "free": "000.00XB",
            "used": "000.00XB",
            "comp": "000.00XB",
            "perc": 0.0,
        },
        lgptfsys={"mtpt": "Unavailable", "fsys": "Unavailable"},
    ):
        super(LgPtWdgt, self).__init__(parent)
        self.setupUi(self)
        self.handle_elements(lgptdevc, lgptfutl, lgptfsys)

    def handle_elements(self, lgptdevc, lgptfutl, lgptfsys):
        self.lgptdvce.setText(str(lgptdevc))
        self.lgptfrtx.setText(lgptfutl["free"])
        self.lgptustx.setText(lgptfutl["used"])
        self.lgptsmtx.setText(lgptfutl["comp"])
        self.lgptpgbr.setValue(int(lgptfutl["perc"]))
        self.lgptfsys.setText("<b>%s</b> (%s)" % (lgptfsys["mtpt"], lgptfsys["fsys"]))
