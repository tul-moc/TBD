import json
from datetime import datetime
from collections import Counter

def get_articles_date(data):
    dates = []
    for article in data:
        if article['formatted_created_date'] is not None:
            dates.append(datetime.strptime(article['formatted_created_date'], '%Y-%m-%dT%H:%M:%S'))
    return dates

def get_articles_count(data):
        print(f'Počet článků: {len(data)}')

def get_duplicated_articles_count(data):
    articles_titles = [article['title'] for article in data]
    articles_titles_counter = Counter(articles_titles)
    duplicated_articles = {title: count for title, count in articles_titles_counter.items() if count > 1}
    print(f'Počet duplicitních článků: {len(duplicated_articles)}')

def get_oldest_article_date(data):
    date = get_articles_date(data)

    oldest_article = min(date)
    print(f'Nejstarší datum: {oldest_article}')

def get_article_with_most_comments(data):
    articles = [article for article in data if article['discussion_count'] is not None]
    article = max(articles, key=lambda article: article['discussion_count'])
    print(f'Článek s nejvíce komentáři: {article["title"]} a počet komentářů: {article["discussion_count"]}')

def get_article_with_most_images(data):
    articles = [article for article in data if article['img_count'] is not None]
    article = max(articles, key=lambda article: article['img_count'])
    print(f'Největší počet obrázků: {article["img_count"]}')

def get_articles_count_by_year(data):
    dates = get_articles_date(data)
    years = [date.year for date in dates]
    year_counts = Counter(years)
    for year, count in year_counts.items():
        print(f"Rok {year}: {count} článků")

def get_articles_categories_count(data):
    categories = []
    for article in data:
        if article['category'] is not None:
            categories.extend(article['category'])
    
    categories_counter = Counter(categories)
    print(f"Počet unikátních kategorií: {len(categories_counter)}")
    for category, count in categories_counter.items():
        print(f"Kategorie {category}: {count} článků")

def get_five_most_used_words_in_2021(data):
    articles_2021 = []
    for article in data:
        if article['formatted_created_date'] is not None and datetime.strptime(article['formatted_created_date'], '%Y-%m-%dT%H:%M:%S').year == 2021:
            articles_2021.append(article)

    words = []
    for article in articles_2021:
        if article['content'] is not None:
            words.extend(article['content'].split())
    
    words_counter = Counter(words)
    most_common_words = words_counter.most_common(5)
    print(f"Top 5 slov v roce 2021: {most_common_words}")

def get_articles_total_comments_count(data):
    sum = 0
    for article in data:
        if article['discussion_count'] is not None:
            sum += article['discussion_count']

    print(f"Celkový počet komentářů: {sum}")

def get_articles_total_words_count(data):
    sum = 0
    for article in data:
        if article['content'] is not None:
            sum += len(article['content'].split())

    print(f"Celkový počet slov: {sum}")


def process():
    with open('articles-small.json', 'r', encoding='utf-8') as file:
        articles = json.load(file)

    get_articles_count(articles)
    get_duplicated_articles_count(articles)
    get_oldest_article_date(articles)
    get_article_with_most_comments(articles)
    get_article_with_most_images(articles)
    get_articles_count_by_year(articles)
    get_articles_categories_count(articles)
    get_five_most_used_words_in_2021(articles)
    get_articles_total_comments_count(articles)
    get_articles_total_words_count(articles)

if __name__ == '__main__':
    process()