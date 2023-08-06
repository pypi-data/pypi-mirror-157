# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['indoNLP', 'indoNLP.preprocessing']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'indonlp',
    'version': '0.1.1',
    'description': 'Indonesian NLP written in python',
    'long_description': '# indoNLP\n\nBahasa | [English](https://github.com/Hyuto/indo-nlp/blob/master/README.en.md)\n\nindoNLP adalah library python sederhana yang bertujuan untuk memudahkan proyek NLP anda.\n\n## Installation\n\nindoNLP dapat diinstall dengan mudah dengan menggunakan `pip`:\n\n```bash\npip install indoNLP\n```\n\n## Preprocessing\n\nModul `indoNLP.preprocessing` menyediakan beberapa fungsi umum untuk menyiapkan dan melakukan\ntransformasi terhadap data teks mentah untuk digunakan pada konteks tertentu.\n\n1. `remove_html`\n\n   Menghapus html tag yang terdapat di dalam teks\n\n   ```python\n   >>> from indoNLP.preprocessing import remove_html\n   >>> remove_html("website <a href=\'https://google.com\'>google</a>")\n   >>> "website google"\n   ```\n\n2. `remove_url`\n\n   Menghapus url yang terdapat di dalam teks\n\n   ```python\n   >>> from indoNLP.preprocessing import remove_url\n   >>> remove_url("retrieved from https://gist.github.com/gruber/8891611")\n   >>> "retrieved from "\n   ```\n\n3. `remove_stopwords`\n\n   > Stopwords merupakan kata yang diabaikan dalam pemrosesan dan biasanya disimpan di dalam stop lists. Stop list ini berisi daftar kata umum yang mempunyai fungsi tapi tidak mempunyai arti\n\n   Menghapus stopwords yang terdapat di dalam teks.\n   List stopwords bahasa Indonesia didapatkan dari https://stopwords.net/indonesian-id/\n\n   ```python\n   >>> from indoNLP.preprocessing import remove_stopwords\n   >>> remove_stopwords("siapa yang suruh makan?!!")\n   >>> "  suruh makan?!!"\n   ```\n\n4. `replace_slang`\n\n   Mengganti kata gaul (_slang_) menjadi kata formal tanpa mengubah makna dari kata tersebut.\n   List kata gaul (_slang words_) bahasa Indonesian didapatkan dari\n   [Kamus Alay - Colloquial Indonesian Lexicon](https://github.com/nasalsabila/kamus-alay)\n   oleh Salsabila, Ali, Yosef, and Ade\n\n   ```python\n   >>> from indoNLP.preprocessing import replace_slang\n   >>> replace_slang("emg siapa yg nanya?")\n   >>> "memang siapa yang bertanya?"\n   ```\n\n5. `replace_word_elongation`\n\n   > Word elongation adalah tindakan untuk menambahkan huruf ke kata, biasanya di akhir kata\n\n   Meghandle word elongation\n\n   ```python\n   >>> from indoNLP.preprocessing import replace_word_elongation\n   >>> replace_word_elongation("kenapaaa?")\n   >>> "kenapa?"\n   ```\n\n**pipelining**\n\nMembuat pipeline dari sequance fungsi preprocessing\n\n```python\n>>> from indoNLP.preprocessing import pipeline, replace_word_elongation, replace_slang\n>>> pipe = pipeline([replace_word_elongation, replace_slang])\n>>> pipe("Knp emg gk mw makan kenapaaa???")\n>>> "kenapa memang enggak mau makan kenapa???"\n```\n',
    'author': 'Wahyu Setianto',
    'author_email': 'wahyusetianto19@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
