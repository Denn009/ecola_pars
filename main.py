import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'}
url_catalog = "https://ecola.spb.ru/price/CAT_SORT_ALL.html"


def new_file_xml():
    root = ET.Element('products')
    tree = ET.ElementTree(root)
    with open('ecola_pars.xml', 'wb') as file:
        tree.write(file)


def get_html(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")
    return soup


def writer(params_dict):
    existing_tree = ET.parse('ecola_pars.xml', parser=ET.XMLParser(encoding="utf-8"))
    root = existing_tree.getroot()

    product = ET.SubElement(root, 'product')

    id = ET.SubElement(product, 'id')
    id.text = params_dict['id']

    title = ET.SubElement(product, 'title')
    title.text = params_dict['title']

    price = ET.SubElement(product, 'price')
    price.text = params_dict['price']

    article = ET.SubElement(product, 'article')
    article.text = params_dict['article']

    img = ET.SubElement(product, 'img')
    img.text = params_dict['img']

    characteristics = ET.SubElement(product, 'characteristics')
    for key, value in params_dict['characteristics'].items():
        char = ET.SubElement(characteristics, 'char')
        char.set('name', key)
        char.text = value

    existing_tree.write('ecola_pars.xml', encoding="utf-8", xml_declaration=True)


new_file_xml()
soup_catalog = get_html(url_catalog)
products_cards = soup_catalog.find('div', class_='col-md-9 col-xs-12 main').find_all("a", class_="list-group-item")

i = 1
for card in products_cards:
    url_card = 'https://ecola.spb.ru' + card.get('href')

    soup_card = get_html(url_card)
    print(f"Product {i} || {url_card}")

    param_dict = dict()

    param_dict['id'] = str(i)
    param_dict['title'] = soup_card.find('h1').text
    param_dict['price'] = soup_card.find('h2', class_='text-primary').find('span').text

    article = soup_card.find("div", class_='alert alert-warning').find('div', class_="small").text
    param_dict['article'] = article.split()[1]

    try:
        img = soup_card.find(id="currentBigPic").get('src')
        param_dict['img'] = 'https://ecola.spb.ru' + img
    except AttributeError as e:
        param_dict['img'] = "0"
        print(f"Произошла ошибка: {e}")

    try:
        char_dict = dict()
        characteristics = soup_card.find('div', id='settings').find('table').find_all('tr')
        for char in characteristics:
            key = char.find_all('td')[0].text
            value = char.find_all('td')[1].text
            char_dict[key.strip()] = value.strip()
        param_dict["characteristics"] = char_dict

    except AttributeError as e:
        param_dict['characteristics'] = {}
        print(f"Произошла ошибка: {e}")

    i += 1

    writer(param_dict)
