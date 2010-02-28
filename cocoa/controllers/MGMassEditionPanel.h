/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "MGPanel.h"
#import "MGDocument.h"
#import "PyMassEditionPanel.h"

@interface MGMassEditionPanel : MGPanel {
    IBOutlet NSTextField *dateField;
    IBOutlet NSTextField *descriptionField;
    IBOutlet NSTextField *payeeField;
    IBOutlet NSTextField *checknoField;
    IBOutlet NSTextField *fromField;
    IBOutlet NSTextField *toField;
    IBOutlet NSComboBox *currencySelector;
    
    NSArray *currencies;
}
- (id)initWithDocument:(MGDocument *)aDocument;
- (PyMassEditionPanel *)py;
/* Python --> Cocoa */
- (void)refresh;
@end
