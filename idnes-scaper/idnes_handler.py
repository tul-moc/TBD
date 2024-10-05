from bs4 import BeautifulSoup
import locale
import json
import os
import asyncio
import idnes_parser
import idnes_formater

locale.setlocale(locale.LC_TIME, "cs_CZ.UTF-8")
MAX_FILE_SIZE = 1 * 1024 * 1024 * 1024 * 1024 # 1 GB
FILE_NAME = 'articles.json'
BATCH_SIZE = 3600 # 3600 articles per batch to avoid memory issues
articles = []

def save_articles():
    if (len(articles) < BATCH_SIZE):
        return
    
    print(f"Saving {len(articles)} articles")

    try:
        if os.path.exists(FILE_NAME):
            with open(FILE_NAME, 'a', encoding='utf-8') as json_file:
                for article in articles:
                    json.dump(article, json_file, ensure_ascii=False, indent=4)
        else:
            with open(FILE_NAME, 'w', encoding='utf-8') as json_file:
                for article in articles:
                    json.dump(article, json_file, ensure_ascii=False, indent=4)
        
        check_file_size()
    except Exception as e:
        print(f"Error saving article data: {e}")

def check_file_size():
    global articles

    size = os.path.getsize(FILE_NAME)
    print(f"File size: {size / 1024 / 1024} MB")

    if size >= MAX_FILE_SIZE:
        print(f"File size limit reached: {MAX_FILE_SIZE / 1024 / 1024} MB")
        exit()

    articles = []

def parse_article_urls(data):
    soup = BeautifulSoup(data, 'html.parser')
    return idnes_parser.parse_article_urls(soup)

def parse_article(data):
    soup = BeautifulSoup(data, 'html.parser')
    article = {}
    article['title'] = idnes_parser.parse_title(soup)
    article['content'] = idnes_parser.parse_content(soup).encode('utf-8', 'ignore').decode('utf-8')
    article['category'] = idnes_parser.parse_categories(soup)
    article['img_count'] = idnes_parser.parse_img_count(soup)

    original_date = idnes_parser.parse_original_created_date(soup)
    article['original_created_date'] = original_date
    article['formatted_created_date'] = idnes_formater.create_formatted_date(original_date)

    article['discussion_count'] = idnes_parser.parse_discussion_count(soup)
    articles.append(article)
