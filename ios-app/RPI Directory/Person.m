//
//  Person.m
//  RPI Directory
//
//  Created by Brendon Justin on 4/13/12.
//  Copyright (c) 2012 Brendon Justin. All rights reserved.
//

#import "Person.h"

@implementation Person

@synthesize name;
@synthesize details;

- (NSString *)rcsid
{
    NSString *rcsid = nil;
    
    if (self.details) {
        rcsid = [self.details objectForKey:@"rcsid"];
    }
    
    return rcsid;
}

@end
