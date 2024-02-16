import grpc
from concurrent import futures
import logging

import time
import market_pb2_grpc as market_pb2_grpc
from market_pb2 import *
from utils import getCategory
 
import seller_pb2_grpc as seller_pb2_grpc
from seller_pb2_grpc import SellerStub, SellerServicer
from seller_pb2 import *


# uri = '34.171.24.193'
seller_URI = '127.0.0.1'
seller_port = 50052

market_URI = '127.0.0.1'
market_port = 50051



class SellerClient(SellerServicer):
    def __init__(self, seller_address, seller_uuid):
        self.seller_address = seller_address
        self.seller_uuid = seller_uuid

    def Notify(self, request, context):
        msg = request.message
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
        # Implement UpdateItem functionality here
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
        # Implement DeleteItem functionality here
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
    seller_address = f"{seller_URI}:{seller_port}"
    seller_uuid = "987a515c-a6e5-11ed-906b-76aef1e817c5"
  
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    seller_pb2_grpc.add_SellerServicer_to_server(SellerClient(seller_address, seller_uuid), server)
    server.add_insecure_port(f'{seller_URI}:{seller_port}')
    server.start()
    print(f"Seller Server started on port {seller_port}")
    

    time.sleep(3)

    # Example: Seller can perform other operations like selling items, updating items, etc.
    # Create a SellerClient instance
    seller_client = SellerClient(seller_address, seller_uuid)

    # Register the seller
    seller_client.register_seller()

    # Add items for sale
    seller_client.sell_item("Laptop", Category.ELECTRONICS, 10, "High-performance laptop", 1200.0)
    seller_client.sell_item("Smartphone", Category.ELECTRONICS, 20, "Latest smartphone model", 800.0)

    # stall for 5 seconds
    time.sleep(1)
    
    # print("Updating seller item")
    # Update the price of an item
    seller_client.update_item(item_id="1", new_price=1000.0, new_quantity=8)

    # Display all uploaded items
    seller_client.display_seller_items()

    # Delete an item
    seller_client.delete_item(item_id="2")

    time.sleep(4)

    # Display all uploaded items
    seller_client.display_seller_items()


    try:
        while True:
            time.sleep(86400)  # One day in seconds
    except KeyboardInterrupt:
        server.stop(0)





