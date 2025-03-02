from typing import Dict, Any, Optional
import json
from tools import EcommerceTools, debug_log, Product
import re
from datetime import datetime, timedelta

SYSTEM_PROMPT = """You are a virtual shopping assistant helping users navigate fashion e-commerce platforms (SiteA, SiteB). Your goal is to interpret requests, reason about which tools to use, and provide clear, actionable responses. Use the following tools when needed:

1. [ProductSearch(query, max_price, color, size)]: Search for products.
2. [ShippingEstimator(product, target_date)]: Check shipping details.
3. [DiscountCalculator(price, code)]: Apply a promo code.
4. [PriceComparison(product)]: Compare prices across sites.
5. [ReturnPolicyChecker(store)]: Get return policy.
6. [QueryParser()]: Extract key details from user queries.

Reason step-by-step, use [Tool(args)] to call tools, and integrate results into your response. Reflect on failures and adjust as needed."""


class ShoppingAssistant:
    def __init__(self):
        self.tools = EcommerceTools()
        # Define common shopping-related terms for better generalised pattern matching
        self.search_patterns = {
            'price': [
                r'under\s*\$(\d+\.?\d*)',
                r'less than\s*\$(\d+\.?\d*)',
                r'cheaper than\s*\$(\d+\.?\d*)',
                r'\$(\d+\.?\d*)\s*or less',
                r'\$(\d+\.?\d*)\s*'
            ],
            'date': [
                r'by\s*(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
                r'before\s*(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
                r'deliver(?:ed|y)?\s*by\s*(\w+\s*\d+)',
                r'arrive\s*by\s*(\w+\s*\d+)'
            ],
            'comparison': [
                r'better deals?',
                r'compare',
                r'cheaper',
                r'best price',
                r'lowest price',
                r'price difference',
                r'price comparison'
            ],
            'return': [
                r'return policy',
                r'can i return',
                r'returns?',
                r'refund',
                r'exchange'
            ]
        }

    def _reason(self, thought: str) -> None:
        """Internal reasoning step"""
        print(f"🤔 Thinking: {thought}")

    def _act(self, action: str, result: Any) -> None:
        """Log action and result"""
        print(f"🔧 Action: {action}")
        print(f"📝 Result: {result}")

    def _use_tool(self, tool_name: str, params: Dict[str, Any] = None) -> None:
        """Log tool usage"""
        param_str = ", ".join(f"{k}={v}" for k, v in (params or {}).items())
        print(f"🛠️ Using Tool: {tool_name}({param_str})")

    def _extract_product_name(self, query: str) -> Optional[str]:
        """Extract product name from query using quotation marks or context"""
        # Try to find product name in quotes
        quote_match = re.search(r'[\'\"](.*?)[\'\"]', query)
        if quote_match and 'code' not in query[:query.find(quote_match.group(0))].lower():
            return quote_match.group(1)

        # Look for product-related keywords with improved patterns
        product_indicators = [
            r'(?:looking for|find|need|want)\s+(?:a|an)?\s*([\w\s]+?)(?:under|\$|in size|with size|color|from|at|\?|$)',
            r'(?:find|get|show)\s+(?:me\s+)?(?:a|an)?\s*([\w\s]+?)(?:under|\$|in size|with size|color|from|at|\?|$)',
            # Special case for items with specific descriptors
            r'(?:a|an)?\s*((?:\w+\s+)?(?:skirt|dress|jacket|shoes|sneakers|top))\s+(?:under|\$|in size|with size|color|from|at|\?|$)'
        ]

        for pattern in product_indicators:
            match = re.search(pattern, query.lower())
            if match:
                # Clean up the extracted product name
                product_name = match.group(1).strip()
                # Remove common filler words
                product_name = re.sub(r'\b(a|an|the|some)\b',
                                      '', product_name).strip()
                if product_name:
                    return product_name

        # Look for specific product types (just for mockup solution)
        product_types = ["skirt", "dress", "jacket", "sneakers", "shoes"]
        for product_type in product_types:
            if product_type in query.lower():
                # Looking for adjectives before the product type
                adj_match = re.search(
                    rf'(\w+)\s+{product_type}', query.lower())
                if adj_match:
                    return f"{adj_match.group(1)} {product_type}"
                return product_type

        return None

    def _parse_delivery_date(self, query: str) -> Optional[datetime]:
        """Parse delivery date requirements from query"""
        for pattern in self.search_patterns['date']:
            match = re.search(pattern, query.lower())
            if match:
                target_day = match.group(1)
                today = datetime.now()

                # Handle day of week
                if target_day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                    days_map = {
                        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
                        'friday': 4, 'saturday': 5, 'sunday': 6
                    }
                    target_day_num = days_map[target_day]
                    current_day = today.weekday()
                    days_until = (target_day_num - current_day) % 7
                    if days_until == 0:
                        days_until = 7
                    return today + timedelta(days=days_until)

                # Handle specific date
                try:
                    return datetime.strptime(target_day, "%B %d")
                except ValueError:
                    pass

        return None

    def parse_query(self, query: str) -> Dict[str, Any]:
        """Parse query for key information using patterns"""
        debug_log("Starting query parsing")

        info = {
            "max_price": None,
            "size": None,
            "color": None,
            "store": None,
            "delivery_target": None,
            "discount_code": None,
            "product_name": None,
            "query_type": "search"  # default type
        }

        # Extract product name first
        info["product_name"] = self._extract_product_name(query)
        debug_log(f"Extracted product name: {info['product_name']}")

        # Extract price using patterns
        for pattern in self.search_patterns['price']:
            match = re.search(pattern, query)
            if match:
                info["max_price"] = float(match.group(1))
                break

        # Extract size (now supports various formats)
        size_patterns = [
            r'size\s+(\w+)',
            r'in\s+(\w+)\s+size',
            r'size:\s*(\w+)'
        ]
        for pattern in size_patterns:
            match = re.search(pattern, query.lower())
            if match:
                info["size"] = match.group(1).upper()
                break

        # Extract color
        colors = ["white", "black", "blue", "red", "green", "yellow", "floral"]
        for color in colors:
            if color in query.lower():
                # Making sure it's not part of another word
                if re.search(rf'\b{color}\b', query.lower()):
                    info["color"] = color
                    break

        # Extract delivery target date
        info["delivery_target"] = self._parse_delivery_date(query)
        if info["delivery_target"]:
            debug_log(f"Found delivery target: {info['delivery_target']}")

        # Determining query type based on patterns
        if any(re.search(pattern, query.lower()) for pattern in self.search_patterns['comparison']):
            info["query_type"] = "comparison"
        elif any(re.search(pattern, query.lower()) for pattern in self.search_patterns['return']):
            info["query_type"] = "return"

        # Extract store information
        store_match = re.search(r'(?:at|from|in|store)\s+(Store[ABC])', query)
        if store_match:
            info["store"] = store_match.group(1)

        # Extract discount code
        discount_patterns = [
            r'discount code [\'\"]([\w\d]+)[\'\"]',
            r'code [\'\"]([\w\d]+)[\'\"]',
            r'coupon [\'\"]([\w\d]+)[\'\"]'
        ]
        for pattern in discount_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                info["discount_code"] = match.group(1)
                break

        debug_log(
            f"Final parsed query info: {json.dumps(info, default=str, indent=2)}")
        return info

    def handle_query(self, query: str) -> str:
        """Main query handling method implementing ReAct pattern"""
        self._reason(
            "Analyzing query to identify required tools and constraints")

        # Parse query for key information
        self._use_tool("QueryParser")
        info = self.parse_query(query)

        # Handle different query types based on detected patterns
        if info["query_type"] == "return" and info["store"]:
            return self._handle_return_query(info)
        elif info["query_type"] == "comparison" and info["product_name"]:
            return self._handle_comparison_query(info)
        else:
            return self._handle_search_query(info)

    def _handle_return_query(self, info: Dict[str, Any]) -> str:
        """Handle return policy related queries"""
        self._reason(f"Checking return policy for {info['store']}")

        self._use_tool("ReturnPolicyChecker", {"store": info["store"]})
        policy = self.tools.get_return_policy(info["store"])

        if policy:
            return (f"{info['store']} accepts returns within {policy.days_allowed} days. "
                    f"{'Returns are free' if policy.free_returns else 'Return shipping fee applies'}. "
                    f"{policy.conditions}")
        return f"Sorry, I couldn't find return policy information for {info['store']}"

    def _handle_comparison_query(self, info: Dict[str, Any]) -> str:
        """Handle price comparison queries"""
        self._reason("Comparing prices across stores")

        if not info["product_name"]:
            return "I couldn't determine which product you want to compare. Please specify the product name."

        self._use_tool("PriceComparison", {"product": info["product_name"]})
        comparisons = self.tools.compare_prices(info["product_name"])

        if comparisons:
            response = f"Here are the prices for the {info['product_name']} across stores:\n"
            for store, price in sorted(comparisons.items(), key=lambda x: x[1]):
                if price <= info["max_price"]:
                    response += f"- {store}: ${price:.2f}\n"
            return response
        return f"Sorry, I couldn't find any price comparisons for {info['product_name']}."

    def _handle_search_query(self, info: Dict[str, Any]) -> str:
        """Handle product search queries"""
        self._reason("Searching for products matching criteria")

        search_params = {
            "query": info["product_name"] if info["product_name"] else "",
            "max_price": info["max_price"],
            "color": info["color"],
            "size": info["size"]
        }
        self._use_tool("ProductSearch", search_params)

        results = self.tools.search_products(**search_params)
        self._act("Product Search", f"Found {len(results)} matching products")

        if not results:
            return "I couldn't find any products matching your criteria."

        return self._format_product_response(results[0], info)

    def _format_product_response(self, product: Product, info: Dict[str, Any]) -> str:
        """Format the product response with all relevant details"""
        response = [
            f"I found a {product.name} in size {product.size} for ${product.price:.2f} at {product.store}.",
            f"It's in stock ({product.stock} available)."
        ]

        if info["delivery_target"]:
            self._use_tool("ShippingEstimator", {
                "product": product.id,
                "target_date": info["delivery_target"]
            })
            shipping = self.tools.get_shipping_estimate(
                product, info["delivery_target"])

            estimated_date = datetime.now() + timedelta(days=shipping.estimated_days)
            date_str = estimated_date.strftime("%A, %B %d")

            if shipping.available:
                response.append(
                    f"It can be delivered by {date_str} (estimated {shipping.estimated_days} days) "
                    f"for ${shipping.cost:.2f} shipping."
                )
            else:
                response.append(
                    f"Sorry, we cannot guarantee delivery by your requested date. "
                    f"Estimated delivery would be {date_str}."
                )

        if info["discount_code"]:
            self._use_tool("DiscountCalculator", {
                "price": product.price,
                "code": info["discount_code"]
            })
            discounted_price = self.tools.apply_discount(
                product.price, info["discount_code"])

            if discounted_price:
                response.append(
                    f"With discount code '{info['discount_code']}', "
                    f"the final price would be ${discounted_price:.2f}."
                )
            else:
                response.append(
                    f"The discount code '{info['discount_code']}' is not valid.")

        return " ".join(response)


def main():
    assistant = ShoppingAssistant()

    # Example queries
    test_queries = [
        "Find a floral skirt under $140 in size S. Is it in stock, and can I apply a discount code 'SAVE10'?",
        "I need white sneakers (size 8) for under $80 that can arrive by Monday.",
        "I found a 'casual denim jacket' at $79 on StoreA. Any better deals?",
        "I want to buy a cocktail dress from StoreB, but only if returns are hassle-free. Do they accept returns?"
    ]

    print("=== Shopping Assistant Demo ===\n")

    print(SYSTEM_PROMPT)

    for query in test_queries:
        print(f"\n👤 User: {query}")
        response = assistant.handle_query(query)
        print(f"🤖 Assistant: {response}\n")
        print("-" * 80)


if __name__ == "__main__":
    main()
