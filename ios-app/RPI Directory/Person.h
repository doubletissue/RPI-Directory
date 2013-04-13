//
//  Person.h
//  RPI Directory
//
//  Created by Brendon Justin on 4/13/12.
//  Copyright (c) 2012 Brendon Justin. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface Person : NSObject

@property (strong, nonatomic) NSDictionary *details;
@property (readonly, nonatomic) NSString *name;
@property (readonly, nonatomic) NSString *rcsid;

@end
