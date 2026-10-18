from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.products.models import Product

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds 02_Ecommerce database with admin, customers, and rich catalog items'

    def handle(self, *args, **options):
        self.stdout.write("Seeding 02_Ecommerce database...")

        # 1. Users
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'store.admin@falconxoft.com',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'address': 'FalconXoft HQ Fulfillment Hub, Silicon Bay'
            }
        )
        admin_user.set_password('Admin@123')
        admin_user.save()

        cust1, _ = User.objects.get_or_create(
            username='talha_customer',
            defaults={
                'email': 'talha.customer@example.com',
                'role': 'customer',
                'phone': '+1 (555) 019-2834',
                'address': '452 Engineering Way, Tech City, CA 94016'
            }
        )
        cust1.set_password('Customer@123')
        cust1.save()

        cust2, _ = User.objects.get_or_create(
            username='sara_shopper',
            defaults={
                'email': 'sara.shopper@example.com',
                'role': 'customer',
                'phone': '+1 (555) 018-7712',
                'address': '789 Developer Boulevard, Seattle, WA 98101'
            }
        )
        cust2.set_password('Customer@123')
        cust2.save()

        # 2. Product Catalog
        products_data = [
            {
                'title': 'UltraWide 49-inch Curved Monitor',
                'description': 'Dual-QHD 5120x1440 curved gaming and workstation display with 144Hz refresh rate, USB-C 90W power delivery, and quantum dot color accuracy.',
                'price': 999.00,
                'stock': 5,
                'sku': 'MON-49-CURV',
                'category': 'electronics',
                'image_url': 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=800&q=80',
            },
            {
                'title': 'Ergonomic Mechanical Keyboard (Hot-swap)',
                'description': 'Custom CNC aluminum chassis, pre-lubed tactile switches, south-facing RGB, and QMK/VIA programmable firmware for maximum engineering velocity.',
                'price': 149.50,
                'stock': 12,
                'sku': 'KEY-MECH-PRO',
                'category': 'accessories',
                'image_url': 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=800&q=80',
            },
            {
                'title': 'Active Noise-Cancelling Studio Headphones',
                'description': 'Bespoke 45mm neodymium drivers delivering flat frequency response, hybrid ANC with 4 beamforming microphones, and 35-hour battery life.',
                'price': 279.00,
                'stock': 8,
                'sku': 'AUD-ANC-STU',
                'category': 'audio',
                'image_url': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=80',
            },
            {
                'title': 'Dual-Motor Standing Desk Frame',
                'description': 'Heavy-duty steel motorized sit-stand desk frame with memory presets, anti-collision sensor, and 120kg weight capacity.',
                'price': 420.00,
                'stock': 4,
                'sku': 'DSK-MOT-FRM',
                'category': 'ergonomics',
                'image_url': 'https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?auto=format&fit=crop&w=800&q=80',
            },
            {
                'title': 'Limited Edition Cyberpunk Keycap Set (Last 1 Unit!)',
                'description': 'PBT dye-sublimated Cherry profile keycaps with bespoke cyberpunk legends. High collector demand — strictly 1 unit left in stock for concurrency testing.',
                'price': 65.00,
                'stock': 1,
                'sku': 'CAP-CYBER-LTD',
                'category': 'accessories',
                'image_url': 'https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?auto=format&fit=crop&w=800&q=80',
            },
            {
                'title': 'Sold Out Retro CRT Gaming Display',
                'description': 'Vintage aperture grille CRT display. Displayed for out-of-stock badge demonstration.',
                'price': 199.00,
                'stock': 0,
                'sku': 'CRT-RETRO-00',
                'category': 'electronics',
                'image_url': 'https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=800&q=80',
            },
        ]

        for p in products_data:
            Product.objects.get_or_create(sku=p['sku'], defaults=p)

        self.stdout.write(self.style.SUCCESS("02_Ecommerce database seeded with admin, customers, and catalog!"))
