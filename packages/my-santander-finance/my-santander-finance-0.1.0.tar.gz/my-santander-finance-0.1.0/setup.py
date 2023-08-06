# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['my_santander_finance']

package_data = \
{'': ['*'], 'my_santander_finance': ['driver/*']}

install_requires = \
['PyAutoGUI>=0.9.53,<0.10.0',
 'SQLAlchemy>=1.4.39,<2.0.0',
 'click>=8.1.3,<9.0.0',
 'numpy>=1.23.0,<2.0.0',
 'pandas>=1.4.3,<2.0.0',
 'pydantic>=1.9.1,<2.0.0',
 'pywin32>=304,<305',
 'selenium>=4.3.0,<5.0.0',
 'webdriver-manager>=3.7.1,<4.0.0',
 'xlrd>=2.0.1,<3.0.0']

entry_points = \
{'console_scripts': ['app = my_santander_finance.app:main']}

setup_kwargs = {
    'name': 'my-santander-finance',
    'version': '0.1.0',
    'description': 'automated process to obtain the consumption of the bank credit and debit cards, classify them and generate a dashboard',
    'long_description': '# App para Automatizacion (web scrapping) de Banco Santander\n\nAplicacion para la gestion de cuentas del banco Santander de Argentina, permite:\n\n- [x] obtener el resumen de la cuenta realizando un download del archivo con los registros de los ultimos 60 dias\n\n- [x] transformarlos y cargarlos en una base de datos sqlite\n\n- [] etiquetar los consumos para luego generar reportes\n\n\n## Environment Variables\n\nPara ejecutar este proyecto se necesitan las siguientes variables de entorno, pudiendo ser definidas en un archivo .env:\n\n`DNI`\n\n`CLAVE`\n\n`USUARIO`\n\n_Estos datos, son los requeridos para el login en la web de Santander._ \n\n\n## Instalacion\n\nInstalar utilizando pip\n\n```bash\n  pip install my-santander-finance\n```\n\n## Utilizacion\n\n```bash\n  app\n```\n\n\n\n## Feedback\n\nContactarme a opaniagu@gmail.com\n\n## Authors\n\n- [@opaniagu](https://www.github.com/opaniagu)\n\n\n## License\n\n[MIT](https://choosealicense.com/licenses/mit/)',
    'author': 'Oscar Paniagua',
    'author_email': 'opaniagu@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/opaniagu/my-santander-finance',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
