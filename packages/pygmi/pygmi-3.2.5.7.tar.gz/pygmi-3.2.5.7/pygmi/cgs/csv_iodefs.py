# -----------------------------------------------------------------------------
# Name:        accuracy.py (part of PyGMI)
#
# Author:      Gabrielle Denner & Patrick Cole
# E-Mail:      pcole@geoscience.org.za
#
# Copyright:   (c) 2022 Council for Geoscience
# Licence:     Confidential, only for CGS,
# -----------------------------------------------------------------------------
"""Import Data."""

import os
import re
from PyQt5 import QtWidgets, QtCore
import numpy as np
import pandas as pd
import pygmi.menu_default as menu_default


class ImportLineData(QtWidgets.QDialog):
    """
    Import Line Data.

    This class imports ASCII point data.

    Attributes
    ----------
    parent : parent
        reference to the parent routine
    outdata : dictionary
        dictionary of output datasets
    ifile : str
        input file name. Used in main.py
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        if parent is None:
            self.showprocesslog = print
        else:
            self.showprocesslog = parent.showprocesslog

        self.parent = parent
        self.indata = {}
        self.outdata = {}
        self.ifile = ''
        self.filt = ''

        self.setupui()

    def setupui(self):
        """
        Set up UI.

        Returns
        -------
        None.

        """
        gridlayout_main = QtWidgets.QGridLayout(self)
        buttonbox = QtWidgets.QDialogButtonBox()
        helpdocs = menu_default.HelpButton('pygmi.vector.iodefs.'
                                           'importpointdata')

        buttonbox.setOrientation(QtCore.Qt.Horizontal)
        buttonbox.setCenterButtons(True)
        buttonbox.setStandardButtons(buttonbox.Cancel | buttonbox.Ok)

        self.setWindowTitle(r'Import Point Data')

        gridlayout_main.addWidget(helpdocs, 3, 0, 1, 1)
        gridlayout_main.addWidget(buttonbox, 3, 1, 1, 3)

        buttonbox.accepted.connect(self.accept)
        buttonbox.rejected.connect(self.reject)

    def settings(self, nodialog=False):
        """
        Entry point into item.

        Parameters
        ----------
        nodialog : bool, optional
            Run settings without a dialog. The default is False.

        Returns
        -------
        bool
            True if successful, False otherwise.

        """
        if not nodialog:
            ext = ('Comma Delimited (*.csv);;'
                   'Tab Delimited (*.txt);;'
                   'All Files (*.*)')

            self.ifile, self.filt = QtWidgets.QFileDialog.getOpenFileName(
                self.parent, 'Open File', '.', ext)
            if self.ifile == '':
                return False

        gdf = pd.read_csv(self.ifile, skip_blank_lines=True).dropna()
        gdf.reset_index(inplace=True, drop=True)

        self.outdata['csv'] = gdf #outputs the dataset


        # if self.filt == 'Comma Delimited (*.csv)':
        #     breakpoint()
        #     gdf = self.get_delimited(',')
        # elif self.filt == 'Tab Delimited (*.txt)':
        #     gdf = self.get_delimited('\t')
        # else:
        #     return False

        # if gdf is None:
        #     return False

        # ltmp = gdf.columns.values

        # xind = 0
        # yind = 1

        # Check for flexible matches
        # for i, tmp in enumerate(ltmp):
        #     tmpl = tmp.lower()
        #     if 'lon' in tmpl or 'x' in tmpl or 'east' in tmpl:
        #         xind = i
        #     if 'lat' in tmpl or 'y' in tmpl or 'north' in tmpl:
        #         yind = i
        # # Check for exact matches. These take priority
        # for i, tmp in enumerate(ltmp):
        #     tmpl = tmp.lower()
        #     if tmpl in ['x', 'e']:
        #         xind = i
        #     if tmpl in ['y', 'n']:
        #         yind = i

        # self.xchan.addItems(ltmp)
        # self.ychan.addItems(ltmp)

        # self.xchan.setCurrentIndex(xind)
        # self.ychan.setCurrentIndex(yind)

        # if not nodialog:
        #     tmp = self.exec_()

        #     if tmp != 1:
        #         return tmp

        # try:
        #     nodata = float(self.nodata.text())
        # except ValueError:
        #     self.showprocesslog('Null Value error - abandoning import')
        #     return False

        # xcol = self.xchan.currentText()
        # ycol = self.ychan.currentText()

        # gdf['pygmiX'] = gdf[xcol]
        # gdf['pygmiY'] = gdf[ycol]
        # gdf['line'] = gdf['line'].astype(str)

        # if 'Line' not in self.outdata:
        #     self.outdata['Line'] = {}

        # gdf = gdf.replace(nodata, np.nan)
        # self.outdata['Line'][self.ifile] = gdf

        return True
