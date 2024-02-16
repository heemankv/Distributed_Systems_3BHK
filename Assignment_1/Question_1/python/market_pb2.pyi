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

class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SUCCESS: _ClassVar[Status]
    FAIL: _ClassVar[Status]
ELECTRONICS: Category
FASHION: Category
OTHERS: Category
ANY: Category
SUCCESS: Status
FAIL: Status

class RegisterSellerRequest(_message.Message):
    __slots__ = ("seller_address", "uuid")
    SELLER_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    seller_address: str
    uuid: str
    def __init__(self, seller_address: _Optional[str] = ..., uuid: _Optional[str] = ...) -> None: ...

class RegisterSellerResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: Status
    def __init__(self, status: _Optional[_Union[Status, str]] = ...) -> None: ...

class SellItemRequest(_message.Message):
    __slots__ = ("name", "quantity", "description", "seller_address", "price_per_unit", "seller_uuid", "category")
    NAME_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SELLER_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    PRICE_PER_UNIT_FIELD_NUMBER: _ClassVar[int]
    SELLER_UUID_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    name: str
    quantity: int
    description: str
    seller_address: str
    price_per_unit: float
    seller_uuid: str
    category: Category
    def __init__(self, name: _Optional[str] = ..., quantity: _Optional[int] = ..., description: _Optional[str] = ..., seller_address: _Optional[str] = ..., price_per_unit: _Optional[float] = ..., seller_uuid: _Optional[str] = ..., category: _Optional[_Union[Category, str]] = ...) -> None: ...

class SellItemResponse(_message.Message):
    __slots__ = ("status", "item_id")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ITEM_ID_FIELD_NUMBER: _ClassVar[int]
    status: Status
    item_id: str
    def __init__(self, status: _Optional[_Union[Status, str]] = ..., item_id: _Optional[str] = ...) -> None: ...

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
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: Status
    def __init__(self, status: _Optional[_Union[Status, str]] = ...) -> None: ...

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
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: Status
    def __init__(self, status: _Optional[_Union[Status, str]] = ...) -> None: ...

class DisplaySellerItemsRequest(_message.Message):
    __slots__ = ("seller_address", "seller_uuid")
    SELLER_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    SELLER_UUID_FIELD_NUMBER: _ClassVar[int]
    seller_address: str
    seller_uuid: str
    def __init__(self, seller_address: _Optional[str] = ..., seller_uuid: _Optional[str] = ...) -> None: ...

class ItemDetails(_message.Message):
    __slots__ = ("item_id", "price_per_unit", "name", "category", "description", "quantity", "seller_address", "rating")
    ITEM_ID_FIELD_NUMBER: _ClassVar[int]
    PRICE_PER_UNIT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    SELLER_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    RATING_FIELD_NUMBER: _ClassVar[int]
    item_id: str
    price_per_unit: float
    name: str
    category: Category
    description: str
    quantity: int
    seller_address: str
    rating: float
    def __init__(self, item_id: _Optional[str] = ..., price_per_unit: _Optional[float] = ..., name: _Optional[str] = ..., category: _Optional[_Union[Category, str]] = ..., description: _Optional[str] = ..., quantity: _Optional[int] = ..., seller_address: _Optional[str] = ..., rating: _Optional[float] = ...) -> None: ...

class DisplaySellerItemsResponse(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[ItemDetails]
    def __init__(self, items: _Optional[_Iterable[_Union[ItemDetails, _Mapping]]] = ...) -> None: ...

class SearchItemRequest(_message.Message):
    __slots__ = ("item_name", "category")
    ITEM_NAME_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    item_name: str
    category: Category
    def __init__(self, item_name: _Optional[str] = ..., category: _Optional[_Union[Category, str]] = ...) -> None: ...

class SearchItemResponse(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[ItemDetails]
    def __init__(self, items: _Optional[_Iterable[_Union[ItemDetails, _Mapping]]] = ...) -> None: ...

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
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: Status
    def __init__(self, status: _Optional[_Union[Status, str]] = ...) -> None: ...

class AddToWishListRequest(_message.Message):
    __slots__ = ("item_id", "buyer_address")
    ITEM_ID_FIELD_NUMBER: _ClassVar[int]
    BUYER_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    item_id: str
    buyer_address: str
    def __init__(self, item_id: _Optional[str] = ..., buyer_address: _Optional[str] = ...) -> None: ...

class AddToWishListResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: Status
    def __init__(self, status: _Optional[_Union[Status, str]] = ...) -> None: ...

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
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: Status
    def __init__(self, status: _Optional[_Union[Status, str]] = ...) -> None: ...

class NotifyBuyerRequest(_message.Message):
    __slots__ = ("type", "item_id", "updated_item")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ITEM_ID_FIELD_NUMBER: _ClassVar[int]
    UPDATED_ITEM_FIELD_NUMBER: _ClassVar[int]
    type: str
    item_id: str
    updated_item: ItemDetails
    def __init__(self, type: _Optional[str] = ..., item_id: _Optional[str] = ..., updated_item: _Optional[_Union[ItemDetails, _Mapping]] = ...) -> None: ...

class NotifySellerRequest(_message.Message):
    __slots__ = ("type", "item_id", "quantity", "buyer_address")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ITEM_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    BUYER_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    type: str
    item_id: str
    quantity: int
    buyer_address: str
    def __init__(self, type: _Optional[str] = ..., item_id: _Optional[str] = ..., quantity: _Optional[int] = ..., buyer_address: _Optional[str] = ...) -> None: ...

class NotificationMessage(_message.Message):
    __slots__ = ("notify_buyer", "notify_seller")
    NOTIFY_BUYER_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_SELLER_FIELD_NUMBER: _ClassVar[int]
    notify_buyer: NotifyBuyerRequest
    notify_seller: NotifySellerRequest
    def __init__(self, notify_buyer: _Optional[_Union[NotifyBuyerRequest, _Mapping]] = ..., notify_seller: _Optional[_Union[NotifySellerRequest, _Mapping]] = ...) -> None: ...
