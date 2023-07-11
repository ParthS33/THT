import psycopg2.pool
import nltk
from nltk.corpus import stopwords
import re
import string
from spellchecker import SpellChecker

# Establish a connection pool
conn_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=5,
    host="localhost",
    database="TheHighTable",
    user="postgres",
    password="RITPostGreSQL"
)

# nltk.download('stopwords')
stop_words = set(stopwords.words('english'))
spell = SpellChecker()

update_query = "UPDATE temp.newphones SET review_without_sw = %s WHERE id = %s"


def spell_check(review):
    review = re.sub(r'\.', ' . ', review)
    tokens = review.lower().split()
    corrected_tokens = [spell.correction(token) if spell.correction(token) is not None else token for token in tokens]
    return ' '.join(corrected_tokens)


def clean_text(review):
    spell_checked_review = spell_check(review)
    review_without_numbers = re.sub(r'\d+', ' ', spell_checked_review)
    review_without_punctuation = ''.join(
        char if char not in string.punctuation else ' ' for char in review_without_numbers)
    review_without_special_char = re.sub(r'[^\w\s]', ' ', review_without_punctuation)
    final_review = re.sub(r'\s+', ' ', review_without_special_char).strip()
    return final_review


# Define batch size for batch processing
batch_size = 500
count = 0

while True:
    with conn_pool.getconn() as connection:
        # Create separate cursors for SELECT and UPDATE
        select_cur = connection.cursor()
        update_cur = connection.cursor()

        select_query = "SELECT * FROM temp.newphones WHERE review_without_sw IS NULL LIMIT %s"
        select_cur.execute(select_query, (batch_size,))

        batch_rows = []
        for row in select_cur:
            id = row[7]
            review = row[3]

            if review:
                tokens = clean_text(review).lower().split()

                # Remove stopwords
                filtered_tokens = [word for word in tokens if word not in stop_words]

                # Join the filtered tokens back into a cleaned review
                clean_review = ' '.join(filtered_tokens)

                batch_rows.append((clean_review, id))

        if not batch_rows:
            break

        # Perform batch update
        update_cur.executemany(update_query, batch_rows)
        connection.commit()

        count += len(batch_rows)
        print(count)

        # Close the cursors
        select_cur.close()
        update_cur.close()

# Close the connection pool
conn_pool.closeall()
