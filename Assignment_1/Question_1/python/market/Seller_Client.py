import grpc
import market_pb2_grpc
from market_pb2 import *


class SellerClient:
    def __init__(self, seller_address, seller_uuid):
        self.seller_address = seller_address
        self.seller_uuid = seller_uuid

    def register_seller(self):
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = market_pb2_grpc.MarketStub(channel)
            request = RegisterSellerRequest(
                seller_address=self.seller_address,
                uuid=self.seller_uuid
            )
            response = stub.RegisterSeller(request)
            if response.status == RegisterSellerResponse.SUCCESS:
                print("Registration successful.")
            else:
                print("Registration failed.")

    def sell_item(self, product_name, category, quantity, description, price_per_unit):
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = market_pb2_grpc.MarketStub(channel)
            request = SellItemRequest(
                product_name=product_name,
                category=category,
                quantity=quantity,
                description=description,
                seller_address=self.seller_address,
                price_per_unit=price_per_unit,
                seller_uuid=self.seller_uuid
            )
            response = stub.SellItem(request)
            if response.status == SellItemResponse.SUCCESS:
                print(f"Seller prints: Item successfully added - Item ID: {response.item_id}")
            else:
                print("Seller prints: Failed to add item.")


    def update_item(self, item_id, new_price, new_quantity):
        # Implement UpdateItem functionality here
         with grpc.insecure_channel('localhost:50051') as channel:
            stub = market_pb2_grpc.MarketStub(channel)
            request = UpdateItemRequest(
                item_id=item_id,
                new_price=new_price,
                new_quantity=new_quantity,
                seller_address=self.seller_address,
                seller_uuid=self.seller_uuid
            )
            response = stub.UpdateItem(request)
            if response.status == UpdateItemResponse.SUCCESS:
                print(f"Seller prints: Item {item_id} updated successfully.")
            else:
                print("Seller prints: Failed to update item.")

    def delete_item(self, item_id):
        # Implement DeleteItem functionality here
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = market_pb2_grpc.MarketStub(channel)
            request = DeleteItemRequest(
                item_id=item_id,
                seller_address=self.seller_address,
                seller_uuid=self.seller_uuid
            )
            response = stub.DeleteItem(request)
            if response.status == DeleteItemResponse.SUCCESS:
                print(f"Seller prints: Item {item_id} deleted successfully.")
            else:
                print("Seller prints: Failed to delete item.")


    def display_seller_items(self):
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = market_pb2_grpc.MarketStub(channel)
            request = DisplaySellerItemsRequest(
                seller_address=self.seller_address,
                seller_uuid=self.seller_uuid
            )
            try:
                response = stub.DisplaySellerItems(request)

                if not response.items:
                    print("Seller prints: Seller not found or has no items.")
                    return

                print("Seller prints: -")
                for item_info in response.items:
                    print(f"Item ID: {item_info.item_id}, Price: ${item_info.price}, "
                          f"Name: {item_info.name}, Category: {item_info.category}, "
                          f"Description: {item_info.description}")
                    print(f"Quantity Remaining: {item_info.quantity_remaining}")
                    print(f"Rating: {item_info.rating} / 5  |  Seller: {item_info.seller}")
                    print("–")
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.NOT_FOUND:
                    print("Seller prints: Seller not found.")
                else:
                    print(f"Seller prints: gRPC error - {e}")

    # def notify_client(self, notification_message):
        # Implement NotifyClient functionality here
        # ...


if __name__ == '__main__':
    seller_address = "192.13.188.178:50051"
    seller_uuid = "987a515c-a6e5-11ed-906b-76aef1e817c5"

   
    # Example: Seller can perform other operations like selling items, updating items, etc.
    # Create a SellerClient instance
    seller_client = SellerClient(seller_address, seller_uuid)

    # Register the seller
    seller_client.register_seller()

    # Add items for sale
    seller_client.sell_item("Laptop", Category.ELECTRONICS, 10, "High-performance laptop", 1200.0)
    seller_client.sell_item("Smartphone", Category.ELECTRONICS, 20, "Latest smartphone model", 800.0)

    # Update the price of an item
    seller_client.update_item(item_id="1", new_price=1000.0, new_quantity=8)

    # Display all uploaded items
    seller_client.display_seller_items()


