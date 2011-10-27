//
//  RPI_DirectoryAppDelegate_iPhone.m
//  RPI Directory
//
//  Created by Brendon Justin on 9/16/11.
//  Copyright 2011 Naga Softworks, LLC. All rights reserved.
//

#import "RPI_DirectoryAppDelegate_iPhone.h"
#import "SearchViewController_iPhone.h"

@implementation RPI_DirectoryAppDelegate_iPhone

@synthesize navController;

- (BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)launchOptions
{
    // Override point for customization after application launch.
    SearchViewController_iPhone *mainViewController = [[SearchViewController_iPhone alloc] initWithNibName:@"SearchViewController_iPhone" bundle:[NSBundle mainBundle]];
    
    self.navController = [[UINavigationController alloc] initWithRootViewController:mainViewController];
    [mainViewController release];
    
    [self.window addSubview:navController.view];
    [self.window makeKeyAndVisible];
    return YES;
}

- (void)dealloc
{
    [self.window release];
    [self.navController release];
    [super dealloc];
}

@end
