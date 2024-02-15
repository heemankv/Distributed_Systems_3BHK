import grpc
from concurrent import futures
import logging

import time

import Market_grpc.market_pb2_grpc as market_pb2_grpc
from Market_grpc.market_pb2 import *
 
from Seller_grpc.seller_pb2_grpc import SellerStub
from Seller_grpc import seller_pb2

from Buyer_grpc.buyer_pb2_grpc import BuyerStub
from Buyer_grpc import buyer_pb2



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
        print(f" Seller join request from {seller_address}, uuid = {uuid}")

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

        print(f" Seller {seller_address} added new item - Item ID: {item_id}")

        return SellItemResponse(status=SellItemResponse.SUCCESS, item_id=item_id)

    def UpdateItem(self, request, context):
        # Implement UpdateItem functionality here
        item_id = request.item_id
        new_price = request.new_price
        new_quantity = request.new_quantity
        seller_address = request.seller_address
        seller_uuid = request.seller_uuid

        print(f" Update Item {item_id} request from {seller_address}")

        # Check if the seller is registered and has the correct UUID
        if seller_address not in self.sellers or self.sellers[seller_address] != seller_uuid:
            return UpdateItemResponse(status=UpdateItemResponse.FAIL)

        # Check if the item exists
        if item_id not in self.items:
            return UpdateItemResponse(status=UpdateItemResponse.FAIL)

        # Update item details
        self.items[item_id]['price_per_unit'] = new_price
        self.items[item_id]['quantity'] = new_quantity

        # Notify buyers about the update (you can implement this based on your NotifyClient logic)
        notificationRequest = NotifyBuyerRequest(
            type = 'UpdateItem',
            item_id = item_id,
            updated_item = self.items[item_id]
        )
        self.NotifyClient(notificationRequest)

        return UpdateItemResponse(status=UpdateItemResponse.SUCCESS)

    def DeleteItem(self, request, context):
        # Implement DeleteItem functionality here
        item_id = request.item_id
        seller_address = request.seller_address
        seller_uuid = request.seller_uuid

        # Check if the seller is registered and has the correct UUID
        if seller_address not in self.sellers or self.sellers[seller_address] != seller_uuid:
            return DeleteItemResponse(status=DeleteItemResponse.FAIL)

        # Check if the item exists
        if item_id not in self.items:
            return DeleteItemResponse(status=DeleteItemResponse.FAIL)

        # Delete the item
        del self.items[item_id]

        print(f" Delete Item {item_id} request from {seller_address}")

        return DeleteItemResponse(status=DeleteItemResponse.SUCCESS)

    def DisplaySellerItems(self, request, context):
        # Implement DisplaySellerItems functionality here
        seller_address = request.seller_address
        seller_uuid = request.seller_uuid

        print(f"Display Items request from {request.seller_address} with UUID {request.seller_uuid}")


        # Check if the seller is registered and has the correct UUID
        if seller_address not in self.sellers or self.sellers[seller_address] != seller_uuid:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Seller not found.")
            return DisplaySellerItemsResponse()  # Empty response indicating failure

        seller_items = []
        for item_id, details in self.items.items():
            if details['seller_address'] == seller_address:
                item_info = DisplaySellerItemsResponse.ItemDetails(
                    item_id=item_id,
                    price=details['price_per_unit'],
                    name=details['product_name'],
                    category=details['category'],
                    description=details['description'],
                    quantity_remaining=details['quantity'],
                    seller=seller_address,
                    rating=sum(details['ratings']) / len(details['ratings']) if details['ratings'] else 0.0
                )
                seller_items.append(item_info)

        return DisplaySellerItemsResponse(items=seller_items)

    def SearchItem(self, request, context):
        # Implement SearchItem functionality here
        item_name = request.item_name
        category = request.category

        matching_items = []
        for item_id, details in self.items.items():
            if (not item_name or item_name.lower() in details['product_name'].lower()) and (
                    category == Category.ANY or details['category'] == category):
                item_info = SearchItemResponse.ItemDetails(
                    item_id=item_id,
                    price=details['price_per_unit'],
                    name=details['product_name'],
                    category=details['category'],
                    description=details['description'],
                    quantity_remaining=details['quantity'],
                    rating=sum(details['ratings']) / len(details['ratings']) if details['ratings'] else 0.0,
                    seller=details['seller_address']
                )
                matching_items.append(item_info)

        print(f" Search request for Item name: {item_name}, Category: {category}")
        print(matching_items)
        return SearchItemResponse(items=matching_items)
    
    def BuyItem(self, request, context):
        # Implement BuyItem functionality here
        item_id = request.item_id
        quantity = request.quantity
        buyer_address = request.buyer_address

        print(f" Buy request {quantity} of item {item_id}, from {buyer_address}.")

        # Check if the item exists
        if item_id not in self.items:
            return BuyItemResponse(status=BuyItemResponse.FAIL)

        # Check if there is enough stock
        if self.items[item_id]['quantity'] < quantity:
            return BuyItemResponse(status=BuyItemResponse.FAIL)

        # Update item quantity
        self.items[item_id]['quantity'] -= quantity

        # Notify the seller about the purchase (you can implement this based on your NotifyClient logic)
        notificationRequest = NotifySellerRequest(
            type = 'BuyItem',
            item_id = item_id,
            purchase_quantity = quantity,
            buyer_address = buyer_address
        )
        self.NotifyClient(notificationRequest)

        return BuyItemResponse(status=BuyItemResponse.SUCCESS)

    def AddToWishList(self, request, context):
        # Implement AddToWishList functionality here
        item_id = request.item_id
        buyer_address = request.buyer_address

        # Check if the item exists
        if item_id not in self.items:
            return AddToWishListResponse(status=AddToWishListResponse.FAIL)
        
        self.buyers[buyer_address].append(item_id)

        print(f" Wishlist request of item {item_id}, from {buyer_address}.")

        return AddToWishListResponse(status=AddToWishListResponse.SUCCESS)

    def RateItem(self, request, context):
        # Implement RateItem functionality here
        item_id = request.item_id
        buyer_address = request.buyer_address
        rating = request.rating

        # Check if the item exists
        if item_id not in self.items:
            return RateItemResponse(status=RateItemResponse.FAIL)

        # Check if the buyer has already rated the item
        if buyer_address in self.items[item_id]['ratings']:
            return RateItemResponse(status=RateItemResponse.FAIL)

        # Add the rating to the item
        self.items[item_id]['ratings'].append(rating)

        # Notify the seller about the rating (you can implement this based on your NotifyClient logic)

        print(f" {buyer_address} rated item {item_id} with {rating} stars.")

        return RateItemResponse(status=RateItemResponse.SUCCESS)

    # write a fn NotifyClient to :
    # 1. Notify the seller about the purchases from the buyers
    # 2. Notify the buyers about update made to product theu have added to wishlist
    def NotifyClient(self, request, context):
        # Implement NotifyClient functionality here
        type_of_notification = request.type

        if type_of_notification == 'BuyItem':
            # send out notification to seller about the purchase
            item_id = request.item_id
            purchase_quantity = request.purchase_quantity
            buyer_address = request.buyer_address
            seller_address = self.items[item_id]['seller_address']
            seller_uuid = self.sellers[seller_address]

            with grpc.insecure_channel(seller_address) as channel:
                seller_stub = SellerStub(channel)
                seller_stub.Notify(
                    seller_pb2.NotifyRequest(
                        message = f"Item {item_id} purchased by {buyer_address} for {purchase_quantity} quantity."
                    )
                )
                print(f"Notification sent to seller {seller_address} about purchase of item {item_id} by {buyer_address} for {purchase_quantity} quantity.")

        elif type_of_notification == 'UpdateItem':
            # send out notification to multiple buyers about the update made to the product they have added to wishlist
            item_id = request.item_id
            updated_item = request.updated_item

            for buyer_address in self.buyers:
                # if buyer has item in wishlist
                if item_id in self.buyers[buyer_address]:
                    with grpc.insecure_channel(buyer_address) as channel:
                        buyer_stub = BuyerStub(channel)
                        buyer_stub.Notify(
                            buyer_pb2.NotifyRequest(
                                message = f"Item {item_id} in your wishlist has been updated: {updated_item}"
                            )
                        )
                        print(f"Notification sent to buyer {buyer_address} about update of item {item_id} in wishlist.")



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
