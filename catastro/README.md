# Catastro Module
El módulo Catastro es una librería de Python que proporciona una interfaz simplificada para acceder a los datos del Catastro Español utilizando la biblioteca pycatastro.

## Dependencies

        - pandas
        - pycatastro

# Instalación

Para instalar este módulo en tu entorno local, puedes utilizar el siguiente comando en tu terminal:

        pip install -e .

Nota: Asegúrate de estar en el directorio donde se encuentra el archivo setup.py de este módulo.


## Class Definitions

### Catastro

La clase Catastro proporciona varios métodos para recuperar y procesar datos de la API del Catastro.


#### Métodos

    obtener_provincias(): Devuelve un DataFrame que contiene las provincias.
    obtener_municipios(provincia): Devuelve un DataFrame que contiene los municipios de una provincia dada.
    obtener_calles(provincia, municipio, tipovia=None, nombrevia=None): Devuelve un DataFrame que contiene las calles de un municipio dado.
    obtener_propiedad(provincia, pueblo, tipo_calle, nombre_calle, numero): Devuelve un diccionario que contiene los detalles de una propiedad dada su dirección.
    obtener_propiedades_en_calle(provincia, pueblo, tipo_calle, nombre_calle, numero_max): Devuelve un DataFrame que contiene los detalles de todas las propiedades en una calle dada.
    obtener_propiedades_coordenadas(long=None, lat=None, srs='EPSG:4326'): Devuelve un DataFrame que contiene los detalles de todas las propiedades dentro de un conjunto dado de coordenadas.
    obtener_info_rc(provincia, municipio, rc): Devuelve un DataFrame que contiene los detalles de una propiedad dado su código de referencia Catastro.
    obtener_codigos_provincias(): Devuelve un diccionario que mapea los códigos de provincias a los nombres de provincias.
    obtener_codigos_municipios(): Devuelve un diccionario que mapea los códigos de municipios a los nombres de municipios.

## Usage Example

        import pycatastro
        from catastro import Catastro

        catastro = pycatastro.PyCatastro()
        gestor = Catastro(catastro)

        provincias = gestor.obtener_provincias()
        provincias = provincias['Nombre'].to_list()

        municipios = gestor.obtener_municipios(provincias[0])
        municipios = municipios['Nombre'].to_list()

        calles = gestor.obtener_calles('Madrid', 'Madrid')
        calles = calles[(calles['Tipo'] == 'CL') | (calles['Tipo'] == 'AV')]
        nombres, tipos = calles['Nombre'].to_list(), calles['Tipo'].to_list()
        for i in range(min(len(nombres), len(tipos))):
            print(f"Dirección {i}: {nombres[i]} , tipo: {tipos[i]}")
