//
//  DetailViewController.h
//  RPI Directory
//
//  Created by Brendon Justin on 10/17/11.
//  Copyright (c) 2011 Naga Softworks, LLC. All rights reserved.
//

#import <UIKit/UIKit.h>

@class Person;

@interface DetailViewController : UITableViewController {
    Person *m_person;
    
}

@property (nonatomic, retain) Person *person;

@end
