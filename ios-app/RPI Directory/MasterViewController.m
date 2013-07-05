//
//  MasterViewController.m
//  RPI Directory
//
//  Created by Brendon Justin on 4/13/12.
//  Copyright (c) 2012-2013 Brendon Justin;
//                2013 Sierra Bravo Corp., dba The Nerdery (http://nerdery.com)
//

#import "MasterViewController.h"

#import "DetailViewController.h"

#import "Constants.h"
#import "Person.h"
#import <SDWebImage/UIImageView+WebCache.h>

#import <ReactiveCocoa/ReactiveCocoa.h>
#import <ReactiveCocoa/EXTScope.h>

//  Base search URL
NSString * const SEARCH_URL = @"http://rpidirectory.appspot.com/api?q=";

@interface MasterViewController ()

@property (nonatomic, strong) RACSubject         *m_searchTextSubject;
@property (nonatomic, strong) RACSubject         *m_searchResultsSubject;
@property (nonatomic, strong) UITableView        *m_currentTableView;
@property (nonatomic) BOOL                       m_textChanged;

@end

@implementation MasterViewController

@synthesize detailViewController = _detailViewController;

@synthesize people = m_people;
@synthesize m_searchTextSubject;
@synthesize m_searchResultsSubject;
@synthesize m_currentTableView;
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
    
    m_searchResultsSubject = [RACSubject subject];
    
    @weakify(self);
    [[[[[m_searchResultsSubject switchToLatest] deliverOn:[RACScheduler mainThreadScheduler]]
       doNext:^(id _) {
           [[UIApplication sharedApplication] setNetworkActivityIndicatorVisible:NO];
       }]
      doError:^(NSError *_) {
          [[UIApplication sharedApplication] setNetworkActivityIndicatorVisible:NO];
      }]
     subscribeNext:^(NSArray *people) {
         @strongify(self);
         self.people = people;
         [self.searchDisplayController.searchResultsTableView reloadData];
         [self.tableView reloadData];
     }];
    
    m_searchTextSubject = [RACSubject subject];
    
    [[[[m_searchTextSubject distinctUntilChanged]
       filter:^BOOL(NSString *searchString) {
           if ([searchString isEqualToString:@""]) {
               return NO;
           }
           
           return YES;
       }]
      doNext:^(id _) {
          [[UIApplication sharedApplication] setNetworkActivityIndicatorVisible:YES];
      }]
     subscribeNext:^(NSString *searchString) {
         // Run the network request for the current search term.
         // -start: calls its block argument on a background thread.
         RACSignal *sig = [RACSignal start:^NSArray *(BOOL *success, NSError *__autoreleasing *error) {
             NSError *err = nil;
             NSString *query = [searchString stringByReplacingOccurrencesOfString:@" " withString:@"+"];
             NSString *searchUrl = [SEARCH_URL stringByAppendingString:query];
             NSString *resultString = [NSString stringWithContentsOfURL:[NSURL URLWithString:searchUrl]
                                                               encoding:NSUTF8StringEncoding
                                                                  error:&err];
             
             if (err == nil) {
                 NSData *resultData = [resultString dataUsingEncoding:NSUTF8StringEncoding];
                 id results = [NSJSONSerialization JSONObjectWithData:resultData
                                                              options:NSJSONReadingMutableLeaves
                                                                error:&err];
                 
                 if (results && [results isKindOfClass:[NSDictionary class]]) {
                     NSArray *data = [results objectForKey:@"data"];
                     RACSequence *people = [data.rac_sequence map:^Person *(NSDictionary *personDict) {
                         Person *person = [[Person alloc] init];
                         person.details = personDict;
                         
                         return person;
                     }];
                     
                     return people.array;
                 }
             }
             
             NSLog(@"Error retrieving search results for string: %@", searchString);
             
             *success = NO;
             *error = err;
             return @[];
         }];
         
         [self.m_searchResultsSubject sendNext:sig];
     }];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
    if ([[UIDevice currentDevice] userInterfaceIdiom] == UIUserInterfaceIdiomPhone) {
        return (interfaceOrientation == UIInterfaceOrientationPortrait);
    } else {
        return YES;
    }
}

#pragma mark - Search Delegate

- (void)searchBar:(UISearchBar *)searchBar textDidChange:(NSString *)searchText
{
    [m_searchTextSubject sendNext:searchText];
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
