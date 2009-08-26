/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "PyMoneyGuruApp.h"

@interface MGAppDelegate : NSObject
{
    IBOutlet NSMenuItem *unlockMenuItem;
    IBOutlet NSPopUpButton *firstWeekdayPopup;
    IBOutlet NSPopUpButton *aheadMonthsPopup;
    IBOutlet NSPopUpButton *yearStartMonthPopup;
    IBOutlet NSTextField *autoSaveIntervalField;
    IBOutlet NSButton *dontUnreconcileButton;
    
    NSWindowController *viewOptionsWindow;
    PyMoneyGuruApp *py;
}

- (PyMoneyGuruApp *)py;

- (IBAction)openExampleDocument:(id)sender;
- (IBAction)openWebsite:(id)sender;
- (IBAction)toggleViewOptionsVisible:(id)sender;
- (IBAction)unlockApp:(id)sender;
@end
