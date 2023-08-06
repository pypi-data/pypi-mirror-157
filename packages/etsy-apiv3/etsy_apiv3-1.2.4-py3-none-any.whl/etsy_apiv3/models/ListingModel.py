from __future__ import annotations
from models.ListingImageModel import ListingImage
from models.ProductionPartnerModel import ProductionPartner
from models.ShippingProfileModel import ShippingProfile
from models.ShopModel import Shop
from models.TranslationModel import Translation
from models.UserModel import User
from models.PriceModel import Price
from typing import List, Optional
from pydantic import BaseModel
from models.ProductModel import Product

class Inventory(BaseModel):
    products: List[Product]
    price_on_property: List[int]
    quantity_on_property: List[int]
    sku_on_property: List[int]
    listing: Optional[Listing]



class Listing(BaseModel):
    listing_id: int
    user_id: int
    shop_id: int
    title: str
    description: str
    state: str
    creation_timestamp: int
    ending_timestamp: int
    original_creation_timestamp: int
    last_modified_timestamp: int
    state_timestamp: int
    quantity: int
    shop_section_id: Optional[int]
    featured_rank: int
    url: str
    num_favorers: int
    non_taxable: bool
    is_customizable: bool
    is_personalizable: bool
    personalization_is_required: bool
    personalization_char_count_max: Optional[int]
    personalization_instructions: Optional[str]
    listing_type: str
    tags: List[str]
    materials: List[str]
    shipping_profile_id: Optional[int]
    processing_min: Optional[int]
    processing_max: Optional[int]
    who_made: Optional[str]
    when_made: Optional[str]
    is_supply: bool
    item_weight: Optional[int]
    item_weight_unit: Optional[str]
    item_length: Optional[int]
    item_width: Optional[int]
    item_height: Optional[int]
    item_dimensions_unit: Optional[str]
    is_private: bool
    style: List[str]
    file_data: str
    has_variations: bool
    should_auto_renew: bool
    language: str
    price: Price
    taxonomy_id: int
    shipping_profile: Optional[ShippingProfile]
    user: Optional[User]
    shop: Optional[Shop]
    images: Optional[List[ListingImage]]
    production_partners: List[ProductionPartner]
    skus: List[str]
    translations: Optional[List[Translation]]
    inventory: Inventory
    
Inventory.update_forward_refs()