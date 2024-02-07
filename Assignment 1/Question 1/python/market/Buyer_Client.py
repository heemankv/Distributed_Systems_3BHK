import grpc
import market_pb2_grpc
from market_pb2 import *

class BuyerClient:
    def __init__(self, buyer_address):
        self.buyer_address = buyer_address

    def search_item(self, item_name="", category=Category.ANY):
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = market_pb2_grpc.MarketStub(channel)
            request = SearchItemRequest(
                item_name=item_name,
                category=category
            )
            response = stub.SearchItem(request)
            self.print_search_results(response)

    def buy_item(self, item_id, quantity):
        # Implement BuyItem functionality here
        # ...

    def add_to_wishlist(self, item_id):
        # Implement AddToWishList functionality here
        # ...

    def rate_item(self, item_id, rating):
        # Implement RateItem functionality here
        # ...

    def notify_client(self, notification_message):
        # Implement NotifyClient functionality here
        # ...

    def print_search_results(self, response):
        print("Buyer prints:")
        for item in response.items:
            print("–")
            print(f"Item ID: {item.item_id}, Price: ${item.price}, Name: {item.name}, Category: {item.category.name},")
            print(f"Description: {item.description}")
            print(f"Quantity Remaining: {item.quantity_remaining}")
            print(f"Rating: {item.rating} / 5  |  Seller: {item.seller}")
        print("–")


if __name__ == '__main__':
    buyer_address = "120.13.188.178:50051"

    buyer_client = BuyerClient(buyer_address)

    # Example: Buyer can perform operations like searching items, buying items, etc.
    buyer_client.search_item()
    # ...

