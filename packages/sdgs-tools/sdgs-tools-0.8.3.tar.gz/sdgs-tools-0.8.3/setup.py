# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sdgs_tools',
 'sdgs_tools.aplikasi_sdgs',
 'sdgs_tools.aplikasi_sdgs.export_individu',
 'sdgs_tools.aplikasi_sdgs.export_individu.kesehatan',
 'sdgs_tools.aplikasi_sdgs.export_keluarga',
 'sdgs_tools.cli',
 'sdgs_tools.cli.aplikasi',
 'sdgs_tools.cli.dashboard',
 'sdgs_tools.dashboard',
 'sdgs_tools.dashboard.auth',
 'sdgs_tools.dashboard.import_individu',
 'sdgs_tools.dashboard.import_individu.enums',
 'sdgs_tools.dashboard.import_keluarga',
 'sdgs_tools.dashboard.import_keluarga.enums',
 'sdgs_tools.ext',
 'sdgs_tools.gui',
 'sdgs_tools.gui.aplikasi',
 'sdgs_tools.gui.dashboard']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=21.2.0,<22.0.0',
 'beautifulsoup4>=4.9.3,<5.0.0',
 'cattrs>=1.8.0,<2.0.0',
 'click>=8.0.1,<9.0.0',
 'openpyxl>=3.0.7,<4.0.0',
 'python-dateutil>=2.8.1,<3.0.0',
 'uiautomator2>=2.16.7,<3.0.0']

extras_require = \
{'ujson': ['ujson>=4.1.0,<5.0.0']}

entry_points = \
{'console_scripts': ['sdgs-tools = sdgs_tools.__main__:main']}

setup_kwargs = {
    'name': 'sdgs-tools',
    'version': '0.8.3',
    'description': '',
    'long_description': '# SDGs Tools\n\n[![sdgs-tools - PyPi](https://img.shields.io/pypi/v/sdgs-tools)](https://pypi.org/project/sdgs-tools/)\n[![Supported Python versions](https://img.shields.io/pypi/pyversions/sdgs-tools)](https://pypi.org/project/sdgs-tools/)\n[![Donate Saweria](https://img.shields.io/badge/Donasi-Saweria-blue)](https://saweria.co/hexatester)\n[![Total Donasi](https://img.shields.io/badge/total%20donasi-Rp%20260.000%20%2C---red)](https://saweria.co/hexatester)\n[![LISENSI](https://img.shields.io/github/license/hexatester/sdgs-tools)](https://github.com/hexatester/sdgs-tools/blob/main/LICENSE)\n\nsdgs-tools adalah alat bantu pendataan SDGs Kemendesa buatan [Habib Rohman](https://github.com/hexatester)\n\nAplikasi ini (sdgs-tools.exe) sama sekali tidak berafiliasi dengan, diizinkan, dipelihara, disponsori atau didukung oleh Kemendesa atau afiliasi atau anak organisasinya. Ini adalah perangkat lunak yang independen dan tidak resmi. Gunakan dengan risiko Anda sendiri.\n\nJika terjadi error yang tidak terduga harap mengubungi saya via Telegram di <https://t.me/hexatester>\nJika Anda merasa terbantu dengan kreasi saya, Anda dapat melakukan donasi di <https://saweria.co/hexatester>\n\n## Daftar Isi\n\n- [SDGs Tools](#sdgs-tools)\n  - [Daftar Isi](#daftar-isi)\n  - [Video Tutorial](#video-tutorial)\n  - [Download](#download)\n  - [Fungsi](#fungsi)\n    - [Memasukan data individu dari excel ke dashboard-sdgs](#memasukan-data-individu-dari-excel-ke-dashboard-sdgs)\n    - [Memasukan data keluarga dari excel ke dashboard-sdgs](#memasukan-data-keluarga-dari-excel-ke-dashboard-sdgs)\n    - [Mengeluarkan data individu dari aplikasi sdgs android](#mengeluarkan-data-individu-dari-aplikasi-sdgs-android)\n    - [Mengeluarkan data keluarga dari aplikasi sdgs android](#mengeluarkan-data-keluarga-dari-aplikasi-sdgs-android)\n\n## Video Tutorial\n\n[![Import Dashboard SDGs](docs/img/Import-Individu-SDGs-Tools.png)](https://www.youtube.com/watch?v=rXU0YYDwNj0 "Memasukan Data Excel ke Dashboard SDGs Kemendesa")\n\n[Memasukan Data Excel ke Dashboard SDGs Kemendesa](https://www.youtube.com/watch?v=rXU0YYDwNj0)\n\n## Download\n\nDownload aplikasi sdgs-tools.exe [klik di sini](https://github.com/hexatester/sdgs-tools/releases/download/v0.8.3/sdgs-tools.exe)\n\n## Fungsi\n\n- Memasukan data individu dari excel ke [dashboard-sdgs kemendesa](https://dashboard-sdgs.kemendesa.go.id/)\n- Memasukan data keluarga dari excel ke [dashboard-sdgs kemendesa](https://dashboard-sdgs.kemendesa.go.id/)\n- Mengeluarkan data individu dari aplikasi sdgs android ke excel.\n- Mengeluarkan data keluarga dari aplikasi sdgs android ke excel\n\n### Memasukan data individu dari excel ke dashboard-sdgs\n\n1. [Download aplikasi](#download)\n2. Downlaod [template individu dashboard](https://github.com/hexatester/sdgs-tools/releases/download/v0.8.3/Template_Individu-Import-Dashboard_SDGS.xlsm)\n3. Salin dan rubah nama file template tersebut sesuai dengan RT / RW.\n4. Isi masing-masing file dengan data sesuai dengan RT / RW, pengisian dapat dilakukan secara offline.\n5. Jika data sudah siap, sambungkan PC / Laptop ke internet dan buka aplikasi `sdgs-tools.exe`\n6. Klik **Dashboard SDGS**\n7. Klik **Import Individu**\n8. Masukkan *Username* dan *Password* **akun enumerator** dari RT / RW yang akan diinput, *jika setiap enumerator berbeda RT / RW*.\n9. Klik Login\n10. Isi kolom Baris dengan jarak baris dari template yang sudah diisi, misalnya di template sudah diisi baris ke 4 sampai ke 100. Maka kolom **Baris** di aplikasi diisi `4-100`\n11. Isi kolom Rt dan Rw sesuai dengan RT / Rw template yang akan diinput. RT dan RW masing-masing harus 3 digit, misal 001.\n12. Klik **Pilih template individu dan mulai import**\n13. Tunggu sampai selesai, program jangan diklik.\n\nKetika melakukan pengisian template sebaiknya menggunakan microsoft excel di pc / laptop, agar dapat mengaktifkan data validation dan macro / content.\n\n### Memasukan data keluarga dari excel ke dashboard-sdgs\n\n1. [Download aplikasi](#download)\n2. Downlaod [template keluarga dashboard](https://github.com/hexatester/sdgs-tools/releases/download/v0.8.3/Template_Keluarga-Import-Dashboard_SDGS.xlsm)\n3. Salin dan rubah nama file template tersebut sesuai dengan RT / RW.\n4. Isi masing-masing file dengan data sesuai dengan RT / RW, pengisian dapat dilakukan secara offline.\n5. Jika data sudah siap, sambungkan PC / Laptop ke internet dan buka aplikasi `sdgs-tools.exe`\n6. Klik **Dashboard SDGS**\n7. Klik **Import Keluarga**\n8. Masukkan *Username* dan *Password* **akun enumerator** dari RT / RW yang akan diinput, *jika setiap enumerator berbeda RT / RW*.\n9. Klik Login\n10. Isi kolom Baris dengan jarak baris dari template yang sudah diisi, misalnya di template sudah diisi baris ke 4 sampai ke 100. Maka kolom **Baris** di aplikasi diisi `4-100`\n11. Isi kolom Rt dan Rw sesuai dengan RT / Rw template yang akan diinput. RT dan RW masing-masing harus 3 digit, misal 001.\n12. Klik **Pilih template keluarga dan mulai import**\n13. Tunggu sampai selesai, program jangan diklik.\n\nKetika melakukan pengisian template sebaiknya menggunakan microsoft excel di pc / laptop, agar dapat mengaktifkan data validation dan macro / content.\n\n### Mengeluarkan data individu dari aplikasi sdgs android\n\n### Mengeluarkan data keluarga dari aplikasi sdgs android\n',
    'author': 'hexatester',
    'author_email': 'hexatester@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/hexatester/sdgs-tools',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.10,<4.0.0',
}


setup(**setup_kwargs)
