import json
import matplotlib.pyplot as plt
from datetime import datetime
from collections import Counter
import pandas as pd

# Vykreslete křivku zobrazující přidávání článků v čase.
def plot_article_growth_in_time(articles):
    dates = []
    for article in articles:
        if article['formatted_created_date'] is not None:
            dates.append(datetime.strptime(article['formatted_created_date'], '%Y-%m-%dT%H:%M:%S'))

    dates.sort()
    cumulative_articles = list(range(1, len(dates) + 1))
    
    plt.figure(figsize=(10, 6))
    plt.plot(dates, cumulative_articles, marker='o')
    plt.title("Kumulativní počet článků v čase")
    plt.xlabel("Datum publikace")
    plt.ylabel("Kumulativní počet článků")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Vykreslete sloupcový graf zobrazující počet článků v jednotlivých rocích.
def plot_article_count_by_year(articles):
    years = []
    for article in articles:
        if article['formatted_created_date'] is not None:
            years.append(datetime.strptime(article['formatted_created_date'], '%Y-%m-%dT%H:%M:%S').year)

    year_counts = Counter(years)
    plt.figure(figsize=(10, 6))
    plt.bar(year_counts.keys(), year_counts.values(), color='skyblue')
    plt.title("Počet článků v jednotlivých rocích")
    plt.xlabel("Rok")
    plt.ylabel("Počet článků")
    plt.grid(True)
    plt.tight_layout()    
    plt.show()

# Vykreslete scatter graf zobrazující vztah mezi délkou článku a počtem komentářů.
def plot_article_length_vs_comments(articles):
    article_lengths = []
    comment_counts = []

    for article in articles:
        if article['content'] is not None and article['discussion_count'] is not None:
            article_length = len(article['content'].split())
            article_lengths.append(article_length)
            comment_counts.append(article['discussion_count'])

    plt.figure(figsize=(10, 6))
    plt.scatter(article_lengths, comment_counts, color='skyblue')
    plt.title("Vztah mezi délkou článku a počtem komentářů")
    plt.xlabel("Počet slov v článku")
    plt.ylabel("Počet komentářů")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Vykreslete koláčový graf zobrazující podíl článků v jednotlivých kategoriích.
def plot_article_category_distribution(articles):
    categories = []
    for article in articles:
        if article['category'] is not None:
            categories.extend(article['category'])

    category_counts = Counter(categories)
    
    plt.figure(figsize=(8, 8))
    plt.pie(category_counts.values(), labels=category_counts.keys(), autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    plt.title("Podíl článků v jednotlivých kategoriích")
    plt.tight_layout()
    plt.show()

# Vykreslete histogram pro počet slov v článcích.
def plot_article_word_count_histogram(articles):
    words = []
    for article in articles:
        if article['content'] is not None:
            words.append(len(article['content'].split()))

    plt.figure(figsize=(10, 6))
    plt.hist(words, color='skyblue')
    plt.title("Histogram počtu slov v článcích")
    plt.xlabel("Počet slov")
    plt.ylabel("Počet článků")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Vykreslete histogram pro délku slov v článcích.
def plot_article_word_length_histogram(articles):
    word_length_counter = Counter()
    for article in articles:
        if article.get('content'):
            word_lengths = [len(word) for word in article['content'].split()]
            word_length_counter.update(word_lengths)

    lengths, counts = zip(*word_length_counter.items())

    plt.figure(figsize=(10, 6))
    plt.bar(lengths, counts, color='skyblue', edgecolor='black')
    plt.title("Histogram délky slov v článcích")
    plt.xlabel("Počet slova")
    plt.ylabel("Délka slov")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# Vykreslete časovou osu zobrazující výskyt slova "koronavirus" v názvu článku a přidejte druhou křivku pro výraz "vakcína".
def plot_word_occurrence_in_titles(articles):
    data = {
        'dates': [],
        'coronavirus_count': [],
        'vaccine_count': []
    }

    for article in articles:
        if article['formatted_created_date'] is not None and article['title'] is not None:
            data['dates'].append(datetime.strptime(article['formatted_created_date'], '%Y-%m-%dT%H:%M:%S'))
            data['coronavirus_count'].append(article['title'].lower().count('koronavirus'))
            data['vaccine_count'].append(article['title'].lower().count('vakcína'))

    df = pd.DataFrame(data)
    df['month'] = df['dates'].dt.to_period('M')
    monthly_counts = df.groupby('month')[['coronavirus_count', 'vaccine_count']].sum()

    plt.figure(figsize=(10, 6))
    plt.plot(monthly_counts.index.to_timestamp(), monthly_counts['coronavirus_count'], label='Koronavirus', marker='o')
    plt.plot(monthly_counts.index.to_timestamp(), monthly_counts['vaccine_count'], label='Vakcína', marker='o', color='orange')    
    plt.title("Výskyt slov v názvu článku v čase")
    plt.xlabel("Počet výskytů")
    plt.ylabel("Datum publikace")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# Vykreslete histogram pro počet článků v v jednotlivých dnech týdne.
def plot_article_count_by_weekday(articles):
    weekdays = []
    for article in articles:
        if article['formatted_created_date'] is not None:
            weekdays.append(datetime.strptime(article['formatted_created_date'], '%Y-%m-%dT%H:%M:%S').weekday())

    weekday_counts = Counter(weekdays)
    plt.figure(figsize=(10, 6))
    plt.bar(weekday_counts.keys(), weekday_counts.values(), color='skyblue')
    plt.title("Počet článků v jednotlivých dnech týdne")
    plt.xlabel("Den v týdnu")
    plt.ylabel("Počet článků")
    plt.grid(True)
    plt.xticks(ticks=range(7), labels=['Po', 'Út', 'St', 'Čt', 'Pá', 'So', 'Ne'])
    plt.tight_layout()
    plt.show()

def process():
    with open('articles-small.json', 'r', encoding='utf-8') as file:
        articles = json.load(file)

    plot_article_growth_in_time(articles)
    plot_article_count_by_year(articles)
    plot_article_length_vs_comments(articles)
    #plot_article_category_distribution(articles)
    #plot_article_word_count_histogram(articles)
    #plot_article_word_length_histogram(articles)
    #plot_word_occurrence_in_titles(articles)
    #plot_article_count_by_weekday(articles)

if __name__ == '__main__':
    process()