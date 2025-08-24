from flask import Flask, render_template, request, redirect, url_for
import boto3, json, os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# AWS S3 configuration
S3_BUCKET = "multi-blogs-1414"
S3_REGION = "us-east-1"
s3 = boto3.client('s3', region_name=S3_REGION)

# Helper: Load catalog
def load_catalog():
    try:
        response = s3.get_object(Bucket=S3_BUCKET, Key="catalog.json")
        return json.loads(response['Body'].read())
    except s3.exceptions.NoSuchKey:
        return []

# Helper: Save catalog
def save_catalog(catalog):
    s3.put_object(Bucket=S3_BUCKET, Key="catalog.json",
                  Body=json.dumps(catalog, indent=4),
                  ContentType="application/json")

@app.route('/')
def index():
    catalog = load_catalog()
    return render_template('index.html', catalog=catalog)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        image = request.files['image']

        filename = secure_filename(image.filename)
        s3.upload_fileobj(image, S3_BUCKET, f"images/{filename}")

        catalog = load_catalog()
        catalog.append({"name": name, "price": price, "image": filename})
        save_catalog(catalog)
        return redirect(url_for('index'))
    return render_template('upload.html')

@app.route('/edit/<int:product_id>', methods=['GET', 'POST'])
def edit(product_id):
    catalog = load_catalog()
    product = catalog[product_id]

    if request.method == 'POST':
        product['name'] = request.form['name']
        product['price'] = request.form['price']
        save_catalog(catalog)
        return redirect(url_for('index'))

    return render_template('edit.html', product=product, product_id=product_id)

@app.route('/delete/<int:product_id>')
def delete(product_id):
    catalog = load_catalog()
    product = catalog.pop(product_id)
    save_catalog(catalog)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
