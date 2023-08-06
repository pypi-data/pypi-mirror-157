# rcd_dev_kit
### Developed by Real Consulting Data

## Description
We've developed `rcd-dev-kit` to facilitate the manipulation and interaction with the OIP ecosystem.

## Installation
```bash
pip install rcd-dev-kit
```

## Modules
We've divided our functions in four main modules:
- [database_manager](./src/rcd_dev_kit/database_manager)
    - GcloudOperator()
    - MysqlOperator()
    - ElasticsearchOperator()
    - RedshiftOperator()
    - SnowflakeOperator()
    - S3Operator()
    - index_json_bulk()
    - index_json()
    - index_json_bulk_parallel()
    - send_to_redshift()
    - read_from_redshift()
    - send_metadata_to_redshift()
    - find_tables_by_column_name()
    - migrate_metadata_from_redshift()
    - upload_raw_s3()
    - download_raw_s3()
    - upload_to_gcloud()
    - download_from_gcloud()

- [dataclass_manager](./src/rcd_dev_kit/dataclass_manager)
    - RawDataFile()

- [decorator_manager](./src/rcd_dev_kit/decorator_manager)
    - timeit()
    - debug()

- [file_manager](./src/rcd_dev_kit/file_manager)
    - FileOperator()
    - detect_path()
    - detect_all_files()
    - write_df_to_json_parallel()

- [pandas_manager](./src/rcd_dev_kit/pandas_manager)
    - strip_all_text_column()
    - check_na()
    - check_duplication()
    - check_quality_table_names()
    - normalize_date_column()
    - detect_aws_type()

- [sql_utils](./src/rcd_dev_kit/sql_utils)

## Pre-requirements
Since some of the functions deal with database connections(S3, Redshift, Snowflake, GCP, Elasticsearch, ...), we must
be careful to sensitive information. Thus, to use the functions correctly we must have a `.env` file following
the `.env.example` template.

## Feedback
Any questions or suggestions?
Please contact package maintainer.

# python-sdk
Refer to book https://py-pkgs.org/01-introduction for best practices

# Maintainers
This package is using poetry for pkg management, it must be installed locally if you are maintaining the package.  
For developing and test the pkg locally, you must run `poetry install`.

After all modifications have been developed, the new version can be published with the following commands:

Build Package: `poetry build`

Publish Package: `poetry publish`

## Contributing
Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License
`rcd_dev_kit` was created by RCD. It is licensed under the terms of the MIT license.

## Credits
`rcd_dev_kit` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).