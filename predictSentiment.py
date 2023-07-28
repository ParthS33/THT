import nltk
import re
import string
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
import psycopg2

# Load NLTK resources (if not already loaded)
# nltk.download('punkt')
# nltk.download('wordnet')

def create_connection():
    conn = psycopg2.connect(user="postgres",
                            password="shipsure",
                            host="127.0.0.1",
                            port="5432",
                            database="postgres")
    return conn

def clean_text(review):
    # Remove numbers
    review_without_numbers = re.sub(r'\d+', ' ', review)

    # Remove punctuations using the string.punctuation string
    review_without_punctuation = ''.join(char if char not in string.punctuation else ' ' for char in review_without_numbers)

    # Remove any remaining special characters or symbols
    review_without_special_char = re.sub(r'[^\w\s]', ' ', review_without_punctuation)

    # Remove extra whitespace
    final_review = re.sub(r'\s+', ' ', review_without_special_char).strip()

    return final_review

def lemmatization_tokenization(review):
    lemmatizer = WordNetLemmatizer()
    tokenized_review = word_tokenize(review)
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokenized_review]
    return ' '.join(lemmatized_tokens)

def train_model(conn):
    cur = conn.cursor()
    query = "SELECT review_clean, sentiment FROM book_reviews WHERE review_clean IS NOT NULL order by product_name limit 60000"
    cur.execute(query)
    rows = cur.fetchall()
    train_data = [row[0] for row in rows]
    train_labels = [row[1] for row in rows]
    cur.close()
    conn.close()

    # Initialize the CountVectorizer for text processing
    vectorizer = CountVectorizer()
    train_reviews = [lemmatization_tokenization(clean_text(review)) for review in train_data]

    # Fit the CountVectorizer on the training data
    vectorizer.fit(train_reviews)

    # Transform the training data
    train_bow_matrix = vectorizer.transform(train_reviews)

    # Initialize and train the Logistic Regression model
    model = LogisticRegression(max_iter=1000000)
    model.fit(train_bow_matrix, train_labels)

    return model, vectorizer

def predict_sentiment(review, model, vectorizer):
    cleaned_review = clean_text(review)
    tokenized_review = lemmatization_tokenization(cleaned_review)

    # Transform the test review using the fitted vectorizer
    test_bow_vector = vectorizer.transform([tokenized_review])

    # Use predict_proba() to get the probability distribution
    predicted_probabilities = model.predict_proba(test_bow_vector)[0]

    # Extract the positive and negative probabilities
    positive_probability = predicted_probabilities[1]
    negative_probability = predicted_probabilities[0]

    # Calculate the intensity of sentiment (percentage)
    total_probability = positive_probability + negative_probability
    positive_percentage = (positive_probability / total_probability) * 100
    negative_percentage = (negative_probability / total_probability) * 100

    return positive_percentage, negative_percentage

# Train the model and get the vectorizer
conn = create_connection()
model, vectorizer = train_model(conn)

# Example usage:
# test_review = "this book could hve been written well. the premise of a two forbidden lovers is a tale as long as time. i felt there are a lot of gaps in the story"
test_review = "this book is great, but i didnt like xyz characters"
positive_percentage, negative_percentage = predict_sentiment(test_review, model, vectorizer)

print("Review:", test_review)
print("Positive Percentage: {:.2f}%".format(positive_percentage))
print("Negative Percentage: {:.2f}%".format(negative_percentage))
