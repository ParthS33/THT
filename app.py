from flask import Flask, render_template, jsonify, request
import psycopg2
import psycopg2.extras
app = Flask(__name__)
from inverted_index import InvertedIndex

conn = psycopg2.connect(user="postgres",
                        password="shipsure",
                        host="127.0.0.1",
                        port="5432",
                        database="postgres")

category = ''
inverted_index = None

@app.route('/searchForProduct')
def searchForProduct():
    # print('In App')
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM categories ORDER BY 1")
    categories = cur.fetchall()
    return render_template('searchProduct.html', categories=categories)


@app.route("/getProducts", methods=["POST"])
def getProducts():
    category_id = int(request.form.get('category_id'))
    if category_id == 1:
        category ="Phone"
    elif category_id == 2:
        category ="PhoneAccessories"
    elif category_id == 3:
        category ="Books"
    elif category_id == 4:
        category ="SkinCare"
    # print("SELECT DISTINCT productname FROM productreviews where category = '"+category+"' ORDER BY productname")
    with conn.cursor() as cur:
        cur.execute(
           "SELECT DISTINCT productname FROM productreviews where category = '"+category+"' ORDER BY productname"
        )
        products =[]
        for row in cur.fetchall():
            name = row[0]
            if len(name)> 100:
                name = name[0:97] + '...'
                print(name)
            products.append({'id': row[0], 'name': name})
        cur.close()

    return jsonify(products=products)

@app.route("/searchData", methods=["POST"])
def searchData():
    global inverted_index
    product_name = request.form.get('product_name')
    category_id = int(request.form.get('category_id'))
    if category_id == 1:
        category = "Phone"
    elif category_id == 2:
        category = "PhoneAccessories"
    elif category_id == 3:
        category = "Books"
    elif category_id == 4:
        category = "SkinCare"
    inverted_index = None
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = "SELECT review, predictedsentiment, positivepercent, negativepercent FROM productreviews WHERE productname = %s AND category = %s ORDER BY 1"
    cur.execute(query, (product_name, category))
    rows = cur.fetchall()
    table1_data =[]
    table2_data =[]
    for item in rows:
        if item[1] == 'Positive':
            table1_data.append({'Review': " \""+item[0]+"\""})
        else:
            table2_data.append({'Review':" \""+item[0]+"\""})

    happy_number = round(rows[0][2], 2)
    sad_number = round(rows[0][3], 2)
    print('0')
    reviews = fetch_reviews(product_name, category)
    print("1")
    inverted_index = InvertedIndex(reviews)
    print("2")
    return jsonify(happy_number=happy_number, sad_number=sad_number, table1_data=table1_data, table2_data=table2_data)

def fetch_reviews(product_name, category):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    print('before select')
    query = "SELECT reviews FROM topProductReviews WHERE productname = %s AND category = %s"
    print(query)
    cur.execute(query, (product_name, category))
    reviews = [row[0] for row in cur.fetchall()]
    return reviews

@app.route("/searchReviews", methods=["POST"])
def searchReviews():
    global inverted_index

    product_name = request.form.get('product_name')
    if inverted_index is not None:
        query_tokens = product_name.split()
        # search_result = inverted_index.search(query_tokens)
        search_result = inverted_index.search_multiple(query_tokens)
        table3_data = []
        print("Search ", search_result)
        if search_result is None:
            return jsonify(table3_data = None)
        for item in search_result:
            table3_data.append({'Review': " \"" + inverted_index.myDocs[item] + "\""})
        # print(product_name)
        # print(search_result)
        if table3_data:
            return jsonify(table3_data = table3_data)
        else:
            return jsonify(table3_data = None)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)


