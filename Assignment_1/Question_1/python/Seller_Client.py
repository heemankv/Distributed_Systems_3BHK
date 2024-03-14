import grpc
from concurrent import futures
import logging
import uuid
import time
import market_pb2_grpc as market_pb2_grpc
from market_pb2 import *
from utils import getCategory
import seller_pb2_grpc as seller_pb2_grpc
from seller_pb2_grpc import SellerStub, SellerServicer
from seller_pb2 import *
from dotenv import load_dotenv
import os
import sys

load_dotenv()
seller_URI = os.getenv('seller_URI')

market_URI = os.getenv('market_URI')
market_port = os.getenv('market_port')

class SellerClient(SellerServicer):
    def __init__(self, seller_address, seller_uuid):
        self.seller_address = seller_address
        self.seller_uuid = seller_uuid

    def Notify(self, request, context):
        msg = request.message
        print()
        print(msg)
        return NotifyResponse(status=Status.SUCCESS)

    def register_seller(self):
        with grpc.insecure_channel(f'{market_URI}:{market_port}') as channel:
            stub = market_pb2_grpc.MarketStub(channel)
            request = RegisterSellerRequest(
                seller_address=self.seller_address,
                uuid=self.seller_uuid
            )
            response = stub.RegisterSeller(request)
            if response.status == Status.SUCCESS:
                print("SUCCESS: Registration successful.")
            else:
                print("FAIL: Registration failed.")

    def sell_item(self, name, category, quantity, description, price_per_unit):
        with grpc.insecure_channel(f'{market_URI}:{market_port}') as channel:
            stub = market_pb2_grpc.MarketStub(channel)
            request = SellItemRequest(
                name=name,
                category=category,
                quantity=quantity,
                description=description,
                seller_address=self.seller_address,
                price_per_unit=price_per_unit,
                seller_uuid=self.seller_uuid
            )
            response = stub.SellItem(request)
            if response.status == Status.SUCCESS:
                print(f"SUCCESS: Item successfully added - Item ID: {response.item_id}")
            else:
                print("FAIL: Failed to add item.")


    def update_item(self, item_id, new_price, new_quantity):
         with grpc.insecure_channel(f'{market_URI}:{market_port}') as channel:
            stub = market_pb2_grpc.MarketStub(channel)
            request = UpdateItemRequest(
                item_id=item_id,
                new_price=new_price,
                new_quantity=new_quantity,
                seller_address=self.seller_address,
                seller_uuid=self.seller_uuid
            )
            response = stub.UpdateItem(request)
            if response.status == Status.SUCCESS:
                print(f"SUCCESS: Item {item_id} updated successfully.")
            else:
                print(f"FAIL: Failed to update item {item_id}.")

    def delete_item(self, item_id):
        with grpc.insecure_channel(f'{market_URI}:{market_port}') as channel:
            stub = market_pb2_grpc.MarketStub(channel)
            request = DeleteItemRequest(
                item_id=item_id,
                seller_address=self.seller_address,
                seller_uuid=self.seller_uuid
            )
            response = stub.DeleteItem(request)
            if response.status == Status.SUCCESS:
                print(f"SUCCESS: Item {item_id} deleted successfully.")
            else:
                print("FAIL: Failed to delete item.")


    def display_seller_items(self):
        with grpc.insecure_channel(f'{market_URI}:{market_port}') as channel:
            stub = market_pb2_grpc.MarketStub(channel)
            request = DisplaySellerItemsRequest(
                seller_address=self.seller_address,
                seller_uuid=self.seller_uuid
            )
            try:
                response = stub.DisplaySellerItems(request)

                if not response.items:
                    print(" Seller not found or has no items.")
                    return

                print("-")
                for itemVals in response.items:
                    print(f"Item ID: {itemVals.item_id}, Price: ${itemVals.price_per_unit}, "
                          f"Name: {itemVals.name}, Category: {getCategory(itemVals.category)}, "
                          f"Description: {itemVals.description}")
                    print(f"Quantity Remaining: {itemVals.quantity}")
                    print(f"Seller: {itemVals.seller_address}")
                    print(f"Rating: {itemVals.rating} / 5 ")
                    print("–")
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.NOT_FOUND:
                    print(" Seller not found.")
                else:
                    print(f" gRPC error - {e}")

        
if __name__ == '__main__':

    seller_port = sys.argv[1]
    seller_address = f"{seller_URI}:{seller_port}"
    seller_uuid = str(uuid.uuid4())
  
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    seller_pb2_grpc.add_SellerServicer_to_server(SellerClient(seller_address, seller_uuid), server)
    server.add_insecure_port(f'{seller_URI}:{seller_port}')
    server.start()
    print(f"Seller Server started on port {seller_port}")
    

    time.sleep(1)

    seller_client = SellerClient(seller_address, seller_uuid)

    print("Welcome to the Seller Client!")
    print("You can perform the following operations:")
    print("1. Register Seller")
    print("2. Sell Item")
    print("3. Update Item")
    print("4. Delete Item") 
    print("5. Display Seller Items")
    print("6. Exit")

    # Ask for the seller's choice in a loop till the seller presses 6 to exit
    choice = 0
    while choice != 6:
        choice = int(input("Enter your choice: "))
        if choice == 1:
            seller_client.register_seller()
        elif choice == 2:
            default_item_1 = {
                "name": "Laptop",
                "category": Category.ELECTRONICS,
                "quantity": 10,
                "description": "High-performance laptop",
                "price_per_unit": 1200.0
            }
            default_item_2 = {
                "name": "Smartphone",
                "category": Category.ELECTRONICS,
                "quantity": 20,
                "description": "Latest smartphone model",
                "price_per_unit": 800.0
            }
            print("Do you want to go with default values or enter your own?")
            print("1. Default")
            print("2. Enter your own")
            choice = int(input("Enter your choice: "))
            if choice == 1:
                seller_client.sell_item(default_item_1["name"], default_item_1["category"], default_item_1["quantity"], default_item_1["description"], default_item_1["price_per_unit"])
                seller_client.sell_item(default_item_2["name"], default_item_2["category"], default_item_2["quantity"], default_item_2["description"], default_item_2["price_per_unit"])
                continue
            elif choice == 2:
                pass
            else:
                print("Invalid choice. Please try again.")
                continue

            name = input("Enter the name of the item: ")
            category = int(input("Enter the category of the item: "))
            quantity = int(input("Enter the quantity of the item: "))
            description = input("Enter the description of the item: ")
            price_per_unit = float(input("Enter the price per unit of the item: "))
            seller_client.sell_item(name, category, quantity, description, price_per_unit)
        elif choice == 3:
            item_id = input("Enter the item ID: ")

            print("Do you want to go with default values or enter your own?, Can update Price and Quantity")
            print("1. Default")
            print("2. Enter your own")
            choice = int(input("Enter your choice: "))
            if choice == 1:
                new_price = 1000.0
                new_quantity = 8
                seller_client.update_item(item_id, new_price, new_quantity)
                continue
            elif choice == 2:
                pass
            else:
                print("Invalid choice. Please try again.")
                continue

            new_price = float(input("Enter the new price: "))
            new_quantity = int(input("Enter the new quantity: "))
            seller_client.update_item(item_id, new_price, new_quantity)
        elif choice == 4:
            item_id = input("Enter the item ID: ")
            seller_client.delete_item(item_id)
        elif choice == 5:
            seller_client.display_seller_items()
        elif choice == 6:
            print("Exiting...")
            exit(0)
        else:
            print("Invalid choice. Please try again.")

    try:
        while True:
            time.sleep(86400)  # One day in seconds
    except KeyboardInterrupt:
        server.stop(0)
