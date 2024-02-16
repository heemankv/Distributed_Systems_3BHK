import grpc
from concurrent import futures
import logging

import time

import market_pb2_grpc as market_pb2_grpc
from market_pb2 import *
 
import buyer_pb2_grpc as buyer_pb2_grpc
from buyer_pb2_grpc import BuyerServicer
from buyer_pb2 import *


# uri = '34.171.24.193'
buyer_URI = '127.0.0.1'
buyer_port = 50053

market_URI = '127.0.0.1'
market_port = 50051

class BuyerClient(BuyerServicer):
    def __init__(self, buyer_address):
        self.buyer_address = buyer_address

    def Notify(self, request, context):
        print({request.message})
        return NotifyResponse(status=Status.SUCCESS)

    def search_item(self, item_name="", category=Category.ANY):
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
                print(" SUCCESS")
            else:
                print(" Failed to buy item.")

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
                print(" Item added to wishlist.")
            else:
                print(" Failed to add item to wishlist.")

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
                print(" SUCCESS")
            else:
                print(" Failed to rate item.")


    def print_search_results(self, response):
        print("")
        for itemVals in response.items:
            print(f"Item ID: {itemVals.item_id}, Price: ${itemVals.price_per_unit}, "
                          f"Name: {itemVals.name}, Category: {itemVals.category}, "
                          f"Description: {itemVals.description}")
            print(f"Quantity Remaining: {itemVals.quantity}")
            print(f"Rating: {itemVals.rating} / 5  |  Seller: {itemVals.seller_address}")
            print("–")
        print("–")


if __name__ == '__main__':

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    buyer_pb2_grpc.add_BuyerServicer_to_server(BuyerServicer(), server)
    server.add_insecure_port(f'{buyer_URI}:{buyer_port}')

    server.start()
    print(f"Buyer Server started on port {buyer_port}")

    time.sleep(3)

    buyer_address = f"{buyer_URI}:{buyer_port}"
    buyer_client = BuyerClient(buyer_address)

    # Example: Buyer can perform operations like searching items, buying items, etc.
    buyer_client.search_item("Laptop", Category.ELECTRONICS)

    # Example: Buyer can perform other operations like adding items to wishlist
    buyer_client.add_to_wishlist("1")

    # Example: Buyer can perform other operations like adding items to wishlist, rating items, etc.
    # buyer_client.rate_item("1", 5)

    # Example : Buyer can perform other operations like buying items
    # buyer_client.buy_item("1", 2)

    try:
        while True:
            time.sleep(86400)  # One day in seconds
    except KeyboardInterrupt:
        server.stop(0)
    
