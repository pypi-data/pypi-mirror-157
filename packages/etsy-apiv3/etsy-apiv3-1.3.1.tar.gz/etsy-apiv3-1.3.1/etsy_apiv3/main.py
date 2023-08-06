import json
from etsy_apiv3.utils.APIV3 import EtsySession
from etsy_apiv3.resources import ListingResource

CLIENT_KEY = "hdvqwd0po24bcbnpb3p8m7c9"
CLIENT_SECRET = "ja6xhs76se"
TOKEN = {'access_token': '486257382.UxSUw5JyN6ePR2uUV_r3XZMM-z7aDhdJV-TKqNKpjvkIG7zpQ2_v2JsY8X_kJU5wifP1ZYOygOqVwwCWVNJcJjDz4s', 'token_type': 'Bearer', 'expires_in': 3600, 'refresh_token': '486257382.1FrkX99vReIOlyAxaCN78qFAKY4kihmWLrin8heBk1_i6Fq_Zdi4BkLRadSH1z1SsL5APYIzvz093msfCsyPzXyk2C', 'expires_at': 1656766099.6343791}

SHOP_ID = 20641892

session = EtsySession(client_key=CLIENT_KEY, client_secret=CLIENT_SECRET, token=TOKEN)
auth = session.create_auth()

resource = ListingResource(auth)

inventory = resource.get_listings_by_listing_ids(listing_ids=[1260997739, 533623129], includes="Inventory")
print(inventory)
"""products = []
print(inventory)
for product in inventory.products:
    
    product_json = product.dict(include={"sku"})
    product_json["offerings"] = [{"price":offer.price.amount / offer.price.divisor, "quantity":offer.quantity, "is_enabled":offer.is_enabled} for offer in product.offerings]
    product_json["property_values"] = [property_values.dict(include={"property_id", "property_name", "scale_id", "value_ids", "values"}) for property_values in product.property_values]

    products.append(product_json)
products[0]["sku"] = "test1"

print(json.dumps({"products":products}))

response = resource.update_listing_inventory(1260997739, products, price_on_property=[200], sku_on_property=[200], quantity_on_property=[200])

#print(response)"""