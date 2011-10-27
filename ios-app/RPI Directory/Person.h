//
//  Person.h
//  RPI Directory
//
//  Created by Brendon Justin on 9/17/11.
//  Copyright 2011 Naga Softworks, LLC. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface Person : NSObject

@property (nonatomic, retain) NSString *name;
@property (nonatomic, retain) NSString *major;
@property (nonatomic, retain) NSString *rcsid;
@property (nonatomic, retain) NSString *email;
@property (nonatomic, retain) NSURL *homepage;
@property (nonatomic, retain) NSString *year;

@end
