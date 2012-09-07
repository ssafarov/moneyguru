# Created By: Virgil Dupras
# Created On: 2009-12-30
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import os
import os.path as op
import shutil
import json
from argparse import ArgumentParser

from setuptools import setup, Extension

from hscommon import sphinxgen
from hscommon.plat import ISOSX
from hscommon.build import (print_and_do, copy_packages, build_all_cocoa_locs, move_all, move,
    copy, symlink, hardlink, add_to_pythonpath, copy_sysconfig_files_for_embed,
    build_cocoalib_xibless)
from hscommon import loc
from hscommon.util import ensure_folder, modified_after

def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--clean', action='store_true', dest='clean',
        help="Clean build folder before building")
    parser.add_argument('--doc', action='store_true', dest='doc',
        help="Build only the help file")
    parser.add_argument('--loc', action='store_true', dest='loc',
        help="Build only localization")
    parser.add_argument('--updatepot', action='store_true', dest='updatepot',
        help="Generate .pot files from source code.")
    parser.add_argument('--mergepot', action='store_true', dest='mergepot',
        help="Update all .po files based on .pot files.")
    parser.add_argument('--cocoamod', action='store_true', dest='cocoamod',
        help="Build only Cocoa modules")
    parser.add_argument('--ext', action='store_true', dest='ext',
        help="Build only ext modules")
    parser.add_argument('--xibless', action='store_true', dest='xibless',
        help="Build only xibless UIs")
    args = parser.parse_args()
    return args

def build_xibless(dest='cocoa/autogen'):
    import xibless
    ensure_folder(dest)
    FNPAIRS = [
        ('lookup.py', 'MGLookup_UI'),
        ('schedule_scope_dialog.py', 'MGRecurrenceScopeDialog_UI'),
        ('custom_date_range_dialog.py', 'MGCustomDateRangePanel_UI'),
        ('account_reassign_panel.py', 'MGAccountReassignPanel_UI'),
        ('csv_layout_name.py', 'MGCSVLayoutNameDialog_UI'),
        ('csv_import_options.py', 'MGCSVImportOptions_UI'),
        ('import_window.py', 'MGImportWindow_UI'),
        ('export_panel.py', 'MGExportPanel_UI'),
        ('budget_panel.py', 'MGBudgetPanel_UI'),
        ('schedule_panel.py', 'MGSchedulePanel_UI'),
        ('mass_editing_panel.py', 'MGMassEditionPanel_UI'),
        ('transaction_panel.py', 'MGTransactionInspector_UI'),
        ('account_panel.py', 'MGAccountProperties_UI'),
        ('newtab_view.py', 'MGEmptyView_UI'),
        ('docprops_view.py', 'MGDocPropsView_UI'),
        ('cashculator_view.py', 'MGCashculatorView_UI'),
        ('transaction_view.py', 'MGTransactionView_UI'),
        ('account_view.py', 'MGAccountView_UI'),
        ('account_sheet_view.py', 'MGAccountSheetView_UI'),
        ('date_range_selector.py', 'MGDateRangeSelector_UI'),
        ('main_window.py', 'MGMainWindowController_UI'),
    ]
    for srcname, dstname in FNPAIRS:
        srcpath = op.join('cocoa', 'ui', srcname)
        dstpath = op.join(dest, dstname)
        if modified_after(srcpath, dstpath + '.h'):
            xibless.generate(srcpath, dstpath, localizationTable='Localizable')

def build_cocoa(dev):
    print("Building xibless UIs")
    build_cocoalib_xibless()
    build_xibless()
    print("Building the cocoa layer")
    ensure_folder('build/py')
    build_cocoa_proxy_module()
    build_cocoa_bridging_interfaces()
    from pluginbuilder import copy_embeddable_python_dylib, get_python_header_folder, collect_dependencies
    copy_embeddable_python_dylib('build')
    symlink(get_python_header_folder(), 'build/PythonHeaders')
    tocopy = ['core', 'hscommon', 'cocoalib/cocoa']
    copy_packages(tocopy, 'build')
    if dev:
        hardlink('cocoa/mg_cocoa.py', 'build/mg_cocoa.py')
    else:
        copy('cocoa/mg_cocoa.py', 'build/mg_cocoa.py')
    os.chdir('build')
    collect_dependencies('mg_cocoa.py', 'py', excludes=['PyQt4'])
    os.chdir('..')
    if dev:
        copy_packages(tocopy, 'build/py', create_links=True)
    copy_sysconfig_files_for_embed('build/py')
    os.chdir('cocoa')
    print('Generating Info.plist')
    # We import this here because we don't want opened module to prevent us replacing .pyd files.
    from core.app import Application as MoneyGuruApp
    contents = open('InfoTemplate.plist').read()
    contents = contents.replace('{version}', MoneyGuruApp.VERSION)
    open('Info.plist', 'w').write(contents)
    print("Building the XCode project")
    args = ['-project moneyguru.xcodeproj']
    if dev:
        args.append('-configuration dev')
    else:
        args.append('-configuration release')
    args = ' '.join(args)
    os.system('xcodebuild {0}'.format(args))
    os.chdir('..')
    print("Creating the run.py file")
    subfolder = 'dev' if dev else 'release'
    app_path = 'cocoa/build/{0}/moneyGuru.app'.format(subfolder)
    tmpl = open('run_template_cocoa.py', 'rt').read()
    run_contents = tmpl.replace('{{app_path}}', app_path)
    open('run.py', 'wt').write(run_contents)

def build_qt(dev):
    qrc_path = op.join('qt', 'mg.qrc')
    pyrc_path = op.join('qt', 'mg_rc.py')
    print_and_do("pyrcc4 -py3 {0} > {1}".format(qrc_path, pyrc_path))
    print("Creating the run.py file")
    shutil.copy('run_template_qt.py', 'run.py')

def build_help(dev):
    if dev:
        print("Generating devdocs")
        print_and_do('sphinx-build devdoc devdoc_html')
    print("Generating Help")
    platform = 'osx' if ISOSX else 'win'
    current_path = op.abspath('.')
    confpath = op.join(current_path, 'help', 'conf.tmpl')
    help_basepath = op.join(current_path, 'help', 'en')
    help_destpath = op.join(current_path, 'build', 'help')
    changelog_path = op.join(current_path, 'help', 'changelog')
    tixurl = "https://hardcoded.lighthouseapp.com/projects/31473-moneyguru/tickets/{0}"
    confrepl = {'platform': platform}
    sphinxgen.gen(help_basepath, help_destpath, changelog_path, tixurl, confrepl, confpath)

def build_localizations(ui):
    print("Building localizations")
    loc.compile_all_po('locale')
    loc.compile_all_po(op.join('hscommon', 'locale'))
    loc.merge_locale_dir(op.join('hscommon', 'locale'), 'locale')
    if ui == 'cocoa':
        print("Creating lproj folders based on .po files")
        enlproj = op.join('cocoa', 'en.lproj')
        for lang in loc.get_langs('locale'):
            if lang == 'en':
                continue
            pofile = op.join('locale', lang, 'LC_MESSAGES', 'ui.po')
            dest_lproj = op.join('cocoa', lang + '.lproj')
            loc.po2allxibstrings(pofile, enlproj, dest_lproj)
            loc.po2strings(pofile, op.join(enlproj, 'Localizable.strings'), op.join(dest_lproj, 'Localizable.strings'))
            pofile = op.join('cocoalib', 'locale', lang, 'LC_MESSAGES', 'cocoalib.po')
            loc.po2allxibstrings(pofile, op.join('cocoalib', 'en.lproj'), op.join('cocoalib', lang + '.lproj'))
        build_all_cocoa_locs('cocoalib')
        build_all_cocoa_locs('cocoa')
    elif ui == 'qt':
        loc.compile_all_po(op.join('qtlib', 'locale'))
        loc.merge_locale_dir(op.join('qtlib', 'locale'), 'locale')
    if op.exists(op.join('build', 'locale')):
        shutil.rmtree(op.join('build', 'locale'))
    shutil.copytree('locale', op.join('build', 'locale'), ignore=shutil.ignore_patterns('*.po', '*.pot'))

def build_updatepot():
    print("Building .pot files from source files")
    print("Building core.pot")
    loc.generate_pot(['core'], op.join('locale', 'core.pot'), ['tr'])
    print("Building columns.pot")
    loc.generate_pot(['core'], op.join('locale', 'columns.pot'), ['trcol'])
    print("Building ui.pot")
    loc.generate_pot(['qt'], op.join('locale', 'ui.pot'), ['tr'])
    print("Building hscommon.pot")
    loc.generate_pot(['hscommon'], op.join('hscommon', 'locale', 'hscommon.pot'), ['tr'])
    print("Building qtlib.pot")
    loc.generate_pot(['qtlib'], op.join('qtlib', 'locale', 'qtlib.pot'), ['tr'])
    print("Enhancing ui.pot with Cocoa's strings files")
    loc.allstrings2pot(op.join('cocoa', 'en.lproj'), op.join('locale', 'ui.pot'),
        excludes={'core', 'message', 'columns'})

def build_mergepot():
    print("Updating .po files using .pot files")
    loc.merge_pots_into_pos('locale')
    loc.merge_pots_into_pos(op.join('hscommon', 'locale'))
    loc.merge_pots_into_pos(op.join('qtlib', 'locale'))

def build_ext():
    print("Building C extensions")
    exts = []
    exts.append(Extension('_amount', [op.join('core', 'modules', 'amount.c')]))
    setup(
        script_args = ['build_ext', '--inplace'],
        ext_modules = exts,
    )
    move_all('_amount*', op.join('core', 'model'))

def build_cocoa_ext(extname, dest, source_files, extra_frameworks=(), extra_includes=()):
    extra_link_args = ["-framework", "CoreFoundation", "-framework", "Foundation"]
    for extra in extra_frameworks:
        extra_link_args += ['-framework', extra]
    ext = Extension(extname, source_files, extra_link_args=extra_link_args, include_dirs=extra_includes)
    setup(script_args=['build_ext', '--inplace'], ext_modules=[ext])
    fn = extname + '.so'
    assert op.exists(fn)
    move(fn, op.join(dest, fn))

def build_cocoa_proxy_module():
    print("Building Cocoa Proxy")
    import objp.p2o
    objp.p2o.generate_python_proxy_code('cocoalib/cocoa/CocoaProxy.h', 'build/CocoaProxy.m')
    build_cocoa_ext("CocoaProxy", 'cocoalib/cocoa',
        ['cocoalib/cocoa/CocoaProxy.m', 'build/CocoaProxy.m', 'build/ObjP.m', 
            'cocoalib/HSErrorReportWindow.m', 'cocoa/autogen/HSErrorReportWindow_UI.m'],
        ['AppKit', 'CoreServices'],
        ['cocoalib', 'cocoa/autogen'])

def build_cocoa_bridging_interfaces():
    print("Building Cocoa Bridging Interfaces")
    import objp.o2p
    import objp.p2o
    add_to_pythonpath('cocoa')
    add_to_pythonpath('cocoalib')
    from cocoa.inter import (PyGUIObject, GUIObjectView, PyTextField, PyTable, TableView, PyColumns,
        ColumnsView, PyOutline, PySelectableList, SelectableListView, PyFairware, FairwareView)
    # This createPool() business is a bit hacky, but upon importing mg_cocoa, we call
    # install_gettext_trans_under_cocoa() which uses proxy functions (and thus need an active
    # autorelease pool). If we don't do that, we get leak warnings.
    from cocoa import proxy
    proxy.createPool()
    from mg_cocoa import (PyPanel, PanelView, PyBaseView,
        PyTableWithDate, PyCompletableEdit, PyDateWidget,
        PyCSVImportOptions, CSVImportOptionsView, PyImportTable, PySplitTable, PyLookup, LookupView,
        PyDateRangeSelector, DateRangeSelectorView, PyImportWindow, ImportWindowView,
        PyFilterBar, FilterBarView, PyReport, ReportView, PyScheduleTable, PyBudgetTable,
        PyEntryTable, PyTransactionTable, PyGeneralLedgerTable, PyChart, PyGraph, PyAccountPanel,
        PyMassEditionPanel, PyBudgetPanel, BudgetPanelView, PyCustomDateRangePanel,
        PyAccountReassignPanel, PyExportPanel, ExportPanelView, PyPanelWithTransaction,
        PanelWithTransactionView, PyTransactionPanel, PySchedulePanel, SchedulePanelView,
        ViewWithGraphView, PyNetWorthView, PyProfitView, PyTransactionView, PyAccountView,
        AccountViewView, PyScheduleView, PyBudgetView, PyCashculatorView, PyGeneralLedgerView,
        PyDocPropsView, PyEmptyView, PyReadOnlyPluginView, PyMainWindow, MainWindowView, PyDocument,
        DocumentView, PyMoneyGuruApp)
    from mg_cocoa import PyPrintView, PySplitPrint, PyTransactionPrint, PyEntryPrint
    allclasses = [PyGUIObject, PyTextField, PyTable, PyColumns, PyOutline, PySelectableList,
        PyFairware, PyPanel, PyBaseView, PyTableWithDate, PyCompletableEdit, PyDateWidget,
        PyCSVImportOptions, PyImportTable, PySplitTable, PyLookup, PyDateRangeSelector,
        PyImportWindow, PyFilterBar, PyReport, PyScheduleTable, PyBudgetTable,
        PyEntryTable, PyTransactionTable, PyGeneralLedgerTable, PyChart, PyGraph, PyAccountPanel,
        PyMassEditionPanel, PyBudgetPanel, PyCustomDateRangePanel, PyAccountReassignPanel,
        PyExportPanel, PyPanelWithTransaction, PyTransactionPanel, PySchedulePanel, PyNetWorthView,
        PyProfitView, PyTransactionView, PyAccountView, PyScheduleView, PyBudgetView,
        PyCashculatorView, PyGeneralLedgerView, PyDocPropsView, PyEmptyView, PyReadOnlyPluginView,
        PyMainWindow, PyDocument, PyMoneyGuruApp]
    proxy.destroyPool()
    allclasses += [PyPrintView, PySplitPrint, PyTransactionPrint, PyEntryPrint]
    for class_ in allclasses:
        objp.o2p.generate_objc_code(class_, 'cocoa/autogen', inherit=True)
    allclasses = [GUIObjectView, TableView, ColumnsView, SelectableListView, FairwareView, 
        PanelView, CSVImportOptionsView, LookupView, DateRangeSelectorView, ImportWindowView,
        FilterBarView, ReportView, BudgetPanelView, ExportPanelView, PanelWithTransactionView,
        SchedulePanelView, ViewWithGraphView, AccountViewView, MainWindowView, DocumentView]
    clsspecs = [objp.o2p.spec_from_python_class(class_) for class_ in allclasses]
    objp.p2o.generate_python_proxy_code_from_clsspec(clsspecs, 'build/CocoaViews.m')
    build_cocoa_ext('CocoaViews', 'build/py', ['build/CocoaViews.m', 'build/ObjP.m'])

def build_normal(ui, dev):
    build_help(dev)
    build_localizations(ui)
    build_ext()
    if ui == 'cocoa':
        build_cocoa(dev)
    elif ui == 'qt':
        build_qt(dev)

def main():
    args = parse_args()
    conf = json.load(open('conf.json'))
    ui = conf['ui']
    dev = conf['dev']
    print("Building moneyGuru with UI {}".format(ui))
    if dev:
        print("Building in Dev mode")
    if args.clean:
        if op.exists('build'):
            shutil.rmtree('build')
    if not op.exists('build'):
        os.mkdir('build')
    if args.doc:
        build_help(dev)
    elif args.loc:
        build_localizations(ui)
    elif args.updatepot:
        build_updatepot()
    elif args.mergepot:
        build_mergepot()
    elif args.cocoamod:
        build_cocoa_proxy_module()
        build_cocoa_bridging_interfaces()
    elif args.ext:
        build_ext()
    elif args.xibless:
        build_cocoalib_xibless()
        build_xibless()
    else:
        build_normal(ui, dev)

if __name__ == '__main__':
    main()
