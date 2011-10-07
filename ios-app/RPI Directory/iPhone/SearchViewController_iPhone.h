//
//  SearchViewController_iPhone.h
//  RPI Directory
//
//  Created by Brendon Justin on 9/16/11.
//  Copyright 2011 Naga Softworks, LLC. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "DataManager.h"

@interface SearchViewController_iPhone : UIViewController <DataManagerDelegate, UITableViewDelegate, UITableViewDataSource, UISearchDisplayDelegate, UISearchBarDelegate> {
    IBOutlet UISwitch *m_instantSearchSwitch;
    BOOL m_instantSearch;
    
    DataManager *m_dataManager;
    
    NSString *m_searchInfo;
    NSArray *m_searchArray;
}

- (IBAction)switchInstantSearch:(id)sender;
- (void)searchWithString:(NSString *)searchString;

@end
