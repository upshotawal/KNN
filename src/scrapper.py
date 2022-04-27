from email import header
import requests
from bs4 import BeautifulSoup
import pandas as pd

baseurl = "https://www.sastodeal.com/"

product_titles = []
product_img_links = []
product_rating = []
product_description = []
product_price = []
product_review = []
products_dict = []

product_count = 0

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"

}


productlinks = []
for x in range(1, 5):
    r = requests.get(
        f'https://www.sastodeal.com/home-and-living/home-decor.html?p={x}')
    soup = BeautifulSoup(r.content, 'lxml')
    productlist = soup.find_all('li', class_='item product product-item')
    for item in productlist:
        for link in item.find_all('a', {'class': 'product photo product-item-photo'}, href=True):
            productlinks.append(link['href'])


for link in productlinks:

    r = requests.get(link, headers=headers)
    soup = BeautifulSoup(r.content, 'lxml')

    try:
        name = soup.find('span', class_='base').text.strip()
        product_titles.append(name)
    except:
        name = 'no name'
        product_titles.append(name)
    try:
        images = []
        for img in soup.findAll('img'):
            images.append(img.get('src'))
            product_img_links.append(images)
    except:
        images = 'no images'
        product_img_links.append(images)

    try:
        price = soup.find('span', class_='price').text.strip()
        product_price.append(price)
    except:
        price = 'no price'
        product_price.append(price)
    try:
        description = soup.find('div', class_='value').text.strip()
        product_description.append(description)
    except:
        description = 'no description'
        product_description.append(description)
    try:
        rating = soup.find(
            'span', class_='product-overall-rating-summary').text.strip()
        if rating is not None and len(rating) > 0:
            section = rating[0]
        else:
            rating = soup.find(
                'span', class_='product-overall-rating-summary').text.strip()
            product_rating.append(rating)
    except:
        rating = 'no rating'
        product_rating.append(rating)
    try:
        review = soup.find(
            'span', itemprop='reviewCount').text.strip()
        product_review.append(review)
    except:
        review = 'no review'
        product_review.append(review)

    dictionary = {
        "title": product_titles[product_count],
        "images": product_img_links[product_count],
        "description": product_description[product_count],
        "price": product_price[product_count],
        "rating": product_rating[product_count],
        "review": product_review[product_count],

    }

    products_dict.append(dictionary)
    print("saving the data")

    print("product "+str(product_count)+" Scrapped")
    product_count += 1

dataset_ar = pd.DataFrame(list(zip(product_titles, product_img_links, product_description, product_price, product_rating, product_review)),
                          columns=['title', 'images', 'description', 'price', 'rating', 'review'])

dataset_ar.to_csv('Appliences.csv')
