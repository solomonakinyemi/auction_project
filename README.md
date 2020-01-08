# auction_project
Auction project, handling and classifying data.

In summary the code takes in an input file with lots of rows of data and prints out the output of the auction items, sold and unsold in a summary.

Install docker: 

windows: https://docs.docker.com/docker-for-windows/install/
mac: https://docs.docker.com/docker-for-mac/install/

Pull down the image from the following using the following: 
docker pull docker.pkg.github.com/solomonakinyemi/auction_project/auction_pod:0.1

Once completed, check for the image id using: docker images

Run the container using the following: docker run -d <IMAGE ID>
  
Check the container is running and get container id with: docker ps

Log into the container: docker exec -it <CONTAINER ID> /bin/bash
  
Enable the python virtual environment: source auction_venv/bin/activate

(optional ) Install nose library with pip to run the tests if you so desire: pip install -r requirements.txt

Go into the source code directory: /auction_project/challenge_src

(optional) Run the tests for the code: nosetests -v test_auction.p

Run the program: python auction_v2.py





