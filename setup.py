import setuptools

setuptools.setup(
    name="catastro",
    version="0.1",
    description="Obtención y consulta de datos a la API del catastro.",
    packages=setuptools.find_packages(include=['catastro*']),
    python_requires='>=3.7',
)
