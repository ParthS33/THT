import sys

import nltk
from nltk.tokenize import word_tokenize
import psycopg2
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from nltk.corpus import stopwords
import re
import string
# nltk.download('punkt')
# nltk.download('wordnet')
# nltk.download('stopwords')
category_id = 3
model_data = 10000


def create_connection():
    # conn = psycopg2.connect(
    #     host="localhost",
    #     database="TheHighTable",
    #     user="postgres",
    #     password="RITPostGreSQL"
    # )
    conn = psycopg2.connect(user="postgres",
                            password="shipsure",
                            host="127.0.0.1",
                            port="5432",
                            database="postgres")
    return conn


def get_data_without_sw(conn):
    query =''
    if category_id == 3:
        query = 'select review_clean, sentiment From book_reviews where review_clean is not null order by product_name limit %s'
    else:
        query = 'select * from temp.newphones where review_without_sw is not null order by id limit 10000'
    cur = conn.cursor()
    cur.execute(query, (model_data, ))
    rows = cur.fetchall()
    return cur, rows


def lemmatization_tokenization(reviews, tokens):
    lemmatizer = WordNetLemmatizer()
    count = 0
    for review in reviews:
        count+=1
        tokenized_review = word_tokenize(review)
        lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokenized_review]
        tokens.append(lemmatized_tokens)

# vectorization/ bag of words
def vectorization_bog(documents):
    vectorizer = CountVectorizer()
    bow_matrix = vectorizer.fit_transform(documents)
    # feature_names = vectorizer.get_feature_names()
    feature_names = vectorizer.get_feature_names_out()

    return vectorizer, bow_matrix, feature_names


def logistic_regression_training(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LogisticRegression(max_iter = 1000000)
    model.fit(X_train, y_train)

    # Make predictions on the testing set
    y_pred = model.predict(X_test)
    # Evaluate the model
    accuracy = accuracy_score(y_test, y_pred)
    print("Accuracy: ", accuracy)
    return model


def clean_text(review):
    # print("before", review)
    # print("after", spell_checked_review)
    review_without_numbers = re.sub(r'\d+', ' ', review)

    # Remove punctuations using the string.punctuation string
    review_without_punctuation = ''.join(char if char not in string.punctuation else ' ' for char in review_without_numbers)

    # Remove any remaining special characters or symbols
    review_without_special_char = re.sub(r'[^\w\s]', ' ', review_without_punctuation)

    # Remove extra whitespace
    final_review = re.sub(r'\s+', ' ', review_without_special_char).strip()

    return final_review


def training(reviews, rows):
    tokens = []
    lemmatization_tokenization(reviews, tokens)
    documents = [' '.join(tokens) for tokens in tokens]
    # print("train",documents)
    vectorizer, bow_matrix, feature_names = vectorization_bog(documents)
    sentiment_labels = [row[1] for row in rows]

    model = logistic_regression_training(bow_matrix, sentiment_labels)
    return model, vectorizer, feature_names


def testing(test_review, model, vectorizer):
    tokens = []
    cleaned_review = clean_text(test_review)
    lemmatization_tokenization([cleaned_review], tokens)
    documents = [' '.join(tokens) for tokens in tokens]
    # print("test", documents)
    test_bow_vector = vectorizer.transform(documents)
    predicted_label = model.predict(test_bow_vector)[0]

    return predicted_label


def main():
    conn = create_connection()
    cur, rows = get_data_without_sw(conn)
    reviews = [row[0] for row in rows]
    model, vectorizer, feature_names = training(reviews, rows)

    # testing data below
    currr = conn.cursor()
    query = "select review_clean, sentiment From book_reviews where review_clean is not null order by product_name limit 20000 offset %s"
    currr.execute(query, (model_data, ))
    teset_rows = currr.fetchall()
    count=0
    for item in teset_rows:
        tokens = clean_text(item[0]).lower().split()
    # print("tokens", tokens)
    #     stop_words = set(stopwords.words('english'))
    #     filtered_tokens = [word for word in tokens if word not in stop_words]
    # print("filtered tokens", filtered_tokens)
    # Join the filtered tokens back into a cleaned review
        clean_review = ' '.join(tokens)
        predicted_label = testing(clean_review, model, vectorizer)
        if predicted_label != item[1]:
            count+=1
            # print("Test Review:", clean_review)
            # print("Predicted Label:", predicted_label)
            # print("Actual Label:", item[1])

    print(count)
    cur.close()
    conn.close()


if __name__ == '__main__':
    main()
