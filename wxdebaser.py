#!/usr/bin/env python

"""
wxdebaser
v0.51 - 12132011
  * Added most of the working features
  * Can select directories and such
  * Log file is working
  * Added command line options using optparse (just for version information)

v0.50 - 12132011

A wxWidgets-based graphical front-end for debaser

Copyright (c) 2011 Andy Kulie.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import wx
import subprocess
import os
import datetime # for timestamping logfiles
from optparse import OptionParser
#import threading

current_version = 'v0.51 - 12132011'

class Wxdebaser(wx.Frame):
    
    def __init__(self, parent, title):
        
        self.debaser_dir = os.path.split(os.path.abspath(__file__))[0] # changed to locate debaser.py in same directory as wxdebaser.py (so you can put it anywhere!)
        self.current_dir = os.getcwd() # add an option to select directory instead of this
        self.default_dir = os.path.join("~","Downloads")

        super(Wxdebaser, self).__init__(parent, title=title, size=(350, 300))
        
        # bind events
        self.Bind(wx.EVT_BUTTON, self.run_app, id=1)
        self.Bind(wx.EVT_BUTTON, self.file_select, id=2)
        
        self.SetIcon(wx.Icon(os.path.join(self.debaser_dir, 'd_icon.ico'), wx.BITMAP_TYPE_ICO))
        self.InitUI()
        self.Centre()
        self.Show()
    
    def InitUI(self):
        # create the panel
        panel = wx.Panel(self)

        # get system font
        font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        font2 = font
        font.SetPointSize(9)
        font2.SetPointSize(8)

        # set up main vertical box sizer
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # create file destination box
        hbox0 = wx.BoxSizer(wx.HORIZONTAL)
        file_label = wx.StaticText(panel, label='Destination:')
        hbox0.Add(file_label, flag=wx.RIGHT|wx.CENTRE, border=8)
        self.file_text = wx.TextCtrl(panel)
        self.file_text.SetValue(self.default_dir)
        hbox0.Add(self.file_text, proportion=4)
        self.file_button = wx.Button(panel, 2, '...')
        hbox0.Add(self.file_button, proportion=1)
        vbox.Add(hbox0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        # create subreddit box
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        subr_label = wx.StaticText(panel, label='Subreddit:')
        hbox1.Add(subr_label, flag=wx.RIGHT|wx.CENTRE, border=8)
        self.subr_text = wx.TextCtrl(panel)
        self.subr_text.SetValue('pics')
        hbox1.Add(self.subr_text, proportion=1)
        vbox.Add(hbox1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)
        
        # create filter box
        filters = ['hot', 'new', 'controversial', 'top']
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        filt_label = wx.StaticText(panel, label='Filter:')
        hbox2.Add(filt_label, flag=wx.RIGHT|wx.CENTRE, border=8)
        self.filt_option = wx.ComboBox(panel, -1, value=filters[0], choices=filters, style=wx.CB_READONLY)
        hbox2.Add(self.filt_option, proportion=1)
        vbox.Add(hbox2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)
        
        # create limit box
        limit = 5
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        limit_label = wx.StaticText(panel, label='Limit:')
        hbox3.Add(limit_label, flag=wx.RIGHT|wx.CENTRE, border=8)
        self.limit_sc = wx.SpinCtrl(panel, -1, '')
        self.limit_sc.SetRange(1,255)
        self.limit_sc.SetValue(limit)
        hbox3.Add(self.limit_sc, proportion=1)
        vbox.Add(hbox3, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)
        
        # create console box
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        self.console_output = wx.TextCtrl(panel, -1, style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.console_output.SetFont(font2)
        hbox4.Add(self.console_output, proportion=1, border=10)
        vbox.Add(hbox4, flag=wx.EXPAND|wx.ALL, border=10)

        # create buttons box
        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        self.log_checkbox = wx.CheckBox(panel, -1, 'Log Output')
        hbox5.Add(self.log_checkbox, flag=wx.RIGHT|wx.CENTRE, border=8)
        go_button = wx.Button(panel, 1, '&Go!')
        hbox5.Add(go_button, proportion=1, border=10)
        vbox.Add(hbox5, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)
        
        panel.SetSizer(vbox)

        
    def run_app(self, event):
        # run the actual app here
        print "Values: subreddit " + self.subr_text.GetValue() + " using filter " +  self.filt_option.GetValue() + " with limit " + str(self.limit_sc.GetValue())
        subr_name = self.subr_text.GetValue()
        filter_name = self.filt_option.GetValue()
        limit = self.limit_sc.GetValue()
        if (subr_name == ''):
            wx.MessageBox('Subreddit field was left blank.\nPlease enter a subreddit!', 'ERROR', wx.OK | wx.ICON_ERROR)
            print "Error encountered.  Subreddit field was left blank."
            return
        if not(self.check_limit(limit)):
            return
        os.chdir(os.path.expanduser(self.file_text.GetValue())) # change to selected directory
        cmd = ["python", os.path.join(self.debaser_dir, "debaser.py"), "--subreddit", self.subr_text.GetValue(), "--filter", filter_name, " --limit ", str(limit), "-v"]
        print "Command generated:"
        print cmd
        print "Starting thread..."
        #thread = threading.Thread(target=self.run_subprocess, args=(cmd,))
        #thread.setDaemon(True)
        #thread.start()
        self.run_subprocess(cmd)
        if (self.log_checkbox.GetValue()):
            self.write_to_log()

    def run_subprocess(self, cmd):
        print "Initiating subprocess..."
        self.console_log = ''
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in proc.stdout:
            wx.CallAfter(self.console_output.AppendText, line)
            self.console_log = self.console_log + line
        print "Subprocess complete!"

    def write_to_log(self):
        print "Writing to log file..."
        print self.console_log
        now = datetime.datetime.now()
        f = open(os.path.join(self.file_text.GetValue(), '.debaser-log'), 'a')
        f.write(str(now) + '\n')
        f.write(self.console_log)
        f.close()
        pass

    def check_limit(self, limit):
        print "Checking limit..." + str(limit)
        if (limit > 20):
            print "Large limit detected.  Asking for confirmation."
            choice = wx.MessageBox('You have selected a large limit.\nPlease note that downloading this will take a very long time\nand will most likely time out.\n\nAre you usure you want to continue?', 'Large Limit Detected', wx.YES_NO|wx.ICON_INFORMATION)
            if choice == wx.YES:
                print "Going forward with large limit."
                return True
            else:
                print "Cancelled."
                return False
        # check for an extremely large limit value
        else:
            print "Large limit not detected."
            return True

    def file_select(self, event):
        print "Directory select dialog..."
        dlg = wx.DirDialog(self, "Choose a destination directory:", style=wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON, defaultPath=os.path.expanduser(self.default_dir))
        choice = dlg.ShowModal()
        if (choice == wx.ID_OK):
            print "Chose " + dlg.GetPath()
            self.file_text.SetValue(dlg.GetPath())
        else:
            return

if __name__ == '__main__':
    
    # add options for parser
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage, version=current_version)
    (options, args) = parser.parse_args()

    app = wx.App()
    Wxdebaser(None, title='Wxdebaser')
    app.MainLoop()


"""
Still to be done:
    - Implement log file
    - Figure out a prettier way to access the debaser.py file without finding it in /opt/debaser
    - Add a field to enter the desired path to download to
    - Modify debaser.py to allow for file overwrite checking
"""
