import psycopg2
import numpy as np
from sklearn.preprocessing import LabelEncoder


conn = psycopg2.connect(
    host="localhost",
    database="TheHighTable",
    user="postgres",
    password="RITPostGreSQL"
)
cur = conn.cursor()

cur.execute("select * from temp.newphones")
rows = cur.fetchall()
cur.close()
conn.close()
ratings_text = [row[5] for row in rows]
label_encoder = LabelEncoder()
encoded_ratings = label_encoder.fit_transform(ratings_text)


print(np.unique(encoded_ratings))
