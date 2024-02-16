import grpc
from concurrent import futures
import logging

import time

import market_pb2_grpc as market_pb2_grpc
from market_pb2 import *
from utils import getCategory
 
from seller_pb2_grpc import SellerStub
from seller_pb2 import NotifyRequest as SellerNotifyRequest

from buyer_pb2_grpc import BuyerStub
from buyer_pb2 import NotifyRequest as BuyerNotifyRequest
from dotenv import load_dotenv
import os

load_dotenv()
market_URI = os.getenv('market_URI')
market_port = os.getenv('market_port')


class MarketClient(market_pb2_grpc.MarketServicer):
    def __init__(self):
        self.sellers = {}
        self.items = {}
        self.buyers = {}

    def RegisterSeller(self, request, context):
        seller_address = request.seller_address
        uuid = request.uuid

        if seller_address in self.sellers:
            return RegisterSellerResponse(status=Status.FAIL)

        self.sellers[seller_address] = uuid
        print(f"Seller join request from {seller_address}, uuid = {uuid}")

        return RegisterSellerResponse(status=Status.SUCCESS)

    def SellItem(self, request, context):
        name = request.name
        category = request.category
        quantity = request.quantity
        description = request.description
        seller_address = request.seller_address
        price_per_unit = request.price_per_unit
        seller_uuid = request.seller_uuid

        if seller_address not in self.sellers or self.sellers[seller_address] != seller_uuid:
            return SellItemResponse(status=Status.FAIL)

        item_id = str(len(self.items) + 1)

        item_details = {
            "item_id": item_id,
            "name": name,
            "category": category,
            "quantity": quantity,
            "description": description,
            "seller_address": seller_address,
            "price_per_unit": price_per_unit,
            "ratings": [],
        }

        self.items[item_id] = item_details

        print(f"Sell Item Request form {seller_address} - Item ID: {item_id}")

        return SellItemResponse(status=Status.SUCCESS, item_id=item_id)

    def UpdateItem(self, request, context):
        item_id = request.item_id
        new_price = request.new_price
        new_quantity = request.new_quantity
        seller_address = request.seller_address
        seller_uuid = request.seller_uuid

        if seller_address not in self.sellers or self.sellers[seller_address] != seller_uuid:
            return UpdateItemResponse(status=Status.FAIL)

        if item_id not in self.items:
            return UpdateItemResponse(status=Status.FAIL)

        self.items[item_id]['price_per_unit'] = new_price
        self.items[item_id]['quantity'] = new_quantity

        #deepcopy
        updated_item = ItemDetails(
            item_id = item_id,
            name = self.items[item_id]['name'],
            category = self.items[item_id]['category'],
            quantity = self.items[item_id]['quantity'],
            description = self.items[item_id]['description'],
            seller_address = self.items[item_id]['seller_address'],
            price_per_unit = self.items[item_id]['price_per_unit'],
            rating=sum(self.items[item_id]['ratings']) / len(self.items[item_id]['ratings']) if self.items[item_id]['ratings'] else 0.0,

        )

        print(f"SUCCESS: Update Item {item_id} request from {seller_address}")

        notificationRequest = NotifyBuyerRequest(
            type = 'UpdateItem',
            item_id = item_id,
            updated_item = updated_item
        )
        self.Notify_Clients(notificationRequest)

        return UpdateItemResponse(status=Status.SUCCESS)

    def DeleteItem(self, request, context):
        item_id = request.item_id
        seller_address = request.seller_address
        seller_uuid = request.seller_uuid

        if seller_address not in self.sellers or self.sellers[seller_address] != seller_uuid:
            return DeleteItemResponse(status=Status.FAIL)

        if item_id not in self.items:
            return DeleteItemResponse(status=Status.FAIL)

        del self.items[item_id]

        print(f"Delete Item {item_id} request from {seller_address}")

        return DeleteItemResponse(status=Status.SUCCESS)

    def DisplaySellerItems(self, request, context):
        seller_address = request.seller_address
        seller_uuid = request.seller_uuid

        if seller_address not in self.sellers or self.sellers[seller_address] != seller_uuid:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Seller not found.")
            return DisplaySellerItemsResponse()

        seller_items = []
        for item_id, details in self.items.items():
            if details['seller_address'] == seller_address:
                item_info = ItemDetails(
                    item_id=item_id,
                    price_per_unit=details['price_per_unit'],
                    name=details['name'],
                    category=details['category'],
                    description=details['description'],
                    quantity=details['quantity'],
                    seller_address=seller_address,
                    rating=sum(details['ratings']) / len(details['ratings']) if details['ratings'] else 0.0
                )
                seller_items.append(item_info)

        print(f"Display Items request from {request.seller_address} with UUID {request.seller_uuid}")

        return DisplaySellerItemsResponse(items=seller_items)

    def SearchItem(self, request, context):
        item_name = request.item_name
        category = request.category

        matching_items = []
        for item_id, details in self.items.items():
            if (not item_name or item_name.lower() in details['name'].lower()) and (
                    category == Category.OTHERS or details['category'] == category):
                item_info = ItemDetails(
                    item_id=item_id,
                    price_per_unit=details['price_per_unit'],
                    name=details['name'],
                    category=details['category'],
                    description=details['description'],
                    quantity=details['quantity'],
                    rating=sum(details['ratings']) / len(details['ratings']) if details['ratings'] else 0.0,
                    seller_address=details['seller_address']
                )
                matching_items.append(item_info)

        print(f"Search request for Item name: {item_name}, Category: {getCategory(category)}")
        return SearchItemResponse(items=matching_items)
    
    def BuyItem(self, request, context):
        item_id = request.item_id
        quantity = request.quantity
        buyer_address = request.buyer_address

        print(f"Buy request {quantity} of item {item_id}, from {buyer_address}.")

        if item_id not in self.items:
            return BuyItemResponse(status=Status.FAIL)

        if self.items[item_id]['quantity'] < quantity:
            return BuyItemResponse(status=Status.FAIL)

        self.items[item_id]['quantity'] -= quantity

        notificationRequest = NotifySellerRequest(
            type = 'BuyItem',
            item_id = item_id,
            quantity = quantity,
            buyer_address = buyer_address
        )
        self.Notify_Clients(notificationRequest)

        return BuyItemResponse(status=Status.SUCCESS)

    def AddToWishList(self, request, context):
        item_id = request.item_id
        buyer_address = request.buyer_address

        if item_id not in self.items:
            return AddToWishListResponse(status=Status.FAIL)
        

        if buyer_address not in self.buyers:
            self.buyers[buyer_address] = [item_id]
        
        self.buyers[buyer_address].append(item_id)

        print(f"Wishlist request of item {item_id}, from {buyer_address}.")

        return AddToWishListResponse(status=Status.SUCCESS)

    def RateItem(self, request, context):
        item_id = request.item_id
        buyer_address = request.buyer_address
        rating = request.rating

        if item_id not in self.items:
            return RateItemResponse(status=Status.FAIL)

        if buyer_address in self.items[item_id]['ratings']:
            return RateItemResponse(status=Status.FAIL)

        self.items[item_id]['ratings'].append(rating)

        print(f"{buyer_address} rated item {item_id} with {rating} stars.")

        return RateItemResponse(status=Status.SUCCESS)

    def Notify_Clients(self, request):
        type_of_notification = request.type

        if type_of_notification == 'BuyItem':
            item_id = request.item_id
            quantity = request.quantity
            buyer_address = request.buyer_address
            seller_address = self.items[item_id]['seller_address']
            seller_uuid = self.sellers[seller_address]

            with grpc.insecure_channel(seller_address) as channel:
                seller_stub = SellerStub(channel)
                response = seller_stub.Notify(
                    SellerNotifyRequest(
                        message = f"Item {item_id} purchased by {buyer_address} for {quantity} quantity.",
                        item_id=item_id,
                    )
                )
                print(f"Notification sent to seller {seller_address} about purchase of item {item_id} by {buyer_address} for {quantity} quantity.")

        elif type_of_notification == 'UpdateItem':
            item_id = request.item_id
            updated_item = request.updated_item

            for buyer_address in self.buyers:
                print(f"Checking buyer {buyer_address} wishlist")
                if item_id in self.buyers[buyer_address]:
                    print(f"Item {item_id} found in buyer {buyer_address} wishlist")
                    with grpc.insecure_channel(buyer_address) as channel:
                        print(f"Sending notification to buyer {buyer_address} about update of item {item_id} in wishlist.", channel)
                        buyer_stub = BuyerStub(channel)
                        response = buyer_stub.Notify(
                            BuyerNotifyRequest(
                                message = f"Item {item_id} in your wishlist has been updated",
                                item_id=item_id,
                            )
                        )
                        if response.status == Status.SUCCESS:
                            print(" SUCCESS")
                        else:
                            print(" Failed to rate item.")
                        print(f"Notification sent to buyer {buyer_address} about update of item {item_id} in wishlist.")




def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    market_pb2_grpc.add_MarketServicer_to_server(MarketClient(), server)
    server.add_insecure_port(f'{market_URI}:{market_port}')
    server.start()

    print(f"Market Server started on {market_URI}:{market_port}") 
    
    try:
        while True:
            time.sleep(86400) 
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':    
    logging.basicConfig()
    serve()
