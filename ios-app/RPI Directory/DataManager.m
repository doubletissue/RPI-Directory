//
//  DataManager.m
//  RPI Directory
//
//  Created by Brendon Justin on 9/17/11.
//  Copyright 2011 Naga Softworks, LLC. All rights reserved.
//

#import "DataManager.h"
#import "JSONKit.h"
#import "Person.h"

@interface DataManager ()
- (void)blockingSearchWithString:(NSString *)searchString;
- (void)updateDelegate;
@end

@implementation DataManager

@synthesize people = m_people;
@synthesize delegate;

- (id)init
{
    self = [super init];
    if (self) {
        // Initialization code here.
        m_baseUrl = [NSURL URLWithString:@"http://rpidirectory.appspot.com/api?name="];
        m_people = [[NSMutableArray alloc] init];
    }
    
    return self;
}

- (void)searchWithString:(NSString *)searchString {
    dispatch_queue_t searchQueue = dispatch_queue_create("com.abstractedsheep.searchqueue", NULL);
	dispatch_async(searchQueue, ^{
        [self blockingSearchWithString:searchString];
        [self performSelectorOnMainThread:@selector(updateDelegate) withObject:nil waitUntilDone:NO];
	});
	
	dispatch_release(searchQueue);
}

- (void)blockingSearchWithString:(NSString *)searchString {
    [m_people removeAllObjects];
    
    NSError *theError = nil;
//    NSURL *jsonUrl = [NSURL URLWithString:nameString relativeToURL:m_baseUrl];
    NSURL *jsonUrl = [NSURL URLWithString:[@"http://rpidirectory.appspot.com/api?name=" stringByAppendingString:searchString]];
    NSString *jsonString = [NSString stringWithContentsOfURL:jsonUrl 
													encoding:NSUTF8StringEncoding 
													   error:&theError];
    
    NSDictionary *dataDict = [jsonString objectFromJSONString];
    
    if (theError) {
//        NSLog(@"Error retrieving JSON data");
        
//        return NO;
    } else {
        for (id key in dataDict) {
            NSLog(@"key: %@, value: %@", key, [dataDict objectForKey:key]);
        }
        
        if (jsonString) {
            for (NSDictionary *individual in [dataDict objectForKey:@"data"]) {
                Person *person = [[Person alloc] init];
                NSString *holdingString;
                
                if ([individual objectForKey:@"name"] != nil) {
                    holdingString = [individual objectForKey:@"name"];
                    person.name = holdingString;
                } else {
                    continue;
                }
                
                if ([individual objectForKey:@"major"] != nil) {
                    holdingString = [individual objectForKey:@"major"];
                    person.major = holdingString;
                }
                
                if ([individual objectForKey:@"rcsid"] != nil) {
                    holdingString = [individual objectForKey:@"rcsid"];
                    person.rcsid = holdingString;
                }
                
                if ([individual objectForKey:@"email"] != nil) {
                    holdingString = [individual objectForKey:@"email"];
                    person.email = holdingString;
                }
                
                if ([individual objectForKey:@"homepage"] != nil) {
                    holdingString = [individual objectForKey:@"homepage"];
                    person.homepage = [NSURL URLWithString:holdingString];
                }
                
                if ([individual objectForKey:@"year"] != nil) {
                    holdingString = [individual objectForKey:@"year"];
                    person.year = holdingString;
                }
                
                [m_people addObject:person];
            }
        } else {
//            return NO;
        }
    }
    
//    return YES;
}

- (void)updateDelegate {
    [delegate searchResultsUpdated:[m_people copy]];
}

@end
