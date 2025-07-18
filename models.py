from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Category(db.Model):
    __tablename__ = 'categories'
    Category_ID = db.Column(db.Integer, primary_key=True)
    Category_Name = db.Column(db.String(100)) 
    Category_Image = db.Column(db.String(255), nullable=True)
    sort_order = db.Column(db.Integer)

class ProductMark(db.Model):
    __tablename__ = 'product_marks'
    Mark_ID = db.Column(db.Integer, primary_key=True)
    Mark_Name = db.Column(db.String(50))

class ProjectParametersAction(db.Model):
    __tablename__ = 'special_project_parameters_actions'
    id = db.Column(db.Integer, primary_key=True)
    action_type = db.Column(db.String(50))
    description = db.Column(db.Text)
    extra_field_1 = db.Column(db.String(255))
    extra_field_2 = db.Column(db.String(255))
    image_url = db.Column(db.String(255))
    sort_order = db.Column(db.Integer)
    url = db.Column(db.String(255), nullable=True)

class ProjectParametersBadge(db.Model):
    __tablename__ = 'special_project_parameters_badges'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    meaning_tag = db.Column(db.String(50), nullable=True)
    sort_order = db.Column(db.Integer)
    url = db.Column(db.String(255))

class ProjectParameter(db.Model):
    __tablename__ = 'special_project_parameters'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True)
    value = db.Column(db.Text)

class DeliveryMethod(db.Model):
    __tablename__ = 'delivery_method_methods_list'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    type = db.Column(db.String(50), unique=True)
    description = db.Column(db.Text)

class DeliveryAddr(db.Model):
    __tablename__ = 'addr_points'
    id = db.Column(db.Integer, primary_key=True)
    method_id = db.Column(db.ForeignKey(DeliveryMethod.id, onupdate='CASCADE', ondelete='CASCADE'))
    address = db.Column(db.String(255))
    name = db.Column(db.String(100))

class FastSearchParameter(db.Model):
    __tablename__ = 'fast_search_strings'
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(100), unique=True)

class AdditionalInfo(db.Model):
    __tablename__ = 'additional_info'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    value = db.Column(db.JSON, nullable=True)
    
class Product(db.Model):
    __tablename__ = 'products'
    Created_At = db.Column(db.String(50))
    OnMain = db.Column(db.Boolean)
    Product_ID = db.Column(db.Integer, primary_key=True)
    Product_Name = db.Column(db.String(100))
    Updated_At = db.Column(db.String(50), nullable=True)
    colors = db.Column(db.JSON)
    excluded = db.Column(db.JSON)
    extras = db.Column(db.JSON)
    importance_num = db.Column(db.Integer, nullable=True)
    marks = db.Column(db.JSON)
    moysklad_connector_products_data = db.Column(db.Text, nullable=True)
    reviews = db.Column(db.JSON)
    reviews_video = db.Column(db.JSON)
    tags = db.Column(db.JSON, nullable=True)
    
class ProductCategories(db.Model):
    __tablename__ = 'products_categories'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.ForeignKey(Product.Product_ID, onupdate='CASCADE', ondelete='CASCADE'))
    category_id = db.Column(db.ForeignKey(Category.Category_ID, onupdate='CASCADE', ondelete='CASCADE'))
    uniqueness = db.UniqueConstraint('product_id', 'category_id')

class ProductImage(db.Model):
    __tablename__ = 'product_images'
    Image_ID = db.Column(db.Integer, primary_key=True)
    Image_URL = db.Column(db.String(255))
    MainImage = db.Column(db.Boolean)
    Product_ID = db.Column(db.ForeignKey(Product.Product_ID, onupdate='CASCADE', ondelete='CASCADE'))
    position = db.Column(db.String(50), nullable=True)
    sort_order = db.Column(db.Integer)
    title = db.Column(db.String(50), nullable=True)
    
class ProductParameter(db.Model):
    __tablename__ = 'product_parameters'
    Parameter_ID = db.Column(db.Integer, primary_key=True)
    Product_ID = db.Column(db.ForeignKey(Product.Product_ID, onupdate='CASCADE', ondelete='CASCADE'))
    chosen = db.Column(db.Boolean, nullable=True)
    disabled = db.Column(db.Boolean, nullable=True)
    extra_field_color = db.Column(db.JSON, nullable=True)
    extra_field_image = db.Column(db.String(255), nullable=True)
    name = db.Column(db.String(50), nullable=True)
    old_price = db.Column(db.Integer, nullable=True)
    parameter_string = db.Column(db.String(100), nullable=True)
    price = db.Column(db.Integer)
    sort_order = db.Column(db.Integer)
    