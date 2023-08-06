# -----------------------------------------------------------------------------
# Name:        ai_seis.py (part of PyGMI)
#
# Author:      Patrick Cole, Michelle Grobbelaar, Emmanuel Sakala
# E-Mail:      pcole@geoscience.org.za
#
# Copyright:   (c) 2021 Council for Geoscience
# Licence:     Confindential, only for CGS
# -----------------------------------------------------------------------------
"""
AI Seismology Routines.
"""

import sys

import numpy as np
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import fiona
from shapely.geometry import shape, Point, LineString
import pyproj

from geopandas import GeoDataFrame
from sklearn.preprocessing import Binarizer
from sklearn.cluster import DBSCAN
from sklearn.metrics import accuracy_score, DistanceMetric

from PyQt5 import QtWidgets
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT

from numpy import vstack
from torch.utils.data import Dataset, DataLoader, random_split
from torch import Tensor
from torch.nn import Linear, ReLU, Sigmoid, Module, BCELoss
from torch.optim import SGD
from torch.nn.init import kaiming_uniform_, xavier_uniform_

from pygmi.misc import getinfo

register_matplotlib_converters()

LARGE_FONT = ("Verdana", 12)


class MyMplCanvas(FigureCanvasQTAgg):
    """Canvas for the actual plot."""

    def __init__(self, parent=None):
        fig = Figure()
        super().__init__(fig)

        if parent is None:
            self.showprocesslog = print
        else:
            self.showprocesslog = parent.showprocesslog

        # figure stuff
        # self.axes = fig.add_subplot(111)

        self.setParent(parent)

        FigureCanvasQTAgg.setSizePolicy(self,
                                        QtWidgets.QSizePolicy.Expanding,
                                        QtWidgets.QSizePolicy.Expanding)
        FigureCanvasQTAgg.updateGeometry(self)

    def t2_linegraph(self, ifile, efile, title, ylabel, ycol, magmin, magmax):
        """
        Common routine to plot a line graph of X vs earthquakes.

        Parameters
        ----------
        ifile : str
            input filename.
        title : str
            graph title.
        ylabel: str
            y axis label.

        Returns
        -------
        None.

        """
        self.figure.clf()

        headers = ['date', ycol]

        dp = pd.read_excel(ifile, usecols=headers)
        dp['date'] = pd.to_datetime(dp['date'], infer_datetime_format=True)
        dp['year'], dp['month'], dp['day'] = (dp['date'].dt.year,
                                              dp['date'].dt.month,
                                              dp['date'].dt.day)

        headers = ['lat', 'long', 'depth', 'date', 'time', 'mag']
        dm = pd.read_excel(efile, usecols=headers)

        dm = dm[(magmin <= dm.mag) & (dm.mag <= magmax)]
        dm['date'] = pd.to_datetime(dm['date'], infer_datetime_format=True)
        dm['year'], dm['month'], dm['day'] = (dm['date'].dt.year,
                                              dm['date'].dt.month,
                                              dm['date'].dt.day)

        ds = dm.groupby(['year', 'month'])['month'].count().to_frame('count').reset_index()
        ds["date"] = pd.to_datetime(ds['year'].map(str) + ' ' +
                                    ds["month"].map(str), format='%Y/%m')

        ax1 = self.figure.add_subplot(111, label='2D')
        ax1.plot(dp['date'], dp[ycol], color='b', label=ylabel)
        ax2 = ax1.twinx()
        ax2.plot(ds['date'], ds['count'], color='r',  label='Earthquakes')

        ax1.set_title(title)
        ax1.set_xlabel('Date')
        ax1.set_ylabel(ylabel)
        ax2.set_ylabel('Number of Earthquakes')

        h1, l1 = ax1.get_legend_handles_labels()
        h2, l2 = ax2.get_legend_handles_labels()

        ax1.legend(h1+h2, l1+l2, loc=2)
        self.figure.tight_layout()
        self.figure.canvas.draw()


class AI_Seis(QtWidgets.QDialog):
    """AI Sesimology routines."""

    def __init__(self, parent=None):
        super().__init__(parent)
        if parent is None:
            self.showprocesslog = print
        else:
            self.showprocesslog = parent.showprocesslog

        self.parent = parent
        self.indata = {}
        self.outdata = {}

        self.tabs = QtWidgets.QTabWidget()
        self.tab1 = QtWidgets.QWidget()
        self.tab2 = QtWidgets.QWidget()
        self.tab3 = QtWidgets.QWidget()
        self.tab4 = QtWidgets.QWidget()
        self.tab5 = QtWidgets.QWidget()

        # Tab 1
        self.qfile = {}

        # Tab 2
        self.mt2 = MyMplCanvas(self)
        self.t2_combobox1 = QtWidgets.QComboBox()
        self.t2_maxmag = QtWidgets.QDoubleSpinBox()
        self.t2_minmag = QtWidgets.QDoubleSpinBox()
        self.t2_firstrun = True

        # Tab 3
        self.cluster = None
        self.mt3 = MyMplCanvas(self)
        self.t3_rundbscan = QtWidgets.QPushButton('Run DBSCAN')
        self.t3_minnum = QtWidgets.QSpinBox()
        self.t3_eps = QtWidgets.QDoubleSpinBox()

        # Tab 4
        self.mt4 = MyMplCanvas(self)
        self.t4_combobox1 = QtWidgets.QComboBox()
        self.t4_text = QtWidgets.QLabel()

        # Tab 5
        # self.mt5 = MyMplCanvas(self)
        self.t5_distlin = QtWidgets.QDoubleSpinBox()
        self.t5_diststream = QtWidgets.QDoubleSpinBox()
        self.t5_watervolume = QtWidgets.QDoubleSpinBox()
        self.t5_monthlyrain = QtWidgets.QDoubleSpinBox()
        self.t5_latitude = QtWidgets.QDoubleSpinBox()
        self.t5_longitude = QtWidgets.QDoubleSpinBox()
        self.t5_text = QtWidgets.QLabel()
        self.t5_text2 = QtWidgets.QLabel()
        self.t5_result = QtWidgets.QLabel('Result:')
        self.t5_pbar = QtWidgets.QProgressBar()
        self.t5_minmag = 0.

        self.setupui()

    def setupui(self):
        """
        Set up UI.

        Returns
        -------
        None.

        """
        layout = QtWidgets.QVBoxLayout(self)
        self.setWindowTitle(r'AI in Seismology')
        self.resize(640, 480)

        # Initialize tab screen

# Add tabs
        self.tabs.addTab(self.tab1, 'Import Data')
        self.tabs.addTab(self.tab2, 'View Data')
        self.tabs.addTab(self.tab3, 'Cluster Determination')
        self.tabs.addTab(self.tab4, 'Completeness and b-value')
        self.tabs.addTab(self.tab5, 'AI')

        self.tabs.setTabEnabled(1, False)
        self.tabs.setTabEnabled(2, False)
        self.tabs.setTabEnabled(3, False)
        self.tabs.setTabEnabled(4, False)

        # Create first tab
        pb_edata = QtWidgets.QPushButton('Earthquake Data (.xlsx)')
        pb_rain = QtWidgets.QPushButton('Monthly Rainfall Data (.xlsx)')
        pb_lineaments = QtWidgets.QPushButton('Geological Lineament Data '
                                              '(.xlsx)')
        pb_streamflow = QtWidgets.QPushButton('Monthly Stream Flow Data '
                                              '(.xlsx)')
        pb_streamshp = QtWidgets.QPushButton(r'Stream/River Vector Data '
                                             '(.shp)')
        pb_lineamentshp = QtWidgets.QPushButton('Geology Lineament Vector Data'
                                                ' (.shp)')

        self.qfile['edata'] = QtWidgets.QLineEdit('')
        self.qfile['rain'] = QtWidgets.QLineEdit('')
        self.qfile['lineaments'] = QtWidgets.QLineEdit('')
        self.qfile['streamflow'] = QtWidgets.QLineEdit('')
        self.qfile['streamshp'] = QtWidgets.QLineEdit('')
        self.qfile['lineamentshp'] = QtWidgets.QLineEdit('')

        tab1_layout = QtWidgets.QGridLayout(self)

        tab1_layout.addWidget(pb_edata, 0, 0, 1, 1)
        tab1_layout.addWidget(self.qfile['edata'], 0, 1, 1, 1)
        tab1_layout.addWidget(pb_rain, 1, 0, 1, 1)
        tab1_layout.addWidget(self.qfile['rain'], 1, 1, 1, 1)
        tab1_layout.addWidget(pb_lineaments, 2, 0, 1, 1)
        tab1_layout.addWidget(self.qfile['lineaments'], 2, 1, 1, 1)
        tab1_layout.addWidget(pb_streamflow, 3, 0, 1, 1)
        tab1_layout.addWidget(self.qfile['streamflow'], 3, 1, 1, 1)
        tab1_layout.addWidget(pb_streamshp, 4, 0, 1, 1)
        tab1_layout.addWidget(self.qfile['streamshp'], 4, 1, 1, 1)
        tab1_layout.addWidget(pb_lineamentshp, 5, 0, 1, 1)
        tab1_layout.addWidget(self.qfile['lineamentshp'], 5, 1, 1, 1)

        self.tab1.setLayout(tab1_layout)

        pb_edata.clicked.connect(lambda: self.load_data('edata', 'xlsx'))
        pb_rain.clicked.connect(lambda: self.load_data('rain', 'xlsx'))
        pb_lineaments.clicked.connect(lambda: self.load_data('lineaments',
                                                             'xlsx'))
        pb_streamflow.clicked.connect(lambda: self.load_data('streamflow',
                                                             'xlsx'))
        pb_streamshp.clicked.connect(lambda: self.load_data('streamshp',
                                                            'shp'))
        pb_lineamentshp.clicked.connect(lambda: self.load_data('lineamentshp',
                                                               'shp'))

        # Create Second Tab
        mpl_toolbar_t2 = NavigationToolbar2QT(self.mt2, self.parent)
        t2_label1 = QtWidgets.QLabel('Calculation:')
        t2_label2 = QtWidgets.QLabel('Minimum Magnitude:')
        t2_label3 = QtWidgets.QLabel('Maximum Magnitude:')
        self.t2_maxmag.setValue(5.)
        self.t2_minmag.setValue(0.)

        self.t2_combobox1.addItems(['Patterns in Seismicity',
                                    'Correlations with rainfall',
                                    'Correlations with stream flow',
                                    'Correlations with geological lineaments'])

        tab2_layout = QtWidgets.QGridLayout(self)
        tab2_layout.addWidget(self.mt2, 0, 0, 1, 2)
        tab2_layout.addWidget(mpl_toolbar_t2, 1, 0, 1, 2)
        tab2_layout.addWidget(t2_label2, 2, 0, 1, 1)
        tab2_layout.addWidget(self.t2_minmag, 2, 1, 1, 1)
        tab2_layout.addWidget(t2_label3, 3, 0, 1, 1)
        tab2_layout.addWidget(self.t2_maxmag, 3, 1, 1, 1)

        tab2_layout.addWidget(t2_label1, 4, 0, 1, 1)
        tab2_layout.addWidget(self.t2_combobox1, 4, 1, 1, 1)

        self.tab2.setLayout(tab2_layout)

        self.t2_combobox1.currentIndexChanged.connect(self.t2_change_graph)
        self.t2_minmag.valueChanged.connect(self.t2_change_graph)
        self.t2_maxmag.valueChanged.connect(self.t2_change_graph)

        # Create Third Tab
        mpl_toolbar_t3 = NavigationToolbar2QT(self.mt2, self.parent)
        # t3_label1 = QtWidgets.QLabel('Calculation:')
        t3_label2 = QtWidgets.QLabel('Minimum number of events to be used '
                                     'in grouping:')
        # changed to minimum number of events to be used for DBSCAN

        t3_label3 = QtWidgets.QLabel('Maximum distance for two events to be '
                                     'grouped:')
        # changed to maximum distance for two events to be grouped
        self.t3_minnum.setValue(80)
        self.t3_eps.setValue(1.07)

        tab3_layout = QtWidgets.QGridLayout(self)
        tab3_layout.addWidget(t3_label2, 2, 0, 1, 1)
        tab3_layout.addWidget(self.t3_minnum, 2, 1, 1, 1)
        tab3_layout.addWidget(t3_label3, 3, 0, 1, 1)
        tab3_layout.addWidget(self.t3_eps, 3, 1, 1, 1)

        tab3_layout.addWidget(self.t3_rundbscan, 4, 0, 1, 2)

        tab3_layout.addWidget(self.mt3, 5, 0, 1, 2)
        tab3_layout.addWidget(mpl_toolbar_t3, 6, 0, 1, 2)

        self.tab3.setLayout(tab3_layout)

        self.t3_rundbscan.clicked.connect(self.t3_run_dbscan)

        # Create Fourth Tab
        mpl_toolbar_t4 = NavigationToolbar2QT(self.mt4, self.parent)
        t4_label1 = QtWidgets.QLabel('Cluster:')

        text = ('Magnitude of completeness (MC): -\n'
                'Total number of earthquakes: -\n'
                'Annual number of earthquakes greater than MC: -\n'
                'Maximum catalog magnitude: -\n'
                'Mmax = -')
        self.t4_text.setText(text)

        tab4_layout = QtWidgets.QGridLayout(self)
        tab4_layout.addWidget(self.mt4, 0, 0, 1, 2)
        tab4_layout.addWidget(mpl_toolbar_t4, 1, 0, 1, 2)
        tab4_layout.addWidget(t4_label1, 2, 0, 1, 1)
        tab4_layout.addWidget(self.t4_combobox1, 2, 1, 1, 1)
        tab4_layout.addWidget(self.t4_text, 3, 0, 1, 2)

        self.tab4.setLayout(tab4_layout)

        self.t4_combobox1.currentIndexChanged.connect(self.t4_change_graph)

        # Create Fifth Tab
        t5_pushbutton = QtWidgets.QPushButton('Calculate')

        # mpl_toolbar_t5 = NavigationToolbar2QT(self.mt5, self.parent)
        t5_label1 = QtWidgets.QLabel('Distance to closest geological '
                                     'lineament (metres)')
        t5_label2 = QtWidgets.QLabel(r'Distance to closest stream/river '
                                     '(metres)')
        t5_label3 = QtWidgets.QLabel('Water volume of stream flow '
                                     '(cubic metres)')
        t5_label4 = QtWidgets.QLabel('Average monthly rainfall (mm)')
        t5_label5 = QtWidgets.QLabel('Latitude:')
        t5_label6 = QtWidgets.QLabel('Longitude:')

        self.t5_distlin.setMinimum(0.)
        self.t5_diststream.setMinimum(0.)
        self.t5_watervolume.setMinimum(0.)
        self.t5_monthlyrain.setMinimum(0.)
        self.t5_latitude.setMinimum(-90.)
        self.t5_longitude.setMinimum(-180.)

        self.t5_distlin.setMaximum(100000.)
        self.t5_diststream.setMaximum(10000.)
        self.t5_watervolume.setMaximum(10000.)
        self.t5_monthlyrain.setMaximum(10000.)
        self.t5_latitude.setMaximum(90.)
        self.t5_longitude.setMaximum(180.)

        self.t5_distlin.setValue(2000.)
        self.t5_diststream.setValue(2000.)
        self.t5_watervolume.setValue(100.)
        self.t5_monthlyrain.setValue(10.)
        self.t5_latitude.setDecimals(4)
        self.t5_longitude.setDecimals(4)
        self.t5_latitude.setValue(-26.9055)
        self.t5_longitude.setValue(26.7666)

        tab5_layout = QtWidgets.QGridLayout(self)
        # tab5_layout.addWidget(self.mt5, 0, 0, 1, 4)
        # tab5_layout.addWidget(mpl_toolbar_t5, 1, 0, 1, 4)
        tab5_layout.addWidget(t5_label1, 2, 0, 1, 1)
        tab5_layout.addWidget(self.t5_distlin, 2, 1, 1, 1)
        tab5_layout.addWidget(t5_label2, 2, 2, 1, 1)
        tab5_layout.addWidget(self.t5_diststream, 2, 3, 1, 1)
        tab5_layout.addWidget(t5_label3, 3, 0, 1, 1)
        tab5_layout.addWidget(self.t5_watervolume, 3, 1, 1, 1)
        tab5_layout.addWidget(t5_label4, 3, 2, 1, 1)
        tab5_layout.addWidget(self.t5_monthlyrain, 3, 3, 1, 1)
        tab5_layout.addWidget(t5_label5, 6, 0, 1, 1)
        tab5_layout.addWidget(self.t5_latitude, 6, 1, 1, 1)
        tab5_layout.addWidget(t5_label6, 6, 2, 1, 1)
        tab5_layout.addWidget(self.t5_longitude, 6, 3, 1, 1)
        tab5_layout.addWidget(self.t5_text, 7, 0, 1, 4)
        tab5_layout.addWidget(self.t5_text2, 7, 2, 1, 2)
        tab5_layout.addWidget(t5_pushbutton, 8, 0, 1, 4)
        tab5_layout.addWidget(self.t5_result, 9, 0, 1, 4)
        tab5_layout.addWidget(self.t5_pbar, 10, 0, 1, 4)

        self.tab5.setLayout(tab5_layout)

        t5_pushbutton.clicked.connect(self.t5_aicalc)
        self.t5_latitude.valueChanged.connect(self.t5_updatetext)
        self.t5_longitude.valueChanged.connect(self.t5_updatetext)

        # General

        self.tabs.currentChanged.connect(self.change_tab)


# Add tabs to widget
        layout.addWidget(self.tabs)

    def t5_updatetext(self):
        """
        Update text relating to event.

        Returns
        -------
        None.

        """

        latn = self.t5_latitude.value()
        lonn = self.t5_longitude.value()
        locations_A = self.cluster
        locations_new = pd.DataFrame({"lat_new": [latn], "lon_new": [lonn]})

        # add columns with radians for latitude and longitude
        locations_A[['lat_radians_A', 'long_radians_A']] = (
            np.radians(locations_A.loc[:, ['lat', 'long']]))

        locations_new[['lat_radians_B', 'long_radians_B']] = (
            np.radians(locations_new.loc[:, ['lat_new', 'lon_new']]))

        dist = DistanceMetric.get_metric('haversine')
        dist_matrix = (dist.pairwise(
            locations_A[['lat_radians_A', 'long_radians_A']],
            locations_new[['lat_radians_B', 'long_radians_B']])*6371.0)
        # Note that 6371.0 is the radius of the earth in kilometres

        locations_A["distance to new point"] = dist_matrix.flatten()

        close = locations_A[locations_A["distance to new point"] ==
                            locations_A["distance to new point"].min()]
        close = close.iloc[0]

        if close['cluster'].max() == -1:
            minclose = -1
        else:
            minclose = close['cluster'][close['cluster'] > -1].min()

        if minclose == -1:
            minmag = 'outside the clusters'
            minmag2 = close["mag"]
            self.t5_minmag = minmag2
        else:
            dr = self.cluster
            df = dr.loc[dr['cluster'] == minclose]
            df = df['mag'].value_counts().to_frame('count').reset_index()
            minmag = df.loc[0, 'index']
            self.t5_minmag = minmag

        if minclose == -1:
            b_mle = 'outside the clusters'
        else:
            df = dr.loc[dr['cluster'] == minclose]
            magnitudes = df.loc[df.mag > minmag].mag
            min_mag = magnitudes.min()
            b_mle = np.log10(np.exp(1)) / (np.mean(magnitudes) - min_mag)

        text = ('Distance to closest earthquake (metres): '
                f'{close["distance to new point"]:.2f}\n'
                f'Date and time: {close["date"]}\n'
                f'Magnitude: {close["mag"]}')

        text2 = (f'Cluster Number: {close["cluster"]}\n'
                 f'Magnitude of completeness: {minmag}\n'
                 f'b-value of cluster: {b_mle}')

        self.t5_text.setText(text)
        self.t5_text2.setText(text2)

    def load_data(self, datatype, ext):
        """
        Load data.

        Returns
        -------
        None.

        """

        if ext == 'xlsx':
            ext = 'Excel file (*.xlsx)'
        else:
            ext = 'Shape file (*.shp)'

        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
                self.parent, 'Open File', '.', ext)
        if filename == '':
            return

        self.qfile[datatype].setText(filename)

        test = [self.qfile[i].text() for i in self.qfile]

        if '' not in test:
            self.tabs.setTabEnabled(1, True)
            self.tabs.setTabEnabled(2, True)

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
            tmp = self.exec_()

        if tmp != 1:
            return False

        # self.show()
        # QtWidgets.QApplication.processEvents()

        # self.mmc.init_graph()
        return True

    def loadproj(self, projdata):
        """
        Load project data into class.

        Parameters
        ----------
        projdata : dictionary
            Project data loaded from JSON project file.

        Returns
        -------
        chk : bool
            A check to see if settings was successfully run.

        """
        return False

    def saveproj(self):
        """
        Save project data from class.

        Returns
        -------
        projdata : dictionary
            Project data to be saved to JSON project file.

        """
        projdata = {}

        # projdata['ftype'] = '2D Mean'

        return projdata

    def change_tab(self, index):
        """
        Change tab

        Parameters
        ----------
        index : int
            Tab index.

        Returns
        -------
        None.

        """
        if index == 1 and self.t2_firstrun is True:
            self.t2_firstrun = False
            self.t2_change_graph()
        elif index == 3:
            self.t4_change_graph()
        elif index == 4:
            self.t5_updatetext()

    def t2_change_graph(self):
        """
        Change the graph type on tab 2.

        Returns
        -------
        None.

        """
        option = self.t2_combobox1.currentText()
        minmag = self.t2_minmag.value()
        maxmag = self.t2_maxmag.value()
        efile = self.qfile['edata'].text()

        if option == 'Patterns in Seismicity':
            self.mt2.figure.clf()

            headers = ['lat', 'long', 'depth', 'date', 'time', 'mag']
            de = pd.read_excel(efile, usecols=headers)
            de = de[(minmag <= de.mag) & (de.mag <= maxmag)]

            ax = self.mt2.figure.add_subplot(111, projection="3d")
            ax.set_title('Patterns in seismicity')
            ax.set_xlabel('Longitude')
            ax.set_ylabel('Latitude')
            ax.set_zlabel('Magnitude')

            ax.scatter(de['lat'], de['long'], de['mag'], label='Earthquakes')
            ax.legend()
            self.mt2.figure.tight_layout()
            self.mt2.figure.canvas.draw()

        elif option == 'Correlations with geological lineaments':
            self.mt2.figure.clf()

            headers = ['lat', 'long', 'properties']
            degeo = pd.read_excel(self.qfile['lineaments'].text(),
                                  usecols=headers)
            headers = ['lat', 'long', 'depth', 'date', 'time', 'mag']
            de = pd.read_excel(efile, usecols=headers)
            de = de[(minmag <= de.mag) & (de.mag <= maxmag)]

            ax = self.mt2.figure.add_subplot(111, projection="3d",
                                             label='3D')
            ax.set_title('Correlation between seismicity and geological '
                         'structures')
            ax.set_xlabel('Longitude')
            ax.set_ylabel('Latitude')
            ax.set_zlabel('Magnitude')

            ax.scatter(de['lat'], de['long'], de['mag'], label='Earthquakes')
            ax.scatter(degeo['lat'], degeo['long'], label='Lineaments')

            ax.legend()

            self.mt2.figure.tight_layout()
            self.mt2.figure.canvas.draw()

        elif option == 'Correlations with rainfall':
            ifile = self.qfile['rain'].text()
            title = 'Rainfall and number of earthquakes per month'
            ylabel = 'Rainfall'
            ycol = 'rain'

            self.mt2.t2_linegraph(ifile, efile, title, ylabel, ycol,
                                  minmag, maxmag)

        elif option == 'Correlations with stream flow':
            ifile = self.qfile['streamflow'].text()
            title = 'Streamflow and number of earthquakes per month'
            ylabel = 'Volume of water'

            self.mt2.t2_linegraph(ifile, efile, title, ylabel, 'metre',
                                  minmag, maxmag)

    def t3_run_dbscan(self):
        """
        Run DBSCAN and update the graph type on tab 3.

        Returns
        -------
        None.

        """
        # text = self.t3_combobox1.currentText()
        dbs = self.t3_minnum.value()
        epsilon = self.t3_eps.value()

        calc_epsilon = self.t3_eps.value()

        headers = ['lat', 'long', 'depth', 'date', 'time', 'mag']
        df = pd.read_excel(self.qfile['edata'].text(), usecols=headers)

        coords = df[['lat', 'long']].to_numpy()

        coords = df[['lat', 'long']].to_numpy()
        kms_per_radian = 6371.0088

        # obtain this result from step4_plot_epsilon
        epsilon = calc_epsilon / kms_per_radian
        db = DBSCAN(epsilon, min_samples=dbs, algorithm='ball_tree',
                    metric='haversine').fit(np.radians(coords))

        df['cluster'] = db.labels_
        self.cluster = df

        self.mt3.figure.clf()
        ax = self.mt3.figure.add_subplot(122)

        ax.set_title('Clusters identified')
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')

        sc = ax.scatter(df['long'], df['lat'], c=db.labels_, cmap='Paired',
                        marker='.')

        ax1 = self.mt3.figure.add_subplot(121)

        minl = np.unique(db.labels_).min()
        maxl = np.unique(db.labels_).max()
        bins = np.arange(minl-0.5, maxl+1.5)
        N, bins, patches = ax1.hist(db.labels_, log=True, bins=bins)

        for i, patch in enumerate(patches):
            height = patch.get_height()
            patch.set_facecolor(sc.to_rgba(i-1))
            ax1.text(patch.get_x() + patch.get_width()/2, height+0.01,
                     f'{int(N[i])}', ha='center', va='bottom')

        ax1.set_title('Cluster Population')
        ax1.set_xlabel('Cluster (where -1 is Noise)')
        ax1.set_ylabel('Count')

        self.mt3.figure.tight_layout()
        self.mt3.figure.canvas.draw()

        # Activate Tab 4 and fill its combobox
        self.tabs.setTabEnabled(3, True)
        dr = self.cluster
        clist = np.unique(dr['cluster'])
        clist = clist[clist >= 0]

        options = ['All Data']
        for i in clist:
            options.append('Cluster '+str(i))

        self.t4_combobox1.disconnect()
        self.t4_combobox1.addItems(options)
        self.t4_combobox1.currentIndexChanged.connect(self.t4_change_graph)

    def t4_change_graph(self):
        """
        Change the graph on tab 4.

        Returns
        -------
        None.

        """

        dr = self.cluster
        option = self.t4_combobox1.currentText()

        self.mt4.figure.clf()
        ax1 = self.mt4.figure.add_subplot(121)
        ax1.set_title('Number of earthquakes per magnitude')
        ax1.set_xlabel('Magnitude')
        ax1.set_ylabel('Number of earthquakes')

        if option == "All Data":
            df = dr['mag'].value_counts().to_frame('count').reset_index()
            mag = df['index'].iloc[0]

            ax1.scatter(x=df['index'], y=df['count'], color='red')
            ax1.set_title('Number of earthquakes per magnitude for dataset')
        else:
            cnum = int(option.split()[1])

            df = dr.loc[dr['cluster'] == cnum]
            df = df['mag'].value_counts().to_frame('count').reset_index()
            mag = df['index'].iloc[0]

            ax1.scatter(x=df['index'], y=df['count'], color='blue')
            ax1.set_title('Number of earthquakes per magnitude for cluster '
                          f'{cnum}')

        # b-value calculations
        if option == "All Data":
            df = dr
        else:
            df = dr.loc[dr['cluster'] == cnum]

        df = df[df['mag'] >= mag]

        magnitudes = df['mag']
        years = df['date'].dt.year
        # This should be the magnitude of completeness from the script
        min_mag = min(magnitudes)
        max_mag = max(magnitudes) + 0.1

        num_eq = len(magnitudes)

        num_years = max(years)-min(years)
        annual_num_eq = num_eq/num_years

        max_mag_bin = max(magnitudes) + 0.15

        # Magnitude bins
        bins = np.arange(min_mag, max_mag_bin, 0.05)
        # Magnitude bins for plotting - we will re-arrange bins later
        plot_bins = np.arange(min_mag, max_mag, 0.05)

        # #####################################################################
        # Generate distribution
        # #####################################################################
        # Generate histogram
        hist = np.histogram(magnitudes, bins=bins)

        # # Reverse array order
        hist = hist[0][::-1]
        bins = bins[::-1]

        # Calculate cumulative sum
        cum_hist = hist.cumsum()
        # Ensure bins have the same length has the cumulative histogram.
        # Remove the upper bound for the highest interval.
        bins = bins[1:]

        # Get annual rate
        cum_annual_rate = cum_hist/num_years

        new_cum_annual_rate = []
        for i in cum_annual_rate:
            new_cum_annual_rate.append(i+1e-20)

        # Take logarithm
        log_cum_sum = np.log10(new_cum_annual_rate)

        # #####################################################################
        # Fit a and b parameters using a varity of methods
        # #####################################################################

        # Fit a least squares curve
        b, a = np.polyfit(bins, log_cum_sum, 1)

        # alpha = np.log(10) * a
        beta = -1.0 * np.log(10) * b
        # Maximum Likelihood Estimator fitting
        # b value
        b_mle = np.log10(np.exp(1)) / (np.mean(magnitudes) - min_mag)
        beta_mle = np.log(10) * b_mle

        # #####################################################################
        # Generate data to plot results
        # #####################################################################
        # Generate data to plot least squares linear curve
        # Calculate y-intercept for least squares solution
        yintercept = log_cum_sum[-1] - b * min_mag
        ls_fit = b * plot_bins + yintercept
        log_ls_fit = []
        for value in ls_fit:
            log_ls_fit.append(np.power(10, value))
        # Generate data to plot bounded Gutenberg-Richter for LS solution
        numer = (np.exp(-1. * beta * (plot_bins - min_mag)) -
                 np.exp(-1. * beta * (max_mag - min_mag)))
        denom = 1. - np.exp(-1. * beta * (max_mag - min_mag))
        ls_bounded = annual_num_eq * (numer / denom)

        # Generate data to plot maximum likelihood linear curve
        mle_fit = (-1.0 * b_mle * plot_bins + 1.0 * b_mle * min_mag +
                   np.log10(annual_num_eq))
        log_mle_fit = []
        for value in mle_fit:
            log_mle_fit.append(np.power(10, value))
        # Generate data to plot bounded Gutenberg-Richter for MLE solution
        numer = (np.exp(-1. * beta_mle * (plot_bins - min_mag)) -
                 np.exp(-1. * beta_mle * (max_mag - min_mag)))
        denom = 1. - np.exp(-1. * beta_mle * (max_mag - min_mag))
        mle_bounded = annual_num_eq * (numer / denom)
        # Compare b-value of 1
        fit_data = -1.0 * plot_bins + min_mag + np.log10(annual_num_eq)
        log_fit_data = []
        for value in fit_data:
            log_fit_data.append(np.power(10, value))
        # #####################################################################
        # Plot the results
        # #####################################################################

        ax = self.mt4.figure.add_subplot(122)

        ax.scatter(bins, new_cum_annual_rate, label='Catalogue')
        ax.plot(plot_bins, log_ls_fit, c='r', label='Least Squares')
        ax.plot(plot_bins, ls_bounded, c='r', linestyle='--',
                label='Least Squares Bounded')
        ax.plot(plot_bins, log_mle_fit, c='g', label='Maximum Likelihood')
        ax.plot(plot_bins, mle_bounded, c='g', linestyle='--',
                label='Maximum Likelihood Bounded')
        ax.plot(plot_bins, log_fit_data, c='b', label='b = 1')

        ax.set_yscale('log')
        ax.legend()
        ax.set_ylim([min(new_cum_annual_rate) * 0.1,
                     max(new_cum_annual_rate) * 10.])
        ax.set_xlim([min_mag - 0.5, max_mag + 0.5])
        ax.set_ylabel('Annual probability')
        ax.set_xlabel('Magnitude')
        ax.set_title('B-value for the data')

        self.mt4.figure.tight_layout()
        self.mt4.figure.canvas.draw()

        text = (f'Magnitude of completeness (MC): {min_mag}\n'
                f'Total number of earthquakes: {num_eq}\n'
                'Annual number of earthquakes greater than MC '
                f'{annual_num_eq}\n'
                f'Maximum catalog magnitude: {max(magnitudes)}\n'
                f'Mmax = {max_mag}\n'
                f'Least Squares: b value {-b}\n'
                f'Least Squares: a value {a}\n'
                f'Maximum Likelihood: b value {b_mle}')
        self.t4_text.setText(text)

        self.tabs.setTabEnabled(4, True)

    def t5_aicalc(self):
        """
        AI Calculation.

        Returns
        -------
        None.

        """
        cut_off_MG = self.t5_minmag
        self.t5_pbar.setMaximum(100)
        self.t5_pbar.setValue(0)

        # ###################### Merge files ##################################

        # self.t5_pbar.setMaximum(100)
        # self.t5_pbar.setValue(10)

        in_rain = self.qfile['rain'].text()
        in_stream = self.qfile['streamflow'].text()
        in_earth = self.qfile['edata'].text()
        stream_file = self.qfile['streamshp'].text()
        lineament_file = self.qfile['lineamentshp'].text()

        # my_dict = {'Rainfall': [self.t5_monthlyrain.value()],
        #            'Stream_flow': [self.t5_watervolume.value()],
        #            'Dis_lineament': [self.t5_distlin.value()],
        #            'Dis_Stream': [self.t5_diststream.value()]}
        # f_pred = pd.DataFrame(my_dict)

        f1 = pd.read_excel(in_rain)
        f2 = pd.read_excel(in_stream)

        file_out_var = pd.merge(f1, f2, on='date')
        # #############Convert datetime to date and time ######################

        headers = ['lat', 'long', 'depth', 'date', 'time', 'mag']
        df_mg = pd.read_excel(in_earth, usecols=headers)

        # ################Seting the lowest cutoff ############################

        df_mg['date'] = pd.to_datetime(df_mg['date'],
                                       infer_datetime_format=True)

        # calculate unix datetime
        df = pd.DataFrame(((df_mg["date"] - pd.Timestamp("1970-01-01")) //
                           pd.Timedelta('1s')).to_frame('timestamp').reset_index())

        # ds = df_mg.merge(df, left_index=True, right_index = True)

        points = [Point(row['long'], row['lat'])
                  for key, row in df_mg.iterrows()]

        geo_df = GeoDataFrame(df_mg, geometry=points)

        self.t5_pbar.setValue(25)

        # #####################################################################
        # Stream File
        output_stream_var = get_distances(stream_file, geo_df, df_mg,
                                          "Dis_Stream")

        self.t5_pbar.setValue(50)
        # #####################################################################
        # Lineament File
        output_line_var = get_distances(lineament_file, geo_df, df_mg,
                                        "Dis_lineament")

        self.t5_pbar.setValue(75)

        # #####################################################################
        # Merge lineaments and stream distances
        out_line_stream_var = pd.merge(output_stream_var,
                                       output_line_var,
                                       how='left', on=['long', 'lat'])

        ds = out_line_stream_var.merge(df, left_index=True, right_index=True)
        # #####################################################################

        df1 = out_line_stream_var
        df2 = file_out_var

        df1['Date'] = pd.to_datetime(df1['date_x'])
        df2['Date'] = pd.to_datetime(df2['date'])

        lefton = df1['Date'].apply(lambda x: (x.year, x.month))
        righton = df2['Date'].apply(lambda y: (y.year, y.month))

        df4 = pd.merge(df1, df2, left_on=lefton, right_on=righton, how='outer')

        # #####################################################################
        ds = df4.merge(df, left_index=True, right_index=True)

        path = pd.DataFrame(ds[['long', 'lat', 'depth_x', 'rain', 'metre',
                                'Dis_lineament', 'Dis_Stream', 'timestamp',
                                'mag_x']])

        train_dl, test_dl = prepare_data(path, cut_off_MG)

        # define the network
        model = MLP(8)

        # train the model
        train_model(train_dl, model, self.t5_pbar)

        # evaluate the model
        acc = evaluate_model(test_dl, model)

        # make a single prediction (expect class=1)

        # Dis_lineament = self.t5_distlin.value()
        # Dis_Stream = self.t5_diststream.value()
        # metre = self.t5_watervolume.value()
        # rain = self.t5_monthlyrain.value()
        # lat = self.t5_latitude.value()
        # long = self.t5_longitude.value()
        # depth_x = 2.0
        # timestamp = round(time.time())

        # row = [long, lat, depth_x, rain, metre, Dis_lineament, Dis_Stream,
        #        timestamp]

        # yhat = predict(row, model)

        x = (f'For these given parameters there is a {acc*100:.3f} % chance of'
             f' an earthquake with magnitude  greater than {cut_off_MG}')

        # breakpoint()

        self.t5_result.setText(x)


class CSVDataset(Dataset):
    """Dataset definition."""

    def __init__(self, path, thres):
        # load the dataset
        # load the csv file as a dataframe
        df = path
        # store the inputs and outputs
        self.X = df.values[1:, :8]
        # df = df.iloc[1: , :]
        self.y = df.values[1:, 8]
        # ensure input data is floats
        self.X = self.X.astype('float32')

        # binary classification
        self.y = self.y.astype('float32')
        self.y = self.y.reshape(-1, 1)

        self.y = Binarizer(threshold=thres).transform(self.y)

    # number of rows in the dataset
    def __len__(self):
        return len(self.X)

    # get a row at an index
    def __getitem__(self, idx):
        return [self.X[idx], self.y[idx]]

    # get indexes for train and test rows
    def get_splits(self, n_test=0.25):
        # determine sizes
        test_size = round(n_test * len(self.X))
        train_size = len(self.X) - test_size
        # calculate the split
        return random_split(self, [train_size, test_size])


class MLP(Module):
    """Model definition - binary."""

    def __init__(self, n_inputs):
        super(MLP, self).__init__()
        # define model elements
        # input to first hidden layer
        self.hidden1 = Linear(n_inputs, 15)
        kaiming_uniform_(self.hidden1.weight, nonlinearity='relu')
        self.act1 = ReLU()
        # second hidden layer
        self.hidden2 = Linear(15, 10)
        kaiming_uniform_(self.hidden2.weight, nonlinearity='relu')
        self.act2 = ReLU()
        self.hidden5 = Linear(10, 8)
        kaiming_uniform_(self.hidden5.weight, nonlinearity='relu')
        self.act5 = ReLU()
        self.hidden3 = Linear(8, 4)
        kaiming_uniform_(self.hidden3.weight, nonlinearity='relu')
        self.act3 = ReLU()
        # third hidden layer and output
        self.hidden4 = Linear(4, 1)
        xavier_uniform_(self.hidden4.weight)
        self.act4 = Sigmoid()

    def forward(self, X):
        """Forward propagate input."""
        # input to first hidden layer
        X = self.hidden1(X)
        X = self.act1(X)
        # second hidden layer
        X = self.hidden2(X)
        X = self.act2(X)
        X = self.hidden5(X)
        X = self.act5(X)
        X = self.hidden3(X)
        X = self.act3(X)
        # third hidden layer and output
        X = self.hidden4(X)
        X = self.act4(X)
        return X


def prepare_data(path, thres):
    """Prepare the dataset."""
    # load the dataset
    dataset = CSVDataset(path, thres)
    # calculate split
    train, test = dataset.get_splits()
    # prepare data loaders
    train_dl = DataLoader(train, batch_size=50, shuffle=True)
    test_dl = DataLoader(test, batch_size=32, shuffle=False)
    return train_dl, test_dl


def train_model(train_dl, model, pbar):
    """Train the model - binary."""
    # define the optimization
    criterion = BCELoss()
    optimizer = SGD(model.parameters(), lr=0.01, momentum=0.9)

    pbar.setMinimum(0)
    pbar.setMaximum(500)
    pbar.setValue(0)
    # enumerate epochs

    old_loss = 0

    for epoch in range(500):

        # total = 0
        # correct = 0
        running_loss = 0

        # enumerate mini batches
        for i, (inputs, targets) in enumerate(train_dl):
            # clear the gradients
            optimizer.zero_grad()
            # compute the model output
            yhat = model(inputs)
            # calculate loss
            loss = criterion(yhat, targets)
            # credit assignment
            loss.backward()
            # update model weights
            optimizer.step()

            running_loss += loss.item()

        diff = abs(running_loss-old_loss)

        if diff < 0.000001:
            break

        old_loss = running_loss

        print(epoch, 'loss:', running_loss/(i+1))
        # breakpoint()

    pbar.setValue(500)


def evaluate_model(test_dl, model):
    """Evaluate the model - binary."""
    predictions = []
    actuals = []
    for i, (inputs, targets) in enumerate(test_dl):
        # evaluate the model on the test set
        yhat = model(inputs)
        # retrieve numpy array
        yhat = yhat.detach().numpy()
        actual = targets.numpy()
        actual = actual.reshape((len(actual), 1))
        # round to class values
        yhat = yhat.round()
        # store
        predictions.append(yhat)
        actuals.append(actual)
    predictions, actuals = vstack(predictions), vstack(actuals)

    # calculate accuracy
    acc = accuracy_score(actuals, predictions)
    return acc


def predict(row, model):
    """Make a class prediction for one row of data."""
    # convert row to data
    row = Tensor([row])
    # make prediction
    yhat = model(row)
    # retrieve numpy array
    yhat = yhat.detach().numpy()
    return yhat


def get_distances(ifile, geo_df, df_mg, lbl):
    """
    Get distances between dataframes.

    Parameters
    ----------
    ifile : str
        File of lines.
    geo_df : GeoDataFrame
        Dataframe of points.

    Returns
    -------
    pd1 : DataFrame
        Output distances.

    """
    transformer = pyproj.Transformer.from_crs("epsg:4326", "epsg:32735",
                                              always_xy=True)
    line = fiona.open(ifile)

    points = [(feat.xy[0][0], feat.xy[1][0]) for feat in geo_df.geometry]

    lines = [zip(shape(feat["geometry"]).coords.xy[0],
                 shape(feat["geometry"]).coords.xy[1])
             for feat in line]

    proj_lines = [[] for i in range(len(lines))]
    for i, item in enumerate(lines):
        for element in item:
            x = element[0]
            y = element[1]
            # x, y = pyproj.transform(srcProj, dstProj, x, y)
            x, y = transformer.transform(x, y)
            proj_lines[i].append((x, y))

    proj_points = []
    for point in points:
        x = point[0]
        y = point[1]
        # x, y = pyproj.transform(srcProj, dstProj, x, y)
        x, y = transformer.transform(x, y)
        proj_points.append(Point(x, y))

    distances = [[] for i in range(len(lines))]

    for i, line in enumerate(proj_lines):
        for point in proj_points:
            distances[i].append(LineString(line).distance(point))

    file1 = pd.DataFrame(min(distances))
    file2 = pd.DataFrame(points)

    results1 = pd.concat([file2, file1], axis=1)
    results1.columns = ["long", "lat", lbl]

    pd1 = pd.merge(results1, df_mg, how='left', on=['long', 'lat'])
    pd1['mag'].replace('', np.nan, inplace=True)
    pd1.dropna(subset=['mag'], inplace=True)

    return pd1


def _testfn():
    """Test routine."""

    app = QtWidgets.QApplication(sys.argv)  # Necessary to test Qt Classes

    tmp = AI_Seis(None)

    tmp.qfile['edata'].setText(r'd:\Work\Programming\AI\AI_SEIS\data\1_earthquake_data.xlsx')
    tmp.qfile['rain'].setText(r'd:\Work\Programming\AI\AI_SEIS\data\2_monthly_rainfall_data.xlsx')
    tmp.qfile['lineaments'].setText(r'd:\Work\Programming\AI\AI_SEIS\data\3_geological_lineament_data.xlsx')
    tmp.qfile['streamflow'].setText(r'd:\Work\Programming\AI\AI_SEIS\data\4_monthly_stream_flow_data.xlsx')
    tmp.qfile['streamshp'].setText(r'd:\Work\Programming\AI\AI_SEIS\data\Vaal_River.shp')
    tmp.qfile['lineamentshp'].setText(r'd:\Work\Programming\AI\AI_SEIS\data\geo_lineament.shp')

    # tmp.qfile['edata'].setText(r'C:\Users\michelle\AppData\Local\Programs\Python\Python37\AI_SEIS\ai_seis\clean_earthquake_data.xlsx')
    # tmp.qfile['rain'].setText(r'C:\Users\michelle\AppData\Local\Programs\Python\Python37\AI_SEIS\ai_seis\rain_input_date.xlsx')
    # tmp.qfile['lineaments'].setText(r'C:\Users\michelle\AppData\Local\Programs\Python\Python37\AI_SEIS\ai_seis\Lineament_input.xlsx')
    # tmp.qfile['streamflow'].setText(r'C:\Users\michelle\AppData\Local\Programs\Python\Python37\AI_SEIS\ai_seis\stream_2013_2018_month.xlsx')
    # tmp.qfile['streamshp'].setText(r'C:\Users\michelle\AppData\Local\Programs\Python\Python37\AI_SEIS\ai_seis\Vaal_River.shp')
    # tmp.qfile['lineamentshp'].setText(r'C:\Users\michelle\AppData\Local\Programs\Python\Python37\AI_SEIS\ai_seis\geo_lineament.shp')
    tmp.tabs.setTabEnabled(1, True)
    tmp.tabs.setTabEnabled(2, True)

    tmp.settings()


if __name__ == "__main__":
    _testfn()
