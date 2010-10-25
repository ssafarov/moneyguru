# Created By: Virgil Dupras
# Created On: 2010-10-24
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from ..model.account import ACCOUNT_SORT_KEY
from .base import PanelGUIObject
from .column import Column
from .table import GUITable, Row

class ExportAccountTable(GUITable, PanelGUIObject):
    def __init__(self, view, export_panel):
        PanelGUIObject.__init__(self, view, export_panel)
        self.document = export_panel.document
        GUITable.__init__(self)
    
    #--- Override
    def _fill(self):
        accounts = sorted(self.document.accounts, key=ACCOUNT_SORT_KEY)
        for account in accounts:
            self.append(ExportAccountTableRow(self, account))
    
    #--- Event Handlers
    def panel_loaded(self):
        self.refresh()
        self.view.refresh()
    

class ExportAccountTableRow(Row):
    def __init__(self, table, account):
        Row.__init__(self, table)
        self.account = account
    
    #--- Public
    def load(self):
        pass # nothing to load
    
    def save(self):
        pass # read-only
    
    #--- Properties
    @property
    def name(self):
        return self.account.name
    
    @property
    def export(self):
        return self.table.panel.is_exported(self.account.name)
    
    @export.setter
    def export(self, value):
        self.table.panel.set_exported(self.account.name, value)
    
