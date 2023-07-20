import pandas as pd
from pycatastro import PyCatastro
from typing import Dict


class Catastro:

    def __init__(self):
        self.catastro = PyCatastro()

    def obtener_provincias(self):
        provincias = self.catastro.ConsultaProvincia()
        provincias_list = provincias['consulta_provinciero']['provinciero']['prov']
        df_provincias = pd.DataFrame(provincias_list)
        df_provincias.rename(
            columns={'cpine': 'Codigo', 'np': 'Nombre'}, inplace=True)
        return df_provincias

    def obtener_municipios(self, provincia):
        municipios = self.catastro.ConsultaMunicipio(provincia)
        municipios_data = municipios["consulta_municipiero"]["municipiero"]["muni"]

        municipios_list = []
        if isinstance(municipios_data, list):
            for m in municipios_data:
                municipios_list.append({
                    'Nombre': m['nm'],
                    'Codigo_Delegacion_MEH': m['locat']['cd'],
                    'Codigo_Municipio_MEH': m['locat']['cmc'],
                    'Codigo_Provincia_INE': m['loine']['cp'],
                    'Codigo_Municipio_INE': m['loine']['cm']
                })
        else:
            municipios_list.append({
                'Nombre': municipios_data['nm'],
                'Codigo_Delegacion_MEH': municipios_data['locat']['cd'],
                'Codigo_Municipio_MEH': municipios_data['locat']['cmc'],
                'Codigo_Provincia_INE': municipios_data['loine']['cp'],
                'Codigo_Municipio_INE': municipios_data['loine']['cm']
            })
        return pd.DataFrame(municipios_list)

    def obtener_calles(self, provincia, municipio, tipovia=None, nombrevia=None):
        calles = self.catastro.ConsultaVia(
            provincia, municipio, tipovia, nombrevia)
        calles_data = calles['consulta_callejero']['callejero']['calle']
        calles_list = []
        for c in calles_data:
            calles_list.append({
                'Codigo_Provincia': c['loine']['cp'],
                'Codigo_Municipio': c['loine']['cm'],
                'Codigo_Calle': c['dir']['cv'],
                'Tipo': c['dir']['tv'],
                'Nombre': c['dir']['nv']
            })
        return pd.DataFrame(calles_list)

    def obtener_propiedad(self, provincia: str, pueblo: str, tipo_calle: str, nombre_calle: str, numero: int) -> Dict:
        propiedad = self.catastro.Consulta_DNPLOC(
            provincia, pueblo, tipo_calle, nombre_calle, numero)
        return propiedad if self.propiedad_existe(propiedad) else None

    def obtener_propiedades_en_calle(self, provincia: str, pueblo: str, tipo_calle: str, nombre_calle: str, numero_max: int) -> pd.DataFrame:
        propiedades = [self.obtener_propiedad(provincia, pueblo, tipo_calle, nombre_calle, i) for i in range(
            numero_max) if self.obtener_propiedad(provincia, pueblo, tipo_calle, nombre_calle, i)]
        df = pd.DataFrame([self.extraer_info(propiedad)
                          for propiedad in propiedades])
        df.dropna(inplace=True)
        return df

    def obtener_propiedades_coordenadas(self, long=None, lat=None, srs='EPSG:4326') -> pd.DataFrame:
        respuesta = self.catastro.Consulta_RCCOOR_Distancia(
            srs, str(lat), str(long))
        lpcd = respuesta.get('consulta_coordenadas_distancias', {}).get(
            'coordenadas_distancias', {}).get('coordd', {}).get('lpcd', {}).get('pcd', [])
        print(lpcd)
        propiedades_list = []
        for pcd in lpcd:
            if isinstance(pcd, dict):
                propiedades_list.append({
                    'referencia_catastral': ''.join([pcd.get('pc', {}).get('pc1', ''), pcd.get('pc', {}).get('pc2', '')]),
                    'provincia': pcd.get('dt', {}).get('loine', {}).get('cp', ''),
                    'municipio': pcd.get('dt', {}).get('loine', {}).get('cm', ''),
                    'direccion': pcd.get('ldt', ''),
                    'distancia': pcd.get('dis', '')
                })

        return pd.DataFrame(propiedades_list)

    def obtener_info_rc(self, provincia, municipio, rc):
        respuesta = self.catastro.Consulta_DNPRC(provincia, municipio, rc)
        return self.extraer_info_rc(respuesta)

    def obtener_codigos_provincias(self):
        provincias = self.obtener_provincias()
        return provincias.set_index('Codigo')['Nombre'].to_dict()

    def obtener_codigos_municipios(self):
        municipios = pd.concat([self.obtener_municipios(provincia)
                               for provincia in self.obtener_provincias()['Nombre']])
        # print(municipios)
        return municipios.set_index('Codigo_Municipio_MEH')['Nombre'].to_dict()

    def propiedad_existe(self, resultado: Dict) -> bool:
        return not (resultado.get("consulta_dnp", {}).get("lerr", {}).get("err", {}).get("des") == "EL NUMERO NO EXISTE")

    def extraer_info(self, datos: Dict) -> Dict:
        if 'consulta_dnp' in datos:
            consulta_dnp = datos['consulta_dnp']
            if 'bico' in consulta_dnp:
                bico = consulta_dnp['bico']
                if 'bi' in bico:
                    bi = bico['bi']
                    if 'idbi' in bi and 'rc' in bi['idbi'] and 'dt' in bi:
                        rc = bi['idbi']['rc']
                        dt = bi['dt']
                        referencia_catastral = ''.join(rc.values())
                        provincia = dt.get('np', '')
                        municipio = dt.get('nm', '')
                        uso = bi.get('debi', {}).get('luso', '')
                        superficie = bi.get('debi', {}).get('sfc', '')
                        coef_participacion = bi.get('debi', {}).get('cpt', '')
                        antiguedad = bi.get('debi', {}).get('ant', '')
                        direccion_estructurada = ''
                        if 'locs' in dt and 'lous' in dt['locs'] and 'lourb' in dt['locs']['lous'] and 'dir' in dt['locs']['lous']['lourb']:
                            dir_ = dt['locs']['lous']['lourb']['dir']
                            direccion_estructurada = ' '.join(
                                [dir_.get(key, '') for key in ['tv', 'nv', 'pnp', 'plp', 'snp']])
                        direccion_no_estructurada = bi.get('ldt', '')
                        direccion = direccion_estructurada or direccion_no_estructurada
                        construcciones = []
                        if 'lcons' in bico:
                            lcons = bico['lcons']
                            if 'cons' in lcons:
                                cons = lcons['cons']
                                # Si 'cons' no es una lista, conviértela en una lista con un solo elemento
                                if not isinstance(cons, list):
                                    cons = [cons]
                                construcciones = [
                                    f"{con.get('lcd', '')} - {con.get('dfcons', {}).get('stl', '')} m^2" for con in cons]
                        return {
                            'referencia_catastral': referencia_catastral,
                            'provincia': provincia,
                            'municipio': municipio,
                            'direccion': direccion,
                            'uso': uso,
                            'superficie': superficie,
                            'coef_participacion': coef_participacion,
                            'antiguedad': antiguedad,
                            'construcciones': construcciones
                        }
        return {}

    def extraer_info_rc(self, datos: Dict) -> pd.DataFrame:
        bi = datos.get('consulta_dnp', {}).get('bico', {}).get('bi', {})
        lista_cons = datos.get('consulta_dnp', {}).get(
            'bico', {}).get('lcons', {}).get('cons', [])
        rc = bi.get('idbi', {}).get('rc')
        if rc is None:
            return pd.DataFrame()  # Devuelve un DataFrame vacío si rc es None
        info = {'referencia_catastral': ''.join(rc.values()),
                'provincia': bi.get('dt', {}).get('np'),
                'municipio': bi.get('dt', {}).get('nm'),
                'uso': bi.get('debi', {}).get('luso'),
                'superficie': bi.get('debi', {}).get('sfc'),
                'coef_participacion': bi.get('debi', {}).get('cpt'),
                'antiguedad': bi.get('debi', {}).get('ant'),
                'direccion': ' '.join([bi.get('dt', {}).get('locs', {}).get('lous', {}).get('lourb', {}).get('dir', {}).get(key, '') for key in ['tv', 'nv', 'pnp', 'plp', 'snp']]),
                'construcciones': [f"{cons.get('lcd')} - {cons.get('dfcons', {}).get('stl')} m^2" for cons in lista_cons if isinstance(cons, dict)]}
        df = pd.DataFrame([info])
        return df
