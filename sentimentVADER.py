import psycopg2
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import time

def create_connection():

    conn = psycopg2.connect(
        host="localhost",
        database="TheHighTable",
        user="postgres",
        password="RITPostGreSQL"
    )
    print("Connection created")
    return conn

def get_data_without_sw(conn):

    curs = conn.cursor()
    curs.execute("select productname "
                 "from temp.newphones "
                 "group by productname "
                 "order by count(*) desc "
                 "limit 2;",)
    products = curs.fetchall()
    curs.close()
    print("Fetched product names")
    return products

def get_data_for_each_product(conn, product_name):
    cur = conn.cursor()
    cur.execute("select ratings, reviews, id, productname "
                "from temp.newphones "
                "where reviews is not null and "
                "ratings is not null "
                "and productname = %s ", (product_name, ))
    rows = cur.fetchall()
    print(f"Fetched data for the product {product_name}")
    return cur, rows



def testing(test_review, model):

    analyzer = model
    scores = analyzer.polarity_scores(test_review)

    # Interpret the sentiment scores to get the predicted label
    if scores['compound'] >= 0.05:
        predicted_label = 'Positive'
    elif scores['compound'] <= -0.05:
        predicted_label = 'Negative'
    else:
        predicted_label = 'Neutral'

    return test_review, predicted_label, scores['compound']

def perform_sentiment_analysis(rows):
    model = SentimentIntensityAnalyzer()
    results_dict = {}
    unique_reviews = set()
    for row in rows:
        test_review, predicted_label, compound_score = testing(row[1], model)
        # print("tr",test_review)
        # exit(0)
        if test_review not in unique_reviews:
            results_dict[row[2]] = (predicted_label, test_review, compound_score)
            unique_reviews.add(test_review)
    return results_dict

def insert_into_product_reviews(conn, category, productName, review, sentiment, compoundScore, positivePercent, negativePercent):
    cur = conn.cursor()
    # insert values into the table temp.productreviews
    cur.execute("INSERT INTO temp.ProductReviews "
                "(category, productName, review, predictedSentiment, score, positivePercent, negativePercent) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (category, productName, review, sentiment, compoundScore, positivePercent, negativePercent))
    conn.commit()
    cur.close()

def get_top_reviews(sorted_reviews, product_name, conn):
    positive_reviews = [review for review in sorted_reviews if review[1][0] == 'Positive']
    negative_reviews = [review for review in reversed(sorted_reviews) if review[1][0] == 'Negative']
    no_of_positive = len(positive_reviews)
    no_of_negative = len(negative_reviews)
    total = len(sorted_reviews)
    positive_percent = no_of_positive*100/total
    negative_percent = no_of_negative*100/total
    print("Positive % = ", positive_percent)
    print("Negative % = ", negative_percent)
    print("Top 5 Positive Reviews:")
    for idx, review in enumerate(positive_reviews[:5], 1):
        print(f"{idx}. Compound Score: {review[1][2]}")
        print(f"   Review: {review[1][1]}")
        print()
        # print(review)
        insert_into_product_reviews(conn, 'Phone', product_name, review[1][1], 'Positive', review[1][2], positive_percent, negative_percent)

    # Printing the top 5 negative reviews
    print("Top 5 Negative Reviews:")
    for idx, review in enumerate(negative_reviews[:5], 1):
        print(f"{idx}. Compound Score: {review[1][2]}")
        print(f"   Review: {review[1][1]}")
        print()
        insert_into_product_reviews(conn, 'Phone', product_name, review[1][1], 'Negative', review[1][2], positive_percent, negative_percent)

    print("Inserted values into the table ProductReviews")
    print()



def predict_for_all_products(product_name, conn):
    cur, rows = get_data_for_each_product(conn, product_name)
    cur.close()

    results_dict = perform_sentiment_analysis(rows)
    sorted_reviews = sorted(results_dict.items(), key=lambda item: (item[1][2], item[1][0]), reverse=True)

    get_top_reviews(sorted_reviews, product_name, conn)

def create_product_reviews_table(conn):
    cur = conn.cursor()
    cur.execute("drop table if exists temp.ProductReviews")
    cur.execute("create table temp.ProductReviews( "
                "category text, "
                "productName text, "
                "review text, "
                "predictedSentiment text, "
                "score numeric, "
                "positivePercent numeric, "
                "negativePercent numeric)")
    cur.execute("select * from temp.ProductReviews")
    conn.commit()
    print("Created the table ProductReviews")

def main():
    conn = create_connection()
    products = get_data_without_sw(conn)
    create_product_reviews_table(conn)
    for product_name in products:
        predict_for_all_products(product_name[0], conn)




if __name__ == '__main__':
    main()
