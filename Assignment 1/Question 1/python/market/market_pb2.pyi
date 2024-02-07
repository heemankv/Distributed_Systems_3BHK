from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Category(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ELECTRONICS: _ClassVar[Category]
    FASHION: _ClassVar[Category]
    OTHERS: _ClassVar[Category]
    ANY: _ClassVar[Category]
ELECTRONICS: Category
FASHION: Category
OTHERS: Category
ANY: Category

class RegisterSellerRequest(_message.Message):
    __slots__ = ("seller_address", "uuid")
    SELLER_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    seller_address: str
    uuid: str
    def __init__(self, seller_address: _Optional[str] = ..., uuid: _Optional[str] = ...) -> None: ...

class RegisterSellerResponse(_message.Message):
    __slots__ = ("status",)
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SUCCESS: _ClassVar[RegisterSellerResponse.Status]
        FAIL: _ClassVar[RegisterSellerResponse.Status]
    SUCCESS: RegisterSellerResponse.Status
    FAIL: RegisterSellerResponse.Status
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: RegisterSellerResponse.Status
    def __init__(self, status: _Optional[_Union[RegisterSellerResponse.Status, str]] = ...) -> None: ...

class SellItemRequest(_message.Message):
    __slots__ = ("product_name", "quantity", "description", "seller_address", "price_per_unit", "seller_uuid")
    class Category(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ELECTRONICS: _ClassVar[SellItemRequest.Category]
        FASHION: _ClassVar[SellItemRequest.Category]
        OTHERS: _ClassVar[SellItemRequest.Category]
    ELECTRONICS: SellItemRequest.Category
    FASHION: SellItemRequest.Category
    OTHERS: SellItemRequest.Category
    PRODUCT_NAME_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SELLER_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    PRICE_PER_UNIT_FIELD_NUMBER: _ClassVar[int]
    SELLER_UUID_FIELD_NUMBER: _ClassVar[int]
    product_name: str
    quantity: int
    description: str
    seller_address: str
    price_per_unit: float
    seller_uuid: str
    def __init__(self, product_name: _Optional[str] = ..., quantity: _Optional[int] = ..., description: _Optional[str] = ..., seller_address: _Optional[str] = ..., price_per_unit: _Optional[float] = ..., seller_uuid: _Optional[str] = ...) -> None: ...

class SellItemResponse(_message.Message):
    __slots__ = ("status", "item_id")
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SUCCESS: _ClassVar[SellItemResponse.Status]
        FAIL: _ClassVar[SellItemResponse.Status]
    SUCCESS: SellItemResponse.Status
    FAIL: SellItemResponse.Status
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ITEM_ID_FIELD_NUMBER: _ClassVar[int]
    status: SellItemResponse.Status
    item_id: str
    def __init__(self, status: _Optional[_Union[SellItemResponse.Status, str]] = ..., item_id: _Optional[str] = ...) -> None: ...

class UpdateItemRequest(_message.Message):
    __slots__ = ("item_id", "new_price", "new_quantity", "seller_address", "seller_uuid")
    ITEM_ID_FIELD_NUMBER: _ClassVar[int]
    NEW_PRICE_FIELD_NUMBER: _ClassVar[int]
    NEW_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    SELLER_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    SELLER_UUID_FIELD_NUMBER: _ClassVar[int]
    item_id: str
    new_price: float
    new_quantity: int
    seller_address: str
    seller_uuid: str
    def __init__(self, item_id: _Optional[str] = ..., new_price: _Optional[float] = ..., new_quantity: _Optional[int] = ..., seller_address: _Optional[str] = ..., seller_uuid: _Optional[str] = ...) -> None: ...

class UpdateItemResponse(_message.Message):
    __slots__ = ("status",)
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SUCCESS: _ClassVar[UpdateItemResponse.Status]
        FAIL: _ClassVar[UpdateItemResponse.Status]
    SUCCESS: UpdateItemResponse.Status
    FAIL: UpdateItemResponse.Status
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: UpdateItemResponse.Status
    def __init__(self, status: _Optional[_Union[UpdateItemResponse.Status, str]] = ...) -> None: ...

class DeleteItemRequest(_message.Message):
    __slots__ = ("item_id", "seller_address", "seller_uuid")
    ITEM_ID_FIELD_NUMBER: _ClassVar[int]
    SELLER_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    SELLER_UUID_FIELD_NUMBER: _ClassVar[int]
    item_id: str
    seller_address: str
    seller_uuid: str
    def __init__(self, item_id: _Optional[str] = ..., seller_address: _Optional[str] = ..., seller_uuid: _Optional[str] = ...) -> None: ...

class DeleteItemResponse(_message.Message):
    __slots__ = ("status",)
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SUCCESS: _ClassVar[DeleteItemResponse.Status]
        FAIL: _ClassVar[DeleteItemResponse.Status]
    SUCCESS: DeleteItemResponse.Status
    FAIL: DeleteItemResponse.Status
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: DeleteItemResponse.Status
    def __init__(self, status: _Optional[_Union[DeleteItemResponse.Status, str]] = ...) -> None: ...

class DisplaySellerItemsRequest(_message.Message):
    __slots__ = ("seller_address", "seller_uuid")
    SELLER_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    SELLER_UUID_FIELD_NUMBER: _ClassVar[int]
    seller_address: str
    seller_uuid: str
    def __init__(self, seller_address: _Optional[str] = ..., seller_uuid: _Optional[str] = ...) -> None: ...

class DisplaySellerItemsResponse(_message.Message):
    __slots__ = ("items",)
    class ItemDetails(_message.Message):
        __slots__ = ("item_id", "price", "name", "category", "description", "quantity_remaining", "seller", "rating")
        class Category(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            ELECTRONICS: _ClassVar[DisplaySellerItemsResponse.ItemDetails.Category]
            FASHION: _ClassVar[DisplaySellerItemsResponse.ItemDetails.Category]
            OTHERS: _ClassVar[DisplaySellerItemsResponse.ItemDetails.Category]
        ELECTRONICS: DisplaySellerItemsResponse.ItemDetails.Category
        FASHION: DisplaySellerItemsResponse.ItemDetails.Category
        OTHERS: DisplaySellerItemsResponse.ItemDetails.Category
        ITEM_ID_FIELD_NUMBER: _ClassVar[int]
        PRICE_FIELD_NUMBER: _ClassVar[int]
        NAME_FIELD_NUMBER: _ClassVar[int]
        CATEGORY_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        QUANTITY_REMAINING_FIELD_NUMBER: _ClassVar[int]
        SELLER_FIELD_NUMBER: _ClassVar[int]
        RATING_FIELD_NUMBER: _ClassVar[int]
        item_id: str
        price: float
        name: str
        category: DisplaySellerItemsResponse.ItemDetails.Category
        description: str
        quantity_remaining: int
        seller: str
        rating: float
        def __init__(self, item_id: _Optional[str] = ..., price: _Optional[float] = ..., name: _Optional[str] = ..., category: _Optional[_Union[DisplaySellerItemsResponse.ItemDetails.Category, str]] = ..., description: _Optional[str] = ..., quantity_remaining: _Optional[int] = ..., seller: _Optional[str] = ..., rating: _Optional[float] = ...) -> None: ...
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[DisplaySellerItemsResponse.ItemDetails]
    def __init__(self, items: _Optional[_Iterable[_Union[DisplaySellerItemsResponse.ItemDetails, _Mapping]]] = ...) -> None: ...

class SearchItemRequest(_message.Message):
    __slots__ = ("item_name", "category")
    class Category(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ELECTRONICS: _ClassVar[SearchItemRequest.Category]
        FASHION: _ClassVar[SearchItemRequest.Category]
        OTHERS: _ClassVar[SearchItemRequest.Category]
        ANY: _ClassVar[SearchItemRequest.Category]
    ELECTRONICS: SearchItemRequest.Category
    FASHION: SearchItemRequest.Category
    OTHERS: SearchItemRequest.Category
    ANY: SearchItemRequest.Category
    ITEM_NAME_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    item_name: str
    category: SearchItemRequest.Category
    def __init__(self, item_name: _Optional[str] = ..., category: _Optional[_Union[SearchItemRequest.Category, str]] = ...) -> None: ...

class SearchItemResponse(_message.Message):
    __slots__ = ("items",)
    class ItemDetails(_message.Message):
        __slots__ = ("item_id", "price", "name", "category", "description", "quantity_remaining", "rating", "seller")
        class Category(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            ELECTRONICS: _ClassVar[SearchItemResponse.ItemDetails.Category]
            FASHION: _ClassVar[SearchItemResponse.ItemDetails.Category]
            OTHERS: _ClassVar[SearchItemResponse.ItemDetails.Category]
        ELECTRONICS: SearchItemResponse.ItemDetails.Category
        FASHION: SearchItemResponse.ItemDetails.Category
        OTHERS: SearchItemResponse.ItemDetails.Category
        ITEM_ID_FIELD_NUMBER: _ClassVar[int]
        PRICE_FIELD_NUMBER: _ClassVar[int]
        NAME_FIELD_NUMBER: _ClassVar[int]
        CATEGORY_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        QUANTITY_REMAINING_FIELD_NUMBER: _ClassVar[int]
        RATING_FIELD_NUMBER: _ClassVar[int]
        SELLER_FIELD_NUMBER: _ClassVar[int]
        item_id: str
        price: float
        name: str
        category: SearchItemResponse.ItemDetails.Category
        description: str
        quantity_remaining: int
        rating: float
        seller: str
        def __init__(self, item_id: _Optional[str] = ..., price: _Optional[float] = ..., name: _Optional[str] = ..., category: _Optional[_Union[SearchItemResponse.ItemDetails.Category, str]] = ..., description: _Optional[str] = ..., quantity_remaining: _Optional[int] = ..., rating: _Optional[float] = ..., seller: _Optional[str] = ...) -> None: ...
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[SearchItemResponse.ItemDetails]
    def __init__(self, items: _Optional[_Iterable[_Union[SearchItemResponse.ItemDetails, _Mapping]]] = ...) -> None: ...

class BuyItemRequest(_message.Message):
    __slots__ = ("item_id", "quantity", "buyer_address")
    ITEM_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    BUYER_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    item_id: str
    quantity: int
    buyer_address: str
    def __init__(self, item_id: _Optional[str] = ..., quantity: _Optional[int] = ..., buyer_address: _Optional[str] = ...) -> None: ...

class BuyItemResponse(_message.Message):
    __slots__ = ("status",)
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SUCCESS: _ClassVar[BuyItemResponse.Status]
        FAIL: _ClassVar[BuyItemResponse.Status]
    SUCCESS: BuyItemResponse.Status
    FAIL: BuyItemResponse.Status
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: BuyItemResponse.Status
    def __init__(self, status: _Optional[_Union[BuyItemResponse.Status, str]] = ...) -> None: ...

class AddToWishListRequest(_message.Message):
    __slots__ = ("item_id", "buyer_address")
    ITEM_ID_FIELD_NUMBER: _ClassVar[int]
    BUYER_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    item_id: str
    buyer_address: str
    def __init__(self, item_id: _Optional[str] = ..., buyer_address: _Optional[str] = ...) -> None: ...

class AddToWishListResponse(_message.Message):
    __slots__ = ("status",)
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SUCCESS: _ClassVar[AddToWishListResponse.Status]
        FAIL: _ClassVar[AddToWishListResponse.Status]
    SUCCESS: AddToWishListResponse.Status
    FAIL: AddToWishListResponse.Status
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: AddToWishListResponse.Status
    def __init__(self, status: _Optional[_Union[AddToWishListResponse.Status, str]] = ...) -> None: ...

class RateItemRequest(_message.Message):
    __slots__ = ("item_id", "buyer_address", "rating")
    ITEM_ID_FIELD_NUMBER: _ClassVar[int]
    BUYER_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    RATING_FIELD_NUMBER: _ClassVar[int]
    item_id: str
    buyer_address: str
    rating: int
    def __init__(self, item_id: _Optional[str] = ..., buyer_address: _Optional[str] = ..., rating: _Optional[int] = ...) -> None: ...

class RateItemResponse(_message.Message):
    __slots__ = ("status",)
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SUCCESS: _ClassVar[RateItemResponse.Status]
        FAIL: _ClassVar[RateItemResponse.Status]
    SUCCESS: RateItemResponse.Status
    FAIL: RateItemResponse.Status
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: RateItemResponse.Status
    def __init__(self, status: _Optional[_Union[RateItemResponse.Status, str]] = ...) -> None: ...

class NotificationMessage(_message.Message):
    __slots__ = ("notification",)
    NOTIFICATION_FIELD_NUMBER: _ClassVar[int]
    notification: str
    def __init__(self, notification: _Optional[str] = ...) -> None: ...
