#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv

from datetime import date, datetime

""" Constants """

# Absolute path where the CVS files are located
FILE_PATH = "gourmetdb"

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


""" Util functions """


def strip_string(string):
    aux = string.strip('"').replace('"\n', '').strip()
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


def generate_dict(dataset_name, dataset, columns):
    ddataset = {}
    for key, values in dataset.items():
        if (len(values) + 1) != len(columns):
            line_length_error(dataset_name, [key, values], len(values) + 1,
                              len(columns))
            continue
        elem = {}
        elem[columns[0]] = key
        for i in range(0, len(values)):
            elem[columns[i + 1]] = values[i]
        ddataset[key] = elem
    return ddataset


def write_csv(filename, dataset):
    with open('{path}/{filename}'.format(path=FILE_PATH, filename=filename),
              'wb') as output:
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
            print("WARN: KeyError happened")
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

# Column names
COLUMNS_SECTION = ['nombre_seccion', 'descripcion_seccion']
COLUMNS_FAMILY = ['nombre_familia', 'descripcion_familia', 'seccion_familia']
COLUMNS_SUBFAMILY = ['nombre_subfamilia', 'descripcion_subfamilia',
                     'familia_subfamilia']
COLUMNS_PRODUCT = ['codigo_producto', 'descripccion_producto',
                   'pais_producto', 'coste_producto', 'precio_venta_producto',
                   'tipo_unidad_producto', 'subfamilia_producto',
                   'marca_producto', 'codigo_proveedor_producto']
COLUMNS_PROVIDER = ['codigo_proveedor', 'nombre_proveedor',
                    'persona_contacto_proveedor', 'direccion_proveedor',
                    'telefono_proveedor', 'periodo_pago_proveedor',
                    'pago_pendiente_proveedor', 'tipo_proveedor_proveedor',
                    'alcance_proveedor']


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
    'SW4': 'Reino Unido',
    'SW3': 'Reino Unido',
    'USA': 'Estados Unidos',
    'Germany': 'Alemania',
    'Belgium': 'Bélgica',
    'Holland': 'Holanda',
    'Denmark': 'Dinamarca',
    'Sweden': 'Suecia',
    'Switzerland': 'Suiza',
    'Ireland': 'Irlanda'
}


def add_provider_attributes(dataset):
    COLUMNS_PROVIDER.append("pais_proveedor")
    for attributes in dataset.values():
        parts = attributes[2].split(' ')
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

# Provider
providers = read_provider('proveedor.cvs')
add_provider_attributes(providers)
#test_key_existence(countries.keys(), 'pais', providers, 'proveedor.cvs', 8)

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
    join_error('Product', 'Subfamilia')

# Generate dictionaries for the datasets
d_providers = generate_dict('proveedor', providers, COLUMNS_PROVIDER)

# Denormalize provider into product
join_datasets(d_products, d_providers, 'codigo_proveedor_producto')
if not join_check(d_products, products, COLUMNS_PRODUCT,
                  COLUMNS_PROVIDER + COLUMNS_SUBFAMILY + COLUMNS_FAMILY
                  + COLUMNS_SECTION):
    join_error('Product', 'Proveedor')

write_csv('denorm_products.csv', d_products)

# ######################################
# ### XXXXXXX ENTITY DENORMALIZATION ###
# ######################################
#
# COLUMNS_TIENDA = ['nombre_tienda', 'direccion_tienda', 'superficie_tienda',
#                   'formato_tienda', 'pais_tienda', 'tipo_zona_tienda']
#
#
# COLUMNS_PROMOCION = ['nombre', 'tipo', 'coste', 'fecha inicio', 'fecha fin',
#                      'codigo producto', 'familia', 'seccion', 'tienda', 'region', 'pais']
#
# COLUMNS_CLIENTE = ['codigo', 'nombre', 'sexo', 'fecha nacimiento', 'estado civil', 'direccion',
#                    'profesion', 'numero hijos', 'region', 'nacionalidad', 'total compras', ' puntos acumulados']
#

# COLUMNS_PEDIDO = ['codigo', 'nombre', 'codigo producto', 'precio compra',
#                   'cantidad solicitada', 'fecha solicitud', 'cantidad entregada', 'fecha entrega']
#
# COLUMNS_REGION = ['nombre_region', 'continente_region']
#
# COLUMNS_PAIS = ['nombre_pais', 'extension_pais', 'poblacion_pais', 'region_pais']
#
# COLUMNS_CABECERA_TICKET = ['codigo de venta', 'tienda', 'fecha', 'hora',
#                            'forma pago', 'codigo cliente', 'importe total', 'total unidades', 'puntos ticket']
#
# COLUMNS_LINEA_TICKET = ['codigo', 'codigo venta', 'tienda', 'codigo producto',
#                         'cantidad', 'precio venta', 'promocion', 'codigo cabecera']
#

# # File names:
# FILENAMES = {
#     'tienda.cvs': COLUMNS_TIENDA,
#     'producto.cvs': COLUMNS_PRODUCTO,
#     'subfamilia.cvs': COLUMNS_SUBFAMILIA,
#     'promocion.cvs': COLUMNS_PROMOCION,
#     'seccion.cvs': COLUMNS_SECCION,
#     'familia.cvs': COLUMNS_FAMILIA,
#     'cliente.cvs': COLUMNS_CLIENTE,
#     'proveedor.cvs': COLUMNS_PROVEEDOR,
#     'pedido.cvs': COLUMNS_PEDIDO,
#     'regiongeografica.cvs': COLUMNS_REGION,
#     'pais.cvs': COLUMNS_PAIS,
#     'cebeceraticket.cvs': COLUMNS_CABECERA_TICKET,
#     'lineticket.cvs': COLUMNS_LINEA_TICKET,
# }
#
#
#
# """ Read files """
#
#
# def read_region(filename):
#     with open('{path}/{filename}'.format(path=FILEPATH, filename=filename)) as content:
#         data = {}
#         lines = 0
#         for line in content:
#             lines += 1
#             parts = line.split(',')
#             if len(parts) != len(COLUMNS_REGION):
#                 line_length_error(filename, line, len(parts), len(COLUMNS_REGION))
#                 continue
#             key = strip_string(parts[0])
#             value = [strip_string(parts[1])]
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
# def read_pais(filename):
#     with open('{path}/{filename}'.format(path=FILEPATH, filename=filename)) as content:
#         data = {}
#         lines = 0
#         for line in content:
#             lines += 1
#             parts = line.split(',')
#             if len(parts) != len(COLUMNS_PAIS):
#                 line_length_error(filename, line, len(parts), len(COLUMNS_PAIS))
#                 continue
#             key = strip_string(parts[0])
#             extension = int(strip_number(parts[1]))
#             poblacion = int(strip_number(parts[2]))
#             region = strip_string(parts[3])
#             value = [extension, poblacion, region]
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
# def read_tienda(filename):
#     with open('{path}/{filename}'.format(path=FILEPATH, filename=filename)) as content:
#         data = {}
#         lines = 0
#         for line in content:
#             lines += 1
#             parts = line.split(',')
#             parts[1] = '{0}{1}'.format(parts[1], parts[2])  # Concatenate address
#             parts.pop(2)  # Delete the remainig duplicated part of the address
#             if len(parts) != len(COLUMNS_TIENDA):
#                 line_length_error(filename, line, len(parts), len(COLUMNS_TIENDA))
#                 continue
#             key = strip_string(parts[0])
#             address = strip_string(parts[1])
#             surface = float(strip_number(parts[2]))
#             shop_format = strip_string(parts[3])
#             country = strip_string(parts[4])
#             zone_type = strip_string(parts[5])
#
#             value = [address, surface, shop_format, country, zone_type]
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
#
#
#
#
# def read_promocion(filename):
#     with open('{path}/{filename}'.format(path=FILEPATH, filename=filename)) as content:
#         data = {}
#         lines = 0
#         for line in content:
#             lines += 1
#             parts = line.split(',')
#             if len(parts) != len(COLUMNS_PROMOCION):
#                 line_length_error(filename, line, len(parts), len(COLUMNS_PROMOCION))
#                 continue
#             key = strip_string(parts[0])
#             promotion_type = strip_string(parts[1])
#             cost = strip_number(parts[2])  # NULLABLE --> Change to int later on
#             start_date = strip_date(parts[3])
#             end_date = strip_date(parts[4])
#             product_code = strip_string(parts[5])
#             family = strip_string(parts[6])  # NULLABLE
#             section = strip_string(parts[7])  # NULLABLE
#             shop = strip_string(parts[8])  # NULLABLE
#             region = strip_string(parts[9])  # NULLABLE
#             country = strip_string(parts[10])  # NULLABLE
#             value = [promotion_type, cost, start_date, end_date, product_code, family, section, shop, region, country]
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

#
#
# def read_cliente(filename):
#     with open('{path}/{filename}'.format(path=FILEPATH, filename=filename)) as content:
#         data = {}
#         lines = 0
#         for line in content:
#             lines += 1
#             parts = line.split(',')
#             parts = process_commas(parts, line, 4, 5, '",', True)
#             parts = process_commas(parts, line, 5, 6, '",', True)
#             if len(parts) != len(COLUMNS_CLIENTE):
#                 line_length_error(filename, line, len(parts), len(COLUMNS_CLIENTE))
#                 continue
#
#             key = strip_string(parts[0])
#             name = strip_string(parts[1])  # NULLABLE
#             gender = strip_string(parts[2])  # NULLABLE
#             birthdate = strip_date(parts[3])  # NULLABLE
#             civil_state = strip_string(parts[4])  # NULLABLE
#             address = strip_string(parts[5])  # NULLABLE
#             profession = strip_string(parts[6])  # NULLABLE
#             num_children = strip_number(parts[7])  # NULLABLE --> Change to int later on
#             region = strip_string(parts[8])  # NULLABLE
#             nationality = strip_string(parts[9])  # NULLABLE
#             total_buys = strip_number(parts[10])  # NULLABLE --> Change to int later on
#             total_points_acc = strip_number(parts[11])  # NULLABLE --> Change to int later on
#             value = [name, gender, birthdate, civil_state, address, profession, num_children, region,
#                      nationality, total_buys, total_points_acc]
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
# def read_orders(filename):
#     with open('{path}/{filename}'.format(path=FILEPATH, filename=filename)) as content:
#         data = {}
#         lines = 0
#         for line in content:
#             lines += 1
#             parts = line.split(',')
#             if len(parts) != len(COLUMNS_PEDIDO):
#                 line_length_error(filename, line, len(parts), len(COLUMNS_PEDIDO))
#                 continue
#
#             key = strip_string(parts[0])
#             shop_name = strip_string(parts[1])
#             product_code = strip_string(parts[2])
#             order_price = strip_number(parts[3])
#             order_amount = int(strip_number(parts[4]))
#             order_date = strip_date(parts[5])
#             delivered_amount = int(strip_number(parts[6]))
#             delivered_date = strip_date(parts[7])
#             value = [shop_name, product_code, order_price, order_amount, order_date, delivered_amount, delivered_date]
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
# def read_ticket_header(filename):
#     with open('{path}/{filename}'.format(path=FILEPATH, filename=filename)) as content:
#         data = {}
#         lines = 0
#         for line in content:
#             lines += 1
#             parts = line.split(',')
#             if len(parts) != len(COLUMNS_CABECERA_TICKET):
#                 line_length_error(filename, line, len(parts), len(COLUMNS_CABECERA_TICKET))
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
# """
# Order code and header code are wrongly named from the data given. The last field 'codigo cabecera' is not used.
# It can be crosschecked with the foreign keys of the db2 file. The header code is the second field 'codigo venta'.
# """
#
#
# def read_ticket_lines(filename):
#     with open('{path}/{filename}'.format(path=FILEPATH, filename=filename)) as content:
#         data = {}
#         lines = 0
#         for line in content:
#             lines += 1
#             parts = line.split(',')
#             if len(parts) != len(COLUMNS_LINEA_TICKET):
#                 line_length_error(filename, line, len(parts), len(COLUMNS_LINEA_TICKET))
#                 continue
#
#             line = strip_string(parts[0])
#             header_code = strip_string(parts[1])
#             key = '{line}-{header}'.format(line=line, header=header_code)
#             shop_name = strip_string(parts[2])
#             product_code = strip_string(parts[3])
#             amount = strip_number(parts[4])
#             price = strip_number(parts[5])
#             promotion_name = strip_string(parts[6])  # NULLABLE
#             header_code_spare = strip_number(parts[7])
#             value = [line, header_code, shop_name, product_code, amount, price, promotion_name, header_code_spare]
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
#
# """ Add attributes functions """
#
#
# def add_country_attributes(dataset):
#     COLUMNS_PAIS.append("densidad_pobl_pais")  # In people/km2
#     for attributes in dataset.values():
#         density = round(float(attributes[1]) / attributes[0], 1)
#         attributes.append(density)
#
#

#
#

#
#
#
# def add_order_attributes(dataset):
#     COLUMNS_PEDIDO.append("excfal_pedido")  # exceso o falta de mercancia entregada
#     for attributes in dataset.values():
#         excfal = attributes[5] - attributes[3]
#         attributes.append(excfal)
#     COLUMNS_PEDIDO.append("tiempo_entrega_pedido")  # Tiempo transcurrido desde el pedido hasta la entrega
#     for attributes in dataset.values():
#         delay = abs((attributes[6] - attributes[4]).days)
#         attributes.append(delay)
#
#
# """ Debug """
#
#
# def print_dict(dictionary):
#     for key, value in dictionary.items():
#         print('Key: {key} Value: {value}'.format(key=key, value=value))
#
#
# ##############################################
# ### READ, CHECK, FORMAT AND ADD ATTRIBUTES ###
# ##############################################
# # Regions
# regions = read_region('regiongeografica.cvs')
# # Countries
# countries = read_pais('pais.cvs')
# add_country_attributes(countries)
# test_key_existence(regions.keys(), 'region', countries, 'pais.cvs', 2)
# # Shops
# shops = read_tienda('tienda.cvs')
# test_key_existence(countries.keys(), 'pais', shops, 'tienda.cvs', 3)
#

# # Promotion
# promotions = read_promocion('promocion.cvs')
# test_key_existence(families.keys(), 'familia', promotions, 'promocion.cvs', 5)
# test_key_existence(sections.keys(), 'seccion', promotions, 'promocion.cvs', 6)
# test_key_existence(shops.keys(), 'tienda', promotions, 'promocion.cvs', 7)
# test_key_existence(regions.keys(), 'region', promotions, 'promocion.cvs', 8)
# test_key_existence(countries.keys(), 'pais', promotions, 'promocion.cvs', 9)

# # Client
# clients = read_cliente('cliente.cvs')
# test_key_existence(regions.keys(), 'region', clients, 'cliente.cvs', 7)
# test_key_existence(countries.keys(), 'pais', clients, 'cliente.cvs', 8)
# # # Order
# # orders = read_orders('pedido.cvs')
# # add_order_attributes(orders)
# # test_key_existence(shops.keys(), 'tienda', orders, 'pedido.cvs', 0)
# # test_key_existence(products.keys(), 'producto', orders, 'pedido.cvs', 1)
# # Ticket header
# ticket_header = read_ticket_header('cabeceraticket.cvs')
# test_key_existence(shops.keys(), 'tienda', ticket_header, 'cabeceraticket.cvs', 0)
# test_key_existence(clients.keys(), 'cliente', ticket_header, 'cabeceraticket.cvs', 4)
# # Ticket line
# ticket_line = read_ticket_lines('lineasticket.cvs')
# test_key_existence(ticket_header.keys(), 'cabeceraticket', ticket_line, 'lineasticket.cvs', 1)
# test_key_existence(shops.keys(), 'tienda', ticket_line, 'lineasticket.cvs', 2)
# test_key_existence(products.keys(), 'producto', ticket_line, 'lineasticket.cvs', 3)
# test_key_existence(promotions.keys(), 'promocion', ticket_line, 'lineasticket.cvs', 6)
