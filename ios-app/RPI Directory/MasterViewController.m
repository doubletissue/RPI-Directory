//
//  MasterViewController.m
//  RPI Directory
//
//  Created by Brendon Justin on 4/13/12.
//  Copyright (c) 2012 Brendon Justin. All rights reserved.
//

#import "MasterViewController.h"

#import "DetailViewController.h"

#import "Person.h"

const NSString *SEARCH_URL = @"http://rpidirectory.appspot.com/api?q=";
const NSTimeInterval SEARCH_INTERVAL = 3;

@interface MasterViewController () {
    NSMutableArray      *m_people;
    NSTimer             *m_searchTimer;
    NSString            *m_searchString;
    NSString            *m_lastString;
    
    dispatch_queue_t    m_queue;
    
    Boolean             m_textChanged;
}

- (void)search;
- (void)searchTimerFunc;

@end

@implementation MasterViewController

@synthesize detailViewController = _detailViewController;

- (void)awakeFromNib
{
    if ([[UIDevice currentDevice] userInterfaceIdiom] == UIUserInterfaceIdiomPad) {
        self.clearsSelectionOnViewWillAppear = NO;
        self.contentSizeForViewInPopover = CGSizeMake(320.0, 600.0);
    }
    [super awakeFromNib];
}

- (void)viewDidLoad
{
    [super viewDidLoad];
	// Do any additional setup after loading the view, typically from a nib.
    
    self.detailViewController = (DetailViewController *)[[self.splitViewController.viewControllers lastObject] topViewController];
    
    m_searchTimer = nil;
    m_queue = nil;
    
    [[NSNotificationCenter defaultCenter] addObserverForName:@"QueryResult" 
                                                      object:nil 
                                                       queue:[NSOperationQueue mainQueue]
                                                  usingBlock:^(NSNotification *notification) {
                                                      m_people = [notification object];
                                                      [self.searchDisplayController.searchResultsTableView reloadData];
                                                      [self.tableView reloadData];
                                                  }];
}

- (void)viewDidUnload
{
    [super viewDidUnload];
    // Release any retained subviews of the main view.
    
    [[NSNotificationCenter defaultCenter] removeObserver:self];
    
    [m_searchTimer invalidate];
    m_searchTimer = nil;
    
    dispatch_release(m_queue);
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
    if ([[UIDevice currentDevice] userInterfaceIdiom] == UIUserInterfaceIdiomPhone) {
        return (interfaceOrientation != UIInterfaceOrientationPortraitUpsideDown);
    } else {
        return YES;
    }
}

- (void)search
{
    //  Search if the search text has changed since last call,
    //  then set the timer between searches
    if (m_queue == nil) {
        m_queue = dispatch_queue_create("com.brendonjustin.searchqueue", NULL);
    }
    
    dispatch_async(m_queue, ^{
        NSError *err = nil;
        NSString *query = [m_searchString stringByReplacingOccurrencesOfString:@" " withString:@"+"];
        NSString *searchUrl = [SEARCH_URL stringByAppendingString:query];
        NSString *resultString = [NSString stringWithContentsOfURL:[NSURL URLWithString:searchUrl]
                                                    encoding:NSUTF8StringEncoding
                                                       error:&err];
        
        NSLog(@"Search URL: %@", searchUrl);
        if (err != nil) {
            NSLog(@"Error retrieving search results for string: %@", m_searchString);
        } else {
            NSData *resultData = [resultString dataUsingEncoding:NSUTF8StringEncoding];
            id results = [NSJSONSerialization JSONObjectWithData:resultData
                                                         options:NSJSONReadingMutableLeaves
                                                           error:&err];
            
            if (results && [results isKindOfClass:[NSDictionary class]]) {
                NSMutableArray *people = [NSMutableArray array];
                
                for (NSDictionary *personDict in [results objectForKey:@"data"]) {
                    NSMutableDictionary *editDict;
                    Person *person = [[Person alloc] init];
                    person.name = [personDict objectForKey:@"name"];
                    
                    //  Remove the 'name' field from the details dictionary
                    //  as it is redundant.
                    editDict = [personDict mutableCopy];
                    if ([editDict objectForKey:@"name"] != nil) {
                        [editDict removeObjectForKey:@"name"];
                    }
                    person.details = editDict;
                    
                    [people addObject:person];
                }
                
                NSNotification *notification = [NSNotification notificationWithName:@"QueryResult"
                                                                             object:people];
                
                [[NSNotificationCenter defaultCenter] postNotification:notification];
            }
        }
    });
}

- (void)searchTimerFunc
{
    m_searchTimer = nil;
    
    if (![m_lastString isEqualToString:m_searchString]) {
        m_searchString = m_lastString;
        
        [self search];
    }
}

#pragma mark - Search Delegate

- (void)searchBar:(UISearchBar *)searchBar textDidChange:(NSString *)searchText
{
    m_lastString = searchText;
    if (m_searchTimer == nil) {
        //  Search
        m_searchString = searchText;
        [self search];
        
        m_searchTimer = [NSTimer scheduledTimerWithTimeInterval:SEARCH_INTERVAL 
                                                         target:self 
                                                       selector:@selector(searchTimerFunc) 
                                                       userInfo:nil 
                                                        repeats:NO];
    }
}

#pragma mark - Table View

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView
{
    return 1;
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
    return m_people.count;
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{
    UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:@"PersonCell"];

    if (cell == nil) {
        cell = [[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault 
                                      reuseIdentifier:@"PersonCell"];
    }
    
    Person *person = [m_people objectAtIndex:indexPath.row];
    cell.textLabel.text = [person name];
    return cell;
}

- (BOOL)tableView:(UITableView *)tableView canEditRowAtIndexPath:(NSIndexPath *)indexPath
{
    // Return NO if you do not want the specified item to be editable.
    return NO;
}

- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath
{
    if ([[UIDevice currentDevice] userInterfaceIdiom] == UIUserInterfaceIdiomPad) {
        Person *person = [m_people objectAtIndex:indexPath.row];
        self.detailViewController.person = person;
    } else if ([[UIDevice currentDevice] userInterfaceIdiom] == UIUserInterfaceIdiomPhone) {
        [self performSegueWithIdentifier:@"showDetail" sender:self];
    }
}

- (void)prepareForSegue:(UIStoryboardSegue *)segue sender:(id)sender
{
    if ([[segue identifier] isEqualToString:@"showDetail"]) {
        NSIndexPath *indexPath = [self.tableView indexPathForSelectedRow];
        Person *person = [m_people objectAtIndex:indexPath.row];
        [[segue destinationViewController] setPerson:person];
    }
}

@end
