import psycopg2
import tokenization


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



def get_sentiment_percentage(product_name, model, vectorizer):
    conn = create_connection()
    cur = conn.cursor()
    query = "SELECT review_clean, sentiment FROM book_reviews WHERE review_clean IS NOT NULL AND product_name = %s"
    cur.execute(query, (product_name, ))
    rows = cur.fetchall()

    total_reviews = len(rows)
    positive_reviews = 0
    negative_reviews = 0

    for item in rows:
        tokens = tokenization.clean_text(item[0]).lower().split()
        clean_review = ' '.join(tokens)
        predicted_label = tokenization.testing(clean_review, model, vectorizer)
        if predicted_label == 'positive':  # Assuming 'positive' is the label for positive sentiment in your model
            positive_reviews += 1
        elif predicted_label == 'negative':  # Assuming 'negative' is the label for negative sentiment in your model
            negative_reviews += 1

    if total_reviews == 0:
        print("No reviews found for the product.")
    else:
        positive_percentage = (positive_reviews / total_reviews) * 100
        negative_percentage = (negative_reviews / total_reviews) * 100
        print(f"Product: {product_name}")
        print(f"Positive Percentage: {positive_percentage:.2f}%")
        print(f"Negative Percentage: {negative_percentage:.2f}%")

    cur.close()
    conn.close()

# Example usage:
product_name = "Pride and Prejudice by Jane Austen"  # Replace this with the actual product name
conn = create_connection()
cur = conn.cursor()
query = "SELECT review_clean, sentiment FROM book_reviews WHERE review_clean IS NOT NULL limit 100000"
cur.execute(query, (product_name, ))
rows = cur.fetchall()

model, vectorizer, feature_names = tokenization.training([row[0] for row in rows], rows)
get_sentiment_percentage(product_name, model, vectorizer)
