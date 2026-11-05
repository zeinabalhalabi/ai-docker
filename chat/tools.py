from .models import Item
from decimal import Decimal

def check_stock(name):
    """Look up how many of an item we have."""
    item = Item.objects.filter(name__iexact=name).first()
    if item is None:
        return {"error": f"No item named '{name}' exists in the inventory."}
    return {"name": item.name, "quantity": item.quantity, "price": str(item.price)}


def list_items():
    """Return every item in the inventory."""
    items = Item.objects.all()
    return {
    "items": [
        {
            "name": i.name,
            "quantity": i.quantity,
            "price": str(i.price)
        }
        for i in items
    ]
}


def add_item(name, quantity, price):
    """Create a new item, or add to an existing one's stock."""
    item = Item.objects.filter(name__iexact=name).first()
    if item is not None:
        item.quantity += quantity
        item.save()
        return {"name": item.name, "quantity": item.quantity, "price": str(item.price), "created": False}
    item = Item.objects.create(name=name, quantity=quantity, price=price)
    return {"name": item.name, "quantity": item.quantity, "price": str(item.price), "created": True}


def remove_stock(name, quantity):
    """Take a quantity out of stock."""
    item = Item.objects.filter(name__iexact=name).first()
    if item is None:
        return {"error": f"No item named '{name}' exists in the inventory."}
    if quantity > item.quantity:
        return {
            "error": f"Cannot remove {quantity}. Only {item.quantity} in stock.",
            "name": item.name,
            "quantity": item.quantity,
        }
    item.quantity -= quantity
    item.save()
    return {"name": item.name, "quantity": item.quantity, "price": str(item.price)}

def increase_price(name, percentage):
    """Increase an inventory item's price by a percentage."""
    item = Item.objects.filter(name__iexact=name).first()

    if item is None:
        return {"error": f"No item named '{name}' exists in the inventory."}

    if percentage < 0:
        return {"error": "Percentage cannot be negative."}

    old_price = item.price
    increase = old_price * Decimal(str(percentage)) / Decimal("100")
    new_price = old_price + increase

    item.price = new_price.quantize(Decimal("0.01"))
    item.save()

    return {
        "name": item.name,
        "old_price": str(old_price),
        "percentage_increase": str(percentage),
        "new_price": str(item.price)
    }
def delete_item(name):
    """Remove an item from the inventory entirely."""
    item = Item.objects.filter(name__iexact=name).first()
    if item is None:
        return {"error": f"No item named '{name}' exists in the inventory."}
    item.delete()
    return {"deleted": name}

def calculate_cost(name, quantity, vat_percent=10):
    """Calculate the total cost of an item including VAT."""
    item = Item.objects.filter(name__iexact=name).first()

    if item is None:
        return {"error": f"No item named '{name}' exists in the inventory."}

    if quantity <= 0:
        return {"error": "Quantity must be greater than 0."}

    vat_percent = Decimal(str(vat_percent))
    subtotal = item.price * Decimal(quantity)
    vat = subtotal * vat_percent / Decimal("100")
    total = subtotal + vat

    return {
        "name": item.name,
        "quantity": quantity,
        "unit_price": float(item.price),
        "subtotal": float(subtotal),
        "vat_percent": float(vat_percent),
        "vat": float(vat),
        "total": float(total),
    }


TOOL_DECLARATIONS = [
    {
        "type": "function",
        "name": "check_stock",
        "description": "Look up the current quantity of a single item in the inventory. Use this whenever the user asks whether something is in stock or how many there are.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the item, e.g. 'Hammer'.",
                },
            },
            "required": ["name"],
        },
    },
    {
    "type": "function",
    "name": "increase_price",
    "description": "Increase the stored price of an existing inventory item by a specified percentage and save the new price. Use this when the user asks to increase an item's price.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The inventory item's name."
            },
            "percentage": {
                "type": "number",
                "description": "The percentage increase, such as 50 for a 50% increase."
            }
        },
        "required": ["name", "percentage"]
    }
},
    {
        "type": "function",
        "name": "list_items",
        "description": "Return every item in the inventory with its quantity. Use this when the user asks what is in stock generally, or asks for a list, rather than about one specific item.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "type": "function",
        "name": "add_item",
        "description": "Add stock to the inventory. If the item does not exist it is created; if it already exists the quantity is added to the existing total. Use this for restocking and for new deliveries.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the item, e.g. 'Hammer'.",
                },
                "quantity": {
                    "type": "integer",
                    "description": "How many units to add. Must be positive.",
                },
                "price": {
                    "type": "number",
                    "description": "The price per unit of the item.",
                },
            },
            "required": ["name", "quantity", "price"],
        },
    },
    {
        "type": "function",
        "name": "remove_stock",
        "description": "Reduce the quantity of an existing item. Use this when items are sold, shipped or used. This does NOT delete the item; it only lowers the number.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the item, e.g. 'Hammer'.",
                },
                "quantity": {
                    "type": "integer",
                    "description": "How many units to remove. Must be positive.",
                },
            },
            "required": ["name", "quantity"],
        },
    },
    {
        "type": "function",
        "name": "delete_item",
        "description": "Permanently remove an item and its record from the inventory entirely. This is destructive. Only use it when the user clearly wants the item gone, not when they want to reduce its quantity.",
        "parameters": {
            "type": "object",
            "properties": {

                "name": {
                    "type": "string",
                    "description": "The name of the item to delete.",
                },
            },
            "required": ["name"],
        },
    },
    {
        "type": "function",
        "name": "calculate_cost",
        "description": "Calculate the total cost of an item including VAT.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the item.",
                },
                "quantity": {
                    "type": "integer",
                    "description": "The quantity of the item.",
                },
                "vat_percent": {
                    "type": "number",
                    "description": "The VAT percentage (default is 10).",
                },
            },
            "required": ["name", "quantity"],
        },
    }
]

TOOL_FUNCTIONS = {
    "check_stock": check_stock,
    "list_items": list_items,
    "add_item": add_item,
    "remove_stock": remove_stock,
    "delete_item": delete_item,
    "calculate_cost": calculate_cost,
    "increase_price": increase_price,
}
