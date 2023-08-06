# -----------------------------------------------------------------------------
# Name:        monitoring.py (part of PyGMI)
#
# Author:      Patrick Cole, Emmanuel Sakala, Gabrielle Janse van Rensburg
# E-Mail:      pcole@geoscience.org.za
#
# Copyright:   (c) 2021 Council for Geoscience
# Licence:     Confidential, only for CGS.
# -----------------------------------------------------------------------------
"""AI Dolomite Routines."""

from PyQt5 import QtWidgets, QtCore
import numpy as np
import pandas as pd

from scipy.interpolate import griddata
import rasterio
import rasterio.mask
import rasterio.shutil
from rasterio.io import MemoryFile
from shapely.geometry import box
from pygmi.misc import ProgressBarText
from rasterio.windows import Window
import pygmi.menu_default as menu_default
from pygmi.raster import datatypes
from pandas.plotting import register_matplotlib_converters
import shapefile as shp
from osgeo import gdal
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT
from shapely.geometry import Polygon
import geopandas as gpd

from pygmi.misc import frm

register_matplotlib_converters()
gdal.UseExceptions()

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

        self.axes = fig.add_subplot(111)

        self.setParent(parent)

        FigureCanvasQTAgg.setSizePolicy(self,
                                        QtWidgets.QSizePolicy.Expanding,
                                        QtWidgets.QSizePolicy.Expanding)
        FigureCanvasQTAgg.updateGeometry(self)

    def t3_raster(self, ifile, ifile1):
        """
        Common routine to plot raster data.

        Parameters
        ----------
        ifile : str
            input filename.

        Returns
        -------
        None.
        """
        sar_img = rasterio.open(ifile)
        img = sar_img.read(1)
        img[img == 0] = sar_img.nodata
        img[img == sar_img.nodata] = np.nan

        """
        with fiona.open(ifile1, "r") as shapefile:
            shapes = [feature["geometry"] for feature in shapefile]

        with rasterio.open(ifile) as src:
            out_image, out_transform = rasterio.mask.mask(src, shapes,
                                                          crop=True)
            out_meta = src.meta

        out_meta.update({"driver": "GTiff",
                         "height": out_image.shape[1],
                         "width": out_image.shape[2],
                         "transform": out_transform})

        with rasterio.open("Test.tif", "w", **out_meta) as dest:
            dest.write(out_image)
        """

        self.figure.clf()
        self.axes = self.figure.add_subplot(111, label='map')
        self.axes.ticklabel_format(style='plain')
        self.axes.tick_params(axis='x', rotation=90)
        self.axes.tick_params(axis='y', rotation=0)

        test = self.axes.imshow(img, cmap='viridis')

        self.figure.colorbar(test)

        # self.axes.imshow(out_image[0], cmap='viridis')

        self.axes.xaxis.set_major_formatter(frm)
        self.axes.yaxis.set_major_formatter(frm)

        self.figure.tight_layout()
        self.figure.canvas.draw()

    def t3_vector(self, ifile1, ifile2):
        """Plot the vector data."""
        shp_read = shp.Reader(ifile1)

        self.figure.clf()
        self.axes = self.figure.add_subplot(111, label='map')
        self.axes.ticklabel_format(style='plain')
        self.axes.tick_params(axis='x', rotation=90)
        self.axes.tick_params(axis='y', rotation=0)

        for shape in shp_read.shapeRecords():
            x = [i[0] for i in shape.shape.points[:]]
            y = [i[1] for i in shape.shape.points[:]]
            self.axes.plot(x, y)

        # shp_read2 = shp.Reader(ifile2) # Shapefile doesn't read .pix

        # for shape in shp_read2.shapeRecords():
            # x = [i[0] for i in shape.shape.points[:]]
            # y = [i[1] for i in shape.shape.points[:]]
            # self.axes.plot(x, y)

        self.axes.xaxis.set_major_formatter(frm)
        self.axes.yaxis.set_major_formatter(frm)

        self.figure.tight_layout()
        self.figure.canvas.draw()

    def t4_bhole_class(self, class_img):
        """Plot borehole class data."""
        self.figure.clf()
        self.axes = self.figure.add_subplot(111, label='map')
        self.axes.ticklabel_format(style='plain')
        self.axes.tick_params(axis='x', rotation=90)

        test = self.axes.imshow(class_img)

        self.figure.colorbar(test)

        self.axes.xaxis.set_major_formatter(frm)
        self.axes.yaxis.set_major_formatter(frm)

        self.figure.tight_layout()
        self.figure.canvas.draw()


class Monitoring(QtWidgets.QDialog):
    """
    Early Warning System Monitoring Module.

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
        else:
            self.showprocesslog = parent.showprocesslog

        self.indata = {}
        self.outdata = {}
        self.parent = parent

        if parent is not None:
            self.piter = parent.pbar.iter
        else:
            self.piter = ProgressBarText().iter

        self.tabs = QtWidgets.QTabWidget()
        self.tab1 = QtWidgets.QWidget()
        self.tab2 = QtWidgets.QWidget()
        self.tab3 = QtWidgets.QWidget()
        self.tab4 = QtWidgets.QWidget()

        # Tab 1
        self.qfile = {}

        # Tab 2
        self.tablewidget = QtWidgets.QTableWidget()
        self.param_ratio = {}
        self.param_threshold = {}

        # Tab 3
        self.mt3 = MyMplCanvas(self)
        self.t3_combobox1 = QtWidgets.QComboBox()
        self.t3_run = True
        self.t3_calculate = QtWidgets.QPushButton('Calculate')
        self.myarray_bh = None
        self.trans_bh = None
        self.out_meta = {}
        self.data = datatypes.Data()

        # Tab 4
        self.mt4 = MyMplCanvas(self)
        self.bhole_rank = []
        self.final_result = []
        self.ofile = ''
        self.t4_export = QtWidgets.QPushButton('Export')

        self.setupui()

    def setupui(self):
        """
        Set up UI.

        Returns
        -------
        None.

        """
        # Initialize tab screen

        layout = QtWidgets.QVBoxLayout(self)
        self.setWindowTitle(r'Monitoring Window')
        self.resize(640, 480)

        # Initialize tab screen

# Add tabs
        self.tabs.addTab(self.tab1, 'Import Data')
        self.tabs.addTab(self.tab2, 'Parameters')
        self.tabs.addTab(self.tab3, 'Early Warning Calculation')
        self.tabs.addTab(self.tab4, 'Results')

        self.tabs.setTabEnabled(1, False)
        self.tabs.setTabEnabled(2, False)
        self.tabs.setTabEnabled(3, False)

        # Create first tab
        area_shp = QtWidgets.QPushButton('Area Vector Data (.shp)')
        stab_shp = QtWidgets.QPushButton('Stability Points Vector Data (.shp,'
                                         ' .pix)')
        insar = QtWidgets.QPushButton('InSAR Raster Data (.tif)')
        bhole = QtWidgets.QPushButton('Borehole Data (.csv)')

        self.qfile['area_shp'] = QtWidgets.QLineEdit('')
        self.qfile['stab_shp'] = QtWidgets.QLineEdit('')
        self.qfile['insar'] = QtWidgets.QLineEdit('')
        self.qfile['bhole'] = QtWidgets.QLineEdit('')

        tab1_layout = QtWidgets.QGridLayout()

        tab1_layout.addWidget(area_shp, 0, 0, 1, 1)
        tab1_layout.addWidget(self.qfile['area_shp'], 0, 1, 1, 1)
        tab1_layout.addWidget(stab_shp, 1, 0, 1, 1)
        tab1_layout.addWidget(self.qfile['stab_shp'], 1, 1, 1, 1)
        tab1_layout.addWidget(insar, 2, 0, 1, 1)
        tab1_layout.addWidget(self.qfile['insar'], 2, 1, 1, 1)
        tab1_layout.addWidget(bhole, 3, 0, 1, 1)
        tab1_layout.addWidget(self.qfile['bhole'], 3, 1, 1, 1)

        self.tab1.setLayout(tab1_layout)

        area_shp.clicked.connect(lambda: self.load_data('area_shp', 'shp'))
        stab_shp.clicked.connect(lambda: self.load_data('stab_shp', 'shp'))
        insar.clicked.connect(lambda: self.load_data('insar', 'tif'))
        bhole.clicked.connect(lambda: self.load_data('bhole', 'csv'))

        # Create Second Tab
        tab2_layout = QtWidgets.QGridLayout()
        # buttonbox = QtWidgets.QDialogButtonBox()
        helpdocs = menu_default.HelpButton('pygmi.rsense.pfeat')
        lbl_set_params = QtWidgets.QLabel('Please set the parameters:')

        table_group = self.tablewidget
        table_group.setRowCount(26)
        table_group.setColumnCount(2)
        table_group.setHorizontalHeaderLabels(['Ratio', 'Threshold'])
        table_group.resizeColumnsToContents()
        self.t2_set_threshold()

        tab2_layout.addWidget(lbl_set_params, 0, 0, 1, 1)
        tab2_layout.addWidget(table_group, 2, 0, 1, 1)
        tab2_layout.addWidget(helpdocs, 4, 0, 1, 1)

        self.tab2.setLayout(tab2_layout)

        # Create Third Tab
        mpl_toolbar_t3 = NavigationToolbar2QT(self.mt3, self.parent)
        t3_label1 = QtWidgets.QLabel('Early Warning System Monitoring Module'
                                     ' Calculation')
        t3_label2 = QtWidgets.QLabel('The InSAR data is combined with the '
                                     'borehole sinkhole hazard classification '
                                     'results')
        t3_label3 = QtWidgets.QLabel('View Data:')
        t3_label4 = QtWidgets.QLabel('Proceed with the calculation:')

        self.t3_combobox1.addItems(['Select:', 'Location Data',
                                    'InSAR Data'])

        tab3_layout = QtWidgets.QGridLayout()
        tab3_layout.addWidget(t3_label1, 0, 0, 1, 4)
        tab3_layout.addWidget(t3_label2, 1, 0, 1, 4)
        tab3_layout.addWidget(t3_label3, 4, 0, 1, 1)
        tab3_layout.addWidget(self.t3_combobox1, 4, 1, 1, 1)
        tab3_layout.addWidget(self.mt3, 5, 1, 2, 2)
        tab3_layout.addWidget(t3_label4, 8, 0, 1, 1)
        tab3_layout.addWidget(self.t3_calculate, 8, 1, 1, 1)

        self.t3_combobox1.currentIndexChanged.connect(self.t3_change_graph)

        self.tab3.setLayout(tab3_layout)

        self.t3_calculate.clicked.connect(self.eng_proc)

        # Create Fourth Tab
        t4_label1 = QtWidgets.QLabel('Classified image:')

        tab4_layout = QtWidgets.QGridLayout()
        tab4_layout.addWidget(t4_label1, 0, 0, 1, 1)
        tab4_layout.addWidget(self.mt4, 1, 1, 2, 2)
        tab4_layout.addWidget(self.t4_export, 6, 2, 1, 1)

        self.t4_export.clicked.connect(self.export_raster)

        self.tab4.setLayout(tab4_layout)

# Add tabs to widget
        layout.addWidget(self.tabs)

    def load_data(self, datatype, ext):
        """
        Load data.

        Returns
        -------
        None.

        """
        # ext = 'Shapefile (*.shp);;' + 'All Files (*.*)'
        if ext == 'csv':
            ext = 'CSV file (*.csv)'
        elif ext == 'tif':
            ext = 'GeoTiff file (*.tif)'
        elif ext == 'pix':
            ext = 'Geomatica file (*.pix)'
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

    def t2_set_threshold(self):
        """Set threshold."""
        self.param_ratio = {'Fill': 1,
                            'Tr - gvl': 1,
                            'Tr - sa': 1,
                            'Tr - si': 0.3,
                            'Tr - cl': 0.2,
                            'Pedo': 0.1,
                            'Res dol - gvl': 0.8,
                            'Res dol - wad': 1,
                            'Res dol - sa': 0.7,
                            'Res dol - si': 0.7,
                            'Res dol - cl': 0.6,
                            'Res chert - gvl': 0.8,
                            'Res chert - sa': 0.8,
                            'Res chert - si': 0.7,
                            'Res chert - cl': 0.7,
                            'Res intru - gvl': 0.5,
                            'Res intru - sa': 0.5,
                            'Res intru - si': 0.3,
                            'Res intru - cl': 0.3,
                            'Res Karoo - gvl': 0.5,
                            'Res Karoo - sa': 0.5,
                            'Res Karoo - si': 0.3,
                            'Res Karoo - cl': 0.3,
                            'Weathered - dol': 0.01,
                            'Weathered - intru': 0.01,
                            'Cavity': 1}

        for name in self.param_ratio:
            item = QtWidgets.QTableWidgetItem(name)
            key_list = list(self.param_ratio)
            row = key_list.index(name)
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
            self.tablewidget.setItem(row, 0, item)

        for name in self.param_ratio:
            item2 = QtWidgets.QTableWidgetItem(str(self.param_ratio[name]))
            key_list = list(self.param_ratio)
            row = key_list.index(name)
            self.tablewidget.setItem(row, 1, item2)

        self.tablewidget.resizeColumnsToContents()

    def t3_change_graph(self):
        """
        Change the graph type on tab 3.

        Returns
        -------
        None.

        """
        option = self.t3_combobox1.currentText()

        if option == 'Location Data':
            self.mt3.figure.clf()
            ifile1 = self.qfile['area_shp'].text()
            ifile2 = self.qfile['stab_shp'].text()

            self.mt3.t3_vector(ifile1, ifile2)

        elif option == 'InSAR Data':
            ifile = self.qfile['insar'].text()
            ifile1 = self.qfile['area_shp'].text()

            self.mt3.t3_raster(ifile, ifile1)

    def export_raster(self):
        """Export raster."""
        # out_location = self.ofile

        # out_location, _ = QtWidgets.QFileDialog.getOpenFileName(
        #         self.parent, 'Open File', '.')
        # if out_location == '':
        #     return

        file_location = self.qfile['insar'].text()
        file_string = file_location[:-4]
        ofile = file_string + '_class.tif'

        with rasterio.open(ofile, 'w', **self.out_meta) as dest:
            dest.write(self.final_result, 1)

        self.showprocesslog(r'Export Complete to ' + ofile)

    def mask_raster_with_geometry(self, raster, transform, shapes, **kwargs):
        """Wrapper for rasterio.mask.mask to allow for in-memory processing.
        by https://gis.stackexchange.com/users/177672/luna

        Docs: https://rasterio.readthedocs.io/en/latest/api/rasterio.mask.html

        Args:
            raster (numpy.ndarray): raster to be masked with dim: [H, W]
            transform (affine.Affine): the transform of the raster
            shapes, **kwargs: passed to rasterio.mask.mask

        Returns:
            masked: numpy.ndarray or numpy.ma.MaskedArray with dim: [H, W]
        """
        with rasterio.io.MemoryFile() as memfile:
            with memfile.open(
                driver='GTiff',
                height=raster.shape[0],
                width=raster.shape[1],
                count=1,
                dtype=raster.dtype,
                transform=transform,
            ) as dataset:
                dataset.write(raster, 1)
            with memfile.open() as dataset:
                output, outtrans = rasterio.mask.mask(dataset, shapes,
                                                      **kwargs)
        return output.squeeze(0), outtrans

    def repose(self, layer_number, df, Ly1):
        """
        Parameters
        ----------
        layer_number : TYPE
            DESCRIPTION.
        df : TYPE
            DESCRIPTION.
        Ly1 : TYPE
            DESCRIPTION.

        Returns
        -------
        radius1 : TYPE
            DESCRIPTION.

        """
        layer_material = 'Layer'+str(layer_number)+'_material'
        layer_condition = 'Layer'+str(layer_number)+'_condition'
        mat = df[layer_material]
        cond1 = df[layer_condition]

        f_d = (mat == 'Fill') & (cond1 == 'Dry')
        rep_f = f_d.astype(int)*47
        f_m = (mat == 'Fill') & (cond1 == 'Moist')
        rep_f1 = rep_f + (f_m.astype(int)*37)
        f_w = (mat == 'Fill') & (cond1 == 'Wet')
        rep_f11 = rep_f1 + f_w.astype(int)*30

        trg_d = (mat == 'Tr - gvl') & (cond1 == 'Dry')
        rep_trg = trg_d.astype(int)*47
        trg_m = (mat == 'Tr - gvl') & (cond1 == 'Moist')
        rep_trg1 = rep_trg + (trg_m.astype(int)*37)
        trg_w = (mat == 'Tr - gvl') & (cond1 == 'Wet')
        rep_trg11 = rep_trg1 + trg_w.astype(int)*30

        trsa_d = (mat == 'Tr - sa') & (cond1 == 'Dry')
        rep_trsa = trsa_d.astype(int)*47
        trsa_m = (mat == 'Tr - sa') & (cond1 == 'Moist')
        rep_trsa1 = rep_trsa + (trsa_m.astype(int)*37)
        trsa_w = (mat == 'Tr - sa') & (cond1 == 'Wet')
        rep_trsa11 = rep_trsa1 + trsa_w.astype(int)*30

        trsi_d = (mat == 'Tr - si') & (cond1 == 'Dry')
        rep_trsi = trsi_d.astype(int)*85
        trsi_m = (mat == 'Tr - si') & (cond1 == 'Moist')
        rep_trsi1 = rep_trsi + (trsi_m.astype(int)*55)
        trsi_w = (mat == 'Tr - si') & (cond1 == 'Wet')
        rep_trsi11 = rep_trsi1 + trsi_w.astype(int)*45

        trcl_d = (mat == 'Tr - cl') & (cond1 == 'Dry')
        rep_trcl = trcl_d.astype(int)*85
        trcl_m = (mat == 'Tr - cl') & (cond1 == 'Moist')
        rep_trcl1 = rep_trcl + (trcl_m.astype(int)*50)
        trcl_w = (mat == 'Tr - cl') & (cond1 == 'Wet')
        rep_trcl11 = rep_trcl1 + trcl_w.astype(int)*35

        p_d = (mat == 'Pedo') & (cond1 == 'Dry')
        rep_p = p_d.astype(int)*90
        p_m = (mat == 'Pedo') & (cond1 == 'Moist')
        rep_p1 = rep_p + (p_m.astype(int)*90)
        p_w = (mat == 'Pedo') & (cond1 == 'Wet')
        rep_p11 = rep_p1 + p_w.astype(int)*90

        wad_d = (mat == 'Res dol - wad') & (cond1 == 'Dry')
        rep_wad = wad_d.astype(int)*85
        wad_m = (mat == 'Res dol - wad') & (cond1 == 'Moist')
        rep_wad1 = rep_wad + (wad_m.astype(int)*55)
        wad_w = (mat == 'Res dol - wad') & (cond1 == 'Wet')
        rep_wad11 = rep_wad1 + wad_w.astype(int)*45

        rdg_d = (mat == 'Res dol - gvl') & (cond1 == 'Dry')
        rep_rdg = rdg_d.astype(int)*47
        rdg_m = (mat == 'Res dol - gvl') & (cond1 == 'Moist')
        rep_rdg1 = rep_rdg + (rdg_m.astype(int)*37)
        rdg_w = (mat == 'Res dol - gvl') & (cond1 == 'Wet')
        rep_rdg11 = rep_rdg1 + rdg_w.astype(int)*30

        rdsa_d = (mat == 'Res dol - sa') & (cond1 == 'Dry')
        rep_rdsa = rdsa_d.astype(int)*70
        rdsa_m = (mat == 'Res dol - sa') & (cond1 == 'Moist')
        rep_rdsa1 = rep_rdsa + (rdsa_m.astype(int)*60)
        rdsa_w = (mat == 'Res dol - sa') & (cond1 == 'Wet')
        rep_rdsa11 = rep_rdsa1 + rdsa_w.astype(int)*50

        rdsi_d = (mat == 'Res dol - si') & (cond1 == 'Dry')
        rep_rdsi = rdsi_d.astype(int)*85
        rdsi_m = (mat == 'Res dol - si') & (cond1 == 'Moist')
        rep_rdsi1 = rep_rdsi + (rdsi_m.astype(int)*55)
        rdsi_w = (mat == 'Res dol - si') & (cond1 == 'Wet')
        rep_rdsi11 = rep_rdsi1 + rdsi_w.astype(int)*45

        rdcl_d = (mat == 'Res dol - cl') & (cond1 == 'Dry')
        rep_rdcl = rdcl_d.astype(int)*85
        rdcl_m = (mat == 'Res dol - cl') & (cond1 == 'Moist')
        rep_rdcl1 = rep_rdcl + (rdcl_m.astype(int)*50)
        rdcl_w = (mat == 'Res dol - cl') & (cond1 == 'Wet')
        rep_rdcl11 = rep_rdcl1 + rdcl_w.astype(int)*35

        rcg_d = (mat == 'Res chert - gvl') & (cond1 == 'Dry')
        rep_rcg = rcg_d.astype(int)*70
        rcg_m = (mat == 'Res chert - gvl') & (cond1 == 'Moist')
        rep_rcg1 = rep_rcg + (rcg_m.astype(int)*60)
        rcg_w = (mat == 'Res chert - gvl') & (cond1 == 'Wet')
        rep_rcg11 = rep_rcg1 + rcg_w.astype(int)*50

        rcsa_d = (mat == 'Res chert - sa') & (cond1 == 'Dry')
        rep_rcsa = rcsa_d.astype(int)*47
        rcsa_m = (mat == 'Res chert - sa') & (cond1 == 'Moist')
        rep_rcsa1 = rep_rcsa + (rcsa_m.astype(int)*37)
        rcsa_w = (mat == 'Res chert - sa') & (cond1 == 'Wet')
        rep_rcsa11 = rep_rcsa1 + rcsa_w.astype(int)*30

        rcsi_d = (mat == 'Res chert - si') & (cond1 == 'Dry')
        rep_rcsi = rcsi_d.astype(int)*85
        rcsi_m = (mat == 'Res chert - si') & (cond1 == 'Moist')
        rep_rcsi1 = rep_rcsi + (rcsi_m.astype(int)*55)
        rcsi_w = (mat == 'Res chert - si') & (cond1 == 'Wet')
        rep_rcsi11 = rep_rcsi1 + rcsi_w.astype(int)*45

        rccl_d = (mat == 'Res chert - cl') & (cond1 == 'Dry')
        rep_rccl = rccl_d.astype(int)*85
        rccl_m = (mat == 'Res chert - cl') & (cond1 == 'Moist')
        rep_rccl1 = rep_rccl + (rccl_m.astype(int)*50)
        rccl_w = (mat == 'Res chert - cl') & (cond1 == 'Wet')
        rep_rccl11 = rep_rccl1 + rccl_w.astype(int)*35

        rig_d = (mat == 'Res intru - gvl') & (cond1 == 'Dry')
        rep_rig = rig_d.astype(int)*47
        rig_m = (mat == 'Res intru - gvl') & (cond1 == 'Moist')
        rep_rig1 = rep_rig + (rig_m.astype(int)*37)
        rig_w = (mat == 'Res intru - gvl') & (cond1 == 'Wet')
        rep_rig11 = rep_rig1 + rig_w.astype(int)*30

        risa_d = (mat == 'Res intru - sa') & (cond1 == 'Dry')
        rep_risa = risa_d.astype(int)*47
        risa_m = (mat == 'Res intru - sa') & (cond1 == 'Moist')
        rep_risa1 = rep_risa + (risa_m.astype(int)*37)
        risa_w = (mat == 'Res intru - sa') & (cond1 == 'Wet')
        rep_risa11 = rep_risa1 + risa_w.astype(int)*30

        risi_d = (mat == 'Res intru - si') & (cond1 == 'Dry')
        rep_risi = risi_d.astype(int)*85
        risi_m = (mat == 'Res intru - si') & (cond1 == 'Moist')
        rep_risi1 = rep_risi + (risi_m.astype(int)*55)
        risi_w = (mat == 'Res intru - si') & (cond1 == 'Wet')
        rep_risi11 = rep_risi1 + risi_w.astype(int)*45

        ricl_d = (mat == 'Res intru - cl') & (cond1 == 'Dry')
        rep_ricl = ricl_d.astype(int)*85
        ricl_m = (mat == 'Res intru - cl') & (cond1 == 'Moist')
        rep_ricl1 = rep_ricl + (ricl_m.astype(int)*50)
        ricl_w = (mat == 'Res intru - cl') & (cond1 == 'Wet')
        rep_ricl11 = rep_ricl1 + ricl_w.astype(int)*35
        rkg_d = (mat == 'Res Karoo - gvl') & (cond1 == 'Dry')
        rep_rkg = rkg_d.astype(int)*70
        rkg_m = (mat == 'Res Karoo - gvl') & (cond1 == 'Moist')
        rep_rkg1 = rep_rkg + (rkg_m.astype(int)*60)
        rkg_w = (mat == 'Res Karoo - gvl') & (cond1 == 'Wet')
        rep_rkg11 = rep_rkg1 + rkg_w.astype(int)*50

        rksa_d = (mat == 'Res Karoo - sa') & (cond1 == 'Dry')
        rep_rksa = rksa_d.astype(int)*46
        rksa_m = (mat == 'Res Karoo - sa') & (cond1 == 'Moist')
        rep_rksa1 = rep_rksa + (rksa_m.astype(int)*35)
        rksa_w = (mat == 'Res Karoo - sa') & (cond1 == 'Wet')
        rep_rksa11 = rep_rksa1 + rksa_w.astype(int)*30

        rksi_d = (mat == 'Res Karoo - si') & (cond1 == 'Dry')
        rep_rksi = rksi_d.astype(int)*46
        rksi_m = (mat == 'Res Karoo - si') & (cond1 == 'Moist')
        rep_rksi1 = rep_rksi + (rksi_m.astype(int)*35)
        rksi_w = (mat == 'Res Karoo - si') & (cond1 == 'Wet')
        rep_rksi11 = rep_rksi1 + rksi_w.astype(int)*30

        rkcl_d = (mat == 'Res Karoo - cl') & (cond1 == 'Dry')
        rep_rkcl = rkcl_d.astype(int)*46
        rkcl_m = (mat == 'Res Karoo - cl') & (cond1 == 'Moist')
        rep_rkcl1 = rep_rkcl + (rkcl_m.astype(int)*35)
        rkcl_w = (mat == 'Res Karoo - cl') & (cond1 == 'Wet')
        rep_rkcl11 = rep_rkcl1 + rkcl_w.astype(int)*30

        wd_d = (mat == 'Weathered - dol') & (cond1 == 'Dry')
        rep_wd = wd_d.astype(int)*46
        wd_m = (mat == 'Weathered - dol') & (cond1 == 'Moist')
        rep_wd1 = rep_wd + (wd_m.astype(int)*35)
        wd_w = (mat == 'Weathered - dol') & (cond1 == 'Wet')
        rep_wd11 = rep_wd1 + wd_w.astype(int)*30

        wi_d = (mat == 'Weathered - intru') & (cond1 == 'Dry')
        rep_wi = wi_d.astype(int)*46
        wi_m = (mat == 'Weathered - intru') & (cond1 == 'Moist')
        rep_wi1 = rep_wi + (wi_m.astype(int)*35)
        wi_w = (mat == 'Weathered - intru') & (cond1 == 'Wet')
        rep_wi11 = rep_wi1 + wi_w.astype(int)*30

        cv_d = (mat == 'Cavity')
        rep_cv = cv_d.astype(int)*0.01

        reposeA = pd.to_numeric(rep_f11+rep_trg11+rep_trsa11+rep_trsi11 +
                                rep_trcl11+rep_p11+rep_wad11+rep_rdg11 +
                                rep_rdsa11+rep_rdsi11+rep_rdcl11+rep_rcg11 +
                                rep_rcsa11+rep_rcsi11+rep_rccl11+rep_rig11 +
                                rep_risa11+rep_risi11+rep_ricl11+rep_rkg11 +
                                rep_rksa11+rep_rksi11+rep_rkcl11+rep_wd11 +
                                rep_wi11+rep_cv)
        angle1 = (22/7*reposeA)/180
        radius1 = Ly1/np.tan(angle1)
        return radius1

    def sink_cal(self, x):
        """
        Sink cal.

        Parameters
        ----------
        x : TYPE
            DESCRIPTION.

        Returns
        -------
        z3 : TYPE
            DESCRIPTION.

        """
        z = np.where(x < 2, 0, x)
        z1 = np.where(((z >= 2) & (z <= 5)), 0.33, z)
        z2 = np.where(((z1 >= 5) & (z1 <= 15)), 0.66, z1)
        z3 = np.where(z2 > 15, 1, z2)

        return z3

    def eng_proc(self):
        """
        Engineering Process calculation and quality check.

        (Calculating the borehole classification)

        Returns
        -------
        None.

        """
        csv_file = self.qfile['bhole'].text()

        df = pd.read_csv(csv_file, skip_blank_lines=True).dropna()
        df.reset_index(inplace=True, drop=True)

        Ly1 = df['Layer1_thickness_m']
        Ly2 = df['Layer2_thickness_m']
        Ly3 = df['Layer3_thickness_m']
        Ly4 = df['Layer4_thickness_m']

        mat1 = df['Layer1_material']
        mat2 = df['Layer2_material']
        mat3 = df['Layer3_material']
        mat4 = df['Layer4_material']

        Total_Radius = (self.repose(1, df, Ly1) +
                        self.repose(2, df, Ly1) +
                        self.repose(3, df, Ly1) +
                        self.repose(4, df, Ly1))
        Sinkhole_diameter = 2*Total_Radius

        WL = df['Depth to water level (m)']
        DBR = df['DDBR_m']
        Ingress = (WL > DBR)
        Ingress_n = Ingress.astype(int)

        # Group 1 parameters
        df_voids = df['Presence of voids'].map({'YES': 1, 'NO': 0})
        df_air = df['Air loss'].map({'YES': 1, 'NO': 0})
        df_mat = df['Material loss'].map({'YES': 1, 'NO': 0})

        df['Sinkhole_Size'] = self.sink_cal(Sinkhole_diameter)
        df['Sinkhole_Size'] = df['Sinkhole_Size'].replace([0, 0.33, 0.66, 1.0],
                                                          ['Small', 'Medium',
                                                           'Large',
                                                           'Very Large'])
        df['Ratio_L1'] = Ly1 / DBR
        df['Ratio_L2'] = Ly2 / DBR
        df['Ratio_L3'] = Ly3 / DBR
        df['Ratio_L4'] = Ly4 / DBR

        if ((df['Ratio_L1'] + df['Ratio_L2'] + df['Ratio_L3'] +
             df['Ratio_L4'] == 1).all()):
            self.showprocesslog('Borehole Quality Control - PASS')
        else:
            # This is never true. The layers are depth to water level
            self.showprocesslog('Quality Control Fail: Please check if the sum'
                                ' of layer thickness is equal to the depth to'
                                ' bedrock')

        # Should this only be three ratios?
        df1 = df[['Ratio_L1', 'Ratio_L2', 'Ratio_L3', 'Ratio_L4']]
        df['Ratio'] = df1.idxmax(1)

        self.showprocesslog('Calculating Ratios...')

        filt = (df['Ratio'] == 'Ratio_L1')
        df.loc[filt, 'Ratio'] = df.loc[filt, 'Layer1_material']
        filt = (df['Ratio'] == 'Ratio_L2')
        df.loc[filt, 'Ratio'] = df.loc[filt, 'Layer2_material']
        filt = (df['Ratio'] == 'Ratio_L3')
        df.loc[filt, 'Ratio'] = df.loc[filt, 'Layer3_material']
        filt = (df['Ratio'] == 'Ratio_L4')
        df.loc[filt, 'Ratio'] = df.loc[filt, 'Layer4_material']

        ratio = df['Ratio']

        # Parameters to be edited
        # Get the threshold info from the table
        numrows = self.tablewidget.rowCount()

        for i in range(numrows):
            key = self.tablewidget.item(i, 0)
            val = self.tablewidget.item(i, 1)
            self.param_threshold[key.text()] = val.text()
        new_val = self.param_threshold

        f_d = (ratio == 'Fill')
        rep_f = f_d.astype(int)*float(new_val['Fill'])
        trg_d = (ratio == 'Tr - gvl')
        rep_trg = rep_f + trg_d.astype(int)*float(new_val['Tr - gvl'])
        trsa_d = (ratio == 'Tr - sa')
        rep_trsa = rep_trg + trsa_d.astype(int)*float(new_val['Tr - sa'])
        trsi_d = (ratio == 'Tr - si')
        rep_trsi = rep_trsa + trsi_d.astype(int)*float(new_val['Tr - si'])
        trcl_d = (ratio == 'Tr - cl')
        rep_trcl = rep_trsi + trcl_d.astype(int)*float(new_val['Tr - cl'])
        p1_d = (ratio == 'Pedo')
        rep_p1 = rep_trcl + p1_d.astype(int)*float(new_val['Pedo'])
        rdg_d = (ratio == 'Res dol - gvl')
        rep_rdg = rep_p1 + rdg_d.astype(int)*float(new_val['Res dol - gvl'])
        rdw_d = (ratio == 'Res dol - wad')
        rep_rdw = rep_rdg + rdw_d.astype(int)*float(new_val['Res dol - wad'])
        rdsa_d = (ratio == 'Res dol - sa')
        rep_rdsa = rep_rdw + rdsa_d.astype(int)*float(new_val['Res dol - sa'])
        rdsi_d = (ratio == 'Res dol - si')
        rep_rdsi = rep_rdsa + rdsi_d.astype(int)*float(new_val['Res dol - si'])
        rdcl_d = (ratio == 'Res dol - cl')
        rep_rdcl = rep_rdsi + rdcl_d.astype(int)*float(new_val['Res dol - cl'])
        rcg_d = (ratio == 'Res chert - gvl')
        rep_rcg = rep_rdcl + rcg_d.astype(int)*float(new_val['Res chert - gvl'])
        rcsa_d = (ratio == 'Res chert - sa')
        rep_rcsa = rep_rcg + rcsa_d.astype(int)*float(new_val['Res chert - sa'])
        rcsi_d = (ratio == 'Res chert - si')
        rep_rcsi = rep_rcsa + rcsi_d.astype(int)*float(new_val['Res chert - si'])
        rccl_d = (ratio == 'Res chert - cl')
        rep_rccl = rep_rcsi + rccl_d.astype(int)*float(new_val['Res chert - cl'])
        rig_d = (ratio == 'Res intru - gvl')
        rep_rig = rep_rccl + rig_d.astype(int)*float(new_val['Res intru - gvl'])
        risa_d = (ratio == 'Res intru - sa')
        rep_risa = rep_rig + risa_d.astype(int)*float(new_val['Res intru - sa'])
        risi_d = (ratio == 'Res intru - si')
        rep_risi = rep_risa + risi_d.astype(int)*float(new_val['Res intru - si'])
        ricl_d = (ratio == 'Res intru - cl')
        rep_ricl = rep_risi + ricl_d.astype(int)*float(new_val['Res intru - cl'])
        rkg_d = (ratio == 'Res Karoo - gvl')
        rep_rkg = rep_ricl + rkg_d.astype(int)*float(new_val['Res Karoo - gvl'])
        rksa_d = (ratio == 'Res Karoo - sa')
        rep_rksa = rep_rkg + rksa_d.astype(int)*float(new_val['Res Karoo - sa'])
        rksi_d = (ratio == 'Res Karoo - si')
        rep_rksi = rep_rksa + rksi_d.astype(int)*float(new_val['Res Karoo - si'])
        rkcl_d = (ratio == 'Res Karoo - cl')
        rep_rkcl = rep_rksi + rkcl_d.astype(int)*float(new_val['Res Karoo - cl'])
        wd_d = (ratio == 'Weathered - dol')
        rep_wd = rep_rkcl + wd_d.astype(int)*float(new_val['Weathered - dol'])
        wi_d = (ratio == 'Weathered - intru')
        rep_wi = rep_wd + wi_d.astype(int)*float(new_val['Weathered - intru'])
        cv_d = (ratio == 'Cavity')
        rep_cv = rep_wi + cv_d.astype(int)*float(new_val['Cavity'])

        ratio1 = pd.to_numeric(rep_cv)

        void_A_loss_max = np.maximum(df_voids, df_air)
        void_A_Mat_loss_max = np.maximum(void_A_loss_max,  df_mat)
        void_ingress_max = np.maximum(void_A_Mat_loss_max, Ingress_n)

        df['Rank_class'] = void_ingress_max / ratio1
        df['Rank_class'] = df['Rank_class'].round(4)
        df['Final_class'] = df['Rank_class']
        df['Final_class'].astype(str)

        df['Test_Out_Drill'] = np.where((mat1 == 'Cavity') |
                                        (mat2 == 'Cavity') |
                                        (mat3 == 'Cavity') |
                                        (mat4 == 'Cavity'), '7',
                                        df['Final_class'])
        df['Test_Out_Mat'] = np.where((df['Presence of voids'] == 'YES') &
                                      (df['Air loss'] == 'YES') &
                                      (df['Material loss'] == 'YES'), '7',
                                      df['Final_class'])
        df['BH_Rank'] = np.where((df['Test_Out_Drill'] == '7') |
                                 (df['Test_Out_Mat'] == '7'),
                                 '5_6_7_8', df['Final_class'])

        df['Cavity'] = '0'
        df.loc[mat1 == 'Cavity', 'Cavity'] = '1'
        df.loc[mat2 == 'Cavity', 'Cavity'] = '2'
        df.loc[mat3 == 'Cavity', 'Cavity'] = '3'
        df.loc[mat4 == 'Cavity', 'Cavity'] = '4'

        L1 = 0
        L2 = Ly1
        L3 = Ly1+Ly2
        L4 = Ly3+Ly2+Ly1

        df['Cavity_1'] = np.where((df['Cavity'] == '1'), L1, '0')
        df['Cavity_1'] = np.where((df['Cavity'] == '2'), L2, df['Cavity_1'])
        df['Cavity_1'] = np.where((df['Cavity'] == '3'), L3, df['Cavity_1'])
        df['Cavity_1'] = np.where((df['Cavity'] == '4'), L4, df['Cavity_1'])
        df['Cavity_2'] = np.where((mat1 == 'Cavity') & (mat2 == 'Cavity') &
                                  (mat3 == 'Cavity') & (mat4 == 'Cavity'),
                                  '0', df['Cavity_1'])
        df['Cavity_3'] = np.where((mat2 == 'Cavity') & (mat3 == 'Cavity') &
                                  (mat4 == 'Cavity') & (mat1 != 'Cavity'),
                                  L2, df['Cavity_2'])
        df['Cavity_4'] = np.where((mat3 == 'Cavity') & (mat4 == 'Cavity') &
                                  (mat1 != 'Cavity') & (mat2 != 'Cavity'), L3,
                                  df['Cavity_3'])
        df['Cavity_4'] = np.where((mat1 == 'Cavity'), L1, df['Cavity_4'])
        df['Cavity_4'] = np.where((mat1 != 'Cavity') & (mat2 == 'Cavity'), L2,
                                  df['Cavity_4'])
        df['Cavity_4'] = np.where((mat1 != 'Cavity') & (mat2 != 'Cavity') &
                                  (mat3 == 'Cavity'), L3, df['Cavity_4'])

        df['Result_Class'] = np.where((df['Cavity_4'].astype(int) > 55),
                                      df['Final_class'], df['BH_Rank'])

        df['Result_Class_1'] = np.where((df['Result_Class'] == str(1.4286)) &
                                        (df['Presence of voids'] == 'YES'),
                                        '5_6_7_8', df['Result_Class'])

        df['Result_Class_1'].replace(['0.0', '3.3333', 'inf', '8'],
                                     '1', inplace=True)

        df['Result_Class_1'].replace(['1.0', '1.25', '1.4286', '1.6667',
                                      '2.0', '5.0', '10.0', '100.0'],
                                     '2_3_4', inplace=True)

        df['Hazard_Class'] = np.where((df['Result_Class'] == str(0.0)) &
                                      (df['Ratio'] == 'Res dol - wad'),
                                      '2_3_4', df['Result_Class_1'])

        filt = (df['Cavity_4'].astype(int) > 55)
        df.loc[filt, 'Hazard_Class'].replace(['3.3333', '0.0', '8.0'],
                                             '1', inplace=True)

        df.loc[filt, 'Hazard_Class'].replace(['1.0', '1.25', '1.4286',
                                              '1.6667'], '2_3_4',
                                             inplace=True)

        df2 = df.drop(['Ratio_L1', 'Ratio_L2', 'Ratio_L3',
                       'Ratio', 'Rank_class', 'Ratio_L4', 'BH_Rank',
                       'Test_Out_Drill', 'Test_Out_Mat',
                       'Cavity', 'Cavity_1', 'Cavity_2', 'Cavity_3',
                       'Cavity_4', 'Result_Class', 'Result_Class_1',
                       'Final_class'], axis=1)

        self.showprocesslog('Borehole Classification Done.')

        self.qfile['bhole_class'] = df2

        # the sar image is fetched here to get the cell size
        sar_file = self.qfile['insar'].text()

        with rasterio.open(sar_file) as tmp:
            cell_size = tmp.transform[0]

        df['Hazard_Class_no'] = df['Hazard_Class'].replace('1', 1)
        df['Hazard_Class_no'] = df['Hazard_Class'].replace('2_3_4', 4)
        df['Hazard_Class_no'] = df['Hazard_Class_no'].replace('5_6_7_8', 7)

        values = df['Hazard_Class_no']
        xv = df['X']
        yv = df['Y']

        n_column = (np.max(xv) - np.min(xv))/cell_size
        n_rows = (np.max(yv) - np.min(yv))/cell_size

        xti = np.linspace(np.min(xv), np.max(xv), int(n_column))
        yti = np.linspace(np.min(yv), np.max(yv), int(n_rows))
        xi, yi = np.meshgrid(xti, yti)

        # interpolate
        zi = griddata((xv, yv), values, (xi, yi), method='linear')

        transform = rasterio.transform.from_origin(xv.min(), yv.max(),
                                                   cell_size, cell_size)
        inshape = self.qfile['area_shp'].text()

        gdf = gpd.read_file(inshape)
        # with fiona.open(inshape, 'r') as shapefile:
        #     shapes = [feature['geometry'] for feature in shapefile]

        coords = gdf['geometry'].loc[0].exterior.coords
        shapes = [Polygon([[p[0], p[1]] for p in coords])]

        self.myarray_bh, self.trans_bh = self.mask_raster_with_geometry(np.flipud(zi),
                                                                        transform,
                                                                        shapes,
                                                                        nodata=np.nan,
                                                                        crop=True)

        self.showprocesslog('Automatic borehole classification - DONE')

        self.insar_incorp()

    def insar_incorp(self):
        """Incorporating the InSAR data"""

        sar_file = self.qfile['insar'].text()

        sar_img = rasterio.open(sar_file)
        myarray_sar = sar_img.read(1)
        myarray_sar[myarray_sar == 0] = sar_img.nodata
        myarray_sar[myarray_sar == sar_img.nodata] = np.nan

        self.showprocesslog('InSAR data import - DONE')

        self.showprocesslog('Creating the SAR class image...')

        with np.errstate(invalid='ignore'):
            x1 = myarray_sar < np.nanmin(myarray_sar)
            x2 = (np.nanmin(myarray_sar) <= myarray_sar) & (myarray_sar < -1)
            x3 = (myarray_sar >= -1) & (myarray_sar < 0)
            x4 = (myarray_sar >= 0) & (myarray_sar <= np.nanmax(myarray_sar))
            x5 = myarray_sar > np.nanmax(myarray_sar)
        myarray_sar[x1] = np.NaN
        myarray_sar[x2] = 3
        myarray_sar[x3] = 2
        myarray_sar[x4] = 1
        myarray_sar[x5] = np.NaN

        self.showprocesslog('INSAR Class Image Done')

        self.showprocesslog('Fetching the borehole image...')
        # Check this is not a repeat

        myarray_bh = self.myarray_bh

        with np.errstate(invalid='ignore'):
            x1 = myarray_bh < 1
            x2 = (myarray_bh >= 1) & (myarray_bh <= 3)
            x3 = (myarray_bh >= 4) & (myarray_bh <= 5)
            x4 = (myarray_bh >= 6) & (myarray_bh <= 8)
            x5 = myarray_bh > 8
        myarray_bh[x1] = np.NaN
        myarray_bh[x2] = 1
        myarray_bh[x3] = 2
        myarray_bh[x4] = 3
        myarray_bh[x5] = np.NaN

        self.out_meta.update({'driver': 'GTiff',
                              'height': myarray_bh.shape[0],
                              'width': myarray_bh.shape[1],
                              'transform': self.trans_bh,
                              'count': 1,
                              'dtype': myarray_bh.dtype,
                              'nodata': np.nan,
                              'crs': rasterio.crs.CRS.from_epsg(4326)})

        with rasterio.open('Bhole_rank_img.tif', 'w', **self.out_meta) as dest:
            dest.write(myarray_bh, 1)

        self.bhole_rank = myarray_bh

        # myarray_bh is the raster image
        # out_meta contains the metadata for this file

        with np.errstate(invalid='ignore'):
            x2 = (myarray_bh == 1)
            x3 = (myarray_bh > 1) & (myarray_bh <= 3)
            x4 = (myarray_bh > 3)

        myarray_bh[x2] = 1
        myarray_bh[x3] = 2
        myarray_bh[x4] = 3

        self.showprocesslog('Creating the borehole class image...')

        bh_class_img = MemoryFile().open(driver='GTiff',
                                         height=myarray_bh.shape[0],
                                         width=myarray_bh.shape[1], count=1,
                                         dtype=myarray_bh.dtype,
                                         transform=self.trans_bh)
        bh_class_img.write(myarray_bh, 1)
        bb_raster1 = box(bh_class_img.bounds[0], bh_class_img.bounds[1],
                         bh_class_img.bounds[2], bh_class_img.bounds[3])
        bb_raster2 = box(sar_img.bounds[0], sar_img.bounds[1],
                         sar_img.bounds[2], sar_img.bounds[3])

        xminR1, _, _, ymaxR1 = bh_class_img.bounds
        xminR2, _, _, ymaxR2 = sar_img.bounds

        intersection = bb_raster1.intersection(bb_raster2)

        p1Y = intersection.bounds[3] - bh_class_img.res[1]/2
        p1X = intersection.bounds[0] + bh_class_img.res[0]/2
        p2Y = intersection.bounds[1] + bh_class_img.res[1]/2
        p2X = intersection.bounds[2] - bh_class_img.res[0]/2
        row1R1 = int((ymaxR1 - p1Y)/bh_class_img.res[1])
        row1R2 = int((ymaxR2 - p1Y)/sar_img.res[1])
        col1R1 = int((p1X - xminR1)/bh_class_img.res[0])
        col1R2 = int((p1X - xminR2)/bh_class_img.res[0])

        row2R1 = int((ymaxR1 - p2Y)/bh_class_img.res[1])
        row2R2 = int((ymaxR2 - p2Y)/sar_img.res[1])
        col2R1 = int((p2X - xminR1)/bh_class_img.res[0])
        col2R2 = int((p2X - xminR2)/bh_class_img.res[0])

        width1 = col2R1 - col1R1 + 1
        width2 = col2R2 - col1R2 + 1
        height1 = row2R1 - row1R1 + 1
        height2 = row2R2 - row1R2 + 1

        array_c_bh = bh_class_img.read(1, window=Window(col1R1, row1R1,
                                                        width1, height1))
        array_c_sar = sar_img.read(1, window=Window(col1R2, row1R2,
                                                    width2, height2))

        with np.errstate(invalid='ignore'):
            x1 = (array_c_sar == 3) & (array_c_bh == 3)
            x2 = (array_c_sar == 3) & (array_c_bh == 2)
            x3 = (array_c_sar == 3) & (array_c_bh == 1)
            x4 = (array_c_sar == 2) & (array_c_bh == 3)
            x5 = (array_c_sar == 2) & (array_c_bh == 2)
            x6 = (array_c_sar == 2) & (array_c_bh == 1)
            x7 = (array_c_sar == 1) & (array_c_bh == 3)
            x8 = (array_c_sar == 1) & (array_c_bh == 2)
            x9 = (array_c_sar == 1) & (array_c_bh == 1)
            x10 = (array_c_sar == 0) & (array_c_bh == 0)

        array_c_bh[x1] = 13
        array_c_bh[x2] = 12
        array_c_bh[x3] = 11
        array_c_bh[x4] = 10
        array_c_bh[x5] = 9
        array_c_bh[x6] = 4
        array_c_bh[x7] = 3
        array_c_bh[x8] = 2
        array_c_bh[x9] = 1
        array_c_bh[x10] = np.NaN

        self.out_meta.update({'driver': 'GTiff',
                              'height': array_c_bh.shape[0],
                              'width': array_c_bh.shape[1],
                              'transform': self.trans_bh,
                              'count': 1,
                              'dtype': array_c_bh.dtype,
                              'nodata': np.nan,
                              'crs': rasterio.crs.CRS.from_epsg(4326)})

        with rasterio.open('Final_Result.tif', 'w', **self.out_meta) as dest:
            dest.write(array_c_bh, 1)

        self.final_result = array_c_bh

        self.showprocesslog("Automatic Classsification Done")

        class_img = self.final_result
        self.mt4.t4_bhole_class(class_img)

        self.tabs.setTabEnabled(3, True)

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
        # tst = self.indata['csv']

        # to check if the data is linked to this process
        if not nodialog:
            temp = self.exec_()
            if temp == 0:
                return False

        self.parent.process_is_active()

        flag = self.run()  # flag gets the database

        if not nodialog:
            self.parent.process_is_active(False)
            self.parent.pbar.to_max()
        return flag
