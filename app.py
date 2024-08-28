from datetime import datetime
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)

# Update MongoDB URI to connect to the 'vendors' database
app.config["MONGO_URI"] = "mongodb://localhost:27017/vendors"

# Initialize PyMongo with the app
mongo = PyMongo(app)

vendors_collection = mongo.db.vendors
purchase_orders_collection = mongo.db.purchase
performance_collection = mongo.db.performance


# Models
# __________________________
# Vendor Model

class VendorModel:
    def __init__(self):
        self.collection = vendors_collection

    def create_vendor(self, data):
        vendor = {
            "name": data["name"],
            "contact_details": data["contact_details"],
            "address": data["address"],
            "vendor_code": data.get("vendor_code", ""),
            "on_time_delivery_rate": 0.0,
            "quality_rating_avg": 0.0,
            "average_response_time": 0.0,
            "fulfillment_rate": 0.0,
        }
        result = self.collection.insert_one(vendor)
        
        # Create default performance record for the vendor
        performance_data = {
            "vendor_id": str(result.inserted_id),
            "date": datetime.now(),
            "on_time_delivery_rate": 0.0,
            "quality_rating_avg": 0.0,
            "average_response_time": 0.0,
            "fulfillment_rate": 0.0,
        }
        performance_model.create_performance_record(performance_data)

        return {
            "message": "Vendor created successfully",
            "vendor_id": str(result.inserted_id),
        }

    # Other vendor methods (get_all_vendors, get_vendor, update_vendor, delete_vendor)...

# Initialize VendorModel
vendor_model = VendorModel()

# _____________________________________________________
# Purchase Order Model

class PurchaseOrderModel:
    def __init__(self):
        self.collection = purchase_orders_collection

    def create_purchase_order(self, data):
        po = self.collection.insert_one(data)
        
        # Update vendor performance upon purchase order creation
        vendor_code = data["vendor_id"]
        update_vendor_performance(vendor_code)
        
        return {
            "message": "Purchase order created successfully",
            "po_id": str(po.inserted_id),
        }

    def update_purchase_order(self, po_id, data):
        result = self.collection.update_one({"_id": ObjectId(po_id)}, {"$set": data})
        
        if result.modified_count > 0:
            # Update vendor performance upon purchase order update
            vendor_code = data.get("vendor_id")
            if vendor_code:
                update_vendor_performance(vendor_code)
            return {"message": "Purchase order updated successfully"}
        else:
            return {"message": "Purchase order not found"}, 404

    # Other purchase order methods (get_all_purchase_orders, get_purchase_order, delete_purchase_order)...

# Initialize PurchaseOrderModel
purchase_order_model = PurchaseOrderModel()

# ________________________________________
# Define the PerformanceModel class

class PerformanceModel:
    def __init__(self):
        self.collection = performance_collection

    def create_performance_record(self, data):
        performance_record = {
            "vendor_id": data["vendor_id"],
            "date": data["date"],
            "on_time_delivery_rate": data["on_time_delivery_rate"],
            "quality_rating_avg": data["quality_rating_avg"],
            "average_response_time": data["average_response_time"],
            "fulfillment_rate": data["fulfillment_rate"],
        }
        result = self.collection.insert_one(performance_record)
        return {
            "message": "Performance record created successfully",
            "performance_id": str(result.inserted_id),
        }

    def get_performance_record(self, vendor_id):
        records = self.collection.find({"vendor_id": vendor_id}).sort("date", -1).limit(1)
        if records.count() > 0:
            record = records[0]
            return {
                "_id": str(record["_id"]),
                "vendor_id": record["vendor_id"],
                "date": record["date"],
                "on_time_delivery_rate": record["on_time_delivery_rate"],
                "quality_rating_avg": record["quality_rating_avg"],
                "average_response_time": record["average_response_time"],
                "fulfillment_rate": record["fulfillment_rate"],
            }
        else:
            return {"message": "Performance record not found"}, 404

# Initialize PerformanceModel
performance_model = PerformanceModel()

# Performance update logic

def update_vendor_performance(vendor_id):

    from performance_matrix import calculate_on_time_delivery_rate, calculate_quality_rating_avg, calculate_response_time, calculate_fulfillment_rate

    on_time_delivery_rate = calculate_on_time_delivery_rate(vendor_id)
    quality_rating_avg = calculate_quality_rating_avg(vendor_id)
    average_response_time = calculate_response_time(vendor_id)
    fulfillment_rate = calculate_fulfillment_rate(vendor_id)

    performance_data = {
        "vendor_id": vendor_id,
        "date": datetime.now(),
        "on_time_delivery_rate": on_time_delivery_rate,
        "quality_rating_avg": quality_rating_avg,
        "average_response_time": average_response_time,
        "fulfillment_rate": fulfillment_rate,
    }

    performance_model.create_performance_record(performance_data)
# Performance Model routes



#_________________________________________________________________________________________
#Routes

#Vendor routes

# Create
@app.route("/api/vendors", methods=["POST"])
@app.route("/api/vendors/", methods=["POST"])
def create_vendor():
    data = request.json
    return vendor_model.create_vendor(data)

# Get all vendors
@app.route("/api/vendors", methods=["GET"])
def get_all_vendors():
    return jsonify(vendor_model.get_all_vendors())

# Get vendor by id
@app.route("/api/vendors/<string:vendor_id>", methods=["GET"])
def get_vendor(vendor_id):
    return jsonify(vendor_model.get_vendor(vendor_id))

# updaye
@app.route("/api/vendors/<string:vendor_id>", methods=["PUT"])
def update_vendor(vendor_id):
    data = request.json
    return jsonify(vendor_model.update_vendor(vendor_id, data))

# delete
@app.route("/api/vendors/<string:vendor_id>", methods=["DELETE"])
def delete_vendor(vendor_id):
    return jsonify(vendor_model.delete_vendor(vendor_id))

#_______________________________________
# Purchase Order routes

# Create
@app.route("/api/purchase_orders", methods=["POST"])
def create_purchase_order():
    data = request.json
    return purchase_order_model.create_purchase_order(data)

# List all
@app.route("/api/purchase_orders", methods=["GET"])
def get_all_purchase_orders():
    vendor_id = request.args.get('vendor_id')
    return jsonify(purchase_order_model.get_all_purchase_orders(vendor_id))

# Get details of one specific
@app.route("/api/purchase_orders/<string:po_id>", methods=["GET"])
def get_purchase_order(po_id):
    return jsonify(purchase_order_model.get_purchase_order(po_id))

# Update
@app.route("/api/purchase_orders/<string:po_id>", methods=["PUT"])
def update_purchase_order(po_id):
    data = request.json
    return jsonify(purchase_order_model.update_purchase_order(po_id, data))

# Delete
@app.route("/api/purchase_orders/<string:po_id>", methods=["DELETE"])
def delete_purchase_order(po_id):
    return jsonify(purchase_order_model.delete_purchase_order(po_id))

#______________________________________
#Performance Model routes

def update_vendor_performance(vendor_code):

    from performance_matrix import calculate_on_time_delivery_rate, calculate_quality_rating_avg, calculate_response_time, calculate_fulfillment_rate

    on_time_delivery_rate = calculate_on_time_delivery_rate(vendor_code)
    quality_rating_avg = calculate_quality_rating_avg(vendor_code)
    average_response_time = calculate_response_time(vendor_code)
    fulfillment_rate = calculate_fulfillment_rate(vendor_code)

    performance_data = {
        "vendor_code": vendor_code,
        "date": datetime.now(),
        "on_time_delivery_rate": on_time_delivery_rate,
        "quality_rating_avg": quality_rating_avg,
        "average_response_time": average_response_time,
        "fulfillment_rate": fulfillment_rate
    }

    performance_model.create_performance_record(performance_data)


#performance route

@app.route("/api/vendors/<string:vendor_id>/performance", methods=["GET"])
def get_vendor_performance(vendor_id):
    return jsonify(performance_model.get_performance_record(vendor_id))


if __name__ == "__main__":
    app.run(debug=True)
