# -*- coding: utf-8 -*-

"""
Given an input file containing instructions to both start auctions, and place bids. 
1. Execute all instructions:
   Instruction type
      a. User listing items for sale - syntax (timestamp|user_id|action|item|reserve_price|close_time)
      b. Bids on items - syntax (timestamp|user_id|action|item|bid_amount)
      c. Heartbeat Messages - syntax (timestamp)

2. Output for each item (upon the auction closing) 
   a. The winning bid,
   b. The final price to be paid
   c. The user who has won the item
   d  Basic stats about the auction
   output syntax - (close_time|item|user_id|status|price_paid|total_bid_count|highest_bid|lowest_bid) 
"""
# -----------------------------------------
# Imported libraries from standard library
# -----------------------------------------
import logging
from logging.config import fileConfig
from collections import namedtuple as data_structure
from collections import defaultdict
import csv
from decimal import Decimal as decimal
import argparse
from pprint import pprint as pp
from auction_listing import AuctionListing
# -----------------------------------------


class Server:
    def __init__(self, input_file=""):
        self.logger = self.set_up_logging()
        self.file_name = input_file
        self.instruction_list = []
        self.instruction_loaded = False
        self.user_listings = {}
        self.bids = defaultdict(list)
        self.heartbeats = []
        self.valid_bid_list = {}
        self.all_listed_items = {}
        self.all_invalid_bids = []
        self.report_list = []
        self.heartbeats = []
        self.within_listing_time = False
        
        #data structure declarations
        self.user_listing  = data_structure('user_listing', 'timestamp user_id action item reserve_price close_time')
        self.bid = data_structure('bid', 'timestamp user_id action item bid_amount')
        self.heartbeat = data_structure ('heartbeat', 'timestamp')
        self.auction_result = data_structure('auction_result', 'close_time item user_id status price_paid total_bid_count highest_bid lowest_bid')
        self.logger.info('Auction program running')


    def set_up_logging(self):
        """
        Function used to initialise logging of activities in this object
            - returns a logger object

        note: file called logging_config.ini should be available in the
            working directory which contains the logging configuration.
        """
        fileConfig('logging_config.ini')
        logger = logging.getLogger('auctionLogger')
        return logger


    def process_instruction_input_file(self,file_name=""):
        """
        Read input file, categorise by parsing each item
        for processing
        """
        try:
            self.logger.info('Attempting to load instructions into memory')
            with open(file_name, newline='') as csvfile:
                csv_instructions = csv.reader(csvfile, delimiter='|')
                list(map(self.data_classification, csv_instructions))
            self.instruction_loaded = True
            self.logger.info('Successfully loaded instructions for processing')
            return self.instruction_list
        except IOError as file_error:
            self.logger.error('Error reading input file {0}'.format(file_error))
            raise Exception('Error reading input file {0}'.format(file_error))


    def data_classification(self, data=[]):
        """
        This function is used to store and classify data entered into memory
        using namedtuples, useful for easily accessing data.
        Rows with 6 columns are user listings
        Rows with 5 columns are bids
        Rows with a single column are heartbeats

            input: list of data
            output: classification type (user_listing, bid, heartbeat)
        """
        data_type = ''
        self.logger.info('Attempting to classify: {0}'.format(data))
        #This section classifies an input as heartbeat, expecting integer
        if len(data) == 1:
            try:
                value = data[0]
                int(value)
                self.instruction_list.append(self.heartbeat._make(data))
                data_type = 'heartbeat'
            except ValueError as input_error:
                self.logger.error('{0}, expecting heartbeat with epoch timestamp'.format(input_error))
        #This section classifies the input as a bid
        if len(data) == 5:
            is_bid_syntax_valid = self.validate_bid_format(data)
            if is_bid_syntax_valid:
                self.instruction_list.append(self.bid._make(data))
                data_type = 'bid'
            else:
                self.logger.error('Invalid syntax for classifying object as a bid: {0}'.format(data))
        # This section classifies the input as a user listing
        if len(data) == 6:
            is_listing_syntax_valid = self.validate_listing_format(data)
            if is_listing_syntax_valid:
                self.instruction_list.append(self.user_listing._make(data))
                data_type = 'user_listing'
            else:
                self.logger.error('Invalid syntax for classifying object as a user listing: {0}'.format(data))
        
        if data_type:
           self.logger.info('Successfully classified {0} as {1}'.format(self.instruction_list[-1], data_type))
        else:
           self.logger.debug('Unable to classify instruction: {0}'.format(data))
        return data_type


    def validate_listing_format(self, validation_data=[]):
        """
        Function used to check if auction listing list is valid (syntax + datatype)
        expecting list order:
            validation_data[0] = timestamp (int)
            validation_data[1] = userid (int)
            validation_data[2] = action (str)
            validation_data[3] = item (str)
            validation_data[4] = reserve_price (decimal)
            validation_data[5] = close_time (int)
        output:
           boolean:
        """
        is_valid=False
        # need to think of how to validate 'item' is a unique string code
        try:
            timestamp_check = validation_data[0]
            int(timestamp_check)
            user_id_check = validation_data[1]
            int(user_id_check)
            action_check = True if validation_data[2] == 'SELL' else False
            reserve_price_check = validation_data[4]
            decimal(reserve_price_check)
            close_time_check = validation_data[5]
            int(close_time_check)
            if action_check:
                is_valid=True
            return is_valid
        except ValueError as value_validation: 
            self.logger.error('{0}'.format(value_validation))


    def validate_bid_format(self, validation_data=[]):
        """
        Function used to check if a bid is valid (syntax + datatype)
        Parameters:
           validation_data[0] (int): timestamp
           validation_data[1] (int): user_id
           validation_data[2] (int): action
           validation_data[3] (str): item
           validation_data[4] (decimal): bid_amount
        Return: 
           boolean : True or False
        """
        is_valid = False
        try:
            timestamp_check = validation_data[0]
            int(timestamp_check)
            user_id_check = validation_data[1]
            int(user_id_check)
            action_check = True if validation_data[2] == 'BID' else False
            bid_amount_check = validation_data[4]
            decimal(bid_amount_check)
            if action_check:
                is_valid=True
            return is_valid
        except ValueError as value_validation: 
            self.logger.error('{0}'.format(value_validation))
        
 
    def process_instruction(self, instruction):
        """
        This function takes in a named tuple of one of the following (user_listing, bid, heartbeat) e.g. 

        - user_listing(timestamp=10, user_id=1, action='SELL', item='toaster_1', reserve_price=10.00, close_time=20)
        - bid(timestamp=12, user_id=8, action='BID', item='toaster_1', bid_price=7.50)
        - heartbeat(timestamp=20)
      
        Each intruction is processed accordigly with no return value
        """
        if isinstance(instruction, self.user_listing):

            self.logger.info('User has listed "{0}"\nprice: £{1},\nstart time: {2}'.format(instruction.item, 
                                                                                instruction.reserve_price, 
                                                                                instruction.timestamp))
        
            #Create an auction listing and add it to the dictionary of all listed items
            self.all_listed_items[instruction.item] = AuctionListing(auction_item_name=instruction.item, auction_listing_data=instruction)
            self.all_listed_items[instruction.item].is_open = True
            self.logger.info('New listing {0}, now accepting bids'.format(instruction))
            self.logger.info('There are currently {0} items listed, they are: {1}'.format(len(self.all_listed_items), self.all_listed_items))

        if isinstance(instruction,self.bid):
            self.logger.info('**************************************************************************************')
            self.logger.info('User {0} has placed a bid on item {1}\ntime: {2}\nprice: £{3}'.format(instruction.user_id, 
                                                                                         instruction.item, 
                                                                                         instruction.timestamp, 
                                                                                         instruction.bid_amount))
            bid = instruction
            self.logger.debug('Processing bid item: {0}'.format(bid))
            bid_price = bid.bid_amount
            auction_items_listed = self.all_listed_items.keys()
            self.logger.debug('All items currently listed: {0}'.format(auction_items_listed))

            if bid.item in auction_items_listed:
                valid_bid_list = self.all_listed_items[bid.item].valid_bids
                self.logger.info('Attempting to check if bid on item {0} is valid'.format(bid.item))
                
                try:
                    is_valid_bid = self.valid_bid_check(bid)
                    self.logger.debug('Completed bid valid check, bid validity state is: {0}'.format(is_valid_bid))
                    if is_valid_bid:
                        self.logger.info('Bid for {0} status: valid, attempting to add bid to valid list'.format(bid.item))
                        if not valid_bid_list:
                            self.logger.info('This is the first bid for {0}, price is £{1}'.format(bid.item, bid_price))
                            self.all_listed_items[bid.item].lowest_valid_bid = str(bid_price)
                            self.logger.info('Lowest bid for {0} is set to £{1}'.format(bid.item, bid_price))
                        
                        self.logger.info('Attempting to add the following valid bid {0}'.format(bid))
                        self.all_listed_items[bid.item].valid_bids.append(bid)

                        self.logger.info('Added bid to valid bid list: {0}'.format(self.all_listed_items[bid.item].valid_bids))

                        self.logger.info('Successfull validation of bid')
                    if not self.all_listed_items[bid.item].all_bids:
                        self.all_listed_items[bid.item].lowest_bid = str(bid_price)

                except Exception as valid_bid_error:
                    self.logger.error('Error whilst checking if bid is valid in process_instruction: {0}'.format(valid_bid_error))
            else:
               self.logger.error('There is currently no auction item listed for {0}'.format(bid.item))
               self.all_invalid_bids.append(bid)

            if self.within_listing_time:
                self.logger.info('Appending {0} for item {1} to all bids.'.format(bid, bid.item))
                self.all_listed_items[bid.item].all_bids.append(bid)
                self.within_listing_time = False
            else:
                self.logger.info('Bid {0} outside listing time'.format(bid))
                self.all_invalid_bids.append(bid)
            
        if isinstance(instruction, self.heartbeat):
            heartbeat = instruction.timestamp
            close_times = self.get_auction_closing_times() # return (item listed and timestamp) as a tuple
            self.logger.info('Close times are as follows: {0}'.format(close_times))

            for item_listed in close_times:
                item_name = item_listed[0]
                close_time = item_listed[1]
                _listing = self.all_listed_items[item_name]
                self.logger.info('Retrieved all items listed: {0}'.format(_listing))
                if heartbeat == close_time:
                    self.logger.info('############ Closing Listing {0} ########'.format(item_name))
                    self.close_listing(item_name=item_name, heartbeat=heartbeat,close_time=close_time,listing=_listing)
                    self.logger.info('Successfully completed listing check')
                else:
                    self.logger.info('Auction is still open for listing {0}'.format(item_name))
                
                
            #    self.get_summary_report()
        self.logger.info('----------------------------------------------------------------------------------------')

    def close_listing(self, item_name, heartbeat, close_time, listing):
        self.logger.info('Current timestamp {0} auction listing close time: {1}'.format(heartbeat, close_time))
        listing.total_bid_count = len(listing.all_bids)
        self.logger.info('Total bids counted for {0} is {1}'.format(listing.item_name, listing.total_bid_count))
        
        listing.highest_bid = str(listing.all_bids[-1].bid_amount) if len(listing.all_bids) > 1 else '0.00' 
        self.logger.info('The HIGHEST bid upon closing is: {0}'.format(listing.highest_bid))

        if listing.valid_bids:
            self.logger.info('Listing has some valid bids')
            if len(listing.valid_bids) >=2:
                self.logger.info('Attempting to set price paid for {0}'.format(listing.item_name))
                listing.price_paid = listing.valid_bids[-2].bid_amount
                listing.sale_status = 'SOLD'
                #listing.is_open = False
                #listing.highest_bid = str(listing.valid_bids[-1].bid_amount)
                self.logger.info('Successfully set price paid for {0} to £{1}, listing is now closed'.format(listing.item_name, listing.price_paid))
            elif len(listing.valid_bids) == 1:
                self.logger.info('Attempting to set price paid for {0}'.format(listing.item_name))
                listing.price_paid = str(listing.item_data.reserve_price)
                listing.sale_status = 'SOLD'
                #listing.is_open = False
                #listing.highest_bid = str(listing.valid_bids[-1].bid_amount)
                self.logger.info('Successfully set price paid for {0} to £{1}, listing is now closed'.format(listing.item_name, listing.price_paid))
            else:
                self.logger.error('Unexpected result, needs investigation whilst closing listing')
        else:
            listing.price_paid = '0.00'
            #listing.lowest_bid = '0.00'
            #listing.highest_bid = '0.00'
            #listing.is_open = False
            self.logger.info('No valid bids for {0}. Listing closed'.format(listing.item_name))
        listing.set_open_status(False)         
        
    def get_auction_closing_times(self):
        """
        Get all closed times
        """
        listed_items = self.all_listed_items
        
        listed_item_objects = list({item_obj for item, item_obj in listed_items.items()})
        all_close_times = list(map(lambda auction_listing_item: (auction_listing_item.item_name, auction_listing_item.item_data.close_time), listed_item_objects))
        return all_close_times
    

    def valid_bid_check(self, bid):
        """
        Function used to identify if a bid is valid
            inputs:
                bid: bid placed by user which is a namedtuple
        """
        self.logger.info('Function called to validate bid: {0}'.format(bid))
        is_valid = False
        #check if there is a list of items to bid for
        if self.all_listed_items:
            self.logger.info('There are items currently listed')
            self.logger.info('Attempting to check if an item is listed for this bid')
            listed_items = self.all_listed_items.keys()
            self.logger.info('The following items have been listed: {0}'.format(listed_items))
            #check it bid item is listed
            if bid.item in listed_items:
                self.logger.info('{0} has been listed'.format(bid.item))
                listing_open_time = self.all_listed_items[bid.item].item_data.timestamp
                bid_time = bid.timestamp
                bid_price = bid.bid_amount
                listing_close_time = self.all_listed_items[bid.item].item_data.close_time
                item_reserve_price = self.all_listed_items[bid.item].item_data.reserve_price
                valid_bid_list = self.all_listed_items[bid.item].valid_bids
                all_bids = self.all_listed_items[bid.item].all_bids

                self.logger.info('---- Here are a list of valid bids ----: {0}'.format(valid_bid_list))
                self.logger.info('.................')
                self.logger.info('All bids for {0}: {1}'.format(bid.item, all_bids))
                
                self.logger.info('Attempting to check if bid for {0} is valid.'.format(bid.item))
                """
                  This section checks if a bid is valid under three different criterias
                   1. Is it within the listed items auction times?
                   2. Is it greater than the reserve price?
                   3. Is it greater then existing bids? 
                """
                if self.is_within_auction_time(auction_open=listing_open_time, 
                                               auction_close=listing_close_time, 
                                               bid_time=bid_time) and \
                    self.is_greater_than_reserve_price(reserve_price=item_reserve_price, 
                                                       bid_price=bid_price) and \
                    self.is_greater_than_existing_bids(valid_bid_list=valid_bid_list, current_bid=bid_price):
                     
                    #Executing commands as bid is valid
                    is_valid = True

                else:
                    #add bid to to a list of all bids for a specific item
                    #self.all_listed_items[bid.item].all_bids.append(bid)
                    self.all_invalid_bids.append(bid) # later sub categorise invalid bids
                    self.logger.info('{0} failed the validity check'.format(bid))                                                     
            else:
                #add bid to to a list of all bids for a specific item
                #self.all_listed_items[bid.item].all_bids.append(bid)
                self.all_invalid_bids.append(bid)
                self.logger.error('Item is not listed, invalid bid')
        else:
            self.all_invalid_bids.append(bid)
            self.logger.error('No items listed currently, invalid bid')
        return is_valid
        

    def is_within_auction_time(self, auction_open, auction_close, bid_time):
        """
          Returns the status of a bid, by checking the auction time
        """
        
        if bid_time >= auction_open and bid_time <= auction_close:
            self.within_listing_time = True
            self.logger.info('Auction close time:{0}\n bid time:{1}\nbid has been place within auction time'.format(auction_close, bid_time))
        else:
            self.logger.info('Bid submitted outside auction time')
        return self.within_listing_time


    def is_greater_than_reserve_price(self, reserve_price, bid_price):
        """
          Returns the status of a bid, by checking the reserve price
        """
        try: 
            status = False
            bid_price = decimal(bid_price)
            reserve_price = decimal(reserve_price)
            
            if bid_price > reserve_price:
                self.logger.info('Bid price £{0} is greater than reserve price £{1}'.format(bid_price, reserve_price))
                status = True
                #self.logger.info('Bid price £{0} is greater than reserve price £{1}'.format(bid_price, reserve_price))
            else:
                self.logger.info('Bid price £{0} is less than reserve price £{1} for the item'.format(bid_price, reserve_price))
            return status
        except Exception as is_greater_than_reserve_price_error:
            output = str(is_greater_than_reserve_price_error)
            self.logger.error('Error in is_greater_than_reserve_price function: {0}'.format(output))


    def is_greater_than_existing_bids(self, valid_bid_list, current_bid):
        """
          Returns the status of a bid, by comparing the highest bid to current bid
        """
        status = False
        if not valid_bid_list:
            status = True
            self.logger.info('Current highest bid submitted at £{0}'.format(current_bid))
            return status
        else:
            try:
                self.logger.info('Assigning variables(highest bid, current bid and converting to decimal)')
                highest_bid = valid_bid_list[-1].bid_amount
                item = valid_bid_list[-1].item
                current_bid = decimal(current_bid)
                highest_bid = decimal(highest_bid)
                self.logger.info('Completed variable assignment, attempting to validate price')
                if current_bid > highest_bid:
                    self.logger.info('Bid price £{0} is greater than current highest bid price £{1}'.format(str(current_bid), str(highest_bid)))
                    status = True
                    self.logger.info('Attempting to make £{0} the highest bid so far'.format(str(current_bid)))
                    self.all_listed_items[item].highest_bid = str(current_bid)
                    self.logger.info('Successfully set £{0} as the highest bid so far for {1}'.format(str(current_bid), item))
                else:
                    self.logger.info('Bid price £{0} is less than current highest bid price £{1}'.format(current_bid, highest_bid))
                    self.logger.info('Unfortunately this bid is unsuccessful')
                return status
            except Exception as existing_bids_error:
                output = str(existing_bids_error)
                self.logger.error('Error translating data from string to decimal: {0}'.format(output))
            
    def auction_summary_report(self, auction):
        #self.logger.info('##### - Attempting to print listing for {0}'.format(listing.item_name))
        #listing.print_auction_data()
        #self.logger.info(auction.all_listed_items['toaster_1'].all_bids)
        internal_list = []
      
        for auction_item_name, auction_item  in auction.items():
            #self.logger.info(auction_item)
            
            self.logger.info('------------- SUMMARY FOR {0} ------------'.format(auction_item.item_name))
            self.logger.info("ALL BIDS: {0}".format(auction_item.all_bids))
            self.logger.info("VALID BIDS: {0}".format(auction_item.valid_bids))
            self.logger.info("PRICE PAID: £{0}".format(auction_item.price_paid))
            self.logger.info("SALE STATUS: {0}".format(auction_item.sale_status))
            self.logger.info("TOTAL BID COUNT: {0}".format(auction_item.total_bid_count))
            self.logger.info("HIGHEST BID: £{0}".format(auction_item.highest_bid))
            self.logger.info("LOWEST BID: £{0}".format(auction_item.lowest_bid))
            self.logger.info('------------- END ------------')

            bids_check = len(auction_item.valid_bids)
            if bids_check > 0:
                winning_user_id = auction_item.valid_bids[-1].user_id
            else:
                winning_user_id = ''

            #close_time|item|user_id|status|price_paid|total_bid_count|highest_bid|lowest_bid


            auction_summary_item = '{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}'.format(auction_item.item_data.close_time, auction_item.item_name, winning_user_id, 
                                                                            auction_item.sale_status, auction_item.price_paid, len(auction_item.all_bids), auction_item.highest_bid, 
                                                                            auction_item.lowest_bid)
            internal_list.append(auction_summary_item)
        for i in internal_list:
            self.logger.info(i)
        return internal_list
            

def main():
    parser = argparse.ArgumentParser(description='Auction program, that processes an instruction file')
    parser.add_argument('--filename', type=str, default='input.txt',
                        help='name of the file to process, default(input.txt)')

    args = parser.parse_args()
    
    run_auction = Server(args.filename)

    console_log = run_auction.set_up_logging()
    console_log.info("Attempting to initialise auction..")
    console_log.info("Successfully initialised auction")

    console_log.info("Attempting to read instruction file {0} into memory".format(args.filename))
    instruction_set = run_auction.process_instruction_input_file(run_auction.file_name)
    console_log.info("Successfully read instruction file into memory")
    #console_log.info(pp(instruction_set))
    console_log.info('    ')
    console_log.info('                        ############  START AUCTION ###############                       ')
   
    console_log.info('    ')
    list(map(run_auction.process_instruction, instruction_set))
    
    summary = run_auction.auction_summary_report(run_auction.all_listed_items)
    for auction_item in summary:
        print(auction_item)
    console_log.info('----    Auction closed  -------')


if __name__ == '__main__':
    main()