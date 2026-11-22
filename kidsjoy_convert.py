"""Convert Apify WooCommerce Products Scraper JSON to Prom-style YML/XML.
Usage: python kidsjoy_convert.py input.json output.xml
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree, indent

COLORS = {'synij':'Синій','rozhevyj':'Рожевий','chervonyj':'Червоний','chornyj':'Чорний','haki':'Хакі','bilyj':'Білий','korychnevyj':'Коричневий'}

def sub(parent, tag, value):
    el = SubElement(parent, tag)
    el.text = str(value)
    return el

def convert(products, destination):
    root = Element('yml_catalog', {'date': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')})
    shop = SubElement(root, 'shop')
    sub(shop, 'name', 'Timosha Shop KidsJoy')
    sub(shop, 'company', 'Timosha Shop')
    sub(shop, 'url', 'https://www.kidjoy.com.ua/')
    currencies = SubElement(shop, 'currencies')
    SubElement(currencies, 'currency', {'id':'UAH','rate':'1'})
    categories = SubElement(shop, 'categories')
    SubElement(categories, 'category', {'id':'10001'}).text = 'Дитячі комбінезони'
    offers = SubElement(shop, 'offers')
    count = 0
    for product in products:
        if product.get('status') != 'ok' or not product.get('variations'):
            continue
        for v in product['variations']:
            attrs = {a.get('name'):a.get('value') for a in v.get('attributes',[])}
            size = attrs.get('Розмір за зростом','')
            color = COLORS.get(attrs.get('Колір',''),attrs.get('Колір',''))
            available = bool(v.get('inStock'))
            if v.get('lowStockRemaining') == 0:
                available = False
            offer = SubElement(offers,'offer',{'id':f"KJ-{v['variationId']}", 'group_id':f"KJ-{product['productId']}", 'available':str(available).lower()})
            sub(offer,'name', f"{product['name']} — {color}, {size}")
            sub(offer,'name_ua', f"{product['name']} — {color}, {size}")
            sub(offer,'url',product['url'])
            sub(offer,'price',v.get('price') or product.get('price'))
            sub(offer,'currencyId','UAH')
            sub(offer,'categoryId','10001')
            sub(offer,'quantity_in_stock',1 if available else 0)
            sub(offer,'vendorCode',f"KJ-{v['variationId']}")
            imgs = [v.get('image'),product.get('image')] + product.get('images',[])
            for pic in list(dict.fromkeys(p for p in imgs if p))[:10]:
                sub(offer,'picture',pic)
            sub(offer,'description',product.get('description') or product['name'])
            sub(offer,'description_ua',product.get('description') or product['name'])
            SubElement(offer,'param',{'name':'Розмір'}).text = str(size)
            SubElement(offer,'param',{'name':'Колір'}).text = str(color)
            count += 1
    indent(root, space='  ')
    ElementTree(root).write(destination,encoding='utf-8',xml_declaration=True)
    return count

if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('Usage: python kidsjoy_convert.py input.json output.xml')
    data = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    print(f'Created {convert(data,sys.argv[2])} variations')
