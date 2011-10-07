//
//  SearchViewController_iPhone.m
//  RPI Directory
//
//  Created by Brendon Justin on 9/16/11.
//  Copyright 2011 Naga Softworks, LLC. All rights reserved.
//

#import "SearchViewController_iPhone.h"
#import "Person.h"

@implementation SearchViewController_iPhone

- (id)initWithNibName:(NSString *)nibNameOrNil bundle:(NSBundle *)nibBundleOrNil
{
    self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil];
    if (self) {
        // Custom initialization
        self.view.frame = [[UIScreen mainScreen] applicationFrame];
    }
    return self;
}

- (void)didReceiveMemoryWarning
{
    // Releases the view if it doesn't have a superview.
    [super didReceiveMemoryWarning];
    
    // Release any cached data, images, etc that aren't in use.
}

- (void)dealloc {
    [m_dataManager release];
    [m_searchArray release];
    [super dealloc];
}

- (IBAction)switchInstantSearch:(id)sender {
    m_instantSearch = [(UISwitch *)sender isOn];
    
    if (!m_instantSearch) {
        [m_searchArray release];
        m_searchArray = [[NSArray alloc] init];
        
        m_searchInfo = @"Click \"Search\"";
    }
}

#pragma mark - View lifecycle

- (void)viewDidLoad
{
    [super viewDidLoad];
    // Do any additional setup after loading the view from its nib.
    
    m_instantSearch = m_instantSearchSwitch.isOn;
    m_dataManager = [[DataManager alloc] init];
    m_dataManager.delegate = self;
    
    m_searchInfo = @"Type to search...";
}

- (void)viewDidUnload
{
    [super viewDidUnload];
    // Release any retained subviews of the main view.
    // e.g. self.myOutlet = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
    // Return YES for supported orientations
    return (interfaceOrientation == UIInterfaceOrientationPortrait);
}


#pragma mark - Data Manager Delegate
//  Custom declared in DataManager

- (void)searchResultsUpdated:(NSArray *)resultsArray {
    [m_searchArray release];
    m_searchArray = resultsArray;
    [m_searchArray retain];
    
    if (self.searchDisplayController.active) {
        [self.searchDisplayController.searchResultsTableView reloadData];
    }
}

#pragma mark - UITableView Delegate and Data Source

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
    if (section == 0) {
        if ([m_searchArray count] == 0) {
            return 1;
        } else {
            return [m_searchArray count];
        }
    } else {
        return 0;
    }
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    static NSString *personCellID = @"personCell";
    
    UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:personCellID];
	if (cell == nil)
	{
		cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:personCellID] autorelease];
        
        if ([m_searchArray count] == 0) {
            cell.accessoryType = UITableViewCellAccessoryNone;
        } else {
            cell.accessoryType = UITableViewCellAccessoryDisclosureIndicator;
        }
	}
	
    if ([m_searchArray count] == 0) {
        cell.textLabel.text = m_searchInfo;
    } else {
        Person *person = [m_searchArray objectAtIndex:indexPath.row];
        cell.textLabel.text = person.name;
    }
    
    return cell;
}

- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath
{
    
}

#pragma mark -

- (void)searchWithString:(NSString *)searchString {
    [m_dataManager searchWithString:searchString];
}

#pragma mark - Search bar button interaction

- (void)searchBarSearchButtonClicked:(UISearchBar *)searchBar {
    if (!m_instantSearch) {
        [m_searchArray release];
        m_searchInfo = @"Searching...";
        
        if (self.searchDisplayController.active) {
            [self.searchDisplayController.searchResultsTableView reloadData];
        }
        
        [self searchWithString:searchBar.text];
    }
}

- (void)searchBar:(UISearchBar *)searchBar textDidChange:(NSString *)searchText {
    if ([searchText isEqual:@""]) {
        [m_searchArray release];
        m_searchArray = [[NSArray alloc] init];
    }
}

#pragma mark - UISearchDisplayController Delegate

- (BOOL)searchDisplayController:(UISearchDisplayController *)controller shouldReloadTableForSearchString:(NSString *)searchString
{
    if (m_instantSearch) {
        if ([m_searchArray count] == 0) {
            m_searchInfo = @"Searching...";
        }
        [self searchWithString:searchString];
        
        return YES;
    } else {
        if ([m_searchArray count] == 0) {
            m_searchInfo = @"Click \"Search\"";
            
            return YES;
        } else {
            return NO;
        }
    }

}

- (BOOL)searchDisplayController:(UISearchDisplayController *)controller shouldReloadTableForSearchScope:(NSInteger)searchOption {
    return YES;
}

@end
