from flask import Flask, render_template, request, redirect
import psycopg2

app = Flask(__name__)

conn = psycopg2.connect(user="postgres",
                        password="shipsure",
                        host="127.0.0.1",
                        port="5432",
                        database="postgres")

cursor = conn.cursor()


@app.route('/', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        product = request.form['product']
        # search by author or book
        cursor.execute(
            "select product_name From book_reviews where product_name =  %s",
            ('product'))
        # conn.commit()
        data = cursor.fetchall()
        # all in the search box will return all the tuples
        # if len(data) == 0 and product == 'all':
        #     cursor.execute("SELECT name, author from Book")
        #     conn.commit()
        #     data = cursor.fetchall()
        return render_template('search.html', data=data)
    return render_template('search.html')


if __name__ == '__main__':
    app.debug = True
    # app.run()
