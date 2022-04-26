import csv
from store.models import Rating, User, Product, Category


def run():
    fhand = open('store/gym.csv')
    reader = csv.reader(fhand)
    next(reader)

    for row in reader:
        print(row)

        c, created = Category.objects.get_or_create(title=row[8])

        r = Product(sku=row[1], title=row[2],  short_description=row[3], price=row[4],
                    product_image=row[7],  category=c)
        r.save()

# def run():
#     fhand = open('store/users.csv')
#     reader = csv.reader(fhand)
#     next(reader)

#     for row in reader:
#         print(row)

#         u, created = User.objects.get_or_create(title=row[2])
#         p, created = Product.objects.get_or_create(title=row[1])

#         r = Rating(rate=row[3], user_id=u, product_id=p)
#         r.save()
