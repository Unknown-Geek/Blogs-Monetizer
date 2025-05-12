import os
from services.ad_service import AdService

def test_fetch_affiliate_products():
    service = AdService()
    products = service.fetch_affiliate_products()
    assert isinstance(products, list), "Products should be a list"
    for idx, product in enumerate(products):
        url = product.get("url")
        image_url = product.get("image_url")
        print(f"Row {idx+1}: URL = {url}, Image URL = {image_url}")
        assert url and url.startswith("http"), f"Row {idx+1}: First column should be a valid affiliate link. Got: {url}"
        assert image_url and (image_url.startswith("http") or image_url.startswith("//")), f"Row {idx+1}: Second column should be a valid image URL. Got: {image_url}"
    print(f"Total products fetched: {len(products)}")

if __name__ == "__main__":
    test_fetch_affiliate_products()
