import csv
from store.models import Category, Product


def run():
    fhand = open('store/gym.csv')
    reader = csv.reader(fhand)
    next(reader)

    Category.objects.all().delete()
    Product.objects.all().delete()

    for row in reader:
        print(row)

        c, created = Category.objects.get_or_create(title=row[8])

        r = Product(sku=row[1], title=row[2],  short_description=row[3], price=row[4],
                    product_image=row[7],  category=c)
        r.save()
