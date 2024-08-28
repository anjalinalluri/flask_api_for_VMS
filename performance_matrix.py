from app import PurchaseOrder
from datetime import datetime

def calculate_on_time_delivery_rate(vendor_code):
    total_orders = PurchaseOrder.objects(vendor_code=vendor_code, status="completed").count()
    on_time_orders = PurchaseOrder.objects(vendor_code=vendor_code, status="completed", delivery_date__lte=datetime.now()).count()
    return (on_time_orders / total_orders) * 100 if total_orders > 0 else 0

def calculate_quality_rating_avg(vendor_code):
    completed_orders = PurchaseOrder.objects(vendor_code=vendor_code, status="completed")
    total_quality = sum([order.quality_rating for order in completed_orders])
    return total_quality / completed_orders.count() if completed_orders.count() > 0 else 0

def calculate_response_time(vendor_code):
    orders = PurchaseOrder.objects(vendor_code=vendor_code)
    total_response_time = sum([(order.acknowledgment_date - order.issue_date).total_seconds() for order in orders if order.acknowledgment_date])
    return total_response_time / orders.count() if orders.count() > 0 else 0

def calculate_fulfillment_rate(vendor_code):
    total_orders = PurchaseOrder.objects(vendor_code=vendor_code).count()
    fulfilled_orders = PurchaseOrder.objects(vendor_code=vendor_code, status="completed").count()
    return (fulfilled_orders / total_orders) * 100 if total_orders > 0 else 0
