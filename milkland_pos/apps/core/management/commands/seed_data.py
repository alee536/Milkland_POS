from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal


class Command(BaseCommand):
    help = 'Seed initial data for MILK LAND POS'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('Seeding MILK LAND POS Data...'))

        # Business Settings
        from apps.core.models import BusinessSettings
        settings, created = BusinessSettings.objects.get_or_create(pk=1)
        settings.shop_name = 'MILK LAND'
        settings.tagline = 'A Satluj Dairies Venture'
        settings.service_highlight = 'Free Home Delivery'
        settings.address = 'Commercial Market, New City, Bahawalnagar'
        settings.contact_number = '+923215307273'
        settings.receipt_footer_message = 'Pure Dairy, Fresh Taste, Delivered to Your Doorstep.'
        settings.currency_symbol = 'PKR'
        settings.save()
        self.stdout.write(self.style.SUCCESS('✓ Business settings configured'))

        # Admin user
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@milkland.pk', 'admin123')
            self.stdout.write(self.style.SUCCESS('✓ Admin user created (admin / admin123)'))
        else:
            self.stdout.write('  Admin user already exists')

        # Staff user
        if not User.objects.filter(username='staff').exists():
            staff = User.objects.create_user('staff', 'staff@milkland.pk', 'staff123')
            staff.first_name = 'Sales'
            staff.last_name = 'Staff'
            staff.save()
            self.stdout.write(self.style.SUCCESS('✓ Staff user created (staff / staff123)'))
        else:
            self.stdout.write('  Staff user already exists')

        # Product Categories
        from apps.products.models import Category, Product
        categories_data = [
            'Fresh Milk',
            'Dairy Products',
            'Yogurt / Dahi',
            'Cream / Malai',
            'Butter / Ghee',
            'Cheese',
            'Beverages',
            'Other',
        ]
        cats = {}
        for cat_name in categories_data:
            cat, _ = Category.objects.get_or_create(name=cat_name, defaults={'is_active': True})
            cats[cat_name] = cat
        self.stdout.write(self.style.SUCCESS(f'✓ {len(cats)} categories created'))

        # Products matching MILK LAND product line
        products_data = [
            # (name, category, unit, purchase_price, sale_price, stock, min_stock)
            ('Fresh Cow Milk', 'Fresh Milk', 'Litre', 150, 180, 100, 10),
            ('Fresh Buffalo Milk', 'Fresh Milk', 'Litre', 170, 200, 80, 10),
            ('Pasteurized Milk', 'Fresh Milk', 'Litre', 160, 190, 50, 5),
            ('Dahi (Plain Yogurt)', 'Yogurt / Dahi', 'KG', 130, 160, 30, 5),
            ('Meethi Dahi', 'Yogurt / Dahi', 'KG', 140, 170, 20, 5),
            ('Fresh Cream (Malai)', 'Cream / Malai', 'KG', 400, 500, 10, 2),
            ('Whipped Cream', 'Cream / Malai', 'KG', 450, 560, 5, 2),
            ('White Butter (Makhan)', 'Butter / Ghee', 'KG', 500, 650, 8, 2),
            ('Desi Ghee', 'Butter / Ghee', 'KG', 1400, 1800, 5, 1),
            ('Paneer (Fresh)', 'Cheese', 'KG', 350, 450, 10, 2),
            ('Lassi (Sweet)', 'Beverages', 'Glass/Bottle', 50, 70, 50, 10),
            ('Lassi (Salted)', 'Beverages', 'Glass/Bottle', 50, 70, 50, 10),
            ('Milk Shake (Banana)', 'Beverages', 'Glass/Bottle', 80, 120, 20, 5),
            ('Milk Shake (Mango)', 'Beverages', 'Glass/Bottle', 80, 120, 20, 5),
            ('Khoya / Mawa', 'Dairy Products', 'KG', 600, 750, 5, 2),
            ('Cottage Cheese', 'Cheese', 'KG', 400, 520, 8, 2),
            ('Flavored Milk (Chocolate)', 'Beverages', '250ml Bottle', 35, 50, 40, 10),
            ('Flavored Milk (Strawberry)', 'Beverages', '250ml Bottle', 35, 50, 40, 10),
        ]

        products_created = 0
        for name, cat_name, unit, pp, sp, stock, min_s in products_data:
            if not Product.objects.filter(name=name).exists():
                Product.objects.create(
                    name=name,
                    category=cats.get(cat_name),
                    unit_type=unit,
                    purchase_price=Decimal(str(pp)),
                    sale_price=Decimal(str(sp)),
                    current_stock=Decimal(str(stock)),
                    minimum_stock_level=Decimal(str(min_s)),
                    is_active=True,
                )
                products_created += 1
        self.stdout.write(self.style.SUCCESS(f'✓ {products_created} products created'))

        # Expense Categories
        from apps.finance.models import ExpenseCategory
        expense_cats = [
            'Utilities (Electricity/Gas)',
            'Staff Salary',
            'Rent',
            'Vehicle / Delivery',
            'Packaging Material',
            'Cleaning & Maintenance',
            'Miscellaneous',
        ]
        for ec_name in expense_cats:
            ExpenseCategory.objects.get_or_create(name=ec_name, defaults={'is_active': True})
        self.stdout.write(self.style.SUCCESS(f'✓ {len(expense_cats)} expense categories created'))

        # Sample Customers
        from apps.parties.models import Customer, Supplier
        customers_data = [
            ('Ahmed Khan', '+92300-1234567', 'New City, Bahawalnagar'),
            ('Fatima Bibi', '+92311-2345678', 'Commercial Market Area'),
            ('Muhammad Ali', '+92321-3456789', 'Near City Park'),
            ('Ayesha Siddiqui', '+92333-4567890', 'Main Road, New City'),
            ('Umar Farooq', '', ''),
        ]
        cust_created = 0
        for name, phone, addr in customers_data:
            if not Customer.objects.filter(name=name).exists():
                Customer.objects.create(name=name, phone=phone, address=addr, is_active=True)
                cust_created += 1
        self.stdout.write(self.style.SUCCESS(f'✓ {cust_created} sample customers created'))

        # Sample Suppliers
        suppliers_data = [
            ('Satluj Dairy Farm', '+92300-9876543', 'Bahawalnagar Dairy Zone'),
            ('Punjab Milk Co.', '+92321-8765432', 'Lahore Road, Bahawalnagar'),
            ('Fresh Farms Ltd.', '+92333-7654321', 'District Bahawalnagar'),
        ]
        supp_created = 0
        for name, phone, addr in suppliers_data:
            if not Supplier.objects.filter(name=name).exists():
                Supplier.objects.create(name=name, phone=phone, address=addr, is_active=True)
                supp_created += 1
        self.stdout.write(self.style.SUCCESS(f'✓ {supp_created} sample suppliers created'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('MILK LAND POS Setup Complete!'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(f'  URL: http://localhost:8000')
        self.stdout.write(f'  Admin Login: admin / admin123')
        self.stdout.write(f'  Staff Login: staff / staff123')
        self.stdout.write(f'  Django Admin: http://localhost:8000/admin/')
        self.stdout.write(self.style.SUCCESS('=' * 50))
