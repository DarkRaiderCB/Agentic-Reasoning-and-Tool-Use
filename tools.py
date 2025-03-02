from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import random


def debug_log(message: str) -> None:
    """Global debug logging function"""
    print(f"🔍 Log: {message}")


@dataclass
class Product:
    id: str
    name: str
    price: float
    color: str
    size: str
    store: str
    stock: int
    description: str


@dataclass
class ShippingDetails:
    available: bool
    cost: float
    estimated_days: int
    delivery_date: datetime


@dataclass
class ReturnPolicy:
    store: str
    days_allowed: int
    free_returns: bool
    conditions: str


class EcommerceTools:
    def __init__(self):
        # Mock product database
        self.products = [
            Product("1", "Floral Summer Skirt", 35.99, "Floral",
                    "S", "StoreA", 10, "Beautiful floral pattern"),
            Product("2", "White Athletic Sneakers", 65.99, "White",
                    "8", "StoreB", 5, "Classic white sneakers"),
            Product("3", "Casual Denim Jacket", 80, "Blue",
                    "M", "StoreA", 8, "Casual denim jacket"),
            Product("4", "Cocktail Dress", 89.99, "Black", "S",
                    "StoreB", 15, "Elegant cocktail dress"),
            Product("5", "Casual Denim Jacket", 75.99, "Blue",
                    "M", "StoreB", 6, "Casual denim jacket"),
            Product("6", "Casual Denim Jacket", 82.99, "Blue",
                    "M", "StoreC", 4, "Casual denim jacket"),
        ]

        self.stores = {
            "StoreA": ReturnPolicy("StoreA", 30, True, "Items must be unworn with tags"),
            "StoreB": ReturnPolicy("StoreB", 14, False, "Return shipping fee applies"),
            "StoreC": ReturnPolicy("StoreC", 21, True, "Free returns within 21 days"),
        }

        self.promo_codes = {
            "SAVE10": 0.10,
            "SUMMER20": 0.20,
        }

    def search_products(self,
                        query: str,
                        max_price: Optional[float] = None,
                        color: Optional[str] = None,
                        size: Optional[str] = None) -> List[Product]:
        """Search for products matching the given criteria"""
        debug_log(f"Starting search with query: '{query}'")
        debug_log(
            f"Filters - Max Price: {max_price}, Color: {color}, Size: {size}")

        results = []

        # Breaking query into meaningful keywords
        keywords = [word.lower() for word in query.split()
                    if word.lower() not in ['a', 'the', 'in', 'with', 'and', 'or', 'for', 'to', 'under']]
        debug_log(f"Search keywords: {keywords}")

        for product in self.products:
            product_text = f"{product.name} {product.description} {product.color}".lower(
            )
            debug_log(f"\nChecking product: {product.name}")
            debug_log(f"Product details: {product_text}")

            # Check keyword matches
            keyword_matches = []
            for keyword in keywords:
                if keyword in product_text:
                    keyword_matches.append(keyword)

            if keyword_matches:
                debug_log(f"✓ Keywords matched: {keyword_matches}")
            else:
                debug_log("✗ No keyword matches")
                continue

            # Check price constraint
            if max_price:
                if product.price > max_price:
                    debug_log(
                        f"✗ Price ${product.price} exceeds max ${max_price}")
                    continue
                debug_log(
                    f"✓ Price check passed: ${product.price} <= ${max_price}")

            # Check color
            if color:
                if color.lower() != product.color.lower():
                    debug_log(
                        f"✗ Color mismatch: wanted {color}, got {product.color}")
                    continue
                debug_log(f"✓ Color matched: {color}")

            # Check size
            if size:
                if size.lower() != product.size.lower():
                    debug_log(
                        f"✗ Size mismatch: wanted {size}, got {product.size}")
                    continue
                debug_log(f"✓ Size matched: {size}")

            debug_log("✓ All criteria matched - adding to results")
            results.append(product)

        return results

    def get_shipping_estimate(self,
                              product: Product,
                              target_date: Optional[datetime] = None) -> ShippingDetails:
        """Calculate shipping details for a product"""
        base_shipping = 5.99
        days = random.randint(5, 7)

        if target_date:
            delivery_date = datetime.now() + timedelta(days=days)
            available = delivery_date <= target_date
        else:
            available = True
            delivery_date = datetime.now() + timedelta(days=days)

        return ShippingDetails(
            available=available,
            cost=base_shipping,
            estimated_days=days,
            delivery_date=delivery_date
        )

    def apply_discount(self, price: float, code: str) -> Optional[float]:
        """Apply discount code to price"""
        debug_log(f"Checking discount code: {code}")
        if code in self.promo_codes:
            discount = self.promo_codes[code]
            final_price = price * (1 - discount)
            debug_log(
                f"✓ Valid code: {code}, {discount*100}% off, final price: ${final_price:.2f}")
            return final_price
        debug_log(f"✗ Invalid discount code: {code}")
        return None

    def compare_prices(self, product_name: str) -> Dict[str, float]:
        """Compare prices across stores"""
        debug_log(f"Comparing prices for: {product_name}")
        results = {}
        for product in self.products:
            if product_name.lower() in product.name.lower():
                results[product.store] = product.price
                debug_log(f"Found in {product.store}: ${product.price:.2f}")
        return results

    def get_return_policy(self, store: str) -> Optional[ReturnPolicy]:
        """Get return policy for a store"""
        debug_log(f"Checking return policy for: {store}")
        policy = self.stores.get(store)
        if policy:
            debug_log(f"✓ Found policy for {store}")
        else:
            debug_log(f"✗ No policy found for {store}")
        return policy
