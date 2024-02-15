import grpc
import market_pb2_grpc as market_pb2_grpc
from market_pb2 import *
 
from buyer_pb2_grpc import BuyerStub,BuyerServicer
from buyer_pb2 import *




# uri = '34.171.24.193'
uri = 'localhost'

class BuyerClient(BuyerServicer):
    def __init__(self, buyer_address):
        self.buyer_address = buyer_address

    def search_item(self, item_name="", category=Category.ANY):
        with grpc.insecure_channel(f'{uri}:50051') as channel:
            stub = market_pb2_grpc.MarketStub(channel)
            request = SearchItemRequest(
                item_name=item_name,
                category=category
            )
            response = stub.SearchItem(request)
            self.print_search_results(response)

    def buy_item(self, item_id, quantity):
        # Implement BuyItem functionality here
        with grpc.insecure_channel(f'{uri}:50051') as channel:
            stub = market_pb2_grpc.MarketStub(channel)
            request = BuyItemRequest(
                item_id=item_id,
                quantity=quantity,
                buyer_address=self.buyer_address
            )
            response = stub.BuyItem(request)
            if response.status == BuyItemResponse.SUCCESS:
                print(" SUCCESS")
            else:
                print(" Failed to buy item.")

    def add_to_wishlist(self, item_id):
        # Implement AddToWishList functionality here
        with grpc.insecure_channel(f'{uri}:50051') as channel:
            stub = market_pb2_grpc.MarketStub(channel)
            request = AddToWishListRequest(
                item_id=item_id,
                buyer_address=self.buyer_address
            )
            response = stub.AddToWishList(request)
            if response.status == AddToWishListResponse.SUCCESS:
                print(" SUCCESS")
            else:
                print(" Failed to add item to wishlist.")

    def rate_item(self, item_id, rating):
        # Implement RateItem functionality here
        with grpc.insecure_channel(f'{uri}:50051') as channel:
            stub = market_pb2_grpc.MarketStub(channel)
            request = RateItemRequest(
                item_id=item_id,
                buyer_address=self.buyer_address,
                rating=rating
            )
            response = stub.RateItem(request)
            if response.status == RateItemResponse.SUCCESS:
                print(" SUCCESS")
            else:
                print(" Failed to rate item.")


    def Notify(self, request, context):
        print({request.message})
    

    def print_search_results(self, response):
        print("")
        for item in response.items:
            print("–")
            print(f"Item ID: {item.item_id}, Price: ${item.price}, Name: {item.name}, Category: {item.category},")
            print(f"Description: {item.description}")
            print(f"Quantity Remaining: {item.quantity_remaining}")
            print(f"Rating: {item.rating} / 5  |  Seller: {item.seller}")
        print("–")


if __name__ == '__main__':
    buyer_address = "120.13.188.178:50051"

    buyer_client = BuyerClient(buyer_address)

    # Example: Buyer can perform operations like searching items, buying items, etc.
    buyer_client.search_item("Laptop", Category.ELECTRONICS)

    # Example: Buyer can perform other operations like adding items to wishlist
    buyer_client.add_to_wishlist("1")

    # Example: Buyer can perform other operations like adding items to wishlist, rating items, etc.
    buyer_client.rate_item("1", 5)

    # Example : Buyer can perform other operations like buying items
    buyer_client.buy_item("1", 2)
    

