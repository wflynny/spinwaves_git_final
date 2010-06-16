import wx
#import wxaddons.sized_controls as sc
import  wx.lib.intctrl
import  wx.grid as  gridlib
import numpy as np
import sys,os
import spinwaves.cross_section.csection_calc as csection_calc
import wx.richtext
from sympy import pi
import spinwaves.cross_section.util.printing as printing
from multiprocessing import Process, Pipe
import copy

    
class RichTextPanel(wx.Panel):
    def __init__(self, allowEdit, *args, **kw):
        wx.Panel.__init__(self, *args, **kw)

     #   self.MakeMenuBar()
     #   self.MakeToolBar()
     #   self.CreateStatusBar()
     #   self.SetStatusText("Welcome to wx.richtext.RichTextCtrl!")
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        self.spinsRtc = wx.richtext.RichTextCtrl(self, style=wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER, size = (620,120));
        self.interactionsRtc = wx.richtext.RichTextCtrl(self, style=wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER, size = (620,120));
     #   wx.CallAfter(self.rtc.SetFocus)
        interactionsTitle = wx.StaticText(self, -1, " Interaction File ")
        spinsTitle = wx.StaticText(self, -1, " Spins File ")
        
        
        self.interactionSave = wx.Button(self, -1, "Save", size = (50,20))
        interactionSizer = wx.BoxSizer(wx.HORIZONTAL)
        interactionSizer.Add(interactionsTitle)
        interactionSizer.Add(self.interactionSave)
        
        self.spinSave = wx.Button(self, -1, "Save", size = (50,20))
        spinSizer = wx.BoxSizer(wx.HORIZONTAL)
        spinSizer.Add(spinsTitle)
        spinSizer.Add(self.spinSave)
        
        
        sizer.Add(interactionSizer)
        sizer.Add(self.interactionsRtc)
        sizer.Add(spinSizer)
        sizer.Add(self.spinsRtc)
        
        self.Bind(wx.EVT_BUTTON, self.OnSaveInteractions, self.interactionSave)
        self.Bind(wx.EVT_BUTTON, self.OnSaveSpins, self.spinSave)
        
        self.Fit()
        self.SetMinSize(self.GetSize())
        
        if not allowEdit:
            self.spinSave.Enable(False)
            self.interactionSave.Enable(False)
        
    
    def OnSaveInteractions(self, evt):
        self.interactionsRtc.SaveFile()
    
    def OnSaveSpins(self, evt):
        self.spinsRtc.SaveFile()
    
    def loadSpins(self, file):
        print "\n\n\n\nfilename: " , file
        self.spinsRtc.LoadFile(file)
    
    def loadInteractions(self, file):
        print "\n\n\n\nfilename: " , file
        self.interactionsRtc.LoadFile(file)

def showEditorWindow(parent, title, allowEditting = True):
    """Creates and displays a simple frame containing the RichTextPanel."""
    frame = wx.Frame(parent, -1, title, size=(630, 320), style = wx.DEFAULT_FRAME_STYLE)
    panel = RichTextPanel(allowEditting, frame, -1)
    #frame.Fit()
    #frame.SetMinSize(frame.GetSize())
    frame.Show()
    return panel

class CrossSectionPanel(wx.Panel):
#    def __init__(self, procManager, *args, **kwds):
    def __init__(self, procManager, *args, **kwds):
        kwds["style"] = wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)
        
        self.window = wx.BoxSizer(wx.VERTICAL)
        
        self.file_box = wx.StaticBox(self, -1, "Select Files")
        self.int_file_label = wx.StaticText(self, -1, " Interaction File: ")
        self.int_browse_btn = wx.Button(self, -1, "Browse")
        self.int_file_txtCtrl = wx.TextCtrl(self, -1, "")
        self.spin_file_label = wx.StaticText(self, -1, " Spin File: ")
        self.spin_browse_btn = wx.Button(self, -1, "Browse")
        self.spin_file_txtCtrl = wx.TextCtrl(self, -1, "")
        self.tau_file_label = wx.StaticText(self, -1, " Tau File ")
        self.tau_browse_btn = wx.Button(self, -1, "Browse")
        self.tau_file_txtCtrl = wx.TextCtrl(self, -1, "")
        self.output_file_label = wx.StaticText(self, -1, " Output File ")
        self.output_browse_btn = wx.Button(self, -1, "Browse")
        self.output_file_txtCtrl = wx.TextCtrl(self, -1, "")

        self.hkl_interval = wx.StaticBox(self, -1, "HKL Interval")
        self.hklmin_label = wx.StaticText(self, -1, "hkl Min:")
        self.hklmin_txtCtrl = wx.TextCtrl(self, -1, "")
        self.hklmin_pi = wx.StaticText(self, -1, "*pi")
        self.hklmax_label = wx.StaticText(self, -1, "hkl Max:")
        self.hklmax_txtCtrl = wx.TextCtrl(self, -1, "")
        self.hklmax_pi = wx.StaticText(self, -1, "*pi")
        self.hkl_steps_label = wx.StaticText(self, -1, "Steps:")
        self.hkl_steps_ctrl = wx.SpinCtrl(self, -1, "", min=0, max=1000)
        
        self.w_interval = wx.StaticBox(self, -1, "Omega Interval")
        self.wmin_label = wx.StaticText(self, -1, "w Min:")
        self.wmin_txtCtrl = wx.TextCtrl(self, -1, "")
        self.wmax_label = wx.StaticText(self, -1, "w Max:")
        self.wmax_txtCtrl = wx.TextCtrl(self, -1, "")
        self.w_steps_label = wx.StaticText(self, -1, "Steps:")
        self.w_steps_ctrl = wx.SpinCtrl(self, -1, "", min=0, max=1000)
        
        self.scan_direction = wx.StaticBox(self, -1, "Scan Direction")
        self.kx_label = wx.StaticText(self, -1, "kx:")
        self.kx_txtCtrl = wx.TextCtrl(self, -1, "")
        self.ky_label = wx.StaticText(self, -1, "ky:")
        self.ky_txtCtrl = wx.TextCtrl(self, -1, "")
        self.kz_label = wx.StaticText(self, -1, "kz:")
        self.kz_txtCtrl = wx.TextCtrl(self, -1, "")
        self.temp_label = wx.StaticText(self, -1, "Temperature")
        self.temp_ctrl = wx.TextCtrl(self, -1, "")
        
        self.plot_range = wx.StaticBox(self, -1, "Plot Range")
        self.zmin_label = wx.StaticText(self, -1, "Minimum")
        self.zmin_ctrl = wx.TextCtrl(self, -1, "")
        self.zmax_label = wx.StaticText(self, -1, "Maximum")
        self.zmax_ctrl = wx.TextCtrl(self, -1, "")
        self.color_bar_box = wx.CheckBox(self, -1, "Display Color Bar")

        self.add_info = wx.StaticBox(self, -1, "Additional Information")
        self.spherical_avg_box = wx.CheckBox(self, -1, "Spherical Averaging")
        self.ok_btn = wx.Button(self, -1, "Ok")
        self.cancel_btn = wx.Button(self, -1, "Cancel")        
        
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnIntFileBrowse, self.int_browse_btn)
        self.Bind(wx.EVT_BUTTON, self.OnSpinFileBrowse, self.spin_browse_btn)
        self.Bind(wx.EVT_BUTTON, self.OnTauFileBrowse, self.tau_browse_btn)
        self.Bind(wx.EVT_BUTTON, self.OnOutFileBrowse, self.output_browse_btn)
        self.Bind(wx.EVT_BUTTON, self.OnOk, self.ok_btn)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.cancel_btn)

        self.processManager = procManager

    def __set_properties(self):
        # begin wxGlade: SpinwavePanel.__set_properties
        self.int_file_txtCtrl.SetMinSize((230, 27))
        self.spin_file_txtCtrl.SetMinSize((230, 27))
        self.tau_file_txtCtrl.SetMinSize((230, 27))
        self.output_file_txtCtrl.SetMinSize((230, 27))
        # end wxGlade

        self.hklmin_txtCtrl.SetValue(str(0))
        self.hklmax_txtCtrl.SetValue(str(2))
        self.hkl_steps_ctrl.SetValue(100)
        self.wmin_txtCtrl.SetValue(str(0))
        self.wmax_txtCtrl.SetValue(str(5))
        self.w_steps_ctrl.SetValue(100)
        
        self.kx_txtCtrl.SetValue(str(1))
        self.ky_txtCtrl.SetValue(str(0))
        self.kz_txtCtrl.SetValue(str(0))
        self.temp_ctrl.SetValue(str(0.001))
        
        self.zmin_ctrl.SetValue(str(0))
        self.zmax_ctrl.SetValue(str(25))
        self.color_bar_box.SetValue(True)
        self.spherical_avg_box.SetValue(False)

    def __do_layout(self):
        # begin wxGlade: SpinwavePanel.__do_layout
       
        filebox = wx.StaticBoxSizer(self.file_box, wx.VERTICAL)
        intfile = wx.BoxSizer(wx.HORIZONTAL)
        spinfile = wx.BoxSizer(wx.HORIZONTAL)
        taufile = wx.BoxSizer(wx.HORIZONTAL)
        outfile = wx.BoxSizer(wx.HORIZONTAL)
        
        hklbox = wx.StaticBoxSizer(self.hkl_interval, wx.HORIZONTAL)
        hklmin = wx.BoxSizer(wx.VERTICAL)
        hklmax = wx.BoxSizer(wx.VERTICAL)
        hklsteps = wx.BoxSizer(wx.VERTICAL)
        hklminlab = wx.BoxSizer(wx.HORIZONTAL)
        hklminctrl = wx.BoxSizer(wx.HORIZONTAL)
        hklmaxlab = wx.BoxSizer(wx.HORIZONTAL)
        hklmaxtctrl = wx.BoxSizer(wx.HORIZONTAL)
        hklstepslab = wx.BoxSizer(wx.HORIZONTAL)
        hklstepsctrl = wx.BoxSizer(wx.HORIZONTAL)
        
        wbox = wx.StaticBoxSizer(self.w_interval, wx.HORIZONTAL)
        wmin = wx.BoxSizer(wx.VERTICAL)
        wmax = wx.BoxSizer(wx.VERTICAL)
        wsteps = wx.BoxSizer(wx.VERTICAL)
        wminlab = wx.BoxSizer(wx.HORIZONTAL)
        wminctrl = wx.BoxSizer(wx.HORIZONTAL)
        wmaxlab = wx.BoxSizer(wx.HORIZONTAL)
        wmaxtctrl = wx.BoxSizer(wx.HORIZONTAL)
        wstepslab = wx.BoxSizer(wx.HORIZONTAL)
        wstepsctrl = wx.BoxSizer(wx.HORIZONTAL)     
    
        scan = wx.StaticBoxSizer(self.scan_direction, wx.HORIZONTAL)
        kx = wx.BoxSizer(wx.VERTICAL)
        ky = wx.BoxSizer(wx.VERTICAL)
        kz = wx.BoxSizer(wx.VERTICAL)
        kxlab = wx.BoxSizer(wx.HORIZONTAL)
        kxctrl = wx.BoxSizer(wx.HORIZONTAL)
        kylab = wx.BoxSizer(wx.HORIZONTAL)
        kyctrl = wx.BoxSizer(wx.HORIZONTAL)
        kzlab = wx.BoxSizer(wx.HORIZONTAL)
        kzctrl = wx.BoxSizer(wx.HORIZONTAL)
        temp = wx.BoxSizer(wx.VERTICAL)
        templab = wx.BoxSizer(wx.HORIZONTAL)
        tempctrl = wx.BoxSizer(wx.HORIZONTAL)
        
        zmin = wx.BoxSizer(wx.VERTICAL)
        zmax = wx.BoxSizer(wx.VERTICAL)
        zminlab = wx.BoxSizer(wx.HORIZONTAL)
        zminctrl = wx.BoxSizer(wx.HORIZONTAL)
        zmaxlab = wx.BoxSizer(wx.HORIZONTAL)
        zmaxctrl = wx.BoxSizer(wx.HORIZONTAL)
        
        addinfo = wx.StaticBoxSizer(self.add_info, wx.HORIZONTAL)
        plotrange = wx.StaticBoxSizer(self.plot_range, wx.HORIZONTAL)
        buttons = wx.BoxSizer(wx.HORIZONTAL) 
        
        intfile.Add(self.int_file_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        intfile.Add(self.int_file_txtCtrl, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        intfile.Add(self.int_browse_btn, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        filebox.Add(intfile, 0, wx.EXPAND, 0)
        spinfile.Add(self.spin_file_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        spinfile.Add(self.spin_file_txtCtrl, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        spinfile.Add(self.spin_browse_btn, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        filebox.Add(spinfile, 0, wx.EXPAND, 0)
        taufile.Add(self.tau_file_label, 0 , wx.ALIGN_CENTER_VERTICAL, 0)
        taufile.Add(self.tau_file_txtCtrl, 0 , wx.ALIGN_CENTER_VERTICAL, 0)
        taufile.Add(self.tau_browse_btn, 0 , wx.ALIGN_CENTER_VERTICAL, 0)
        filebox.Add(taufile, 0, wx.EXPAND, 0)
        outfile.Add(self.output_file_label, 0 , wx.ALIGN_CENTER_VERTICAL, 0)
        outfile.Add(self.output_file_txtCtrl, 0 , wx.ALIGN_CENTER_VERTICAL, 0)
        outfile.Add(self.output_browse_btn, 0 , wx.ALIGN_CENTER_VERTICAL, 0)
        filebox.Add(outfile, 0, wx.EXPAND, 0)
        self.window.Add(filebox, 0, wx.EXPAND, 0)

        hklbox.Add((15, 15), 0, 0, 0)
        hklminlab.Add(self.hklmin_label, 0, wx.ALIGN_BOTTOM|wx.ALIGN_CENTER_HORIZONTAL, 0)
        hklmin.Add(hklminlab, 1, wx.EXPAND, 0)
        hklminctrl.Add(self.hklmin_txtCtrl, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        hklminctrl.Add(self.hklmin_pi, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        hklmin.Add(hklminctrl, 1, wx.EXPAND, 0)
        hklbox.Add(hklmin, 1, wx.EXPAND, 0)
        hklmaxlab.Add(self.hklmax_label, 0, wx.ALIGN_BOTTOM|wx.ALIGN_CENTER_HORIZONTAL, 0)
        hklmax.Add(hklmaxlab, 1, wx.EXPAND, 0)
        hklmaxtctrl.Add(self.hklmax_txtCtrl, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        hklmaxtctrl.Add(self.hklmax_pi, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        hklmax.Add(hklmaxtctrl, 1, wx.EXPAND, 0)
        hklbox.Add(hklmax, 1, wx.EXPAND, 0)
        hklstepslab.Add(self.hkl_steps_label, 0, wx.ALIGN_BOTTOM|wx.ALIGN_CENTER_HORIZONTAL, 0)
        hklsteps.Add(hklstepslab, 1, wx.EXPAND, 0)
        hklstepsctrl.Add(self.hkl_steps_ctrl, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        hklsteps.Add(hklstepsctrl, 1, wx.EXPAND, 0)
        hklbox.Add(hklsteps, 1, wx.EXPAND, 0)
        self.window.Add(hklbox, 0, wx.EXPAND, 0)

        wbox.Add((15, 15), 0, 0, 0)
        wminlab.Add(self.wmin_label, 0, wx.ALIGN_BOTTOM|wx.ALIGN_CENTER_HORIZONTAL, 0)
        wmin.Add(wminlab, 1, wx.EXPAND, 0)
        wminctrl.Add(self.wmin_txtCtrl, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        wmin.Add(wminctrl, 1, wx.EXPAND, 0)
        wbox.Add(wmin, 1, wx.EXPAND, 0)
        wmaxlab.Add(self.wmax_label, 0, wx.ALIGN_BOTTOM|wx.ALIGN_CENTER_HORIZONTAL, 0)
        wmax.Add(wmaxlab, 1, wx.EXPAND, 0)
        wmaxtctrl.Add(self.wmax_txtCtrl, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        wmax.Add(wmaxtctrl, 1, wx.EXPAND, 0)
        wbox.Add(wmax, 1, wx.EXPAND, 0)
        wstepslab.Add(self.w_steps_label, 0, wx.ALIGN_BOTTOM|wx.ALIGN_CENTER_HORIZONTAL, 0)
        wsteps.Add(wstepslab, 1, wx.EXPAND, 0)
        wstepsctrl.Add(self.w_steps_ctrl, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        wsteps.Add(wstepsctrl, 1, wx.EXPAND, 0)
        wbox.Add(wsteps, 1, wx.EXPAND, 0)
        self.window.Add(wbox, 0, wx.EXPAND, 0)

        scan.Add((15, 15), 0, 0, 0)
        kxlab.Add(self.kx_label, 0, wx.ALIGN_BOTTOM|wx.ALIGN_CENTER_HORIZONTAL, 0)
        kx.Add(kxlab, 1, wx.EXPAND, 0)
        kxctrl.Add(self.kx_txtCtrl, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        kx.Add(kxctrl, 1, wx.EXPAND, 0)        
        scan.Add(kx, 1, wx.EXPAND, 0)
        kylab.Add(self.ky_label, 0, wx.ALIGN_BOTTOM|wx.ALIGN_CENTER_HORIZONTAL, 0)
        ky.Add(kylab, 1, wx.EXPAND, 0)
        kyctrl.Add(self.ky_txtCtrl, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        ky.Add(kyctrl, 1, wx.EXPAND, 0)        
        scan.Add(ky, 1, wx.EXPAND, 0)
        kzlab.Add(self.kz_label, 0, wx.ALIGN_BOTTOM|wx.ALIGN_CENTER_HORIZONTAL, 0)
        kz.Add(kzlab, 1, wx.EXPAND, 0)
        kzctrl.Add(self.kz_txtCtrl, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        kz.Add(kzctrl, 1, wx.EXPAND, 0)        
        scan.Add(kz, 1, wx.EXPAND, 0)
        self.window.Add(scan, 0, wx.EXPAND, 0)
        
        plotrange.Add((15,15), 0, 0, 0)
        zminlab.Add(self.zmin_label, 0, wx.ALIGN_BOTTOM|wx.ALIGN_CENTER_HORIZONTAL, 0)
        zmin.Add(zminlab, 1, wx.EXPAND, 0)
        zminctrl.Add(self.zmin_ctrl, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        zmin.Add(zminctrl, 1, wx.EXPAND, 0)
        plotrange.Add(zmin, 1, wx.EXPAND, 0)
        zmaxlab.Add(self.zmax_label, 0, wx.ALIGN_BOTTOM|wx.ALIGN_CENTER_HORIZONTAL, 0)
        zmax.Add(zmaxlab, 1, wx.EXPAND, 0)
        zmaxctrl.Add(self.zmax_ctrl, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        zmax.Add(zmaxctrl, 1, wx.EXPAND, 0)
        plotrange.Add(zmax, 1, wx.EXPAND, 0)
        plotrange.Add(self.color_bar_box, 1, wx.ALIGN_BOTTOM|wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.window.Add(plotrange, 0, wx.EXPAND, 0)

        addinfo.Add((15,15), 0, 0, 0)
        templab.Add(self.temp_label, 0, wx.ALIGN_BOTTOM|wx.ALIGN_CENTER_HORIZONTAL, 0)
        temp.Add(templab, 1, wx.EXPAND, 0)
        tempctrl.Add(self.temp_ctrl, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        temp.Add(tempctrl, 1, wx.EXPAND, 0)
        addinfo.Add(temp, 1, wx.EXPAND, 0)
        addinfo.Add(self.spherical_avg_box, 1, wx.ALIGN_BOTTOM|wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.window.Add(addinfo, 0, wx.EXPAND, 0)

        buttons.Add(self.ok_btn, 0, wx.ALIGN_BOTTOM|wx.ALIGN_CENTER_HORIZONTAL, 0)
        buttons.Add(self.cancel_btn, 0, wx.ALIGN_BOTTOM|wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.window.Add(buttons, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        self.SetSizer(self.window)
        self.SetAutoLayout(True)
        self.window.Fit(self)
        self.SendSizeEvent()
        self.Refresh()
        # end wxGlade
        
    def OnIntFileBrowse(self, event):
        confBase = wx.ConfigBase.Create()
        confBase.SetStyle(wx.CONFIG_USE_LOCAL_FILE)
        defaultDir=confBase.Get().GetPath()

        wildcard="files (*.txt)|*.txt|All files (*.*)|*.*"
        dlg = wx.FileDialog(self, message="Choose an Interaction file", 
                            defaultDir=defaultDir, defaultFile="", wildcard=wildcard,
                            style=wx.OPEN | wx.CHANGE_DIR)

        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            interactionfile=paths[0].encode('ascii')
            self.int_file_txtCtrl.SetValue(interactionfile)

        dlg.Destroy()
    
    def OnSpinFileBrowse(self, event):
        confBase = wx.ConfigBase.Create()
        confBase.SetStyle(wx.CONFIG_USE_LOCAL_FILE)
        defaultDir=confBase.Get().GetPath()

        wildcard="files (*.txt)|*.txt|All files (*.*)|*.*"
        dlg = wx.FileDialog(self, message="Choose a Spin Configuration file",
                            defaultDir=defaultDir, defaultFile="", wildcard=wildcard,
                            style=wx.OPEN | wx.CHANGE_DIR)

        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            spinfile=paths[0].encode('ascii')
            self.spin_file_txtCtrl.SetValue(spinfile)
        
        dlg.Destroy()
    
    def OnTauFileBrowse(self, event):
        confBase = wx.ConfigBase.Create()
        confBase.SetStyle(wx.CONFIG_USE_LOCAL_FILE)
        defaultDir=confBase.Get().GetPath()

        wildcard="files (*.txt)|*.txt|All files (*.*)|*.*"
        dlg = wx.FileDialog(self, message="Choose a file of tau vectors",
                            defaultDir=defaultDir, defaultFile="", wildcard=wildcard,
                            style=wx.OPEN | wx.CHANGE_DIR)

        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            spinfile=paths[0].encode('ascii')
            self.tau_file_txtCtrl.SetValue(spinfile)
        
        dlg.Destroy()
    
    def OnOutFileBrowse(self, event):
        confBase = wx.ConfigBase.Create()
        confBase.SetStyle(wx.CONFIG_USE_LOCAL_FILE)
        defaultDir=confBase.Get().GetPath()

        wildcard="files (*.txt)|*.txt|All files (*.*)|*.*"
        dlg = wx.FileDialog(self, message="Choose a destination file for output",
                            defaultDir=defaultDir, defaultFile="", wildcard=wildcard,
                            style=wx.OPEN | wx.CHANGE_DIR)

        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            spinfile=paths[0].encode('ascii')
            self.output_file_txtCtrl.SetValue(spinfile)
        
        dlg.Destroy()
    
    def OnOk(self, event):
        failed, hkl_interval, w_interval, tau_list, direction, temp, sphavg_bool, plotstats = self.Validate()
        
        if not failed:
            int_file = self.int_file_txtCtrl.GetValue()
            spin_file = self.spin_file_txtCtrl.GetValue()
            output_file = self.output_file_txtCtrl.GetValue()
            print 'yay'
            
            tau_list = np.array(tau_list)
            csection_calc.cs_driver(int_file, spin_file, hkl_interval, w_interval, tau_list, 
                                    direction, temp, output_file, sphavg_bool, plotstats)
#            self.processManager.startAnalyticDispersion(int_file, spin_file)
#            self.processManager.startNumericDispersion(int_file, spin_file, data, kMin*pi, kMax*p
    
    def OnCancel(self, event):
        self.GetParent().Close()
    
    def Validate(self):
        """Checks that all values are the right type. Any field that is not of the right
        type will be turned pink.
        
        Returns failed, data, kMin, kMax
        failed is True if validation fails and false otherwise."""
        
        hklmin = self.hklmin_txtCtrl.GetValue()
        hklmax = self.hklmax_txtCtrl.GetValue()
        hklsteps = self.hkl_steps_ctrl.GetValue()
        
        wmin = self.wmin_txtCtrl.GetValue()
        wmax = self.wmax_txtCtrl.GetValue()
        wsteps = self.w_steps_ctrl.GetValue()
        
        kx = self.kx_txtCtrl.GetValue()
        ky = self.ky_txtCtrl.GetValue()
        kz = self.kz_txtCtrl.GetValue()
        
        zmin = self.zmin_ctrl.GetValue()
        zmax = self.zmax_ctrl.GetValue()
        colorbar_bool = self.color_bar_box.GetValue()
        
        temp = self.temp_ctrl.GetValue()
        sphavg_bool = self.spherical_avg_box.GetValue()
         
        bgColor = "pink"
        failed = False
        
        #Validate hkl values
        num_hklmin = None
        num_hklmax = None
        try:
            num_hklmin = float(hklmin)*np.pi
            self.hklmin_txtCtrl.SetBackgroundColour("white")
        except:
            self.hklmin_txtCtrl.SetBackgroundColour(bgColor)
            failed = True
        try:
            num_hklmax = float(hklmax)*np.pi
            self.hklmax_txtCtrl.SetBackgroundColour("white")
        except:
            self.hklmax_txtCtrl.SetBackgroundColour(bgColor)
            failed = True      
        
        #Validate w values
        num_wmin = None
        num_wmax = None
        try:
            num_wmin = float(wmin)
            self.wmin_txtCtrl.SetBackgroundColour("white")
        except:
            self.wmin_txtCtrl.SetBackgroundColour(bgColor)
            failed = True
        try:
            num_wmax = float(wmax)
            self.wmax_txtCtrl.SetBackgroundColour("white")
        except:
            self.wmax_txtCtrl.SetBackgroundColour(bgColor)
            failed = True      
            
        #Validate kx,ky,kz,temp,zmin,zmax values
        num_kx = None
        num_ky = None
        num_kz = None
        num_temp = None
        num_zmin = None
        num_zmax = None
        try:
            num_kx = float(kx)
            self.kx_txtCtrl.SetBackgroundColour("white")
        except:
            self.kx_txtCtrl.SetBackgroundColour(bgColor)
            failed = True
        try:
            num_ky = float(ky)
            self.ky_txtCtrl.SetBackgroundColour("white")
        except:
            self.ky_txtCtrl.SetBackgroundColour(bgColor)
            failed = True      
        try:
            num_kz = float(kz)
            self.kz_txtCtrl.SetBackgroundColour("white")
        except:
            self.kz_txtCtrl.SetBackgroundColour(bgColor)
            failed = True
        try:
            num_temp = float(temp)
            self.temp_ctrl.SetBackgroundColour("white")
        except:
            self.temp_ctrl.SetBackgroundColour(bgColor)
            failed = True
        try:
            num_zmin = float(zmin)
            self.zmin_ctrl.SetBackgroundColour("white")
        except:
            self.zmin_ctrl.SetBackgroundColour(bgColor)
            failed = True
        try:
            num_zmax = float(zmax)
            self.zmax_ctrl.SetBackgroundColour("white")
        except:
            self.zmax_ctrl.SetBackgroundColour(bgColor)
            failed = True
            
        #Validate File Fields
        int_str = self.int_file_txtCtrl.GetValue()
        spin_str = self.spin_file_txtCtrl.GetValue()
        tau_str = self.tau_file_txtCtrl.GetValue()
        out_str = self.output_file_txtCtrl.GetValue()
        if int_str:
            self.int_file_txtCtrl.SetBackgroundColour("white")
        else: 
            self.int_file_txtCtrl.SetBackgroundColour(bgColor)
            failed = True
        if spin_str:
            self.spin_file_txtCtrl.SetBackgroundColour("white")
        else: 
            self.spin_file_txtCtrl.SetBackgroundColour(bgColor)
            failed = True
        if tau_str:
            self.tau_file_txtCtrl.SetBackgroundColour("white")
        else: 
            self.tau_file_txtCtrl.SetBackgroundColour(bgColor)
            failed = True
        if out_str:
            self.output_file_txtCtrl.SetBackgroundColour("white")
        else: 
            self.output_file_txtCtrl.SetBackgroundColour(bgColor)
            failed = True
            
        direction = {}
        direction['kx'] = num_kx
        direction['ky'] = num_ky
        direction['kz'] = num_kz
        hkl_interval = [num_hklmin, num_hklmax, int(self.hkl_steps_ctrl.GetValue())]
        w_interval = [num_wmin, num_wmax, int(self.w_steps_ctrl.GetValue())]
        
        tau_text = ''
        try:
            tau_file = open(tau_str,'r')
            tau_text = tau_file.read()
            self.tau_file_txtCtrl.SetBackgroundColour("white")
        except:
            self.tau_file_txtCtrl.SetBackgroundColour(bgColor)
            failed = True

        items = tau_text.split()
        if len(items)%3 and not len(items):
            failed = True

        tau_list = []
        i = 0
        while not failed and i < len(items)-3:
            tau1, tau2, tau3 = None, None, None
            try:
                tau1 = float(items[i])
                tau2 = float(items[i+1])
                tau3 = float(items[i+2])
                self.tau_file_txtCtrl.SetBackgroundColour("white")
            except:
                self.tau_file_txtCtrl.SetBackgroundColour(bgColor)
                failed = True
            tau_list.append([tau1,tau2,tau3])
            i+=3
        
        self.Refresh()
#        self.window.Show(True,True)
        
        plotstats = [zmin, zmax, colorbar_bool]
        
        return failed, hkl_interval, w_interval, tau_list, direction, num_temp, sphavg_bool, plotstats

#class FormDialog(sc.SizedPanel):
class FormDialog(wx.Panel):
    def __init__(self, parent, id, procManager):
        self.parent = parent
        #self.process_list = []
        self.processManager = procManager
        
        #valstyle=wx.WS_EX_VALIDATE_RECURSIVELY
        #sc.SizedPanel.__init__(self, parent, -1,
        #                style= wx.RESIZE_BORDER)#| wx.WS_EX_VALIDATE_RECURSIVELY)
        wx.Panel(self,parent, -1, style = wx.RESIZE_BORDER)
        self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)
        pane = self
        pane.SetSizerType("vertical")
               
        print 'FormDialog called'
        #FilePane = sc.SizedPanel(pane, -1)
        FilePane = wx.Panel(pane, -1)
        FilePane.SetSizerType("vertical")
        FilePane.SetSizerProps(expand=True)
   
        self.interactionfile=''
        self.interactionfilectrl=wx.StaticText(FilePane, -1, "Interaction File:%s"%(self.interactionfile,))
        b = wx.Button(FilePane, -1, "Browse")
        self.Bind(wx.EVT_BUTTON, self.OnOpenInt, b)
        
        self.spinfile=''
        self.spinfilectrl=wx.StaticText(FilePane, -1, "Spin File:%s"%(self.spinfile,))
        b = wx.Button(FilePane, -1, "Browse")
        self.Bind(wx.EVT_BUTTON, self.OnOpen, b)
        



        self.data={}
        self.data['kx']=str(0.0)
        self.data['ky']=str(0.0)
        self.data['kz']=str(1.0)
        #DirectionPane = sc.SizedPanel(pane, -1)
        DirectionPane = wx.Panel(pane, -1)
        DirectionPane.SetSizerType("vertical")
        DirectionPane.SetSizerProps(expand=True)
        wx.StaticText(DirectionPane, -1, "Scan Direction")
        
        #DirectionsubPane = sc.SizedPanel(pane, -1
        DirectionsubPane = wx.Panel(pane, -1)
        DirectionsubPane.SetSizerType("horizontal")
        DirectionsubPane.SetSizerProps(expand=True)

        

        DirectionsubPane.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)
        WalkTree(pane)
        
        wx.StaticText(DirectionsubPane, -1, "qx")
        qx=wx.TextCtrl(DirectionsubPane, -1, self.data['kx'],validator=mFormValidator(self.data,'kx'))
        #print 'qx', qx
        #self.Bind(wx.EVT_TEXT, self.Evtqx, qx)
        wx.StaticText(DirectionsubPane, -1, "qy")
        qy=wx.TextCtrl(DirectionsubPane, -1, self.data['ky'],validator=mFormValidator(self.data,'ky'))
        #self.Bind(wx.EVT_TEXT, self.Evtqx, qy)
        wx.StaticText(DirectionsubPane, -1, "qz")
        qz=wx.TextCtrl(DirectionsubPane, -1, self.data['kz'],validator=mFormValidator(self.data,'kz'))
        #self.Bind(wx.EVT_TEXT, self.Evtqx, qz)
        #print 'Directed'


        wx.StaticText(DirectionsubPane, -1, "Number of divisions")
        
        spinctrl = wx.SpinCtrl(DirectionsubPane, -1, "", (30, 50))
        spinctrl.SetRange(1,100)
        spinctrl.SetValue(self.data['step'])
        self.Bind(wx.EVT_SPINCTRL,self.EvtSpinCtrl)
        self.spinctrl=spinctrl
        
        
        #Add Range
        self.kRange = {}
        self.kRange['kMin'] = str(0)
        self.kRange['kMax'] = str(2)
        
        wx.StaticText(pane, -1, "k Range")
        #kRangePane = sc.SizedPanel(pane, -1
        kRangePane = wx.Panel(pane, -1)
        kRangePane.SetSizerType("horizontal")
        
        wx.StaticText(kRangePane, -1, "Min =")
        self.kMinCtrl = wx.TextCtrl(kRangePane, -1, self.kRange['kMin'],validator=mFormValidator(self.kRange,'kMin'))
        wx.StaticText(kRangePane, -1, "*pi")
        
        wx.StaticText(kRangePane, -1, "    Max =")
        self.kMaxCtrl = wx.TextCtrl(kRangePane, -1, self.kRange['kMax'],validator=mFormValidator(self.kRange,'kMax'))
        wx.StaticText(kRangePane, -1, "*pi")
        
        
        
        # add dialog buttons
        
        #Getting rid of standard button function
        #self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL))
        
        #btnPane = sc.SizedPanel(pane, -1)
        btnPane = wx.Panel(pane, -1)
        btnPane.SetSizerType("horizontal")
        btnPane.SetSizerProps(expand=True)
        
        self.btnOk = wx.Button(btnPane,-1, "Ok")
        #self.btnOk.SetDefault()
        #btnsizer.Add(self.btnOk)

        btnCancel = wx.Button(btnPane, -1, "Cancel")
        #btnsizer.Add(btn)
        
        #self.GetSizer().Add(btnsizer)
        
        #intercept OK button click event
        self.Bind(wx.EVT_BUTTON, self.OnOk, self.btnOk)
        
        #intercept Cancel button click event
        self.Bind(wx.EVT_BUTTON, self.OnCancel, btnCancel)
        

        
        #self.TransferDataToWindow()
        # a little trick to make sure that you can't resize the dialog to
        # less screen space than the controls need
        self.Fit()
        size = self.GetSize()
        size = (size[0]+5, size[1]+35)#I think borders may not be included because size is consisitantly too small
        self.parent.SetSize(size)
        self.parent.SetMinSize(size)
        #This trick is not working because the self.GetSize() is too small
        #self.parent.SetMinSize((645, 245))
        #self.parent.SetMinSize((400,400))
        
           
                
        #Text editor
        #self.editorWin = RichTextFrame(self, -1, "Editor",
        #                    size=(620, 250),
        #                    style = wx.DEFAULT_FRAME_STYLE)
        #self.editorWin.Show(True)
        self.editorWin = showEditorWindow(self, "Spinwave File Editor")

        
        
    def EvtSpinCtrl(self,evt):
        print self.__dict__
        print 'event',evt.__dict__
        #spinCtrl=evt.control
        self.data['step']=self.spinctrl.GetValue()
        #sc.SizedDialog.GetW
        #self.G
        #self.kx=text
 
       


    def OnOpenInt(self,event):
        # Create the dialog. In this case the current directory is forced as the starting
        # directory for the dialog, and no default file name is forced. This can easilly
        # be changed in your program. This is an 'open' dialog, and allows multitple
        # file selections as well.
        #
        # Finally, if the directory is changed in the process of getting files, this
        # dialog is set up to change the current working directory to the path chosen.

        #defaultDir=os.getcwd()
        #defaultDir=r'C:\polcorrecter\data'
        confBase = wx.ConfigBase.Create()
        confBase.SetStyle(wx.CONFIG_USE_LOCAL_FILE)
        defaultDir=confBase.Get().GetPath()
        #defaultDir=wx.ConfigBase.Get().GetPath()
        wildcard="files (*.txt)|*.txt|All files (*.*)|*.*"
        dlg = wx.FileDialog(
            self, message="Choose an Interaction file",
            defaultDir=defaultDir,
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.CHANGE_DIR
            )

        # Show the dialog and retrieve the user response. If it is the OK response,
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            # This returns a Python list of files that were selected.
            paths = dlg.GetPaths()
            #self.log.WriteText('You selected %d files:' % len(paths))
            self.interactionfile=paths[0].encode('ascii')
            self.interactionfilectrl.SetLabel("Interaction File:%s"%(self.interactionfile,))
            #wx.StaticText(FilePane, -1, "CellFile:%s"%(self.groupdata['cellfile'],))
            
            #display in richtextcontrol
            #self.interactionsRtc.LoadFile(paths[0])
            self.editorWin.loadInteractions(paths[0])
            
        # Destroy the dialog. Don't do this until you are done with it!
        # BAD things can happen otherwise!
        dlg.Destroy()


class MyApp(wx.App):
    def __init__(self, redirect=False, filename=None, useBestVisual=False, clearSigInt=True):
        wx.App.__init__(self,redirect,filename,clearSigInt)


    def OnInit(self):
        return True
    

if __name__=='__main__':
    from spinwaves.utilities.Processes import ProcessManager
    app=MyApp()
    frame1 = wx.Frame(None, -1, "Spinwaves")#, size = (600,600))
    dlg=CrossSectionPanel(None, parent=frame1,id=-1)
    frame1.Show()
    if 0:
        frame1 = wx.Frame(None, -1, "Spinwaves")
        dlg=FormDialog(parent=frame1,id=-1)
        frame1.Show()
        result=dlg.ShowModal()
        if result==wx.ID_OK:
            dlg.Validate()
            print "OK"
            dlg.TransferDataFromWindow()
            print dlg.data
        else:
            print "Cancel"
    
        dlg.Destroy()

    app.MainLoop()
