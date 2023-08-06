# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['rcd_dev_kit',
 'rcd_dev_kit.database_manager',
 'rcd_dev_kit.dataclass_manager',
 'rcd_dev_kit.decorator_manager',
 'rcd_dev_kit.file_manager',
 'rcd_dev_kit.pandas_manager',
 'rcd_dev_kit.sql_utils']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.22.7,<2.0.0',
 'botocore>=1.25.7,<2.0.0',
 'elasticsearch>=8.2.0,<9.0.0',
 'google-api-python-client>=2.47.0,<3.0.0',
 'google-cloud-storage>=2.3.0,<3.0.0',
 'google>=3.0.0,<4.0.0',
 'numpy>=1.22.3,<2.0.0',
 'pandas>=1.4.2,<2.0.0',
 'psycopg2-binary>=2.9.3,<3.0.0',
 'pyproject-toml>=0.0.11,<0.0.12',
 'python-dotenv>=0.20.0,<0.21.0',
 'snowflake-connector-python==2.7.1',
 'sqlalchemy-redshift>=0.8.9,<0.9.0',
 'sqlalchemy>=1.4,<2.0',
 'sqlparse>=0.4.2,<0.5.0']

setup_kwargs = {
    'name': 'rcd-dev-kit',
    'version': '0.0.13',
    'description': 'Interact with OIP ecosystem.',
    'long_description': "# rcd_dev_kit\n### Developed by Real Consulting Data\n\n## Description\nWe've developed `rcd-dev-kit` to facilitate the manipulation and interaction with the OIP ecosystem.\n\n## Installation\n```bash\npip install rcd-dev-kit\n```\n\n## Modules\nWe've divided our functions in four main modules:\n- [database_manager](./src/rcd_dev_kit/database_manager)\n    - GcloudOperator()\n    - MysqlOperator()\n    - ElasticsearchOperator()\n    - RedshiftOperator()\n    - SnowflakeOperator()\n    - S3Operator()\n    - index_json_bulk()\n    - index_json()\n    - index_json_bulk_parallel()\n    - send_to_redshift()\n    - read_from_redshift()\n    - send_metadata_to_redshift()\n    - find_tables_by_column_name()\n    - migrate_metadata_from_redshift()\n    - upload_raw_s3()\n    - download_raw_s3()\n    - upload_to_gcloud()\n    - download_from_gcloud()\n\n- [dataclass_manager](./src/rcd_dev_kit/dataclass_manager)\n    - RawDataFile()\n\n- [decorator_manager](./src/rcd_dev_kit/decorator_manager)\n    - timeit()\n    - debug()\n\n- [file_manager](./src/rcd_dev_kit/file_manager)\n    - FileOperator()\n    - detect_path()\n    - detect_all_files()\n    - write_df_to_json_parallel()\n\n- [pandas_manager](./src/rcd_dev_kit/pandas_manager)\n    - strip_all_text_column()\n    - check_na()\n    - check_duplication()\n    - check_quality_table_names()\n    - normalize_date_column()\n    - detect_aws_type()\n\n- [sql_utils](./src/rcd_dev_kit/sql_utils)\n\n## Pre-requirements\nSince some of the functions deal with database connections(S3, Redshift, Snowflake, GCP, Elasticsearch, ...), we must\nbe careful to sensitive information. Thus, to use the functions correctly we must have a `.env` file following\nthe `.env.example` template.\n\n## Feedback\nAny questions or suggestions?\nPlease contact package maintainer.\n\n# python-sdk\nRefer to book https://py-pkgs.org/01-introduction for best practices\n\n# Maintainers\nThis package is using poetry for pkg management, it must be installed locally if you are maintaining the package.  \nFor developing and test the pkg locally, you must run `poetry install`.\n\nAfter all modifications have been developed, the new version can be published with the following commands:\n\nBuild Package: `poetry build`\n\nPublish Package: `poetry publish`\n\n## Contributing\nInterested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.\n\n## License\n`rcd_dev_kit` was created by RCD. It is licensed under the terms of the MIT license.\n\n## Credits\n`rcd_dev_kit` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).",
    'author': 'Davi FACANHA',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/OpenInnovationProgram/rcd-dev-kit',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
