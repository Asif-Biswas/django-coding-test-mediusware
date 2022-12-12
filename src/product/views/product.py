from django.views import generic
import math

from product.models import Variant, Product, ProductVariant, ProductVariantPrice


class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context


class BaseProductView(generic.View):
    model = Product
    template_name = 'products/create.html'
    success_url = '/product/list'

class ProductView(BaseProductView, generic.ListView):
    template_name = 'products/list.html'
    paginate_by = 2
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
        for key in self.request.GET:
            if self.request.GET.get(key):
                if key == 'page':
                    continue
                elif key == 'title':
                    filter_string['title__icontains'] = self.request.GET.get(key)
                elif key == 'variant':
                    other_filter_string['variant'] = [int(self.request.GET.get(key))]
                else:
                    other_filter_string[key] = self.request.GET.get(key)

        # filter products with variants and prices
        products = Product.objects.filter(**filter_string).order_by('id')
        if other_filter_string['date']:
            products = products.filter(created_at__date=other_filter_string['date'])
        
        for product in products:
            product_variants = ProductVariant.objects.filter(product=product)
            product_variants = [v for v in product_variants if ProductVariantPrice.objects.filter(product_variant_one=v).exists() and \
                                ProductVariantPrice.objects.filter(product_variant_one=v)[0].stock > 0 \
                                and ProductVariantPrice.objects.filter(product_variant_one=v)[0].price > int(other_filter_string['price_from']) \
                                and ProductVariantPrice.objects.filter(product_variant_one=v)[0].price < int(other_filter_string['price_to']) \
                                and v.variant.id in other_filter_string['variant']]
            
            for variant in product_variants:
                variant.price = ProductVariantPrice.objects.filter(product_variant_one=variant)[0].price if \
                    ProductVariantPrice.objects.filter(product_variant_one=variant).exists() else 0
                variant.stock = ProductVariantPrice.objects.filter(product_variant_one=variant)[0].stock if \
                    ProductVariantPrice.objects.filter(product_variant_one=variant).exists() else 0

            product.variants = product_variants
        return products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = True
        context['request'] = ''

        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['variants'] = list(variants.all())

        # get the search query
        search_query = ''
        for key in self.request.GET:
            if self.request.GET.get(key):
                if key == 'page':
                    continue
                search_query += f'{key}={self.request.GET.get(key)}&'
        context['search_query'] = search_query

        return context

    def get(self, request, *args, **kwargs):
        return super(ProductView, self).get(request, *args, **kwargs)


