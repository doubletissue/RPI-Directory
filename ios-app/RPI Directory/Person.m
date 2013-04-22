//
//  Person.m
//  RPI Directory
//
//  Created by Brendon Justin on 4/13/12.
//  Copyright (c) 2012 Brendon Justin. All rights reserved.
//

#import "Person.h"

@implementation Person

- (NSDictionary *)details
{
    // Remove some fields from the details dictionary that aren't
    // necessary to display.
    NSMutableDictionary *editDict = [_details mutableCopy];
    NSArray *keysToRemove = @[ @"name", @"first_name", @"middle_name", @"last_name", @"has_pic" ];
    
    NSPredicate *pred = [NSPredicate predicateWithFormat:@"SELF CONTAINS %@", @"html"];
    NSArray *keysContainingHtml = [[editDict allKeys] filteredArrayUsingPredicate:pred];
    keysToRemove = [keysToRemove arrayByAddingObjectsFromArray:keysContainingHtml];
    
    [editDict removeObjectsForKeys:keysToRemove];
    
    return [NSDictionary dictionaryWithDictionary:editDict];
}

- (NSDictionary *)completeDetails
{
    return _details;
}

- (NSString *)name
{
    return [_details objectForKey:@"name"];
}

- (NSString *)rcsid
{
    NSString *rcsid = nil;
    
    if (self.details) {
        rcsid = [self.details objectForKey:@"rcsid"];
    }
    
    return rcsid;
}

@end
