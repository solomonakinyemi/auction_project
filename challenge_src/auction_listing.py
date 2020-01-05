# -*- coding: utf-8 -*-


class AuctionListing:
    """
    Class created as a data structure to store auction
    listing information
        - auction_item_name: Name of item being auctioned
        - auction_listing_data: Named tuple in the following format
                                data_structure('user_listing', 'timestamp user_id action item reserve_price close_time')
    """
    def __init__(self, auction_item_name, auction_listing_data):
        self.item_name = auction_item_name
        self.item_data = auction_listing_data
        self.all_bids = []
        self.valid_bids = []
        self.price_paid = ''
        self.sale_status = 'UNSOLD'
        self.total_bid_count = ''
        self.highest_bid = ''
        self.lowest_bid = ''
        self.lowest_valid_bid = ''
        self.is_open = False

    def get_auction_item_name(self):
        return self.item_name
    
    def get_auction_item_data(self):
        return self.item_data
    
    def add_bid_to_all_bids_list(self, new_bid):
        self.all_bids.append(new_bid)

    def add_bid_to_valid_bid_list(self, valid_bid):
        self.valid_bids.append(valid_bid)

    def get_all_listing_bids(self):
        return self.all_bids

    def get_valid_bids(self):
        return self.valid_bids

    def print_auction_data(self,):
        #close_time|item|user_id|status|price_paid|total_bid_count|highest_bid|lowest_bid
        print('{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}'.format(self.item_data.close_time, 
                                                            self.item_name, 
                                                            self.item_data.user_id, 
                                                            self.sale_status, 
                                                            self.price_paid, 
                                                            self.total_bid_count, 
                                                            self.highest_bid, 
                                                            self.lowest_bid))

    def set_sale_status(self, status='SOLD'):
        self.sale_status = status

    def set_highest_bid(self):
        self.highest_bid = str(self.valid_bids[-1]) if len(auction_item.valid_bids) > 1 else '0.00'

    def set_open_status(self, status=False):
        self.is_open = status

    def get_status(self):
        return self.is_open
