# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['iscc_core']

package_data = \
{'': ['*']}

install_requires = \
['base58>=2.1,<3.0',
 'bases>=0.2,<0.3',
 'bitarray-hardbyte',
 'blake3',
 'data-url>=1.0,<2.0',
 'jcs>=0.2,<0.3',
 'loguru>=0.6,<0.7',
 'more-itertools',
 'pybase64',
 'pydantic[dotenv]',
 'uvarint>=1.2,<2.0',
 'xxhash']

extras_require = \
{'turbo': ['cython']}

setup_kwargs = {
    'name': 'iscc-core',
    'version': '0.2.10',
    'description': 'ISCC - Core Algorithms',
    'long_description': '# ISCC - Codec & Algorithms\n\n[![Build](https://github.com/iscc/iscc-core/actions/workflows/tests.yml/badge.svg)](https://github.com/iscc/iscc-core/actions/workflows/tests.yml)\n[![Version](https://img.shields.io/pypi/v/iscc-core.svg)](https://pypi.python.org/pypi/iscc-core/)\n[![Coverage](https://codecov.io/gh/iscc/iscc-core/branch/main/graph/badge.svg?token=7BJ7HJU815)](https://codecov.io/gh/iscc/iscc-core)\n[![Quality](https://app.codacy.com/project/badge/Grade/ad1cc48ac0c0413ea2373a938148f019)](https://www.codacy.com/gh/iscc/iscc-core/dashboard)\n[![Downloads](https://pepy.tech/badge/iscc-core)](https://pepy.tech/project/iscc-core)\n\n`iscc-core` is a Python library that implements the core algorithms of the [ISCC](https://iscc.codes) (*International Standard Content Code*)\n\n## What is an ISCC\n\nThe ISCC is a similarity preserving identifier for digital media assets.\n\nISCCs are generated algorithmically from digital content, just like cryptographic hashes. However, instead of using a single cryptographic hash function to identify data only, the ISCC uses various algorithms to create a composite identifier that exhibits similarity-preserving properties (soft hash).\n\nThe component-based structure of the ISCC identifies content at multiple levels of abstraction. Each component is self-describing, modular, and can be used separately or with others to aid in various content identification tasks. The algorithmic design supports content deduplication, database synchronization, indexing, integrity verification, timestamping, versioning, data provenance, similarity clustering, anomaly detection, usage tracking, allocation of royalties, fact-checking and general digital asset management use-cases.\n\n## What is `iscc-core`\n\n`iscc-core` is the python based library of the core algorithms to create standard-compliant ISCC codes. It also serves as a reference for porting ISCC to other programming languages.\n\n!!! tip\n    This is a low level reference implementation. `iscc-core` does not support mediatype detection, metadata extraction or file format specific content extraction. For easy generation of ISCC codes see: [iscc-cli](https://github.com/iscc/iscc-cli/releases)\n\n## ISCC Architecture\n\n![ISCC Architecture](https://raw.githubusercontent.com/iscc/iscc-core/master/docs/images/iscc-codec-light.png)\n\n## ISCC MainTypes\n\n| Idx | Slug     | Bits | Purpose                                                  |\n|-----|:---------|------|----------------------------------------------------------|\n| 0   | META     | 0000 | Match on metadata similarity                             |\n| 1   | SEMANTIC | 0001 | Match on semantic content similarity                     |\n| 2   | CONTENT  | 0010 | Match on perceptual content similarity                   |\n| 3   | DATA     | 0011 | Match on data similarity                                 |\n| 4   | INSTANCE | 0100 | Match on data identity                                   |\n| 5   | ISCC     | 0101 | Composite of two or more components with common header   |\n| 6   | ID       | 0110 | Short unique identifier bound to ISCC, timestamp, pubkey |\n| 7   | FLAKE    | 0111 | Unique time, randomness and counter based distributed ID |\n\n## Installation\n\nUse the package manager [pip](https://pip.pypa.io/en/stable/) to install `iscc-core`.\n\n```bash\npip install iscc-core\n```\n\n## Quick Start\n\n```python\nimport json\nimport iscc_core as ic\n\nmeta_code = ic.gen_meta_code(name="ISCC Test Document!")\n\nprint(f"Meta-Code:     {meta_code[\'iscc\']}")\nprint(f"Structure:     {ic.iscc_explain(meta_code[\'iscc\'])}\\n")\n\n# Extract text from file\nwith open("demo.txt", "rt", encoding="utf-8") as stream:\n    text = stream.read()\n    text_code = ic.gen_text_code_v0(text)\n    print(f"Text-Code:     {text_code[\'iscc\']}")\n    print(f"Structure:     {ic.iscc_explain(text_code[\'iscc\'])}\\n")\n\n# Process raw bytes of textfile\nwith open("demo.txt", "rb") as stream:\n    data_code = ic.gen_data_code(stream)\n    print(f"Data-Code:     {data_code[\'iscc\']}")\n    print(f"Structure:     {ic.iscc_explain(data_code[\'iscc\'])}\\n")\n\n    stream.seek(0)\n    instance_code = ic.gen_instance_code(stream)\n    print(f"Instance-Code: {instance_code[\'iscc\']}")\n    print(f"Structure:     {ic.iscc_explain(instance_code[\'iscc\'])}\\n")\n\n# Compbine ISCC-UNITs into ISCC-CODE\niscc_code = ic.gen_iscc_code(\n    (meta_code["iscc"], text_code["iscc"], data_code["iscc"], instance_code["iscc"])\n)\n\n# Create convenience `Code` object from ISCC string\niscc_obj = ic.Code(iscc_code["iscc"])\nprint(f"ISCC-CODE:     {ic.iscc_normalize(iscc_obj.code)}")\nprint(f"Structure:     {iscc_obj.explain}")\nprint(f"Multiformat:   {iscc_obj.mf_base32}\\n")\n\n# Compare with random ISCC-CODE:\nrand_iscc = ic.Code.rnd(mt=ic.MT.ISCC, bits=256)\nprint(f"Compare ISCC-CODES:\\n{iscc_obj.uri}\\n{rand_iscc.uri}")\nprint(json.dumps(ic.iscc_compare(iscc_obj.code, rand_iscc.code), indent=2))\n\n# Generate an ISCC-ID\niscc_id = ic.gen_iscc_id(iscc_obj.code, chain_id=1, wallet="1Bq568oLhi5HvdgC6rcBSGmu4G3FeAntCz")\niscc_id_obj = ic.Code(iscc_id["iscc"])\nprint("\\nConstruct ISCC-ID:")\nprint(f"ISCC-ID:       {ic.iscc_normalize(iscc_id_obj.code)}")\nprint(f"Structure:     {iscc_id_obj.explain}")\nprint(f"Multiformat:   {iscc_id_obj.mf_base32}")\n```\n\nThe output of this example is as follows:\n\n```\nMeta-Code:     ISCC:AAAT4EBWK27737D2\nStructure:     META-NONE-V0-64-3e103656bffdfc7a\n\nText-Code:     ISCC:EAAQMBEYQF6457DP\nStructure:     CONTENT-TEXT-V0-64-060498817dcefc6f\n\nData-Code:     ISCC:GAA7UJMLDXHPPENG\nStructure:     DATA-NONE-V0-64-fa258b1dcef791a6\n\nInstance-Code: ISCC:IAA3Y7HR2FEZCU4N\nStructure:     INSTANCE-NONE-V0-64-bc7cf1d14991538d\n\nISCC-CODE:     ISCC:KACT4EBWK27737D2AYCJRAL5Z36G76RFRMO4554RU26HZ4ORJGIVHDI\nStructure:     ISCC-TEXT-V0-MCDI-3e103656bffdfc7a060498817dcefc6ffa258b1dcef791a6bc7cf1d14991538d\nMultiformat:   bzqavabj6ca3fnp757r5ambeyqf6457dp7isywhoo66i2npd46hiutektru\n\nCompare ISCC-CODES:\nISCC:KACT4EBWK27737D2AYCJRAL5Z36G76RFRMO4554RU26HZ4ORJGIVHDI\nISCC:KMDMRJYGHHVRCZ5TM6U4G6D4MXA6LAXC4ZRPOKFU7JBEQXR2BJOS6NA\n{\n  "meta_dist": 37,\n  "data_dist": 39,\n  "instance_match": false\n}\n\nConstruct ISCC-ID:\nISCC-ID:       ISCC:MEAJU5AXCPOIOYFL\nStructure:     ID-BITCOIN-V0-64-9a741713dc8760ab\nMultiformat:   bzqawcae2oqlrhxehmcvq\n```\n\n## Documentation\n\n<https://core.iscc.codes>\n\n## Project Status\n\nThe ISCC has been accepted by ISO as full work item ISO/AWI 24138 - International Standard Content\nCode and is currently being standardized at TC 46/SC 9/WG 18. https://www.iso.org/standard/77899.html\n\n!!! attention\n\n    The iscc-core library and the accompanying documentation is under development. API changes and\n    other backward incompatible changes are to be expected until the upcoming v1.5 stable release.\n\n\n## Maintainers\n[@titusz](https://github.com/titusz)\n\n## Contributing\n\nPull requests are welcome. For significant changes, please open an issue first to discuss your plans. Please make sure to update tests as appropriate.\n\nYou may also want join our developer chat on Telegram at <https://t.me/iscc_dev>.\n',
    'author': 'Titusz',
    'author_email': 'tp@py7.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://iscc.codes',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
