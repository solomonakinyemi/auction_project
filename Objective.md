Consider you are running an auction website in which people can put items up for sale, and others
can bid to buy them. At the end of each auction if there are bids meeting or in excess of the
reserve price the highest bidder wins the item, however they pay the price of the second highest
valid bid.

A bid is considered valid if it:
  * Arrives after the auction start time and before or on the closing time.
  * Is larger than any previous valid bids submitted by the user.

At the end of the auction the winner will pay the price of the second highest bidder, if there
is only a single valid bid they will pay the reserve price of the auction. If two bids are received
for the same amount then the earliest bid wins the item.


===========================================

** EXERCISE **

Given an input file containing instructions to both start auctions, and place bids. You must
execute all instructions, and output for each item (upon the auction closing) the winning bid,
the final price to be paid, and the user who has won the item as well as some basic stats about
the auction. You will be provided a basic sample input file to help you test your program.

Input:

You will receive a pipe-delimited input file representing the started auctions, and bids. The
first entry on each line of this file will be a timestamp, the file will be strictly in-order
of timestamp. There are three types of rows found in this file:

1) Users listing items for sale.

This appears in the format:

timestamp|user_id|action|item|reserve_price|close_time

`timestamp` will be an integer representing a unix epoch time and is the auction start time,
`user_id` is an integer user id
`action` will be the string "SELL"
`item` is a unique string code for that item.
`reserve_price` is a decimal representing the item reserve price in the site's local currency.
`close_time` will be an integer representing a unix epoch time


2) Bids on items

This will appear in the format:

timestamp|user_id|action|item|bid_amount

`timestamp` will be an integer representing a unix epoch time and is the time of the bid,
`user_id` is an integer user id
`action` will be the string "BID"
`item` is a unique string code for that item.
`bid_amount` is a decimal representing a bid in the auction site's local currency.

3) Heartbeat messages

These messages may appear periodically in the input to ensure that auctions can be closed
in the absence of bids, they take the format:

timestamp

`timestamp` will be an integer representing a unix epoch time.


Expected Output:

The program should produce the following expected output, with each line representing the
outcome of a completed auction. This should be written to stdout or a file and be pipe
delimited with the following format:

close_time|item|user_id|status|price_paid|total_bid_count|highest_bid|lowest_bid

`close_time` should be a unix epoch of the time the auction finished
`item` is the unique string item code.
`user_id` is the integer id of the winning user, or blank if the item did not sell.
`status` should contain either "SOLD" or "UNSOLD" depending on the auction outcome.
`price_paid` should be the price paid by the auction winner (0.00 if the item is UNSOLD), as a
number to two decimal places
`total_bid_count` should be the number of valid bids received for the item.
'highest_bid' the highest bid received for the item as a number to two decimal places
`lowest_bid` the lowest bid placed on the item as a number to two decimal places


Example:

Input:

10|1|SELL|toaster_1|10.00|20
12|8|BID|toaster_1|7.50
13|5|BID|toaster_1|12.50
15|8|SELL|tv_1|250.00|20
16
17|8|BID|toaster_1|20.00
18|1|BID|tv_1|150.00
19|3|BID|tv_1|200.00
20
21|3|BID|tv_1|300.00


Output:

20|toaster_1|8|SOLD|12.50|3|20.00|7.50
20|tv_1||UNSOLD|0.00|2|200.00|150.00

