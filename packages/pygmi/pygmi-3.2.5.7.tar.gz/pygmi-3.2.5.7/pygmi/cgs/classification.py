# -----------------------------------------------------------------------------
# Name:        accuracy.py (part of PyGMI)
#
# Author:      Gabrielle Denner & Patrick Cole
# E-Mail:      pcole@geoscience.org.za
#
# Copyright:   (c) 2021 Council for Geoscience
# Licence:     Confidential, only for CGS,
# -----------------------------------------------------------------------------
"""
Created on Wed Aug 18 12:36:19 2021

@author: mdenner

text='Currently classification of boreholes '
                                'in terms of the hazard of sinkhole formation'
                                ' is done \nmanually and results vary from '
                                'one expert to another. To reduce the bias '
                                'amongst various \nexperts, this module '
                                'automates the classification using an '
                                'expert system built by combining \nexpert '
                                'knowledge on sinkhole formation and a '
                                'vast number of boreholes (> 1 500) already '
                                '\nclassified by experts.'
"""

import copy
from PyQt5 import QtWidgets, QtCore
import numpy as np
import pandas as pd
import pygmi.menu_default as menu_default
from pygmi.misc import ProgressBarText


class Classification(QtWidgets.QDialog):
    """
    Borehole Classification Class.

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

        self.setupui()


    def setupui(self):
        """
        Set up UI.

        Returns
        -------
        None.

        """

        # helpdocs = menu_default.HelpButton('pygmi.clust.cluster')
        gridlayout = QtWidgets.QGridLayout(self)

        buttonbox = QtWidgets.QDialogButtonBox()
        label = QtWidgets.QLabel('Start borehole classification?')

        buttonbox.setOrientation(QtCore.Qt.Horizontal)
        buttonbox.setStandardButtons(buttonbox.Cancel | buttonbox.Ok)

        self.setWindowTitle('Borehole Classification')

        gridlayout.addWidget(label, 0, 2, 1, 1)
        gridlayout.addWidget(buttonbox, 10, 4, 1, 1)

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

    def run(self):
        """
        Run the cluster analysis.

        Returns
        -------
        None.

        """
        df = copy.copy(self.indata['csv'])

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
                                ' of layer thickness is equal to the depth to '
                                'bedrock')

        # Should this only be three ratios?
        df1 = df[['Ratio_L1', 'Ratio_L2', 'Ratio_L3', 'Ratio_L4']]
        df['Ratio'] = df1.idxmax(1)

        filt = (df['Ratio'] == 'Ratio_L1')
        df.loc[filt, 'Ratio'] = df.loc[filt, 'Layer1_material']
        filt = (df['Ratio'] == 'Ratio_L2')
        df.loc[filt, 'Ratio'] = df.loc[filt, 'Layer2_material']
        filt = (df['Ratio'] == 'Ratio_L3')
        df.loc[filt, 'Ratio'] = df.loc[filt, 'Layer3_material']
        filt = (df['Ratio'] == 'Ratio_L4')
        df.loc[filt, 'Ratio'] = df.loc[filt, 'Layer4_material']

        ratio = df['Ratio']

        f_d = (ratio == 'Fill')
        rep_f = f_d.astype(int)*1
        trg_d = (ratio == 'Tr - gvl')
        rep_trg = rep_f + trg_d.astype(int)*1
        trsa_d = (ratio == 'Tr - sa')
        rep_trsa = rep_trg + trsa_d.astype(int)*1
        trsi_d = (ratio == 'Tr - si')
        rep_trsi = rep_trsa + trsi_d.astype(int)*0.3
        trcl_d = (ratio == 'Tr - cl')
        rep_trcl = rep_trsi + trcl_d.astype(int)*0.2
        p1_d = (ratio == 'Pedo')
        rep_p1 = rep_trcl + p1_d.astype(int)*0.1
        rdg_d = (ratio == 'Res dol - gvl')
        rep_rdg = rep_p1 + rdg_d.astype(int)*0.8
        rdw_d = (ratio == 'Res dol - wad')
        rep_rdw = rep_rdg + rdw_d.astype(int)*1
        rdsa_d = (ratio == 'Res dol - sa')
        rep_rdsa = rep_rdw + rdsa_d.astype(int)*0.7
        rdsi_d = (ratio == 'Res dol - si')
        rep_rdsi = rep_rdsa + rdsi_d.astype(int)*0.7
        rdcl_d = (ratio == 'Res dol - cl')
        rep_rdcl = rep_rdsi + rdcl_d.astype(int)*0.6
        rcg_d = (ratio == 'Res chert - gvl')
        rep_rcg = rep_rdcl + rcg_d.astype(int)*0.8
        rcsa_d = (ratio == 'Res chert - sa')
        rep_rcsa = rep_rcg + rcsa_d.astype(int)*0.8
        rcsi_d = (ratio == 'Res chert - si')
        rep_rcsi = rep_rcsa + rcsi_d.astype(int)*0.7
        rccl_d = (ratio == 'Res chert - cl')
        rep_rccl = rep_rcsi + rccl_d.astype(int)*0.7
        rig_d = (ratio == 'Res intru - gvl')
        rep_rig = rep_rccl + rig_d.astype(int)*0.5
        risa_d = (ratio == 'Res intru - sa')
        rep_risa = rep_rig + risa_d.astype(int)*0.5
        risi_d = (ratio == 'Res intru - si')
        rep_risi = rep_risa + risi_d.astype(int)*0.3
        ricl_d = (ratio == 'Res intru - cl')
        rep_ricl = rep_risi + ricl_d.astype(int)*0.3
        rkg_d = (ratio == 'Res Karoo - gvl')
        rep_rkg = rep_ricl + rkg_d.astype(int)*0.5
        rksa_d = (ratio == 'Res Karoo - sa')
        rep_rksa = rep_rkg + rksa_d.astype(int)*0.5
        rksi_d = (ratio == 'Res Karoo - si')
        rep_rksi = rep_rksa + rksi_d.astype(int)*0.3
        rkcl_d = (ratio == 'Res Karoo - cl')
        rep_rkcl = rep_rksi + rkcl_d.astype(int)*0.3
        wd_d = (ratio == 'Weathered - dol')
        rep_wd = rep_rkcl + wd_d.astype(int)*0.01
        wi_d = (ratio == 'Weathered - intru')
        rep_wi = rep_wd + wi_d.astype(int)*0.01
        cv_d = (ratio == 'Cavity')
        rep_cv = rep_wi + cv_d.astype(int)*1

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

        df = df.drop(['Ratio_L1', 'Ratio_L2', 'Ratio_L3',
                      'Ratio', 'Rank_class', 'Ratio_L4', 'BH_Rank',
                      'Test_Out_Drill', 'Test_Out_Mat',
                      'Cavity', 'Cavity_1', 'Cavity_2', 'Cavity_3',
                      'Cavity_4', 'Result_Class', 'Result_Class_1',
                      'Final_class'], 1)

        return df

        self.showprocesslog('Classification complete')
