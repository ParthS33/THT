

from flask import Flask, render_template, jsonify, request
import psycopg2
import psycopg2.extras
import sys
app = Flask(__name__)

conn = psycopg2.connect(user="postgres",
                        password="shipsure",
                        host="127.0.0.1",
                        port="5432",
                        database="postgres")

category = ''
@app.route('/')
def main():

    # print(sys.version)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM categories ORDER BY 1")
    categories = cur.fetchall()
    return render_template('index.html', categories=categories)


@app.route("/getProducts", methods=["POST"])
def getProducts():
    category_id = int(request.form.get('category_id'))
    if category_id == 1:
        category ="Phones"
    elif category_id == 2:
        category ="Books"
    elif category_id == 3:
        category ="Books"
    elif category_id == 4:
        category ="Books"
    # print("SELECT DISTINCT productname FROM productreviews where category = '"+category+"' ORDER BY productname")
    with conn.cursor() as cur:
        cur.execute(
           "SELECT DISTINCT productname FROM productreviews where category = '"+category+"' ORDER BY productname"
        )
        products = [{'id': row[0], 'name': row[0]} for row in cur.fetchall()]
        # cur.close()

    return jsonify(products=products)

@app.route("/searchData", methods=["POST"])
def searchData():
    product_name = request.form.get('product_name')
    category_id = int(request.form.get('category_id'))
    if category_id == 1:
        category = "Phones"
    elif category_id == 2:
        category = "Books"
    elif category_id == 3:
        category = "Books"
    elif category_id == 4:
        category = "Books"
    # print(category)
    # product_name.replace(,)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = "SELECT review, predictedsentiment, positivepercent, negativepercent FROM productreviews WHERE productname = %s AND category = %s ORDER BY 1"
    print(query)
    cur.execute(query, (product_name, category))
    rows = cur.fetchall()
    # print(rows)
    table1_data =[]
    table2_data =[]
    for item in rows:
        if item[1] == 'Positive':
            table1_data.append({'Review': " \""+item[0]+"\""})
        else:
            table2_data.append({'Review':" \""+item[0]+"\""})

    happy_number = round(rows[0][2], 2)
    sad_number = 100 - happy_number

    return jsonify(happy_number=happy_number, sad_number=sad_number, table1_data=table1_data, table2_data=table2_data)


if __name__ == "__main__":
    app.run(debug=True)


