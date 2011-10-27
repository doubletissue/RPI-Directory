//
//  Person.m
//  RPI Directory
//
//  Created by Brendon Justin on 9/17/11.
//  Copyright 2011 Naga Softworks, LLC. All rights reserved.
//

#import "Person.h"

@implementation Person

@synthesize name;
@synthesize major;
@synthesize rcsid;
@synthesize email;
@synthesize homepage;
@synthesize year;


- (id)init
{
    self = [super init];
    if (self) {
        // Initialization code here.
    }
    
    return self;
}

@end
