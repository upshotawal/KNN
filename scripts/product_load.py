import csv

from store.models import Category, Product


def run():
    fhand = open('store/gym.csv')
    reader = csv.reader(fhand)
    next(reader)

    for row in reader:
        print(row)

        # create for category and products

        c, created = Category.objects.get_or_create(title=row[7])

        r = Product(sku=row[0], title=row[1], short_description=row[2],
                    price=row[3], product_image=row[6], category=c)
        r.save()
