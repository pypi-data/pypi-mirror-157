import json
from utils.APIV3 import EtsySession
from resources import ListingResource, ReceiptResource
from models.ReceiptModel import ReceiptType
import time
import asyncio

FALKEL_CLIENT_KEY = "paiimgc9v4jeh24la7eouzu5"
FALKEL_CLIENT_SECRET = "a2xer79vbd"
FALKEL_TOKEN = {'access_token': '230829585.8TlG3bOTeeLmVc_zBgTkUgntSHocHTZHBFydEanXDlh2J36EF16AHlWCo9Ax4K-UvxQPIbuinoklo-Ih2w5TEfl3No', 'token_type': 'Bearer', 'expires_in': 3600, 'refresh_token': '230829585.T3xORQnKSk9PCUtb0fBsNVgINj88BknoonsfVhf_At8RtnkFjHha90hrNfDHswGXo7VNlNQnFo9uQSb8nuqCI_XqQ8', 'expires_at': 1652797307.4995313}

CLIENT_KEY = "hdvqwd0po24bcbnpb3p8m7c9"
CLIENT_SECRET = "ja6xhs76se"
TOKEN = {'access_token': '486257382.UxSUw5JyN6ePR2uUV_r3XZMM-z7aDhdJV-TKqNKpjvkIG7zpQ2_v2JsY8X_kJU5wifP1ZYOygOqVwwCWVNJcJjDz4s', 'token_type': 'Bearer', 'expires_in': 3600, 'refresh_token': '486257382.1FrkX99vReIOlyAxaCN78qFAKY4kihmWLrin8heBk1_i6Fq_Zdi4BkLRadSH1z1SsL5APYIzvz093msfCsyPzXyk2C', 'expires_at': 1656766099.6343791}

SHOP_ID = 20641892

session = EtsySession(client_key=FALKEL_CLIENT_KEY, client_secret=FALKEL_CLIENT_SECRET, token=FALKEL_TOKEN)
auth = session.create_auth()

resource = ListingResource(auth)
resource_ = ReceiptResource(auth)

offset = 0
receipts = []

start_time = time.time()



async def get_receipts(offset: int):
    receipts = resource_.find(SHOP_ID, limit=100, offset=offset, type=ReceiptType.PAID).results
    return receipts

async def main():
    tasks = []
    offset = 0
    for i in range(25):
        task = asyncio.create_task(get_receipts(offset))
        offset += 100
        tasks.append(task)
    result = await asyncio.gather(*tasks)
    print(result)

asyncio.run(main())

print(f"Finish Time: {time.time() - start_time}")

"""inventory = resource.get_listing_inventory(listing_id=1260997739)
#print(inventory)
products = []
for product in inventory.products:
    
    product_json = product.dict(include={"sku"})
    product_json["offerings"] = [{"price":float(offer.price.amount), "quantity":offer.quantity, "is_enabled":offer.is_enabled} for offer in product.offerings]
    product_json["property_values"] = [property_values.dict(include={"property_id", "property_name", "scale_id", "value_ids", "values"}) for property_values in product.property_values]

    products.append(product_json)
products[0]["sku"] = "test1"
products[1]["sku"] = "test2"
#print(json.dumps({"products":products}))

response = resource.update_listing_inventory(1260997739, products)

#print(response)"""