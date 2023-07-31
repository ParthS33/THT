import psycopg2
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

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

def get_data_without_sw(conn, limit, offset):
    """
    Get data from the database
    :param conn: the database connection object
    :return: database cursor and a list of fetched rows
    :rtype: tuple
    """
    cur = conn.cursor()
    cur.execute("select review_clean, sentiment From book_reviews where review_clean is not null limit %s offset %s", (limit, offset))
    rows = cur.fetchall()
    return cur, rows




def testing(test_review, model):
    """
    This function will test the input data/reviews using VADER
    :param test_review: review to be tested
    :param model: trained VADER model (SentimentIntensityAnalyzer)
    :param vectorizer: not used in VADER (can be omitted)
    :return label such as positive/negative/neutral
    :rtype: string
    """
    analyzer = model
    scores = analyzer.polarity_scores(test_review)

    # Interpret the sentiment scores to get the predicted label
    if scores['compound'] >= 0:
        predicted_label = 'Positive'
    else:
        predicted_label = 'Negative'

    return predicted_label

def main():
    conn = create_connection()
    cur, rows = get_data_without_sw(conn, 10000, 0)
    sentiment_labels = [row[1] for row in rows]
    # print(sentiment_labels)
    model = SentimentIntensityAnalyzer()
    # testing data below
    count = 0
    test_reviews = [row[0].lower() for row in rows]
    for index, test_review in enumerate(test_reviews):
        # test_review = "great phone with a bad camera and average battery"
        predicted_label = testing(test_review, model)
        # print("Test Review:", test_review)
        # print("Predicted Label:", predicted_label)
        if predicted_label.lower() != sentiment_labels[index]:
            # print("Test Review:", test_review)
            # print("Predicted Label:", predicted_label)
            # print("Actual", sentiment_labels[index])
            count+=1
    print(count)

    cur.close()
    conn.close()

if __name__ == '__main__':
    main()