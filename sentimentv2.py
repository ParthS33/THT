from nltk.sentiment import SentimentIntensityAnalyzer

def combine_scores(compound_score, rating_score):

    weight_compound = 0.2
    weight_rating = 0.8
    # print(compound_score)

    # Normalize the rating score to a scale of 0 to 1.
    normalized_rating = (rating_score - 1) / 4  # Assumes rating_score is between 1 and 5.

    # Combine the scores using the weighted average.
    combined_score = (weight_compound * compound_score) + (weight_rating * normalized_rating)

    # Return the combined score.
    return combined_score

def get_sentiment(text):
    sid = SentimentIntensityAnalyzer()
    scores = sid.polarity_scores(text)
    compound_score = scores['compound']

    return compound_score

# Example usage:
text ="bebe spends so much time telling us how appealing we think she should be (ex. /paraphrase: i must have looked like a raphael painting), that it's hard to get a real sense of the era. and of course most of it was spent in hotels, in the back of a limosine . . . --it girl, good girl, lean back now-- . 'female jealousy?' heck no! there are tons of us who find this submitting behind the behind-the-velvet-rope crud--& having no redeeming features--kind of pathetic. stay in school girls! this is a cautionary tale. other major turnoffs: she has this snobby misogynistic attitude that insidiously manifests itself throughout the book (ex/paraphrase. todd slept with groupies on the road, i.e. oh you know the type, low-rent nobodies! bebe spent her time with high rent types.) ummm, nice! some other unappealing stuff: oh my, elvis costello! jimmy page episodes: for gosh sakes, lancelot & guinevere? fairies? dainty little boots? hyuuuck! i recommend pamela des barres' book instead. des barres is funny and smarter and gives a crazy fun sense of the 60s/70s."
# text = "deloss mcgraw has been one of my favorite artists for years. i love what he did for 'alice'. i saw the display of his preliminary sketches for 'throught the looking-glass' at arundel books in los angeles two years ago. it was a marvelous treat, and portends yet another feast for the eyes and mind."
rating = 2  # Assume the rating score is on a scale of 1 to 5.

compound_score = get_sentiment(text)
combined_score = combine_scores(compound_score, rating)

print(text)
print("Compound Score:", compound_score)
print("Rating Score:", rating)
print("Combined Score:", combined_score)

