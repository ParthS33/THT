from flask import Flask, render_template, jsonify, request
import psycopg2
import psycopg2.extras

app = Flask(__name__)

conn = psycopg2.connect(user="postgres",
                        password="shipsure",
                        host="127.0.0.1",
                        port="5432",
                        database="postgres")


@app.route('/')
def main():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM categories ORDER BY 1")
    categories = cur.fetchall()
    return render_template('index.html', categories=categories)


@app.route("/getProducts", methods=["POST"])
def getProducts():
    category_id = request.form.get('category_id')
    query = request.form.get('query')
    query = '%' + query.lower() + '%'
    with conn.cursor() as cur:
        cur.execute(
            "SELECT DISTINCT product_name FROM book_reviews WHERE lower(product_name) LIKE '"+ query +"' ORDER BY product_name LIMIT 10"
        )
        products = [{'id': row[0], 'name': row[0]} for row in cur.fetchall()]
        # cur.close()

    return jsonify(products=products)


if __name__ == "__main__":
    app.run(debug=True)
