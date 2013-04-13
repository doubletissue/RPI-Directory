//
//  MasterViewController.m
//  RPI Directory
//
//  Created by Brendon Justin on 4/13/12.
//  Copyright (c) 2012 Brendon Justin. All rights reserved.
//

#import "MasterViewController.h"

#import "DetailViewController.h"

#import "Constants.h"
#import "Person.h"
#import <SDWebImage/UIImageView+WebCache.h>

//  Base search URL
NSString * const SEARCH_URL = @"http://rpidirectory.appspot.com/api?q=";

//  0.5 seconds
const NSTimeInterval SEARCH_INTERVAL = 0.5f;

@interface MasterViewController ()

- (void)search;
- (void)searchTimerFunc;

@property (nonatomic, strong) NSTimer           *m_searchTimer;
@property (nonatomic, strong) NSString          *m_searchString;
@property (nonatomic, strong) NSString          *m_lastString;
@property (nonatomic, strong) UITableView       *m_currentTableView;
@property (nonatomic, strong) NSOperationQueue  *m_queue;
@property (nonatomic) BOOL                      m_textChanged;

@end

@implementation MasterViewController

@synthesize detailViewController = _detailViewController;

@synthesize people = m_people;
@synthesize m_searchTimer;
@synthesize m_searchString;
@synthesize m_lastString;
@synthesize m_currentTableView;
@synthesize m_queue;
@synthesize m_textChanged;

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
    m_queue = [[NSOperationQueue alloc] init];
    m_queue.name = @"com.brendonjustin.RPI-Directory.search";
    m_queue.maxConcurrentOperationCount = 1;
    
    //  Update the array of people on the main thread, when a new array is available.
    //  Also make both table views reflect the new data.
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
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
    if ([[UIDevice currentDevice] userInterfaceIdiom] == UIUserInterfaceIdiomPhone) {
        return (interfaceOrientation == UIInterfaceOrientationPortrait);
    } else {
        return YES;
    }
}

//  Asynchronously search for people with the current query.
- (void)search
{
    [m_queue cancelAllOperations];
    
    [m_queue addOperationWithBlock:^{
        NSError *err = nil;
        NSString *query = [m_searchString stringByReplacingOccurrencesOfString:@" " withString:@"+"];
        NSString *searchUrl = [SEARCH_URL stringByAppendingString:query];
        NSString *resultString = [NSString stringWithContentsOfURL:[NSURL URLWithString:searchUrl]
                                                    encoding:NSUTF8StringEncoding
                                                       error:&err];
        
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
                    Person *person = [[Person alloc] init];
                    person.details = personDict;
                    
                    [people addObject:person];
                }
                
                NSNotification *notification = [NSNotification notificationWithName:@"QueryResult"
                                                                             object:people];
                
                [[NSNotificationCenter defaultCenter] postNotification:notification];
            }
        }
    }];
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

//  Search if the search text has changed since last call of this function,
//  then set the timer between searches.
- (void)searchBar:(UISearchBar *)searchBar textDidChange:(NSString *)searchText
{
    m_lastString = searchText;
    if (m_searchTimer == nil && ![m_lastString isEqualToString:@""]) {
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
        cell = [[UITableViewCell alloc] initWithStyle:UITableViewCellStyleSubtitle 
                                      reuseIdentifier:@"PersonCell"];
    }
    
    Person *person = [m_people objectAtIndex:indexPath.row];
    cell.textLabel.text = [person name];
    [cell.imageView setImageWithURL:[NSURL URLWithString:[PHOTO_URL stringByAppendingString:person.rcsid]]
                   placeholderImage:[UIImage imageNamed:@"photo_placeholder"]];
    
    NSString *subtitle = [[person details] objectForKey:@"year"];
    if (subtitle == nil) {
        subtitle = [[person details] objectForKey:@"title"];
    }
    
    if (subtitle != nil) {
        cell.detailTextLabel.text = subtitle;
    }
    return cell;
}

- (BOOL)tableView:(UITableView *)tableView canEditRowAtIndexPath:(NSIndexPath *)indexPath
{
    // Return NO if you do not want the specified item to be editable.
    return NO;
}

- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath
{
    m_currentTableView = tableView;
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
        NSIndexPath *indexPath = [m_currentTableView indexPathForSelectedRow];
        Person *person = [m_people objectAtIndex:indexPath.row];
        [[segue destinationViewController] setPerson:person];
    }
}

@end
