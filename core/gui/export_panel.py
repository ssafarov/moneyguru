# Created By: Virgil Dupras
# Created On: 2010-10-24
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.notify import Broadcaster

from ..saver.qif import save as save_qif
from .base import MainWindowPanel

class ExportPanel(MainWindowPanel, Broadcaster):
    def __init__(self, view, mainwindow):
        MainWindowPanel.__init__(self, view, mainwindow)
        Broadcaster.__init__(self)
    
    def _load(self):
        self.exported_names = set()
        self.export_all = True
        self.export_path = None
        self.notify('panel_loaded')
    
    def _save(self):
        accounts = self.document.accounts
        if not self.export_all:
            accounts = [a for a in accounts if a.name in self.exported_names]
        save_qif(self.export_path, accounts)
    
    #--- Public
    def is_exported(self, name):
        return name in self.exported_names
    
    def set_exported(self, name, value):
        if value:
            self.exported_names.add(name)
        else:
            self.exported_names.discard(name)
        self.view.set_export_button_enabled(bool(self._export_all or self.exported_names))
    
    #--- Properties
    @property
    def export_all(self):
        return self._export_all
    
    @export_all.setter
    def export_all(self, value):
        self._export_all = value
        self.view.set_table_enabled(not self._export_all)
        self.view.set_export_button_enabled(bool(self._export_all or self.exported_names))
    
