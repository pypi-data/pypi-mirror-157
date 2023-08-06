# -----------------------------------------------------------------------------
# Name:        accuracy.py (part of PyGMI)
#
# Author:      Gabrielle Denner & Patrick Cole
# E-Mail:      pcole@geoscience.org.za
#
# Copyright:   (c) 2022 Council for Geoscience
# Licence:     Confidential, only for CGS,
# -----------------------------------------------------------------------------
"""Binary Classification Accuracy Assessment tool."""

import os
import sys
import copy
import numpy as np
from PyQt5 import QtWidgets, QtCore
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib import cm
from matplotlib.artist import Artist
from matplotlib.patches import Polygon as mPolygon
from matplotlib.lines import Line2D
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
from shapely.geometry import shape
from PIL import Image, ImageDraw
import sklearn.metrics as skm
from sklearn.preprocessing import LabelEncoder

import pygmi.vector
from pygmi.vector.graphs import PlotVector
from pygmi.misc import frm
from pygmi.misc import ProgressBarText


class GraphMap(FigureCanvasQTAgg):
    """
    Graph Map.

    Attributes
    ----------
    parent : parent
        reference to the parent routine
    """

    def __init__(self, parent=None):
        self.figure = Figure()

        super().__init__(self.figure)
        self.setParent(parent)

        self.parent = parent
        self.polyi = None
        self.data = []
        self.cdata = []
        self.mindx = [0, 0]
        self.csp = None
        self.subplot = None

    def init_graph(self):
        """
        Initialise the graph.

        Returns
        -------
        None.

        """

        self.figure.clf()
        self.subplot = self.figure.add_subplot(111)

        axes = self.figure.gca()

        axes.set_xlabel('Eastings')
        axes.set_ylabel('Northings')

        axes.xaxis.set_major_formatter(frm)
        axes.yaxis.set_major_formatter(frm)

        self.figure.canvas.draw()

    def update_graph(self):
        """
        Update graph.

        Returns
        -------
        None.

        """
        pass


class Accuracy(QtWidgets.QDialog):
    """
    Main Supervised Classification Tool Routine.

    Attributes
    ----------
    parent : parent
        reference to the parent routine
    indata : dictionary
        dictionary of input datasets
    outdata : dictionary
        dictionary of output datasets
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        if parent is None:
            self.showprocesslog = print
            self.piter = ProgressBarText().iter
        else:
            self.showprocesslog = parent.showprocesslog
            self.piter = parent.pbar.iter

        self.indata = {}
        self.outdata = {}
        self.parent = parent
        self.m1 = 0
        self.c = [0, 1, 0]
        self.m = [0, 0]
        self.df = None

        self.map = GraphMap(self)
        self.label1 = QtWidgets.QLabel()

        self.mpl_toolbar = NavigationToolbar2QT(self.map, self.parent)

        self.setupui()

        self.map.mindx = self.m

    def setupui(self):
        """
        Set up UI.

        Returns
        -------
        None.

        """

        grid_main = QtWidgets.QGridLayout(self)
        group_map = QtWidgets.QGroupBox('Insert Data')
        grid_right = QtWidgets.QGridLayout(group_map)

        group_class = QtWidgets.QGroupBox('ROC Curve')
        grid_class = QtWidgets.QGridLayout(group_class)

        buttonbox = QtWidgets.QDialogButtonBox()
        buttonbox.setOrientation(QtCore.Qt.Horizontal)
        buttonbox.setStandardButtons(buttonbox.Cancel | buttonbox.Ok)

        loadshape = QtWidgets.QPushButton('Load Class Shapefile')
        calcmetrics = QtWidgets.QPushButton('Calculate and Display Metrics')

        self.setWindowTitle('Binary Class Accuracy Assessment')

        grid_right.addWidget(calcmetrics, 1, 2, 1, 1)
        grid_right.addWidget(loadshape, 1, 0, 1, 1)

        grid_main.addWidget(self.map, 0, 0, 2, 1)
        grid_main.addWidget(self.mpl_toolbar, 2, 0, 1, 1)

        grid_main.addWidget(group_map, 0, 1, 1, 1)
        grid_main.addWidget(group_class, 1, 1, 1, 1)
        grid_main.addWidget(buttonbox, 2, 1, 1, 1)

        loadshape.clicked.connect(self.load_shape)
        calcmetrics.clicked.connect(self.calc_metrics)

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
        if 'Vector' not in self.indata:
            self.showprocesslog('Error: You must have a shapefile '
                                'dataset')
            return False

        self.map.data = self.indata['Vector']

        self.map.init_graph()


        tmp = self.exec_()

        if tmp == 0:
            return False

        return True

    def load_shape(self):
        """
        Load shapefile.

        Returns
        -------
        bool
            True if successful, False otherwise.

        """
        ext = 'Shapefile (*.shp)'

        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self.parent,
                                                            'Open File',
                                                            '.', ext)
        if filename == '':
            return False

        df = gpd.read_file(filename)
        df.columns = df.columns.str.lower()
        if 'id' in df:
            df = df.drop('id', axis='columns')

        if 'class' not in df or 'geometry' not in df:
            return False

        print("Shapefile loaded.")

        self.df = df.dropna()

        self.prep_data()

        return True

    def prep_data(self):
        """
        Extracts the y_test and y_prep data for calc_metrics.

        Returns
        -------
        y_test, y_pred, tlbls

        """
        predicted_data = self.map.data['Polygon'] # predicted data is in a tuple format
        predicted_data = predicted_data[:] # removes the tuple
        pred_geom = predicted_data['geometry']
        true_data = self.df
        true_geom = true_data['geometry']

        le = LabelEncoder()

        classes = np.array(true_data['class'])
        y_test = le.fit_transform(classes)

        tlbls = np.unique(classes)

        # finding overlapping polygons
        # List to collect pairs of intersecting features
        """
        poly_intersect = []

        for i in pred_geom:
            for j in true_geom:
                if shape(i).intersects(shape(j)):
                    area = i.intersection(j).area/i.area*100
                    poly_intersect.append([i, j, area])
        print("the first column is for y_pred")
        print("the second column is for y_test")

        """
        # if true_geom intersects at >= 50 % assing a 0
        y_pred_test = []
        intersects = 0
        for i in self.piter(true_geom):
            for j in pred_geom:
                if i.intersects(j):
                    intersects += 1
                    if i.intersection(j).area/i.area*100 >= 50:
                        # j = 0
                        y_pred_test.append(0)
            # elif true_geom intersects at < 50 % assing a 1
                    else:
                        # j = 1
                        y_pred_test.append(1)
            # where the true polygon exists but there is no overlap-assign a 0
                # else:
                #     j = 0


        # would this be faster the other way around? Nope..
        breakpoint()
        #insert a progress bar here...
        overlap = np.array(poly_intersect)

        # if the overlap of the two shapefiles per polygon in more than
        # 50% assign a 1 else assign a 0 in true_data
        """
        geom_p1 = [ shape(feat["geometry"]) for feat in polygon1 ]
        geom_p8 = [ shape(feat["geometry"]) for feat in polygon8 ]

        for i, g1 in enumerate(geom_p1):
            for j, g8 in enumerate(geom_p8):
                if g1.intersects(g8):
                    print i, j, (g1.intersection(g8).area/g1.area)*100
        """




        return y_test, y_pred, tlbls

    def calc_metrics(self):
        """
        Calculate metrics.

        Returns
        -------
        None.

        """
        if self.df is None:
            return

        y_test, y_pred, tlbls = self.prep_data()

        cmat = skm.confusion_matrix(y_test, y_pred)
        accuracy = skm.accuracy_score(y_test, y_pred)
        kappa = skm.cohen_kappa_score(y_pred, y_test)

        message = '<p>Confusion Matrix:</p>'
        message += pd.DataFrame(cmat, columns=tlbls, index=tlbls).to_html()
        message += '<p>Accuracy: '+str(accuracy)+'</p>'
        message += '<p>Kappa:\t  '+str(kappa)+'</p>'

        qsave = QtWidgets.QMessageBox.Save
        qokay = QtWidgets.QMessageBox.Ok
        ret = QtWidgets.QMessageBox.information(self.parent, 'Metrics',
                                                message,
                                                buttons=qsave | qokay)
        if ret == qsave:
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                self.parent, 'Save File', '.', 'Excel spreadsheet (*.xlsx)')

            if filename != '':
                df = pd.DataFrame(cmat, columns=tlbls, index=tlbls)
                df.loc['Accuracy'] = np.nan
                df.loc['Accuracy', tlbls[0]] = accuracy
                df.loc['Kappa'] = np.nan
                df.loc['Kappa', tlbls[0]] = kappa

                df.to_excel(filename)


def _testfn():
    """Test."""
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                 '..//..')))
    from pygmi.misc import ProgressBarText
    from pygmi.vector import iodefs
    app = QtWidgets.QApplication(sys.argv)

    piter = ProgressBarText().iter

    ifile = r'd:/Workdata/people/gabby/sandb_2020_clip250m_RF_exc.shp'
    os.chdir(r'd:/Workdata/people/gabby/')

    IS = iodefs.ImportShapeData()
    IS.ifile = ifile
    IS.settings(nodialog=True)
    outdata = IS.outdata

    tmp = Accuracy()
    tmp.indata = outdata
    tmp.settings()


if __name__ == "__main__":

    _testfn()
