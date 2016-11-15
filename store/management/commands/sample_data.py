from django.core.management.base import BaseCommand, CommandError
from store.models import Product
import random
import string

flavour = [
    'Chocolate Chip',
    'Cookie Dough',
    'Rainbow Sherbet',
    'Vanilla',
    'Chocolate Mint',
    'Jamoca',
    'Rocky Road',
    'Very Berry Strawberry',
    'Chocolate',
    'Paline and Cream'
]

icecream_img = [
    'choc-chip.jpg',
    'cookie-dough.jpg', 
    'RainbowSherbet.jpg',
    'vanilla.jpg',
    'choc-mint.png',
    'jamoca.png',
    'RockyRoad2.jpg',
    'very-berry-stawberry.png',
    'chocolate.png',
    'paline-n-cream.png',
]


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'
    
    def add_arguments(self, parser):
        parser.add_argument('product_count', nargs='+', type=int)

    def handle(self, *args, **options):
        self.r = random.randint(0,9)
        def random_icecream():
            self.r = random.randint(0,9)
        def random_name():
            return flavour[self.r]
        def random_price():
            return random.randint(100, 300)
        def random_score():
            return random.randint(0, 10)
        def random_amount():
            return random.randint(0, 100)
        def random_description():
            return "description_%s" % (''.join([ random.choice(string.letters) for i in range(20)] ))
        def random_image():
            return "/product_image/{icecream_img}".format(icecream_img=icecream_img[self.r])

        for product_count in options['product_count']:
            for i in range(product_count):
                random_icecream()
                product = Product(name=random_name(), price=random_price(), amount=random_amount(), score=random_score(), description=random_description(), image=random_image())
                product.save()
