//
//  DataManager.h
//  RPI Directory
//
//  Created by Brendon Justin on 9/17/11.
//  Copyright 2011 Naga Softworks, LLC. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol DataManagerDelegate
- (void)searchResultsUpdated:(NSArray *)resultsArray;
@end

@interface DataManager : NSObject {
    NSURL *m_baseUrl;
    NSMutableArray *m_people;
    
    id <DataManagerDelegate> delegate;
}

@property (readonly) NSArray *people;
@property (nonatomic, assign) id delegate;

- (void)searchWithString:(NSString *)searchString;

@end
