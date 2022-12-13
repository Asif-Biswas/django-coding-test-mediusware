from django.views import generic
from django.http import JsonResponse
from django.shortcuts import render

import math
import json


from product.models import Variant, Product, ProductVariant, ProductVariantPrice, ProductImage


class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context


def createProduct(request):
    if request.method == 'POST':
        title = request.POST.get('name')
        sku = request.POST.get('sku')
        description = request.POST.get('description')
        media = request.POST.get('media') # base64 encoded list of images
        variants = request.POST.get('variants')
        
        if Product.objects.filter(sku=sku).exists():
            return JsonResponse({'success': False, 'message': 'Product already exists'})

        product = Product.objects.create(title=title, sku=sku, description=description)
        product.save()
        if media and media != '[]' and media != 'null' and media != 'undefined':
            media = json.loads(media)
            for m in media:
                # decode base64 image
                image = ProductImage.objects.create(product=product, file_path=m)
                image.save()
                
        if variants:
            variants = json.loads(variants)
            size_list = ['sm', 'md', 'lg', 'xl', 'xxl', 'm', 'l', 'xl', 'xxl', 'xxxl', 's', 'xs', 'xxs', 'xxxl', 'xxxxl']
            color_list = ['red', 'blue', 'green', 'yellow', 'black', 'white', 'pink', 'purple', 'orange', 'brown', 'grey', 'silver', 'gold',]
            
            for variant in variants:
                variant_title = variant['title']
                # if / in variant title last charecter then remove it
                if variant_title[-1] == '/':
                    variant_title = variant_title[:-1]

                variant_list = variant_title.split('/')
                for v in variant_list:
                    if v in size_list:
                        variant_obj = Variant.objects.get(title__icontains='size')
                    elif v in color_list:
                        variant_obj = Variant.objects.get(title__icontains='color')
                    else:
                        # get or create
                        variant_obj, created = Variant.objects.get_or_create(title=v)
                    product_variant, created = ProductVariant.objects.get_or_create(product=product, variant=variant_obj, variant_title=variant_title)
                    product_variant.save()
                    product_variant_price = ProductVariantPrice.objects.create(product_variant_one=product_variant, price=float(variant['price']), stock=float(variant['stock']), product=product)
                    product_variant_price.save()


        return JsonResponse({'success': True, 'message': 'Product created successfully'})


def editProduct(request, product_id):
    if request.method == 'POST':
        title = request.POST.get('name')
        sku = request.POST.get('sku')
        description = request.POST.get('description')
        media = request.POST.get('media') # base64 encoded list of images
        variants = request.POST.get('variants')
        
        if not Product.objects.filter(sku=sku).exists():
            return JsonResponse({'success': False, 'message': 'Product does not exists'})

        product = Product.objects.get(id=product_id)
        product.title = title
        product.sku = sku
        product.description = description
        product.save()
        ProductImage.objects.filter(product=product).delete()
        if media and media != '[]' and media != 'null' and media != 'undefined':
            # remove all images for product
            media = json.loads(media)
            for m in media:
                # decode base64 image
                image = ProductImage.objects.create(product=product, file_path=m)
                image.save()

        if variants:
            # remove all variants for product
            ProductVariant.objects.filter(product=product).delete()
            variants = json.loads(variants)
            size_list = ['sm', 'md', 'lg', 'xl', 'xxl', 'm', 'l', 'xl', 'xxl', 'xxxl', 's', 'xs', 'xxs', 'xxxl', 'xxxxl']
            color_list = ['red', 'blue', 'green', 'yellow', 'black', 'white', 'pink', 'purple', 'orange', 'brown', 'grey', 'silver', 'gold',]
            
            for variant in variants:
                variant_title = variant['title']
                # if / in variant title last charecter then remove it
                if variant_title[-1] == '/':
                    variant_title = variant_title[:-1]

                variant_list = variant_title.split('/')
                for v in variant_list:
                    if v in size_list:
                        variant_obj = Variant.objects.get(title__icontains='size')
                    elif v in color_list:
                        variant_obj = Variant.objects.get(title__icontains='color')
                    else:
                        # get or create
                        variant_obj, created = Variant.objects.get_or_create(title=v)
                    product_variant, created = ProductVariant.objects.get_or_create(product=product, variant=variant_obj, variant_title=variant_title)
                    product_variant.save()
                    product_variant_price = ProductVariantPrice.objects.create(product_variant_one=product_variant, price=float(variant['price']), stock=float(variant['stock']), product=product)
                    product_variant_price.save()

        return JsonResponse({'success': True, 'message': 'Product updated successfully'})

    variants = Variant.objects.filter(active=True).values('id', 'title')
    product = Product.objects.get(id=product_id)
    product_images = ProductImage.objects.filter(product=product).values('id', 'file_path')
    product_variants = ProductVariant.objects.filter(product=product).values('id', 'variant_title')
    product_variant_prices = ProductVariantPrice.objects.filter(product=product).values('id', 'price', 'stock', 'product_variant_one')
    
    product = {
        'id': product.id,
        'title': product.title,
        'sku': product.sku,
        'description': product.description,
    }
    context = {}
    context['product_obj'] = product
    context['variants'] = list(variants.all())
    context['product'] = True
    context['product_images'] = list(product_images.all())
    context['product_variants'] = list(product_variants.all())
    context['product_variant_prices'] = list(product_variant_prices.all())
    context['edit'] = product_id
    
    return render(request, 'products/create.html', context)


class BaseProductView(generic.View):
    model = Product
    template_name = 'products/create.html'
    success_url = '/product/list'

class ProductView(BaseProductView, generic.ListView):
    template_name = 'products/list.html'
    #paginate_by = 2
    model = Product

    def get_queryset(self):
        filter_string = {}
        all_variants_id_list = [v.id for v in Variant.objects.all()]
        other_filter_string = {
            'variant': all_variants_id_list,
            'price_from': 0,
            'price_to': 999999999,
            'date': '',
        }
        has_query_key = False
        for key in self.request.GET:
            if self.request.GET.get(key):
                if key == 'page':
                    continue
                elif key == 'title':
                    filter_string['title__icontains'] = self.request.GET.get(key)
                elif key == 'variant':
                    other_filter_string['variant'] = [int(self.request.GET.get(key))]
                    has_query_key = True
                else:
                    other_filter_string[key] = self.request.GET.get(key)
                    has_query_key = True

        # filter products with variants and prices
        products = Product.objects.filter(**filter_string).order_by('id')
        if other_filter_string['date']:
            products = products.filter(created_at__date=other_filter_string['date'])
        
        product_remove_id_list = []
        for product in products:
            product_variants = ProductVariant.objects.filter(product=product)
            product_variants = [v for v in product_variants if ProductVariantPrice.objects.filter(product_variant_one=v).exists() \
                                and ProductVariantPrice.objects.filter(product_variant_one=v)[0].stock > 0 \
                                and ProductVariantPrice.objects.filter(product_variant_one=v)[0].price > int(other_filter_string['price_from']) \
                                and ProductVariantPrice.objects.filter(product_variant_one=v)[0].price < int(other_filter_string['price_to']) \
                                and v.variant.id in other_filter_string['variant']]

            # if product_variants has multiple item with same title then remove the 2nd item
            product_variants = [product_variants[i] for i in range(len(product_variants)) if product_variants[i].variant_title not in [product_variants[j].variant_title for j in range(i)]]

            if has_query_key and len(product_variants) == 0:
                product_remove_id_list.append(product.id)
                continue
            
            for variant in product_variants:
                variant.price = ProductVariantPrice.objects.filter(product_variant_one=variant)[0].price if \
                                ProductVariantPrice.objects.filter(product_variant_one=variant).exists() else 0
                variant.stock = ProductVariantPrice.objects.filter(product_variant_one=variant)[0].stock if \
                                ProductVariantPrice.objects.filter(product_variant_one=variant).exists() else 0

            product.variants = product_variants

        products = [p for p in products if p.id not in product_remove_id_list]

        return products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = True
        context['request'] = ''

        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['variants'] = list(variants.all())

        # get the search query
        search_query = ''
        page_number = 1
        for key in self.request.GET:
            if self.request.GET.get(key):
                if key == 'page':
                    page_number = self.request.GET.get(key)
                    continue
                search_query += f'{key}={self.request.GET.get(key)}&'
        context['search_query'] = search_query
        total_product = len(context['object_list'])
        context['page_number'] = int(page_number)
        context['max_page_number'] = math.ceil(total_product / 2)
        context['has_next'] = True if int(page_number) < context['max_page_number'] else False
        context['has_previous'] = True if int(page_number) > 1 else False
        context['next_page_number'] = int(page_number) + 1
        context['previous_page_number'] = int(page_number) - 1
        context['total_product'] = total_product
        context['page_range'] = [i for i in range(1, context['max_page_number'] + 1)]
        context['object_list'] = context['object_list'][(int(page_number) - 1) * 2: int(page_number) * 2]
        context['showing_start_index'] = (int(page_number) - 1) * 2 + 1
        if total_product == 0:
            context['showing_start_index'] = 0
        context['showing_end_index'] = int(page_number) * 2 if int(page_number) * 2 < total_product else total_product

        return context

    def get(self, request, *args, **kwargs):
        return super(ProductView, self).get(request, *args, **kwargs)


