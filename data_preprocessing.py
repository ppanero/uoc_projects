#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import unidecode  # pip install unidecode

from datetime import date, datetime
from dateutil.relativedelta import *  # pip install python-dateutil

""" Constants """

# Absolute path where the CVS files are located
FILE_PATH = "gourmetdb"

# Absolut path where the processed CSV files are written
OUTPUT_PATH = "denorm_gourmetdb"

# Null string
NULL_STRING = "NULL"


""" Error functions """


def line_length_error(filename, line, length, expected_length):
    print("ERROR: Found line with different number of columns for {filename}\n"
          "\tLine: {line}\n"
          "\tGot: {length}\n"
          "\tExpected: {expected_length}\n".format(
        filename=filename,
        line=str(line).strip('\n'),
        length=length,
        expected_length=expected_length
    ))


def repeated_key_error(filename, key, old_value, new_value):
    print("ERROR: Repeated key for dataset {filename} for key '{key}'.\n"
          "\tCurrent value: {old_value}.\n"
          "\tGot new value: {new_value}.\n"
          "\tIt will be overwritten.".format(
        filename=filename,
        key=key,
        old_value=old_value,
        new_value=new_value
    ))


def file_data_legth_mismatch_error(filename, content_length, data_length):
    print("WARNING: Processing data for {filename} got {data_length} out of {content_length}".format(
        filename=filename,
        data_length=data_length,
        content_length=content_length
    ))


def join_error(orig_dataset, extra_dataset):
    print("ERROR: Join check failed for origin dataset {orig} and "
          "extra dataset {extra}".format(
        orig=orig_dataset,
        extra=extra_dataset,
    ))


""" Debug """


def print_dict(dictionary):
    for key, value in dictionary.items():
        print('Key: {key} Value: {value}'.format(key=key, value=value))


""" Util functions """


def strip_string(string):
    aux = string.strip('"').replace('"\n', '').strip().replace(' ', '-')
    aux = unidecode.unidecode(aux.decode('utf-8'))
    return NULL_STRING if not aux else aux


def strip_number(number):
    # There is no case with doubles (i.e. value after the dot
    # so there is no need for more precise treatments
    aux = number.strip('+').strip('.').replace('\n', '')
    return NULL_STRING if not aux else aux


def strip_date(date_string):
    aux = str(date_string).replace('\n', '')
    if len(aux) != 8:
        line_length_error('strip date', date, len(aux), 8)
        return NULL_STRING
    return date(int(aux[0:4]), int(aux[4:6]), int(aux[6:8]))


def strip_datetime(date_string, time_string):
    aux_date = str(date_string).replace('\n', '')
    if len(aux_date) != 8:
        line_length_error('strip date', date, len(aux_date), 8)
        return NULL_STRING
    if not time_string:
        return date(int(aux_date[0:4]), int(aux_date[4:6]), int(aux_date[6:8]))
    aux_time = str(time_string).replace('\n', '')
    # No case with more than hour (e.g. minutes, seconds) has been spotted therefore not implemented.
    if len(aux_time) == 2:  # Hour
        return datetime(int(aux_date[0:4]), int(aux_date[4:6]), int(aux_date[6:8]), int(aux_time))


def process_commas(parts, line, index, replace_index=None, split_char='","',
                   treat_nulls=False):
    if not replace_index:
        replace_index = index
    if treat_nulls:
        line = line.replace(',,', ',"",')
    aux = line.split(split_char)
    parts[replace_index] = aux[index].replace(',', ' ')
    to_delete = len(aux[index].split(',')) - 1
    for i in range(0, to_delete):
        # Delete the remaining duplicated part of the address
        parts.pop(replace_index + 1)
    return parts


def generate_dict(dataset_name, dataset, columns, include_header=False):
    ddataset = {}
    for key, values in dataset.items():
        len_values = len(values) + 1 if not include_header else len(values)
        if len_values != len(columns):
            line_length_error(dataset_name, [key, values], len_values,
                              len(columns))
            continue
        elem = {}
        elem[columns[0]] = key
        if not include_header:
            for i in range(0, len(values)):
                elem[columns[i + 1]] = values[i]
        else:
            for i in range(0, len(values)-1):
                elem[columns[i + 1]] = values[i+1]
        ddataset[key] = elem
    return ddataset


def write_csv(filename, dataset, mode='wb'):
    with open('{path}/{filename}'.format(path=OUTPUT_PATH, filename=filename),
              mode) as output:
        rows = dataset.values()
        writer = csv.DictWriter(output, rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


""" Debug functions"""


def print_dict(dictionary):
    for key, value in dictionary.items():
        print('Key: {key} Value: {value}'.format(key=key, value=value))


# extra_column in case the origin_column is not the key of the extra_dataset
# NOT IMPLEMENTED YET (specified by extra_is_key boolean)
def join_datasets(origin_dataset, extra_dataset, origin_column, extra_column=None,
                  extra_is_key=True):
    for key, data in origin_dataset.items():
        lookup_key = data[origin_column]
        # We assume key existence since it was checked in the previous steps
        try:
            extra_data = extra_dataset[lookup_key]
            data.update(extra_data)
        except KeyError:
            # TODO: Log properly
            # print("WARN: KeyError happened")
            # TODO: boolean check to log WARN if not found when NOT NULLABLE
            test = list(extra_dataset.values())[0].keys()
            dummy = dict((column, NULL_STRING) for column in test)
            data.update(dummy)


"""Test functions """


def test_key_existence(keyset, keyset_name, dataset, dataset_name, key_index):
    for key, attributes in dataset.items():
        key_lookup = attributes[key_index]
        if key_lookup != NULL_STRING and key_lookup not in keyset:
            print("ERROR: Key {key_lookup} for base key {key} ({dataset_name}) not "
                  "found in [{keyset_name}]:{keyset}".format(
                key_lookup=key_lookup,
                key=key,
                dataset_name=dataset_name,
                keyset_name=keyset_name,
                keyset=keyset
            ))


def join_check(join_dataset, orig_dataset, orig_dataset_columns,
               extra_dataset_columns):
    join_attr_len = len(orig_dataset_columns) + len(extra_dataset_columns)
    for value in join_dataset.values():
        if len(value) != join_attr_len:
            return False
    if len(join_dataset) == len(orig_dataset):
        return True
    return False


######################################
### PRODUCT ENTITY DENORMALIZATION ###
######################################

COLUMNS_SECTION = ['nombre_seccion', 'descripcion_seccion']
COLUMNS_FAMILY = ['nombre_familia', 'descripcion_familia', 'seccion_familia']
COLUMNS_SUBFAMILY = ['nombre_subfamilia', 'descripcion_subfamilia',
                     'familia_subfamilia']
COLUMNS_PRODUCT = ['codigo_producto', 'descripcion_producto',
                   'pais_producto', 'coste_producto', 'precio_venta_producto',
                   'tipo_unidad_producto', 'subfamilia_producto',
                   'marca_producto', 'codigo_proveedor_producto']
COLUMNS_PROVIDER = ['codigo_proveedor', 'nombre_proveedor',
                    'persona_contacto_proveedor', 'direccion_proveedor',
                    'telefono_proveedor', 'periodo_pago_proveedor',
                    'pago_pendiente_proveedor', 'tipo_proveedor_proveedor',
                    'alcance_proveedor']
# Region and country are needed to test the providers FK
COLUMNS_REGION = ['nombre_region', 'continente_region']
COLUMNS_COUNTRY = ['nombre_pais', 'extension_pais', 'poblacion_pais', 'region_pais']


def read_sections(filename):
    with open('{path}/{filename}'.format(path=FILE_PATH, filename=filename)) as content:
        data = {}
        lines = 0
        for line in content:
            lines += 1
            parts = line.split(',')
            if len(parts) != len(COLUMNS_SECTION):
                line_length_error(filename, line, len(parts), len(COLUMNS_SECTION))
                continue
            key = strip_string(parts[0])
            description = strip_string(parts[1])  # NULLABLE
            value = [description]
            if key in data.keys():
                repeated_key_error(filename, key, data[key], value)
            data[key] = value

        if lines != len(data):
            file_data_legth_mismatch_error(filename, lines, len(data))

        return data


def read_families(filename):
    with open('{path}/{filename}'.format(path=FILE_PATH, filename=filename)) as content:
        data = {}
        lines = 0
        for line in content:
            lines += 1
            parts = line.split(',')
            if len(parts) != len(COLUMNS_FAMILY):
                line_length_error(filename, line, len(parts), len(COLUMNS_FAMILY))
                continue
            key = strip_string(parts[0])
            description = strip_string(parts[1])  # NULLABLE
            section = strip_string(parts[2])
            value = [description, section]
            if key in data.keys():
                repeated_key_error(filename, key, data[key], value)
            data[key] = value

        if lines != len(data):
            file_data_legth_mismatch_error(filename, lines, len(data))

        return data


def read_subfamilies(filename):
    with open('{path}/{filename}'.format(path=FILE_PATH, filename=filename)) as content:
        data = {}
        lines = 0
        for line in content:
            lines += 1
            parts = line.split(',')
            if len(parts) != len(COLUMNS_SUBFAMILY):
                line_length_error(filename, line, len(parts), len(COLUMNS_SUBFAMILY))
                continue
            key = strip_string(parts[0])
            description = strip_string(parts[1])  # NULLABLE
            family = strip_string(parts[2])
            value = [description, family]
            if key in data.keys():
                repeated_key_error(filename, key, data[key], value)
            data[key] = value

        if lines != len(data):
            file_data_legth_mismatch_error(filename, lines, len(data))

        return data


def read_regions(filename):
    with open('{path}/{filename}'.format(path=FILE_PATH, filename=filename)) as content:
        data = {}
        lines = 0
        for line in content:
            lines += 1
            parts = line.split(',')
            if len(parts) != len(COLUMNS_REGION):
                line_length_error(filename, line, len(parts), len(COLUMNS_REGION))
                continue
            key = strip_string(parts[0])
            value = [strip_string(parts[1])]
            if key in data.keys():
                repeated_key_error(filename, key, data[key], value)
            data[key] = value

        if lines != len(data):
            file_data_legth_mismatch_error(filename, lines, len(data))

        return data


def read_countries(filename):
    with open('{path}/{filename}'.format(path=FILE_PATH, filename=filename)) as content:
        data = {}
        lines = 0
        for line in content:
            lines += 1
            parts = line.split(',')
            if len(parts) != len(COLUMNS_COUNTRY):
                line_length_error(filename, line, len(parts), len(COLUMNS_COUNTRY))
                continue
            key = strip_string(parts[0])
            extension = int(strip_number(parts[1]))
            poblacion = int(strip_number(parts[2]))
            region = strip_string(parts[3])
            value = [extension, poblacion, region]
            if key in data.keys():
                repeated_key_error(filename, key, data[key], value)
            data[key] = value

        if lines != len(data):
            file_data_legth_mismatch_error(filename, lines, len(data))

        return data


def read_provider(filename):
    with open('{path}/{filename}'.format(path=FILE_PATH, filename=filename)) as content:
        data = {}
        lines = 0
        for line in content:
            lines += 1
            parts = line.split(',')
            parts = process_commas(parts, line, 1)
            parts = process_commas(parts, line, 3)
            if len(parts) != len(COLUMNS_PROVIDER):
                line_length_error(filename, parts, len(parts), len(COLUMNS_PROVIDER))
                continue
            key = int(strip_string(parts[0]))
            name = strip_string(parts[1])
            contact_person = strip_string(parts[2])
            address = strip_string(parts[3])
            phone = int(strip_string(parts[4]))
            payment_period = strip_number(parts[5])  # NULLABLE --> Change to int later on
            payment_pending = strip_number(parts[6])  # NULLABLE --> Change to int later on
            provider_type = strip_string(parts[7])  # NULLABLE
            scope = strip_string(parts[8])
            value = [name, contact_person, address, phone, payment_period, payment_pending, provider_type, scope]
            if key in data.keys():
                repeated_key_error(filename, key, data[key], value)
            data[key] = value

        if lines != len(data):
            file_data_legth_mismatch_error(filename, lines, len(data))

        return data


COUNTRY_MAPPING = {
    'France': 'Francia',
    'SW4': 'Reino-Unido',
    'SW3': 'Reino-Unido',
    'USA': 'Estados-Unidos',
    'Germany': 'Alemania',
    'Belgium': 'Belgica',
    'Holland': 'Holanda',
    'Denmark': 'Dinamarca',
    'Sweden': 'Suecia',
    'Switzerland': 'Suiza',
    'Ireland': 'Irlanda'
}


def add_provider_attributes(dataset):
    COLUMNS_PROVIDER.append("pais_proveedor")
    for attributes in dataset.values():
        parts = attributes[2].split('-')
        # Always the last part of the address
        country = strip_string(parts[len(parts) - 1])
        country = COUNTRY_MAPPING.get(country, country)
        attributes.append(country)


def read_product(filename):
    with open('{path}/{filename}'.format(path=FILE_PATH, filename=filename)) as content:
        data = {}
        lines = 0
        for line in content:
            lines += 1
            parts = line.split(',')
            if len(parts) != len(COLUMNS_PRODUCT):
                line_length_error(filename, line, len(parts), len(COLUMNS_PRODUCT))
                continue

            key = strip_string(parts[0])
            description = strip_string(parts[1])
            country = strip_string(parts[2])
            cost = float(strip_number(parts[3]))
            price = float(strip_number(parts[4]))
            unit_type = strip_string(parts[5])
            subfamily = strip_string(parts[6])
            brand = strip_string(parts[7])
            provider_code = int(strip_string(parts[8]))
            value = [description, country, cost, price, unit_type, subfamily, brand, provider_code]
            if key in data.keys():
                repeated_key_error(filename, key, data[key], value)
            data[key] = value

        if lines != len(data):
            file_data_legth_mismatch_error(filename, lines, len(data))

        return data


def add_country_attributes(dataset):
    COLUMNS_COUNTRY.append("densidad_pobl_pais")  # In people/km2
    for attributes in dataset.values():
        density = round(float(attributes[1]) / attributes[0], 1)
        attributes.append(density)


def add_product_attributes(dataset):
    COLUMNS_PRODUCT.append("beneficio_producto")
    for attributes in dataset.values():
        # Round to 3 decimals as the cost and price
        benefit = round(attributes[3] - attributes[2], 3)
        attributes.append(benefit)


# Sections
sections = read_sections('seccion.cvs')
# Family
families = read_families('familia.cvs')
test_key_existence(sections.keys(), 'seccion', families, 'familia.cvs', 1)
# Subfamily
subfamilies = read_subfamilies('subfamilia.cvs')
test_key_existence(families.keys(), 'familia', subfamilies, 'subfamilia.cvs', 1)

# Generate dictionaries for the datasets
d_sections = generate_dict('seccion', sections, COLUMNS_SECTION)
d_families = generate_dict('familia', families, COLUMNS_FAMILY)
d_subfamilies = generate_dict('subfamilia', subfamilies, COLUMNS_SUBFAMILY)

# Denormalize section into family
join_datasets(d_families, d_sections, 'seccion_familia')
if not join_check(d_families, families, COLUMNS_FAMILY, COLUMNS_SECTION):
    join_error('Familia', 'Seccion')

# Denormalize family into subfamily
join_datasets(d_subfamilies, d_families, 'familia_subfamilia')
if not join_check(d_subfamilies, subfamilies, COLUMNS_SUBFAMILY,
                  COLUMNS_FAMILY + COLUMNS_SECTION):
    join_error('Subfamilia', 'Familia')

# Region
regions = read_regions('regiongeografica.cvs')

# Country
countries = read_countries('pais.cvs')
add_country_attributes(countries)
test_key_existence(regions.keys(), 'region', countries, 'pais.cvs', 2)

# Generate dictionaries for the datasets
d_regions = generate_dict('region', regions, COLUMNS_REGION)
d_countries = generate_dict('pais', countries, COLUMNS_COUNTRY)

# Denormalize subfamily into product
join_datasets(d_countries, d_regions, 'region_pais')
if not join_check(d_countries, countries, COLUMNS_COUNTRY, COLUMNS_REGION):
    join_error('Pais', 'Region')

# Provider
providers = read_provider('proveedor.cvs')
add_provider_attributes(providers)
test_key_existence(countries.keys(), 'pais', providers, 'proveedor.cvs', 8)

# Product
products = read_product('producto.cvs')
add_product_attributes(products)
# test_key_existence(countries.keys(), 'pais', products, 'producto.cvs', 1)
test_key_existence(subfamilies.keys(), 'subfamilia', products, 'producto.cvs', 5)
test_key_existence(providers.keys(), 'proveedor', products, 'producto.cvs', 7)

# Generate dictionaries for the datasets
d_products = generate_dict('producto', products, COLUMNS_PRODUCT)

# Denormalize subfamily into product
join_datasets(d_products, d_subfamilies, 'subfamilia_producto')
if not join_check(d_products, products, COLUMNS_PRODUCT,
                  COLUMNS_SUBFAMILY + COLUMNS_FAMILY + COLUMNS_SECTION):
    join_error('Producto', 'Subfamilia')

# Generate dictionaries for the datasets
d_providers = generate_dict('proveedor', providers, COLUMNS_PROVIDER)

# Denormalize provider into product
join_datasets(d_products, d_providers, 'codigo_proveedor_producto')
if not join_check(d_products, products, COLUMNS_PRODUCT,
                  COLUMNS_PROVIDER + COLUMNS_SUBFAMILY + COLUMNS_FAMILY
                  + COLUMNS_SECTION):
    join_error('Product', 'Proveedor')

write_csv('denorm_products.csv', d_products)

# ####################################
# ### ORDER ENTITY DENORMALIZATION ###
# ####################################

COLUMNS_SHOP = ['nombre_tienda', 'direccion_tienda', 'superficie_tienda',
                  'formato_tienda', 'pais_tienda', 'tipo_zona_tienda']
COLUMNS_ORDER = ['codigo_pedido', 'tienda_pedido', 'codigo_producto_pedido', 
                 'precio_compra_pedido', 'cantidad_solicitada_pedido', 
                 'fecha_solicitud_pedido', 'cantidad_entregada_pedido', 
                 'fecha_entrega_pedido']


def read_shops(filename):
    with open('{path}/{filename}'.format(path=FILE_PATH, filename=filename)) as content:
        data = {}
        lines = 0
        for line in content:
            lines += 1
            parts = line.split(',')
            parts[1] = '{0}{1}'.format(parts[1], parts[2])  # Concatenate address
            parts.pop(2)  # Delete the remainig duplicated part of the address
            if len(parts) != len(COLUMNS_SHOP):
                line_length_error(filename, line, len(parts), len(COLUMNS_SHOP))
                continue
            key = strip_string(parts[0])
            address = strip_string(parts[1])
            surface = float(strip_number(parts[2]))
            shop_format = strip_string(parts[3])
            country = strip_string(parts[4])
            zone_type = strip_string(parts[5])

            value = [address, surface, shop_format, country, zone_type]
            if key in data.keys():
                repeated_key_error(filename, key, data[key], value)
            data[key] = value

        if lines != len(data):
            file_data_legth_mismatch_error(filename, lines, len(data))

        return data


def read_orders(filename):
    with open('{path}/{filename}'.format(path=FILE_PATH, filename=filename)) as content:
        data = {}
        lines = 0
        for line in content:
            lines += 1
            parts = line.split(',')
            if len(parts) != len(COLUMNS_ORDER):
                line_length_error(filename, line, len(parts), len(COLUMNS_ORDER))
                continue

            key = strip_string(parts[0])
            shop_name = strip_string(parts[1])
            product_code = strip_string(parts[2])
            order_price = strip_number(parts[3])
            order_amount = int(strip_number(parts[4]))
            order_date = strip_date(parts[5])
            delivered_amount = int(strip_number(parts[6]))
            delivered_date = strip_date(parts[7])
            value = [shop_name, product_code, order_price, order_amount, order_date, delivered_amount, delivered_date]
            if key in data.keys():
                repeated_key_error(filename, key, data[key], value)
            data[key] = value

        if lines != len(data):
            file_data_legth_mismatch_error(filename, lines, len(data))

        return data


""" Add attributes functions """


def add_order_attributes(dataset):
    COLUMNS_ORDER.append("excfal_pedido")  # exceso o falta de mercancia entregada
    for attributes in dataset.values():
        excfal = attributes[5] - attributes[3]
        attributes.append(excfal)
    COLUMNS_ORDER.append("tiempo_entrega_pedido")  # Tiempo transcurrido desde el pedido hasta la entrega
    for attributes in dataset.values():
        # Fix years 1900 
        if attributes[6].year == 1900:
            attributes[6] = attributes[6].replace(attributes[4].year)
        # Calculate difference of dates in days
        delay = (attributes[6] - attributes[4]).days
        attributes.append(delay)


# Shops
shops = read_shops('tienda.cvs')
test_key_existence(countries.keys(), 'pais', shops, 'tienda.cvs', 3)

# Generate dictionaries for the datasets
d_shops = generate_dict('tienda', shops, COLUMNS_SHOP)

# Denormalize countries into shops
join_datasets(d_shops, d_countries, 'pais_tienda')
if not join_check(d_shops, shops, COLUMNS_SHOP,
                  COLUMNS_COUNTRY + COLUMNS_REGION):
    join_error('Tienda', 'Pais')

# Order
orders = read_orders('pedido.cvs')
add_order_attributes(orders)
test_key_existence(shops.keys(), 'tienda', orders, 'pedido.cvs', 0)
test_key_existence(products.keys(), 'producto', orders, 'pedido.cvs', 1)

# Generate dictionaries for the datasets
d_orders = generate_dict('pedido', orders, COLUMNS_ORDER)

# Denormalize shops into orders
join_datasets(d_orders, d_shops, 'tienda_pedido')
if not join_check(d_orders, orders, COLUMNS_ORDER,
                  COLUMNS_SHOP + COLUMNS_COUNTRY + COLUMNS_REGION):
    join_error('Pedido', 'Tienda')

# Denormalize products into orders
join_datasets(d_orders, d_products, 'codigo_producto_pedido')
if not join_check(d_orders, orders, COLUMNS_ORDER,
                  COLUMNS_SHOP + COLUMNS_COUNTRY + COLUMNS_REGION +
                  COLUMNS_PRODUCT + COLUMNS_PROVIDER + COLUMNS_SUBFAMILY +
                  COLUMNS_FAMILY + COLUMNS_SECTION):
    join_error('Pedido', 'Tienda')

write_csv('denorm_orders.csv', d_orders)


# ####################################
# ### CLIENT ENTITY DENORMALIZATION ###
# ####################################

COLUMNS_CLIENT = ['codigo_cliente', 'nombre_cliente', 'sexo_cliente',
                  'fecha_nacimiento_cliente', 'estado_civil_cliente',
                  'direccion_cliente', 'profesion_cliente', 'numero_hijos_cliente',
                  'region_cliente', 'nacionalidad_cliente', 'total_compras_cliente',
                  'puntos_acumulados_cliente']


def read_client(filename):
    with open('{path}/{filename}'.format(path=FILE_PATH, filename=filename)) as content:
        data = {}
        lines = 0
        for line in content:
            lines += 1
            parts = line.split(',')
            parts = process_commas(parts, line, 4, 5, '",', True)
            parts = process_commas(parts, line, 5, 6, '",', True)
            if len(parts) != len(COLUMNS_CLIENT):
                line_length_error(filename, line, len(parts), len(COLUMNS_CLIENT))
                continue

            key = strip_string(parts[0])
            name = strip_string(parts[1])  # NULLABLE
            gender = strip_string(parts[2])  # NULLABLE
            birthdate = strip_date(parts[3])  # NULLABLE
            civil_state = strip_string(parts[4])  # NULLABLE
            address = strip_string(parts[5])  # NULLABLE
            profession = strip_string(parts[6])  # NULLABLE
            num_children = strip_number(parts[7])  # NULLABLE --> Change to int later on
            region = strip_string(parts[8])  # NULLABLE
            nationality = strip_string(parts[9])  # NULLABLE
            total_buys = strip_number(parts[10])  # NULLABLE --> Change to int later on
            total_points_acc = strip_number(parts[11])  # NULLABLE --> Change to int later on
            value = [name, gender, birthdate, civil_state, address, profession, num_children, region,
                     nationality, total_buys, total_points_acc]
            if key in data.keys():
                repeated_key_error(filename, key, data[key], value)
            data[key] = value

        if lines != len(data):
            file_data_legth_mismatch_error(filename, lines, len(data))

        return data


def add_client_attributes(dataset):
    COLUMNS_CLIENT.append("edad_cliente")  # Age in years
    for attributes in dataset.values():
        # Calculate difference of dates in days
        age = relativedelta(datetime.today().date(), attributes[2]).years
        attributes.append(age)
        

# Client
clients = read_client('cliente.cvs')
add_client_attributes(clients)
test_key_existence(regions.keys(), 'region', clients, 'cliente.cvs', 7)
test_key_existence(countries.keys(), 'pais', clients, 'cliente.cvs', 8)

# Generate dictionaries for the datasets
d_clients = generate_dict('cliente', clients, COLUMNS_CLIENT)

# Guardar el dataset
write_csv('denorm_clients.csv', d_clients)

# ##########################################
# ### TICKET LINE ENTITY DENORMALIZATION ###
# ##########################################

COLUMNS_PROMOTION = ['nombre_promocion', 'tipo_promocion', 'coste_promocion',
                     'fecha_inicio_promocion', 'fecha_fin_promocion',
                     'codigo_producto_promocion', 'familia_promocion',
                     'seccion_promocion', 'tienda_promocion', 'region_promocion',
                     'pais_promocion']

COLUMNS_TICKET_LINE = ['codigo_tl', 'codigo_venta_tl', 'tienda_tl', 'codigo_producto_tl',
                       'cantidad_tl', 'precio_venta_tl', 'promocion_tl', 'codigo_cabecer_tl']


def read_promotions(filename):
    with open('{path}/{filename}'.format(path=FILE_PATH, filename=filename)) as content:
        data = {}
        lines = 0
        for line in content:
            lines += 1
            parts = line.split(',')
            if len(parts) != len(COLUMNS_PROMOTION):
                line_length_error(filename, line, len(parts), len(COLUMNS_PROMOTION))
                continue
            key = strip_string(parts[0])
            promotion_type = strip_string(parts[1])
            cost = strip_number(parts[2])  # NULLABLE --> Change to int later on
            start_date = strip_date(parts[3])
            end_date = strip_date(parts[4])
            product_code = strip_string(parts[5])
            family = strip_string(parts[6])  # NULLABLE
            section = strip_string(parts[7])  # NULLABLE
            shop = strip_string(parts[8])  # NULLABLE
            region = strip_string(parts[9])  # NULLABLE
            country = strip_string(parts[10])  # NULLABLE
            value = [promotion_type, cost, start_date, end_date, product_code, family, section, shop, region, country]
            if key in data.keys():
                repeated_key_error(filename, key, data[key], value)
            data[key] = value

        if lines != len(data):
            file_data_legth_mismatch_error(filename, lines, len(data))

        return data


"""
Order code and header code are wrongly named from the data given. The last field 'codigo cabecera' is not used.
It can be crosschecked with the foreign keys of the db2 file. The header code is the second field 'codigo venta'.
"""


def read_ticket_lines(filename):
    with open('{path}/{filename}'.format(path=FILE_PATH, filename=filename)) as content:
        data = {}
        lines = 0
        for line in content:
            lines += 1
            parts = line.split(',')
            if len(parts) != len(COLUMNS_TICKET_LINE):
                line_length_error(filename, line, len(parts), len(COLUMNS_TICKET_LINE))
                continue

            line = strip_string(parts[0])
            header_code = strip_string(parts[1])
            key = '{line}-{header}'.format(line=line, header=header_code)
            shop_name = strip_string(parts[2])
            product_code = strip_string(parts[3])
            amount = strip_number(parts[4])
            price = strip_number(parts[5])
            promotion_name = strip_string(parts[6])  # NULLABLE
            header_code_spare = strip_number(parts[7])
            value = [line, header_code, shop_name, product_code, amount, price, promotion_name, header_code_spare]
            if key in data.keys():
                repeated_key_error(filename, key, data[key], value)
            data[key] = value
            if lines % 10000 == 0:
                print(lines)

        if lines != len(data):
            file_data_legth_mismatch_error(filename, lines, len(data))

        return data


# Promotion
promotions = read_promotions('promocion.cvs')
test_key_existence(families.keys(), 'familia', promotions, 'promocion.cvs', 5)
test_key_existence(sections.keys(), 'seccion', promotions, 'promocion.cvs', 6)
test_key_existence(shops.keys(), 'tienda', promotions, 'promocion.cvs', 7)
test_key_existence(regions.keys(), 'region', promotions, 'promocion.cvs', 8)
test_key_existence(countries.keys(), 'pais', promotions, 'promocion.cvs', 9)
# Ticket line
# Too much memory consumption. File divided in several by split in bash
# E.g. split -l 20000 lineasticket.cvs
files = ['xaa', 'xab', 'xac', 'xad', 'xae', 'xaf', 'xag', 'xah', 'xai']
ticket_lines_global = {}
for file in files:
    ticket_lines = read_ticket_lines('lineasticket/{file}'.format(file=file))
    test_key_existence(shops.keys(), 'tienda', ticket_lines, 'lineasticket.cvs', 2)
    test_key_existence(products.keys(), 'producto', ticket_lines, 'lineasticket.cvs', 3)
    test_key_existence(promotions.keys(), 'promocion', ticket_lines, 'lineasticket.cvs', 6)
    ticket_lines_global.update(ticket_lines)

# Generate dictionaries for the datasets
d_promotions = generate_dict('promocion', promotions, COLUMNS_PROMOTION)
d_ticket_lines = generate_dict('linea ticket', ticket_lines_global, COLUMNS_TICKET_LINE,
                               include_header=True)

# Denormalize promotions into ticket lines
join_datasets(d_ticket_lines, d_promotions, 'promocion_tl')
if not join_check(d_ticket_lines, ticket_lines_global, COLUMNS_TICKET_LINE,
                  COLUMNS_PROMOTION):
    join_error('Linea Ticket', 'Promocion')

# Denormalize products into ticket lines
join_datasets(d_ticket_lines, d_products, 'codigo_producto_tl')
if not join_check(d_ticket_lines, ticket_lines_global, COLUMNS_TICKET_LINE,
                  COLUMNS_PROMOTION + COLUMNS_PRODUCT + COLUMNS_PROVIDER +
                  COLUMNS_SUBFAMILY + COLUMNS_FAMILY + COLUMNS_SECTION):

    join_error('Linea Ticket', 'Promocion')
# Guardar el dataset
write_csv('denorm_ticket_line.csv', d_ticket_lines)

# ############################################
# ### TICKET HEADER ENTITY DENORMALIZATION ###
# ############################################

#
# COLUMNS_TICKET_HEADER = ['codigo de venta', 'tienda', 'fecha', 'hora',
#                            'forma pago', 'codigo cliente', 'importe total', 'total unidades', 'puntos ticket']
#
#
# def read_ticket_headers(filename):
#     with open('{path}/{filename}'.format(path=FILE_PATH, filename=filename)) as content:
#         data = {}
#         lines = 0
#         for line in content:
#             lines += 1
#             parts = line.split(',')
#             if len(parts) != len(COLUMNS_TICKET_HEADER):
#                 line_length_error(filename, line, len(parts), len(COLUMNS_TICKET_HEADER))
#                 continue
#
#             key = strip_string(parts[0])
#             shop_name = strip_string(parts[1])
#             ticket_date = strip_date(parts[2])
#             ticket_datetime = strip_datetime(parts[2], parts[3])
#             payment_method = strip_string(parts[4])
#             client_code = strip_string(parts[5])  # NULLABLE
#             total = strip_number(parts[6])
#             units = strip_number(parts[7])
#             points = strip_number(parts[8])
#             value = [shop_name, ticket_date, ticket_datetime, payment_method, client_code, total, units, points]
#             if key in data.keys():
#                 repeated_key_error(filename, key, data[key], value)
#             data[key] = value
#
#         if lines != len(data):
#             file_data_legth_mismatch_error(filename, lines, len(data))
#
#         return data
#
#
# # Ticket header
# ticket_header = read_ticket_headers('cabeceraticket.cvs')
# test_key_existence(shops.keys(), 'tienda', ticket_header, 'cabeceraticket.cvs', 0)
# test_key_existence(clients.keys(), 'cliente', ticket_header, 'cabeceraticket.cvs', 4)
#
# # Test ticket lines agains headers
# test_key_existence(ticket_header.keys(), 'cabeceraticket', ticket_line, 'lineasticket.cvs', 1)