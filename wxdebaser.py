#!/usr/bin/env python

"""
wxdebaser
v0.531 - 12162011
  * Added Ctrl+Q keyboard shortcut
  * Initial focus set to file_button

v0.53 - 12162011
  * Added check for exist & correct version of debaser.py
  * Created global variable for window title
  * Modified console box behavior

v0.52 - 12162011
  * Added extended options (overwrite & nsfw)
  * Added construct-command method to break out command construction
  * Fixed typo in info dialog box

v0.511 - 12142011
  * Made version output match debaser.py format
  * Removed extraneous variables
  * Added tons of comments
  * Removed debug console output
  * Fixed a bug where limit value wasn't getting passed to debaser.py (oops! D:)

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
import sys # for early exit on failed debaser check
from optparse import OptionParser

current_version = '%prog 0.531-12162011'
window_title = 'Wxdebaser'

"""
Wxdebaser(wx.Frame)
  Class to construct the Wxdebaser window and
  make everything work beautifully.
"""
class Wxdebaser(wx.Frame):

    """
    __init__(parent, title)
      Initializes the Wxdebaser object.
      
      parent - the parent object [Wxdebaser]
      title - window title [STRING]
      
      returns nothing
    """
    def __init__(self, parent, title):
        
        self.debaser_dir = os.path.split(os.path.abspath(__file__))[0] # changed to locate debaser.py in same directory as wxdebaser.py (so you can put it anywhere!)
        self.default_dir = os.path.join("~","Downloads")
        
        super(Wxdebaser, self).__init__(parent, title=title, size=(350, 300))
        
        # bind events
        self.Bind(wx.EVT_BUTTON, self.run_app, id=1)
        self.Bind(wx.EVT_BUTTON, self.file_select, id=2)

        # bind ctrl+q key combo
        randomId = wx.NewId()
        self.Bind(wx.EVT_MENU, self.quit_key, id=randomId)
        accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('q'), randomId)])
        self.SetAcceleratorTable(accel_tbl)

        # check debaser version
        required_version = 0.54
        if not(self.check_debaser(required_version)):
            sys.exit(1)

        self.SetIcon(wx.Icon(os.path.join(self.debaser_dir, 'd_icon.ico'), wx.BITMAP_TYPE_ICO))
        self.InitUI()

        # set first focus on file button, to allow for keyboard input
        self.file_button.SetFocus()

        self.Centre()
        self.Show()
    
    """
    InitUI()
      Initializes the user interface.
   
      returns nothing
    """
    def InitUI(self):
        # create the panel
        panel = wx.Panel(self)

        # get system font
        font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(8)

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
        self.console_output.SetFont(font)
        hbox4.Add(self.console_output, proportion=1, border=10)
        vbox.Add(hbox4, flag=wx.EXPAND|wx.ALL, border=10)

        # create extended options box
        hbox4_5 = wx.BoxSizer(wx.HORIZONTAL)
        self.over_checkbox = wx.CheckBox(panel, -1, 'Overwrite')
        hbox4_5.Add(self.over_checkbox, flag=wx.RIGHT|wx.CENTRE, border=8)
        self.nsfw_checkbox = wx.CheckBox(panel, -1, 'Allow nsfw')
        hbox4_5.Add(self.nsfw_checkbox, proportion=1, border=8)
        vbox.Add(hbox4_5, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)

        # create buttons box
        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        self.log_checkbox = wx.CheckBox(panel, -1, 'Log Output')
        hbox5.Add(self.log_checkbox, flag=wx.RIGHT|wx.CENTRE, border=8)
        go_button = wx.Button(panel, 1, '&Go!')
        hbox5.Add(go_button, proportion=1, border=10)
        vbox.Add(hbox5, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)
        
        panel.SetSizer(vbox)

    """
    run_app(event)
      Run the debaser.py application on an event.

      event - event passed by wx button [wx.__core.PyEventBinder]
   
      returns nothing
    """
    def run_app(self, event):
        subr_name = self.subr_text.GetValue()
        filter_name = self.filt_option.GetValue()
        limit = self.limit_sc.GetValue()
        over_sel = self.over_checkbox.GetValue()
        nsfw_sel = self.nsfw_checkbox.GetValue()
        if (subr_name == ''):
            wx.MessageBox('Subreddit field was left blank.\nPlease enter a subreddit!', 'ERROR', wx.OK | wx.ICON_ERROR)
            return
        if not(self.check_limit(limit)):
            return
        os.chdir(os.path.expanduser(self.file_text.GetValue())) # change to selected directory
        cmd = self.construct_command(subr=subr_name, filt=filter_name, limit=limit, over_flag=over_sel, nsfw_flag=nsfw_sel)
        self.run_subprocess(cmd)
        if (self.log_checkbox.GetValue()):
            self.write_to_log()

    """
    run_subprocess(cmd)
      Runs the debaser.py script as a subprocess and
      captures stdout to return to console_output widget.
   
      cmd - command string [STRING]

      returns nothing
    """
    def run_subprocess(self, cmd):
        self.console_log = ''
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in proc.stdout:
            wx.CallAfter(self.console_output.AppendText, line)
            self.console_log = self.console_log + line

    """
    write_to_log()
      Write to a log file in the working directory.

      returns nothing
    """
    def write_to_log(self):
        now = datetime.datetime.now()
        f = open(os.path.join(self.file_text.GetValue(), '.debaser-log'), 'a')
        f.write(str(now) + '\n')
        f.write(self.console_log)
        f.close()

    """
    check_limit(limit)
      Check to see if the limit value is huge and ask for
      permission to continue.

      limit - limit value [INT]

      returns boolean
    """
    def check_limit(self, limit):
        if (limit > 20):
            choice = wx.MessageBox('You have selected a large limit.\nPlease note that downloading this will take a very long time\nand will most likely time out.\n\nAre you sure you want to continue?', 'Large Limit Detected', wx.YES_NO|wx.ICON_INFORMATION)
            if choice == wx.YES:
                return True
            else:
                return False
        # check for an extremely large limit value
        else:
            return True

    """
    file_select(event)
      Open the directory selection dialog and set
      the value of self.file_text with the results.

      event - event passed by the wx button [wx.__core.PyEventBinder]

      returns nothing
    """
    def file_select(self, event):
        dlg = wx.DirDialog(self, "Choose a destination directory:", style=wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON, defaultPath=os.path.expanduser(self.default_dir))
        choice = dlg.ShowModal()
        if (choice == wx.ID_OK):
            self.file_text.SetValue(dlg.GetPath())
        else:
            return

    """
    construct_command(subr, filt, limit, over_flag, nsfw_flag)
      Construct a debaser.py command line.

      subr - subreddit name [STRING]
      filt - subreddit filter (hot, controversial, new, top) [STRING]
      limit - limit of submissions [INT]
      over_flag - overwrite flag [BOOLEAN]
      nsfw_flag - nsfw flag [BOOLEAN]
      
      returns [LIST OF STRINGS]
    """
    def construct_command(self, subr='pics', filt='hot', limit=5, over_flag=False, nsfw_flag=False):
        cmd = ["python", os.path.join(self.debaser_dir, "debaser.py"), "--subreddit", subr, "--filter", filt, "--limit", str(limit), "-v"]
        if over_flag: cmd.append("-o")
        if nsfw_flag: cmd.append("-n")
        return cmd

    """
    check_debaser(req_ver)
      Check to see if debaser.py script exists & is correct version
     
      req_ver - required version of debaser.py [FLOAT]

      returns [BOOLEAN]
    """
    def check_debaser(self, req_ver):
        check_path = os.path.join(self.debaser_dir, "debaser.py")
        check_version = ''
        if os.path.exists(check_path):
            cmd = ["python", check_path, "--version"]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in proc.stdout:            
                check_version = check_version + line
            if (float(check_version[11:15]) < req_ver):
                wx.MessageBox('You are using an old version of debaser.py (v' + check_version[11:15] + ').\nThis version of wxdebaser is built for debaser.py v' + str(req_ver) + ' or later. \nSome features may not operate properly.\n\nThe latest version can be downloaded here:\nhttps://github.com/askulie/debaser','Wxdebaser: Old debaser.py detected',wx.OK|wx.ICON_WARNING)
                return True
            else:
                return True
        else:
            wx.MessageBox('The debaser.py script was not found in the wxdebaser directory.\nPlease install debaser.py (v' + str(req_ver) + ' or later) into the same directory as wxdebaser.py.\n\nThe latest version can be downloaded here:\nhttps://github.com/askulie/debaser ', 'Wxdebaser: Critical Error', wx.OK|wx.ICON_ERROR)
            return False

    """
    quit_key (event)
      Exit the program if key event is pressed

      event - event passed by the wx key combo [wx.__core.PyEventBinder]

      returns nothing
    """
    def quit_key(self, event):
        sys.exit(0)
        
if __name__ == '__main__':
    
    # add options for parser
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage, version=current_version)
    (options, args) = parser.parse_args()

    app = wx.App()
    Wxdebaser(None, title=window_title) # changed to use global variable at top for title
    app.MainLoop()
