import json
from datetime import datetime
from collections import Counter

def process_article_content(article):
    words = []
    for word in article:
        if len(word) >= 6:
            words.append(word)
    return words

def get_eight_most_used_words(articles):
    words = []
    for article in articles:
        if article['content'] is not None:
            words.extend(process_article_content(article['content'].split()))
    
    words_counter = Counter(words)
    most_common_words = words_counter.most_common(8)
    for word, count in most_common_words:
        print(f"Slovo '{word}' se vyskytuje {count}x")

def get_three_articles_with_most_of_covid_mentions(articles):
    for article in articles:
        article['covid_count'] = 0
        if article['content'] is not None:
            article['covid_count'] += article['content'].lower().count('covid-19')
    
    sorted_articles = sorted(articles, key=lambda x: x['covid_count'], reverse=True)
    top_3_articles = sorted_articles[:3]
    for article in top_3_articles:
        print(f"'{article['title']}' - Počet výskytů: {article['covid_count']}")

def get_articles_lowest_and_highest_word_count(articles):
    for article in articles:
        article['word_count'] = 0
        if article['content'] is not None:
            article['word_count'] = len(article['content'].split())
    
    sorted_articles = sorted(articles, key=lambda x: x['word_count'])
    print(f"Článek s nejmenším počtem slov: '{sorted_articles[0]['title']}' - Počet slov: {sorted_articles[0]['word_count']}")
    print(f"Článek s největším počtem slov: '{sorted_articles[-1]['title']}' - Počet slov: {sorted_articles[-1]['word_count']}")

def get_articles_avarage_word_length(articles):
    words = []
    for article in articles:
        if article['content'] is not None:
            words.extend(article['content'].split())
    
    sum_of_word_lengths = sum([len(word) for word in words])
    avarage_word_length = sum_of_word_lengths / len(words)
    print(f"Průměrná délka slova v článcích je {avarage_word_length} znaků")

def get_articles_month_with_lowest_and_highest_articles(articles):
    month_counter = Counter()
    for article in articles:
        if article['formatted_created_date'] is not None:
            article_date = datetime.strptime(article['formatted_created_date'], '%Y-%m-%dT%H:%M:%S')
            month_counter[f"{article_date.year}-{article_date.month}"] += 1

    most_common_month = month_counter.most_common(1)[0]
    least_common_month = month_counter.most_common()[-1]
    
    print(f"Měsíc s nejvíce články: {most_common_month[0]} - Počet článků: {most_common_month[1]}")
    print(f"Měsíc s nejméně články: {least_common_month[0]} - Počet článků: {least_common_month[1]}")

def process():
    with open('articles-small.json', 'r', encoding='utf-8') as file:
        articles = json.load(file)

    get_eight_most_used_words(articles)
    get_three_articles_with_most_of_covid_mentions(articles)
    get_articles_lowest_and_highest_word_count(articles)
    get_articles_avarage_word_length(articles)
    get_articles_month_with_lowest_and_highest_articles(articles)

if __name__ == '__main__':
    process()