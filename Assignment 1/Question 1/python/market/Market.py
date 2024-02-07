import grpc
from concurrent import futures
import logging

import time
import market_pb2_grpc
from market_pb2 import *


class MarketServicer(market_pb2_grpc.MarketServicer):
    def __init__(self):
        self.sellers = {}
        self.items = {}
        self.buyers = {}

    def RegisterSeller(self, request, context):
        seller_address = request.seller_address
        uuid = request.uuid

        if seller_address in self.sellers:
            return RegisterSellerResponse(status=RegisterSellerResponse.FAIL)

        self.sellers[seller_address] = uuid
        print(f"Market prints: Seller join request from {seller_address}, uuid = {uuid}")
        print(f"Seller prints: SUCCESS")

        return RegisterSellerResponse(status=RegisterSellerResponse.SUCCESS)

    def SellItem(self, request, context):
        product_name = request.product_name
        category = request.category
        quantity = request.quantity
        description = request.description
        seller_address = request.seller_address
        price_per_unit = request.price_per_unit
        seller_uuid = request.seller_uuid

        # Check if the seller is registered
        if seller_address not in self.sellers or self.sellers[seller_address] != seller_uuid:
            return SellItemResponse(status=SellItemResponse.FAIL)

        # TODO: Use a more robust method to generate item ID
        item_id = str(len(self.items) + 1)

        # Create item details
        item_details = {
            "item_id": item_id,
            "product_name": product_name,
            "category": category,
            "quantity": quantity,
            "description": description,
            "seller_address": seller_address,
            "price_per_unit": price_per_unit,
            "ratings": [],
        }

        # Store item details
        self.items[item_id] = item_details

        print(f"Market prints: Seller {seller_address} added new item - Item ID: {item_id}")

        return SellItemResponse(status=SellItemResponse.SUCCESS, item_id=item_id)

    def UpdateItem(self, request, context):
        # Implement UpdateItem functionality here
        # ...

    def DeleteItem(self, request, context):
        # Implement DeleteItem functionality here
        # ...

    def DisplaySellerItems(self, request, context):
        # Implement DisplaySellerItems functionality here
        # ...

    def SearchItem(self, request, context):
        # Implement SearchItem functionality here
        # ...

    def BuyItem(self, request, context):
        # Implement BuyItem functionality here
        # ...

    def AddToWishList(self, request, context):
        # Implement AddToWishList functionality here
        # ...

    def RateItem(self, request, context):
        # Implement RateItem functionality here
        # ...

    def NotifyClient(self, request_iterator, context):
        for message in request_iterator:
            # Implement NotifyClient functionality here
            # ...

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    market_pb2_grpc.add_MarketServicer_to_server(MarketServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Market Server started on port 50051")
    try:
        while True:
            time.sleep(86400)  # One day in seconds
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    logging.basicConfig()
    serve()
