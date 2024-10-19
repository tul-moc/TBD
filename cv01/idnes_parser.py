from bs4 import BeautifulSoup
import re

def parse_article_urls(soup: BeautifulSoup):
    try:       
        urls = []

        content_with_urls = soup.find('div', class_='list-art')
        if content_with_urls is None:
            return urls

        links = content_with_urls.find_all('a', class_='art-link')
        for link in links:
            if 'href' in link.attrs:
                urls.append(link['href'])

        return urls 
    except Exception as e:
        print(f"Error getting article urls: {e}")
        return []

def parse_title(soup: BeautifulSoup):
    try:
        title = soup.select_one('h1[itemprop="name headline"]')
        if title is None:
            return None

        return title.text
    except Exception as e:
        print(f"Error getting title: {e}")
        return None

def parse_content(soup: BeautifulSoup):
    text = ''
    try:
        opener = soup.find('div', class_='opener')
        if opener is not None:
            text += opener.text + '\n'

        content = soup.find('div', id='art-text')
        if content is None:
            return text
    
        content = content.find_all('p')
        if content is None:
            return text
            
        for p in content:
            text += p.text + '\n'

        return text
    except Exception as e:
        print(f"Error getting content: {e}")
        return text

def parse_categories(soup: BeautifulSoup):
    try:
        category = soup.find('ul', class_='iph-breadcrumb')
        if category is None:
            return []

        category = category.find_all('a')
        if category is None:
            return []

        categories = []
        for category in category:
            categories.append(category.text)
        return categories
    except Exception as e:
        print(f"Error getting categories: {e}")
        return []

def parse_img_count(soup: BeautifulSoup):
    try:
        img_count = 0
        art_full = soup.find_all('div', class_='art-full')
        if art_full is None:
            return img_count

        for div in art_full:
            imgs = div.find_all('img')
            if imgs is not None:
                img_count += len(imgs)

        return img_count
    except Exception as e:
        print(f"Error getting image count: {e}")
        return None

def parse_original_created_date(soup: BeautifulSoup):
    try:
        created_at = soup.find('span', class_='time')
        if created_at is None:
            return None

        cleaned = created_at.text.replace('\n', '').replace('\r', '').replace('\t', '').strip()
        cleaned = ' '.join(cleaned.split())
        return cleaned if cleaned else None
    except Exception as e:
        print(f"Error getting original created date: {e}")
        return None

def parse_discussion_count(soup: BeautifulSoup):
    try:
        discussion_count = soup.find('li', class_='community-discusion')
        if discussion_count is None:
            return None

        discussion_count = discussion_count.find('span')
        if discussion_count is None:
            return None
    
        match = re.search(r'\d+', discussion_count.text)
        return int(match.group()) if match else 0
    except Exception as e:
        print(f"Error getting discussion count: {e}")
        return None
    
