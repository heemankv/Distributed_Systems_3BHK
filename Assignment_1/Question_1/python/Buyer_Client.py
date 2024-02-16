import grpc
from concurrent import futures
import logging

import time

import market_pb2_grpc as market_pb2_grpc
from market_pb2 import *
 
import buyer_pb2_grpc as buyer_pb2_grpc
from buyer_pb2_grpc import BuyerServicer
from buyer_pb2 import *
from utils import getCategory
from dotenv import load_dotenv
import os


# uri = '34.171.24.193'
load_dotenv()
buyer_URI = os.getenv('buyer_URI')
buyer_port = os.getenv('buyer_port')

market_URI = os.getenv('market_URI')
market_port = os.getenv('market_port')

class BuyerClient(BuyerServicer):
    def __init__(self, buyer_address):
        self.buyer_address = buyer_address

    def Notify(self, request, context):
        msg = request.message
        print()
        print(msg)
        # self.print_search_results(request)
        return NotifyResponse(status=Status.SUCCESS)

    def search_item(self, item_name="", category=Category.OTHERS):
        with grpc.insecure_channel(f'{market_URI}:{market_port}') as channel:
            stub = market_pb2_grpc.MarketStub(channel)
            request = SearchItemRequest(
                item_name=item_name,
                category=category
            )
            response = stub.SearchItem(request)
            self.print_search_results(response)

    def buy_item(self, item_id, quantity):
        # Implement BuyItem functionality here
        with grpc.insecure_channel(f'{market_URI}:{market_port}') as channel:
            stub = market_pb2_grpc.MarketStub(channel)
            request = BuyItemRequest(
                item_id=item_id,
                quantity=quantity,
                buyer_address=self.buyer_address
            )
            response = stub.BuyItem(request)
            if response.status == Status.SUCCESS:
                print(f"SUCCESS: Bought {quantity} items of ID {item_id}.")
            else:
                print(f"FAIL: Failed to buy item of ID {item_id}.")

    def add_to_wishlist(self, item_id):
        # Implement AddToWishList functionality here
        with grpc.insecure_channel(f'{market_URI}:{market_port}') as channel:
            stub = market_pb2_grpc.MarketStub(channel)
            request = AddToWishListRequest(
                item_id=item_id,
                buyer_address=self.buyer_address
            )
            response = stub.AddToWishList(request)
            if response.status == Status.SUCCESS:
                print(f"SUCCESS: Item {item_id} added to wishlist.")
            else:
                print(f"FAIL: Failed to add item {item_id} to wishlist.")

    def rate_item(self, item_id, rating):
        # Implement RateItem functionality here
        with grpc.insecure_channel(f'{market_URI}:{market_port}') as channel:
            stub = market_pb2_grpc.MarketStub(channel)
            request = RateItemRequest(
                item_id=item_id,
                buyer_address=self.buyer_address,
                rating=rating
            )
            response = stub.RateItem(request)
            if response.status == Status.SUCCESS:
                print(f"SUCCESS: Raiting added to item {item_id}.")
            else:
                print(f"FAIL: Failed to rate item {item_id}.")


    def print_search_results(self, response):
        print("")
        for itemVals in response.items:
            print(f"Item ID: {itemVals.item_id}, Price: ${itemVals.price_per_unit}, "
                          f"Name: {itemVals.name}, Category: {getCategory(itemVals.category)}, "
                          f"Description: {itemVals.description}")
            print(f"Quantity Remaining: {itemVals.quantity}")
            print(f"Rating: {itemVals.rating} / 5  |  Seller: {itemVals.seller_address}")
            print("–")
        print("–")


if __name__ == '__main__':    
    buyer_address = f"{buyer_URI}:{buyer_port}"

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    buyer_pb2_grpc.add_BuyerServicer_to_server(BuyerClient(buyer_address), server)
    server.add_insecure_port(f'{buyer_URI}:{buyer_port}')

    server.start()
    print(f"Buyer Server started on port {buyer_port}")

    time.sleep(3)

    buyer_client = BuyerClient(buyer_address)

    # # Example: Buyer can perform operations like searching items, buying items, etc.
    # buyer_client.search_item("Laptop", Category.ELECTRONICS)

    # # Example: Buyer can perform other operations like adding items to wishlist
    # buyer_client.add_to_wishlist("1")

    # # Example: Buyer can perform other operations like adding items to wishlist, rating items, etc.
    # buyer_client.rate_item("1", 5)

    # time.sleep(3)

    # # Example : Buyer can perform other operations like buying items
    # buyer_client.buy_item("1", 2)

    # Make a menu for the buyer to perform operations
    print("Welcome to the Buyer Client!")
    print("You can perform the following operations:")
    print("1. Search Item")
    print("2. Buy Item")
    print("3. Add to Wishlist")
    print("4. Rate Item")
    print("6. Exit")

    # Ask for the seller's choice in a loop till the seller presses 6 to exit
    choice = 0
    while choice != 6:
        choice = int(input("Enter your choice: "))
        if choice == 1:
            item_name = input("Enter the name of the item you want to search: ")
            print("Categories:")
            print("0. ELECTRONICS")
            print("1. FASHION")
            print("2. OTHERS")
            category = int(input("Enter the category of the item you want to search: "))

            if (category == 0):
                category = Category.ELECTRONICS
            elif (category == 1):
                category = Category.FASHION
            elif (category == 2):
                category = Category.OTHERS
            
            else:
                print("Invalid category. Please enter a valid category.")
                continue

            buyer_client.search_item(item_name,  category)

        elif choice == 2:
            item_id = input("Enter the ID of the item you want to buy: ")
            quantity = int(input("Enter the quantity of the item you want to buy: "))
            buyer_client.buy_item(item_id, quantity)
        elif choice == 3:
            item_id = input("Enter the ID of the item you want to add to wishlist: ")
            buyer_client.add_to_wishlist(item_id)
        elif choice == 4:
            item_id = input("Enter the ID of the item you want to rate: ")
            rating = int(input("Enter the rating you want to give to the item: "))
            buyer_client.rate_item(item_id, rating)
        elif choice == 6:
            break
        else:
            print("Invalid choice. Please enter a valid choice.")

    try:
        while True:
            time.sleep(86400)  # One day in seconds
    except KeyboardInterrupt:
        server.stop(0)
    

