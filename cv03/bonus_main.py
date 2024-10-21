from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')

db = client['cv03']
collection = db['articles']

# Vypiště jeden náhodný článek 
random_article = collection.aggregate([{"$sample": {"size": 1}}])
for article in random_article:
    print(article['title'])

# Vypiště celkový počet článků
pocet_clanku = collection.count_documents({})
print(f'Počet článků: {pocet_clanku}')

# Vypiště průměrný počet fotek na článek
avg_img_count = collection.aggregate([
    {
        "$group": {
            "_id": None,
            "prumer": {"$avg": "$img_count"}
        }
    }
])
for result in avg_img_count:
    print(f"Průměrný počet fotek na článek: {result['prumer']}")

# Vypiště počet článků s více než 100 komentáři
count_articles_with_more_than_100_comments = collection.count_documents({"discussion_count": {"$gt": 100}})
print(f"Počet článků s více než 100 komentáři: {count_articles_with_more_than_100_comments}")

# Pro každou kategorii vypiště počet článků z roku 2022
articles_by_category = collection.aggregate([
    {
        "$match": {
            "formatted_created_date": {"$regex": "^2022"}
        }
    },
    {
        "$group": {
            "_id": "$category",
            "articles_count": {"$sum": 1}
        }
    }
])
for result in articles_by_category:
    print(f"Kategorie: {result['_id']}, Počet článků: {result['articles_count']}")