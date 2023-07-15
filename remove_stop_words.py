import psycopg2
import nltk
from nltk.corpus import stopwords
import re
import string
from spellchecker import SpellChecker


conn = psycopg2.connect(
    host="localhost",
    database="TheHighTable",
    user="postgres",
    password="RITPostGreSQL"
)
cur = conn.cursor()

# nltk.download('stopwords')
stop_words = set(stopwords.words('english'))
spell = SpellChecker()


query = "select * from temp.newphones where review_without_sw is null"
cur.execute(query)


def spell_check(review):
    review = re.sub(r'\.', ' . ', review)
    tokens = review.lower().split()
    # print("incorrect",tokens)
    corrected_tokens = [spell.correction(token) if spell.correction(token) is not None else token for token in tokens]
    # print("corrected", corrected_tokens)
    return ' '.join(corrected_tokens)


def clean_text(review):
    # print("before", review)
    spell_checked_review = spell_check(review)
    # print("after", spell_checked_review)
    review_without_numbers = re.sub(r'\d+', ' ', spell_checked_review)

    # Remove punctuations using the string.punctuation string
    review_without_punctuation = ''.join(char if char not in string.punctuation else ' ' for char in review_without_numbers)

    # Remove any remaining special characters or symbols
    review_without_special_char = re.sub(r'[^\w\s]', ' ', review_without_punctuation)

    # Remove extra whitespace
    final_review = re.sub(r'\s+', ' ', review_without_special_char).strip()

    return final_review


update_query = "UPDATE temp.newphones SET review_without_sw = %s WHERE id = %s"


for rows in cur:
    id = rows[7]
    review = rows[3]
    if review:
        tokens = clean_text(review).lower().split()

        # Remove stopwords
        filtered_tokens = [word for word in tokens if word not in stop_words]

        # Join the filtered tokens back into a cleaned review
        clean_review = ' '.join(filtered_tokens)

        update_cur = conn.cursor()
        update_cur.execute(update_query, (clean_review, id,))
        conn.commit()
        update_cur.close()
        print(clean_review)


cur.close()
conn.close()

