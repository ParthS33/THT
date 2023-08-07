# app.py
import psycopg2
import psycopg2.extras
from flask import Flask, render_template, redirect

app = Flask(__name__)

conn = psycopg2.connect(user="postgres",
                        password="shipsure",
                        host="127.0.0.1",
                        port="5432",
                        database="postgres")


@app.route('/')
def getDashBoardDate():
    table1_data = getDataForCategory('Phone')
    table2_data = getDataForCategory('PhoneAccessories')
    table3_data = getDataForCategory('Books')
    table4_data = getDataForCategory('SkinCare')
    return render_template('index.html', table1_data=table1_data,
                           table2_data=table2_data,
                           table3_data=table3_data, table4_data=table4_data)


def getDataForCategory(category):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = "SELECT distinct productname, positivepercent FROM productreviews WHERE category = %s ORDER BY positivepercent DESC LIMIT 5"
    cur.execute(query, (category,))
    print(query)
    rows = cur.fetchall()
    data = []
    i = 1
    for row in rows:
        data.append({'Id': str(i), 'Name': row[0] ,
                     'Percent': str(round(row[1], 2)) })
        i +=1

    return data

@app.route('/searchForProduct')
def searchForProduct():
    return redirect('http://localhost:5000/searchForProduct')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
