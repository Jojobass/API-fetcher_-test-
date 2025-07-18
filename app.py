from flask import Flask, Response
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
import requests
from models import *
import logging
from logging.handlers import RotatingFileHandler
import os
from flask import render_template
from sqlalchemy.inspection import inspect
import threading



API_URL_1 = "https://bot-igor.ru/api/products?on_main=true"
API_URL_2 = "https://bot-igor.ru/api/products?on_main=false"
INTERVAL = 60

# --- Logging setup ---
log_dir = "logs"
log_file = "app.log"

os.makedirs(log_dir, exist_ok=True)

# Set up root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),  # Console
        RotatingFileHandler(
            filename=os.path.join(log_dir, log_file),
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=3,
            encoding="utf-8"
        )
    ]
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

# --- Configuration ---
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "1111")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "mydb")

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


# --- API Fetching Logic ---
def store_key_value(key, value):
    record = AdditionalInfo.query.filter_by(name=key).first()
    if not record:
        record = AdditionalInfo(name=key)
        db.session.add(record)
    record.value = value

def upsert(model, pk_name, pk_value, updates):
    pk_column = getattr(model, pk_name)
    existing = db.session.query(model).filter(pk_column == pk_value).first()
    if existing:
        for key, value in updates.items():
            if key != pk_name:
                setattr(existing, key, value)
    else:
        db.session.add(model(**updates))

# --- Load JSON into DB ---
def load_data_from_json_onmain():
    try:
        res1 = requests.get(API_URL_1)
        res1.raise_for_status()
        data = res1.json()
    except Exception as e:
        logger.error(f"❌ Error fetching first API: {e}")
        return

    for item in data.get("categories", []):
        upsert(Category, "Category_ID", item["Category_ID"], item)

    for item in data.get("product_marks", []):
        upsert(ProductMark, "Mark_ID", item["Mark_ID"], item)

    for item in data.get("special_project_parameters_actions", []):
        upsert(ProjectParametersAction, "id", item["id"], item)

    for item in data.get("special_project_parameters_badges", []):
        upsert(ProjectParametersBadge, "id", item["id"], item)

    for key, value in data.get("special_project_parameters", {}).items():
        existing = db.session.query(ProjectParameter).filter(ProjectParameter.key == key).first()
        if existing:
            setattr(existing, 'value', value)
        else:
            db.session.merge(ProjectParameter(key=key, value=value))

    for method in data.get("special_project_parameters_json", {}).get("delivery_method", {}).get("methods_list", []):
        existing = db.session.query(DeliveryMethod).filter(DeliveryMethod.type == method.get("type")).first()
        if existing:
            setattr(existing, 'name', method.get("name"))
            setattr(existing, 'description', method.get("description"))
        else:
            method_db = DeliveryMethod(
                name=method.get("name"),
                type=method.get("type"),
                description=method.get("description")
            )
            db.session.merge(method_db)
        for addr in method.get("addr_points", []):
            existing = db.session.query(DeliveryAddr).filter(DeliveryAddr.address == addr.get("address") and DeliveryAddr.name == addr.get("name")).first()
            if not existing:
                db.session.merge(DeliveryAddr(
                    method_id=method_db.id,
                    address=addr.get("address"),
                    name=addr.get("name")
                ))

    for val in data.get("special_project_parameters_json", {}).get("fast_search_strings", {}).get("parameters_list", []):
        existing = db.session.query(FastSearchParameter).filter(FastSearchParameter.value == val).first()
        if not existing:
            db.session.merge(FastSearchParameter(value=val))

    gr = data.get("special_project_parameters_json", {}).get("global_reviews", {})
    if gr:
        store_key_value("global_reviews", gr)

    is_side_menu = data.get("special_project_parameters_json", {}).get("is_side_menu", None)
    store_key_value("is_side_menu", is_side_menu)

    status = data.get("status")
    store_key_value("status", status)

    db.session.commit()
    
def load_data_from_json_notonmain():
    try:
        res1 = requests.get(API_URL_2)
        res1.raise_for_status()
        data = res1.json()
    except Exception as e:
        print(f"❌ Error fetching second API: {e}")
        return
    
    for product in data.get("products", []):
        existing = db.session.query(Product).filter(Product.Product_ID == product.get("Product_ID")).first()
        if existing:
            setattr(existing, "Created_At", product.get("Created_At"))
            setattr(existing, "OnMain", product.get("OnMain"))
            setattr(existing, "Product_Name", product.get("Product_Name"))
            setattr(existing, "Updated_At", product.get("Updated_At"))
            setattr(existing, "colors", product.get("colors"))
            setattr(existing, "excluded", product.get("excluded"))
            setattr(existing, "extras", product.get("extras"))
            setattr(existing, "importance_num", product.get("importance_num"))
            setattr(existing, "marks", product.get("marks"))
            setattr(existing, "moysklad_connector_products_data", product.get("moysklad_connector_products_data"))
            setattr(existing, "reviews", product.get("reviews"))
            setattr(existing, "reviews_video", product.get("reviews_video"))
            setattr(existing, "tags", product.get("tags"))
        else:
            product_db = Product(
                Created_At=product.get("Created_At"),
                OnMain=product.get("OnMain"),
                Product_ID=product.get("Product_ID"),
                Product_Name=product.get("Product_Name"),
                Updated_At=product.get("Updated_At"),
                colors=product.get("colors"),
                excluded=product.get("excluded"),
                extras=product.get("extras"),
                importance_num=product.get("importance_num"),
                marks=product.get("marks"),
                moysklad_connector_products_data=product.get("moysklad_connector_products_data"),
                reviews=product.get("reviews"),
                reviews_video=product.get("reviews_video"),
                tags=product.get("tags"),
            )
            db.session.merge(product_db)
        
        for category in product.get("categories", []):
            db.session.merge(ProductCategories(product_id=product.get("Product_ID"), category_id=category.get("Category_ID")))
        
        for image in product.get("images", []):
            existing = db.session.query(ProductImage).filter(ProductImage.Image_ID == image.get("Image_ID")).first()
            if existing:
                setattr(existing, "Image_URL", image.get("Image_URL"))
                setattr(existing, "MainImage", image.get("MainImage"))
                setattr(existing, "Product_ID", product.get("Product_ID"))
                setattr(existing, "position", image.get("position"))
                setattr(existing, "sort_order", image.get("sort_order"))
                setattr(existing, "title", image.get("title"))
            else:
                db.session.merge(ProductImage(
                    Image_ID = image.get("Image_ID"),
                    Image_URL = image.get("Image_URL"),
                    MainImage = image.get("MainImage"),
                    Product_ID = product_db.Product_ID,
                    position = image.get("position"),
                    sort_order = image.get("sort_order"),
                    title = image.get("title"),
                ))
        
        for parameter in product.get("parameters", []):
            upsert(ProductParameter, "Parameter_ID", parameter["Parameter_ID"], parameter)
            
            
    db.session.commit()

def load_data_from_json():
    with app.app_context():
        load_data_from_json_onmain()
        load_data_from_json_notonmain()
        logger.info("✅Data loaded successfully")
    
def run_data_loader_threaded():
    def thread_job():
        with app.app_context():
            load_data_from_json()
            logger.info("✅ Data loaded successfully (in background thread)")

    threading.Thread(target=thread_job, daemon=True).start()


@app.route("/overview")
def overview():
    counts = {
        "Categories": Category.query.count(),
        "Product Marks": ProductMark.query.count(),
        "Actions": ProjectParametersAction.query.count(),
        "Badges": ProjectParametersBadge.query.count(),
        "Project Parameters": ProjectParameter.query.count(),
        "Delivery Methods": DeliveryMethod.query.count(),
        "Delivery Addresses": DeliveryAddr.query.count(),
        "Fast Search Params": FastSearchParameter.query.count(),
        "Additional: global_reviews": AdditionalInfo.query.filter_by(name="global_reviews").count(),
        "Additional: is_side_menu": AdditionalInfo.query.filter_by(name="is_side_menu").count(),
        "Additional: status": AdditionalInfo.query.filter_by(name="status").count(),
        "Products": Product.query.count(),
    }
    summary = "\n".join(f"{k}: {v}" for k, v in counts.items())
    return Response(summary, mimetype="text/plain")

@app.route("/info")
def info():
    def serialize(model):
        return [
            {c.key: getattr(obj, c.key) for c in inspect(model).mapper.column_attrs}
            for obj in db.session.query(model).all()
        ]

    all_data = {
        "Categories": serialize(Category),
        "Product Marks": serialize(ProductMark),
        "Actions": serialize(ProjectParametersAction),
        "Badges": serialize(ProjectParametersBadge),
        "Project Parameters": serialize(ProjectParameter),
        "Delivery Methods": serialize(DeliveryMethod),
        "Delivery Addresses": serialize(DeliveryAddr),
        "Fast Search Params": serialize(FastSearchParameter),
        "Additional Info": serialize(AdditionalInfo),
        "Product": serialize(Product),
        "ProductCategories": serialize(ProductCategories),
        "ProductImage": serialize(ProductImage),
        "ProductParameter": serialize(ProductParameter)
    }

    return render_template("info.html", data=all_data)


with app.app_context():
    db.create_all()
    run_data_loader_threaded()  # Start first fetch in background

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=run_data_loader_threaded, trigger="interval", seconds=INTERVAL)
    scheduler.start()
        

if __name__ == "__main__":
    app.run(debug=True, threaded=True, use_reloader=False, host="0.0.0.0", port=5000)