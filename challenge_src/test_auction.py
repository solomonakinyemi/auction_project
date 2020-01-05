# -*- coding: utf-8 -*-

"""
Purpose: 
   This class is used to test the Auction module
"""

import unittest
from auction_v2 import Server
from auction_listing import AuctionListing
from decimal import Decimal as decimal
from collections import namedtuple as data_structure

#variables
file_input = "input_test_file.txt"

data_classification_timestamp = [1524349374]

class TestAuctionServer(unittest.TestCase):
    """
       TestAuction is used to test the individual functions
          available in the Auction class
    """
    def setUp(self):
        self.auction_obj = Server(file_input)

    def test_01_process_instruction_input_file(self):
        """
        Read file and process data by calling classification function
        output can be seen in the log file: thought_machine/logs
        """
        result = self.auction_obj.process_instruction_input_file(self.auction_obj.file_name)
        assert len(result) > 1, "Nothing read from input file"
        assert isinstance(result, list), "Unexpected return type, expecting list"
        assert isinstance(result[0], tuple), "Expecting tuple"
        

    def test_02_data_classification(self):
        """
        Test if data can be classified
        """
        data_classification_list = ['10', '1', 'SELL', 'toaster_1', '10.00', '20']
        data_type = self.auction_obj.data_classification(data_classification_list)
        assert data_type == 'user_listing', "Unable to classify data, expecting user_listing classification"


    def test_03_data_classification_empty_list(self):
        """
        Test empty list classification
        """
        data_type = self.auction_obj.data_classification([])
        assert data_type == '', "Unexpected classification, expecting empty result"


    def test_04_data_classification_timestamp(self):
        """
        Test if data type has been classified for timestamp
        """
        data_type = self.auction_obj.data_classification(data_classification_timestamp)
        assert data_type == 'heartbeat', "Error unexpected input type"

    def test_05_data_classification_bid_and_syntax(self):
        """
        Test bid classification is accurate by using bid data type
        """
        data_classification_bid = ["17", "8", "BID", "toaster_1", "20.00"]

        data_type = self.auction_obj.data_classification(data_classification_bid)
        assert data_type == 'bid', "Error unexpected input type, expecting bid"
    
    def test_06_process_instruction(self):
        """
        Testing ability to process instructions
        """
        result = self.auction_obj.process_instruction_input_file(self.auction_obj.file_name)
        for item in range(3):
            #print(type(result[item]))
            #print(item)
            self.auction_obj.process_instruction(result[item])
            assert isinstance(result[item], tuple), "Unexpected instancd type"

    def test_07_auction_times(self):
        """
        Testing the auction close times function
        """
        result = self.auction_obj.get_auction_closing_times()
        assert result == [], "Not expecting a result for this, plesse check value returned"
    
    
    def test_08_validate_listing_format(self):
        """
        Test to validate the format/row of a user listing along with data type
        """
        validation_obj = [1234, 73, 'SELL', 'toaster', 20.00, 1238]
        result = self.auction_obj.validate_listing_format(validation_obj)
        assert result == True

    def test_09_validate_bid_format(self):
        """
        Test to validate bid format/row expected by program
        """
        validation_obj = [1234, 73, 'BID', 'toaster', 2.00]
        result = self.auction_obj.validate_bid_format(validation_obj)
        assert result == True

    def test_10_close_listing(self):
        """
        Test to check closing a listed item being auctioned
        """
        user_listing_list = [1234, 73, 'SELL', 'toaster', 20.00, 1238]
        bid_list = [1235, 73, 'BID', 'toaster', 22.00]
        listing_object = data_structure('user_listing', 'timestamp user_id action item reserve_price close_time')
        bid_object = data_structure('bid', 'timestamp user_id action item bid_amount')
        user_listing = listing_object._make(user_listing_list)
        bid = bid_object._make(bid_list)
        item_name = 'toaster'
        auction_listing = AuctionListing(item_name, user_listing)
        auction_listing.set_open_status(True)
        
        auction_listing.valid_bids.append(bid)
        auction_listing.all_bids.append(bid)
        heartbeat = 1238
        close_time = 1238
        result = self.auction_obj.close_listing(item_name, heartbeat, close_time, auction_listing)
        assert auction_listing.is_open == False
        
    def test_11_get_auction_closing_times(self):
        """
        Test function to get a list of closing times for all listed items
        """
        user_listing_list = [
                             [1234, 73, 'SELL', 'toaster', 20.00, 1238], 
                             [1236, 333, 'SELL', 'oven', 20.00, 1239], 
                             [1237, 111, 'SELL', 'tv', 20.00, 1240]
                            ]
        check_times = [1238, 1235, 1240]
        user_listing_objects = []
       
        listing_object = data_structure('user_listing', 'timestamp user_id action item reserve_price close_time')
        
        # create named tuples for testing
        for listing in user_listing_list:
            user_listing_objects.append(listing_object._make(listing))
        

        # create auction listing
        for a_listing in user_listing_objects:
            self.auction_obj.all_listed_items[a_listing.item] = AuctionListing(a_listing.item, a_listing)
       

        times = self.auction_obj.get_auction_closing_times()

        for item_time in times:
            assert isinstance(item_time, tuple), 'Expected a tuple instance type, recieved {0}'.format(type(item_time))
            assert len(item_time) == 2, 'Expecting a tuple with two elements'
            assert isinstance(item_time[1], int), 'Expecting time to be integer'
    
    def test_12_valid_bid(self):
        """
        Check valid bid has been submitted
        output can be seen in the log file: thought_machine/logs
        """
        instruction_set = self.auction_obj.process_instruction_input_file(self.auction_obj.file_name)
    
        list(map(self.auction_obj.process_instruction, instruction_set))
        list_of_valid_bids = self.auction_obj.all_listed_items['toaster_1'].valid_bids  
        assert len(list_of_valid_bids) > 1, 'Expecting valid bids, list of valid bids is empty'
        assert list_of_valid_bids[0].item == 'toaster_1', 'Expected valid bids for toaster, {0} recieved'.format(list_of_valid_bids[0].item)
        
    

    #class TestAuctionListing(unittest.TestCase):
    """
       TestAuctionListing is used to test the individual functions
          available in the AuctionListing class
    """
     #def setUp(self):
    #    self.auction_obj = AuctionListing



        

if __name__ == '__main__':
    unittest.main()
