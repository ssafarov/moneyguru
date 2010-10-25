/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyDocument.h"

@interface MGDocument : NSDocument
{
    PyDocument *py;
}

- (PyDocument *)py;

/* Actions */
- (IBAction)import:(id)sender;

/* Misc */
- (void)stopEdition;

/* Python -> Cocoa */
- (BOOL)queryForScheduleScope;
@end
