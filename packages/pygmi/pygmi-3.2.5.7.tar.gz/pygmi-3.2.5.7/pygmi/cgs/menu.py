# -----------------------------------------------------------------------------
# Name:        menu.py (part of PyGMI)
#
# Author:      Patrick Cole
# E-Mail:      pcole@geoscience.org.za
#
# Copyright:   (c) 2022 Council for Geoscience
# Licence:     GPL-3.0
#
# This file is part of PyGMI
#
# PyGMI is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyGMI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# -----------------------------------------------------------------------------
"""
CGS menu routines.
"""
from PyQt5 import QtWidgets

from pygmi.cgs import classification
from pygmi.cgs import monitoring
from pygmi.cgs import ai_seis
from pygmi.cgs import scan_imp


class MenuWidget():
    """
    Widget class to call the main interface.

    This widget class creates the clustering menus to be found on the main
    interface. Normal as well as context menus are defined here.

    Attributes
    ----------
    parent : pygmi.main.MainWidget
        Reference to MainWidget class found in main.py
    """

    def __init__(self, parent=None):

        self.parent = parent

# Normal menus
        self.menu = QtWidgets.QMenu('CGS')
        parent.menubar.addAction(self.menu.menuAction())

        self.action_monitoring = QtWidgets.QAction('AI Dolomite')
        self.menu.addAction(self.action_monitoring)
        self.action_monitoring.triggered.connect(self.monitor)

        self.action_aiseis = QtWidgets.QAction('AI Seismology')
        self.menu.addAction(self.action_aiseis)
        self.action_aiseis.triggered.connect(self.aiseis)

        self.action_iscan = QtWidgets.QAction('Import Scanned Bulletins')
        self.menu.addAction(self.action_iscan)
        self.action_iscan.triggered.connect(self.import_scans)

    def classify_borehole(self):
        """Borehole Classification."""
        self.parent.item_insert('Step', 'Borehole Classification',
                                classification.Classification)

    def import_scans(self):
        """Import scanned records."""
        self.parent.item_insert('Io', 'Import Scanned Bulletins',
                                scan_imp.SIMP)

    def monitor(self):
        """Monitoring Module"""
        self.parent.item_insert('Io', 'Monitoring Window',
                                monitoring.Monitoring)

    def aiseis(self):
        """Import CSV data."""
        self.parent.item_insert('Io', 'AI Seismology',
                                ai_seis.AI_Seis)
