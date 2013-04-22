//
//  DetailViewController.m
//  RPI Directory
//
//  Created by Brendon Justin on 4/13/12.
//  Copyright (c) 2012 Brendon Justin. All rights reserved.
//

#import "DetailViewController.h"
#import "Constants.h"
#import "Person.h"
#import <SDWebImage/UIImageView+WebCache.h>
#import <AddressBook/AddressBook.h>
#import <AddressBookUI/AddressBookUI.h>

const CGFloat kNameLabelHorizontalOffset = 68.0f;

@interface DetailViewController () <ABPeoplePickerNavigationControllerDelegate>

@property UIImage *personImage;

- (void)configureView;
- (void)addToExistingContact;
- (void)createNewContact;

@property (strong, nonatomic) UIPopoverController *masterPopoverController;

@end

@implementation DetailViewController

@synthesize person;
@synthesize masterPopoverController = _masterPopoverController;

#pragma mark - Managing the detail item

- (void)setPerson:(Person *)newPerson
{
    if (person != newPerson) {
        person = newPerson;
        
        // Update the view.
        [self configureView];
    }

    if (self.masterPopoverController != nil) {
        [self.masterPopoverController dismissPopoverAnimated:YES];
    }
}

- (void)configureView
{
    // Update the user interface for the person.
    UIView *view = self.headerView;
    UIImageView *imageView = (UIImageView *)[view viewWithTag:1];
    UILabel *label = (UILabel *)[view viewWithTag:2];

    if (self.person) {
        [self.tableView reloadData];
        
        if (imageView.hidden) {
            label.frame = CGRectOffset(label.frame, kNameLabelHorizontalOffset, 0);
            imageView.hidden = NO;
        }
        
        [imageView setImageWithURL:[NSURL URLWithString:[PHOTO_URL stringByAppendingString:self.person.rcsid]]
                  placeholderImage:[UIImage imageNamed:@"placeholder_photo"]];
        label.text = self.person.name;
    } else {
        if (!imageView.hidden) {
            imageView.hidden = YES;
            label.frame = CGRectOffset(label.frame, -kNameLabelHorizontalOffset, 0);
        }
    }
}

- (void)viewDidLoad
{
    [super viewDidLoad];
	// Do any additional setup after loading the view, typically from a nib.
    [self configureView];
}

- (void)viewDidUnload
{
    [self setHeaderView:nil];
    [super viewDidUnload];
    // Release any retained subviews of the main view.
    self.person = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
    if ([[UIDevice currentDevice] userInterfaceIdiom] == UIUserInterfaceIdiomPhone) {
        return (interfaceOrientation != UIInterfaceOrientationPortraitUpsideDown);
    } else {
        return YES;
    }
}

- (void)addToExistingContact
{
    ABPeoplePickerNavigationController *peoplePicker = [[ABPeoplePickerNavigationController alloc] init];
    peoplePicker.peoplePickerDelegate = self;
    [self presentModalViewController:peoplePicker animated:YES];
}

- (void)createNewContact
{
    NSDictionary *personDetails = self.person.completeDetails;
    NSString *firstName = nil;
    NSString *lastName = nil;
    NSString *office = nil;
    NSString *email = nil;
    NSString *phone = nil;
    UIImage *image = nil;
    
    CFErrorRef error = NULL;
    ABRecordRef record = ABPersonCreate();
    
    if ((firstName = personDetails[@"first_name"])) {
        ABRecordSetValue(record, kABPersonFirstNameProperty, (__bridge CFStringRef)firstName, &error);
    }
    
    if ((lastName = personDetails[@"last_name"])) {
        ABRecordSetValue(record, kABPersonLastNameProperty, (__bridge CFStringRef)lastName, &error);
    }
    
    if ((office = personDetails[@"office_location"])) {
        ABRecordSetValue(record, kABPersonAddressProperty, (__bridge CFStringRef)office, &error);
    }
    
    if ((email = personDetails[@"email"])) {
        ABMutableMultiValueRef multiemail = ABMultiValueCreateMutable(kABMultiStringPropertyType);
        ABMultiValueAddValueAndLabel(multiemail, (__bridge CFStringRef)email, kABOtherLabel, NULL);
        ABRecordSetValue(record, kABPersonEmailProperty, multiemail, &error);
    }
    
    if ((phone = personDetails[@"phone"])) {
        ABMutableMultiValueRef multiphone = ABMultiValueCreateMutable(kABMultiStringPropertyType);
        ABMultiValueAddValueAndLabel(multiphone, (__bridge CFStringRef)phone, kABPersonPhoneMainLabel, NULL);
        ABRecordSetValue(record, kABPersonPhoneProperty, multiphone, &error);
    }
    
    // set the person record's image, if we got one
    if ((image = self.personImage)) {
        NSData *imageData = UIImagePNGRepresentation(image);
        ABPersonSetImageData(record, (__bridge CFDataRef)imageData, nil);
    }
}

#pragma mark ABPeoplePickerNavigationControllerDelegate methods

- (BOOL)peoplePickerNavigationController:(ABPeoplePickerNavigationController *)peoplePicker shouldContinueAfterSelectingPerson:(ABRecordRef)person
{
    [self dismissModalViewControllerAnimated:YES];
    return NO;
}

- (BOOL)peoplePickerNavigationController:(ABPeoplePickerNavigationController *)peoplePicker shouldContinueAfterSelectingPerson:(ABRecordRef)person property:(ABPropertyID)property identifier:(ABMultiValueIdentifier)identifier
{
    [self dismissModalViewControllerAnimated:YES];
    return NO;
}

- (void)peoplePickerNavigationControllerDidCancel:(ABPeoplePickerNavigationController *)peoplePicker
{
    [self dismissModalViewControllerAnimated:YES];
}

#pragma mark - Table View

- (CGFloat)tableView:(UITableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath
{
    NSString *labelString = nil;
    NSString *detailString = nil;
    CGFloat height, height2, greaterHeight, padding;
    
    int count = 0;
    for (NSString *string in self.person.details) {
        if (count++ == indexPath.row) {
            labelString = string;
            detailString = [self.person.details objectForKey:string];
        }
    }
    
    if (labelString == nil || detailString == nil) {
        return 44;
    } else {
        labelString = [labelString stringByReplacingOccurrencesOfString:@"_" 
                                                             withString:@" "];
        
        //  Based on code by Tim Rupe on StackOverflow:
        //  http://stackoverflow.com/questions/129502/how-do-i-wrap-text-in-a-uitableviewcell-without-a-custom-cell
        UIFont *cellFont = [UIFont fontWithName:@"Helvetica" size:12.0];
        CGSize constraintSize = CGSizeMake(67.0f, MAXFLOAT);
        CGSize labelSize = [labelString sizeWithFont:cellFont 
                                   constrainedToSize:constraintSize 
                                       lineBreakMode:UILineBreakModeWordWrap];
        
        height = labelSize.height;
        
        cellFont = [UIFont fontWithName:@"Helvetica" size:17.0];
        constraintSize = CGSizeMake(320.0f - 67.0f - 20.0f, MAXFLOAT);
        
        if ([[UIDevice currentDevice] userInterfaceIdiom] == UIUserInterfaceIdiomPad) {
            constraintSize = CGSizeMake(768.0f - 67.0f - 60.0f, MAXFLOAT);
        }
        labelSize = [detailString sizeWithFont:cellFont 
                             constrainedToSize:constraintSize 
                                 lineBreakMode:UILineBreakModeWordWrap];
        height2 = labelSize.height;
        
        //  Find the greater of the two.  If it is less than 30 pixels (empirically determined),
        //  then just return 44.
        if (height > height2) {
            greaterHeight = height;
            padding = 14;
        } else {
            greaterHeight = height2;
            padding = 10;
        }
        
        return greaterHeight > 30 ? greaterHeight + padding : 44;
    }
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView
{
    return 1;
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
    if (self.person) {
        return [self.person.details count];
    } else {
        return 0;
    }
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{
    UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:@"DetailCell"];
    
    if (cell == nil) {
        cell = [[UITableViewCell alloc] initWithStyle:UITableViewCellStyleValue2 
                                      reuseIdentifier:@"DetailCell"];
        cell.textLabel.numberOfLines = 0;
        cell.detailTextLabel.numberOfLines = 0;
    }
    
    int count = 0;
    for (NSString *string in self.person.details) {
        if (count++ == indexPath.row) {
            cell.textLabel.text = [string stringByReplacingOccurrencesOfString:@"_" 
                                                                    withString:@" "];
            cell.detailTextLabel.text = [self.person.details objectForKey:string];
        }
    }
    
    return cell;
}

- (BOOL)tableView:(UITableView *)tableView canEditRowAtIndexPath:(NSIndexPath *)indexPath
{
    // Return NO if you do not want the specified item to be editable.
    return NO;
}

- (UIView *)tableView:(UITableView *)tableView viewForHeaderInSection:(NSInteger)section
{
    UIView *view = self.headerView;
    UIImageView *imageView = (UIImageView *)[view viewWithTag:1];
    UILabel *label = (UILabel *)[view viewWithTag:2];
    
    if (self.person) {
        [imageView setImageWithURL:[NSURL URLWithString:[PHOTO_URL stringByAppendingString:self.person.rcsid]]
                  placeholderImage:[UIImage imageNamed:@"placeholder_photo"]
                         completed:^(UIImage *image, NSError *error, SDImageCacheType cacheType) {
                             if (image) {
                                 self.personImage = image;
                             }
                         }];
        label.text = self.person.name;
    }
    
    return view;
}

#pragma mark - Split view

- (void)splitViewController:(UISplitViewController *)splitController willHideViewController:(UIViewController *)viewController withBarButtonItem:(UIBarButtonItem *)barButtonItem forPopoverController:(UIPopoverController *)popoverController
{
    barButtonItem.title = NSLocalizedString(@"Search RPI", @"Search RPI");
    [self.navigationItem setLeftBarButtonItem:barButtonItem animated:YES];
    self.masterPopoverController = popoverController;
}

- (void)splitViewController:(UISplitViewController *)splitController willShowViewController:(UIViewController *)viewController invalidatingBarButtonItem:(UIBarButtonItem *)barButtonItem
{
    // Called when the view is shown again in the split view, invalidating the button and popover controller.
    [self.navigationItem setLeftBarButtonItem:nil animated:YES];
    self.masterPopoverController = nil;
}

@end
