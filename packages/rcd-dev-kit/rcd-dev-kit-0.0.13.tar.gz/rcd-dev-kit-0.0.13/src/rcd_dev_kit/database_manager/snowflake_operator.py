from typing import List, Optional
from .redshift_operator import RedshiftOperator
from .s3_operator import S3Operator
from ..sql_utils import convert_to_snowflake_syntax, correct_sql_system_variables_syntax
import pandas as pd
import snowflake.connector
import sqlparse
import os
import re


def migrate_data_from_redshift(rs_source_schema: str,
                               sn_target_schema: str,
                               exclude_tables: List[str],
                               bucket: Optional[str]):
    """
    If we want to migrate the data itself from Redshift into Snowflake, there is a SQL method on Snowflake
    to copy the tables directly from S3 into Snowflake.
    :param rs_source_schema(str): Source schema name in Redshift.
    :param sn_target_schema(str): Source schema name in Snowflake.
    :param exclude_tables(List[str]): Tables to be excluded when migrating the data.
    :param bucket(Optional[str]): Bucket name in S3. If none is passed, it will take the bucket name from
                                  the environment variable S3_BUCKET_DATAMART.
    :return:
    """
    so = S3Operator()
    so.bucket = os.environ.get("S3_BUCKET_DATAMART") if bucket is None else bucket
    so.prefix = f"{rs_source_schema}/"

    if so.detect_prefix():
        list_obj = so.list_s3_obj()
        list_tables = [obj.split("/")[-1].split(".")[0] for obj in list_obj if
                       ((len(obj.split("/")[-1]) > 0) and (obj.split(".")[-1] == "csv"))]
    else:
        raise ValueError(f'❌ The chosen schema {so.prefix} does not exist in S3!')

    list_tables = list(set(list_tables).difference(exclude_tables)) if exclude_tables is not None else list_tables

    # We first migrate the metadata in order to create the tables with all the columns and its descriptions.
    # Only after we are sure all the tables were created in snowflake, we can migrate the data itself from s3
    # to the snowflake tables.
    migrate_metadata_from_redshift(rs_db="oip",
                                   sf_db="oip",
                                   schemas_list=[rs_source_schema],
                                   create_tables=True,
                                   tables_list=list_tables,
                                   not_include=[],
                                   schema_migration_dict={rs_source_schema: sn_target_schema})

    sf = SnowflakeOperator()
    for table in list_tables:
        sf.copy_from_S3(rs_source_schema, f"{table}.csv", "oip", "emea_sales", table)

    sf.conn.cursor().close()
    sf.conn.close()
    print("✅ Process finished successfully!")


def migrate_metadata_from_redshift(rs_db: str,
                                   sf_db: str,
                                   schemas_list: List[str] = [],
                                   tables_list: List[str] = [],
                                   create_tables: bool = False,
                                   logging: bool = True,
                                   verbose: bool = True,
                                   not_include: Optional[List[str]] = None,
                                   schema_migration_dict: Optional[dict] = None):
    """
    Airbyte is our main tool for Data Migration. However, it is responsible only for the data migration, not metadata.
    This function aims, therefore, to retrieve all the DDL Queries on Redshift and replicate then in Snowflake.
    :param rs_db(str): Redshift database name.
    :param sf_db(str): Snowflake database name.
    :param schemas_list(List[str]): List of schemas to be migrated.
    :param tables_list(List[str]): List of tables to be migrated.
    :param create_tables(bool): If the tables being migrated don't exist beforehand, they must be created.
    :param logging(bool): Since SQL Syntax errors can be pretty hard to understand and debug, we can set logging
                          to True in order to have the problematic queries written down into the query_log_errors.txt
                          file.
    :param verbose(bool): See all the DDL Queries being read from the redshift tables.
    :param not_include(Optional[List[str]]): List of schemas not to be included.
    :param schema_migration_dict(Optional[dict]): If the migration happens to be between schemas with different names,
                                                  we can set this config as a dictionary.
                                                  - For example:
                                                        If we want to migrate the metadata from schema1 in Redshift
                                                        into schema2 in Snowflake, we can set this relation as:
                                                        >>> schema_migration_dict = {schema1: schema2}.
    :return:
    """
    print("🦆 Starting the metadata migration process | Redshift -> Snowflake")
    ro = RedshiftOperator(database=rs_db)
    ddl_model = ro.get_DDL(verbose=verbose,
                           schema_names=schemas_list,
                           table_names=tables_list,
                           not_include=not_include)
    ddl_model.fillna("", inplace=True)

    if schemas_list:
        ddl_model = ddl_model[ddl_model.schema_name.isin(schemas_list)]
    if tables_list:
        ddl_model = ddl_model[ddl_model.table_name.isin(tables_list)]

    print("❄️ Connecting to Snowflake...")
    sf = SnowflakeOperator(snowflake_database=sf_db.upper())
    print("Done!")

    if schema_migration_dict is not None:
        ddl_model.replace(schema_migration_dict, regex=True, inplace=True)

    if logging:
        if os.path.exists("query_log_errors.txt"):
            os.remove("query_log_errors.txt")

    if create_tables:
        print("🖼 Creating tables if they don't already exist...")
        # Some of these corrections below must be done because 'year', 'level', 'region', 'names' are SQL Syntax Names
        # and AWS parse them as strings when creating the column names. However, Snowflake parses it otherwise because
        # it can distinguish the column names and the SQL Variables as different things.
        ddl_model["create_query"] = correct_sql_system_variables_syntax(ddl_model, "create_query")
        sf.execute_metadata_query(ddl_model.create_query.values, logging=logging, correct_syntax=True)

    print("🏷 Migrating Table Descriptions...")
    sf.execute_metadata_query(ddl_model.table_description.values, logging=logging)

    print("🏷 Migrating Columns Descriptions...")
    ddl_model["columns_description"] = correct_sql_system_variables_syntax(ddl_model, "columns_description")
    sf.execute_metadata_query(ddl_model.columns_description.values, logging=logging)

    print("🔑 Migrating Primary Keys...")
    sf.execute_key_query(ddl_model, key="primary", logging=logging)

    print("🔑 Migrating Unique Keys...")
    sf.execute_key_query(ddl_model, key="unique", logging=logging)

    print("🔑 Migrating Foreign Keys...")
    sf.execute_metadata_query(ddl_model.foreign_keys.values, logging=logging)

    sf.conn.cursor().close()
    sf.conn.close()
    print("✅ All metadata have been migrated successfully !")


class SnowflakeOperator:
    def __init__(self,
                 snowflake_user=None,
                 snowflake_password=None,
                 snowflake_account=None,
                 snowflake_warehouse=None,
                 snowflake_role=None,
                 snowflake_database=None) -> None:

        self.snowflake_user = (
            os.environ.get("SNOWFLAKE_USER")
            if snowflake_user is None
            else snowflake_user.upper()
        )
        self.snowflake_password = (
            os.environ.get("SNOWFLAKE_PASSWORD")
            if snowflake_password is None
            else snowflake_password
        )
        self.snowflake_account = (
            os.environ.get("SNOWFLAKE_ACCOUNT")
            if snowflake_account is None
            else snowflake_account.upper()
        )
        self.snowflake_warehouse = (
            os.environ.get("SNOWFLAKE_WAREHOUSE")
            if snowflake_warehouse is None
            else snowflake_warehouse.upper()
        )
        self.snowflake_role = (
            os.environ.get("SNOWFLAKE_ROLE")
            if snowflake_role is None
            else snowflake_role.upper()
        )
        self.snowflake_database = (
            os.environ.get("SNOWFLAKE_DATABASE")
            if snowflake_database is None
            else snowflake_database.upper()
        )

        self.conn = snowflake.connector.connect(
            user=self.snowflake_user,
            password=self.snowflake_password,
            account=self.snowflake_account,
            warehouse=self.snowflake_warehouse,
            role=self.snowflake_role,
            database=self.snowflake_database,
        )

    def truncate(self, database, schema, table):
        sql = f"truncate table {database}.{schema}.{table} ;"
        self.conn.cursor().execute(sql)

    def copy_from_S3(self, s3_prefix, s3_file, database, schema, table):
        """
        The Snowflake SGBD has a SQL Command dedicated to copy tables directly from S3 into a schema.

        :param s3_prefix: Object prefix in s3.
        :param s3_file: Table name in s3.
        :param database: Database name in Snowflake.
        :param schema: Schema name in Snowflake.
        :param table: Table name in Snowflake.
        :return:
        """
        self.conn.cursor().execute(
            f"""
            COPY INTO {database.upper()}.{schema.upper()}.{table.upper()} 
            FROM s3://{os.environ.get("S3_DATAMART_BUCKET")}/{s3_prefix.lower()}/{s3_file.lower()}
            CREDENTIALS = (
            aws_key_id='{os.environ.get("AWS_ACCESS_KEY_ID")}',
            aws_secret_key='{os.environ.get("AWS_SECRET_ACCESS_KEY")}'
            )
            FILE_FORMAT=(field_delimiter='|', SKIP_HEADER=1, FIELD_OPTIONALLY_ENCLOSED_BY='"', NULL_IF=(''))
            FORCE = TRUE
            ON_ERROR = 'skip_file';
            """
        )

    def correct_syntax(self, query: str, no_comments: bool = False) -> str:
        """
        Snowflake has a specific SQL syntax. If we get a SQL from another SGBD, we must firstly
        correct the syntax into the snowflake constraints.

        Args:
            query: String containing the SQL script.
            no_comments: If we want to keep the SQL comments as well or not. Recommended keeping as false.

        Returns: The same query but snowflake-compatible.
        """
        return convert_to_snowflake_syntax(query, no_comments)

    def execute_metadata_query(self, query: List[str], logging: bool = False, correct_syntax=False):
        """

        :param query:
        :param logging:
        :param correct_syntax:
        :return:
        """
        # The snowflake python API allows only one command per request. That's why we must split the input query into
        # a list of commands.
        # Also, snowflake has a specific SQL syntax. If we get a SQL from another database manager, we must firstly
        # correct the syntax into the snowflake constraints.
        if correct_syntax:
            queries_list = "".join(self.correct_syntax(command) for command in query if not re.match(r"^\s*$", command))
        else:
            queries_list = "".join(command for command in query if not re.match(r"^\s*$", command))
        queries_list = sqlparse.split(queries_list)

        for command in queries_list:
            try:
                self.conn.cursor().execute(f"{command.strip()};")
            except snowflake.connector.errors.ProgrammingError as e:
                if ("does not exist or not authorized" not in str(e)) or ("Empty SQL statement" not in str(e)):
                    if logging:
                        print(f"Problem found. Skipping command. Check the query_log_errors.txt for more details.")
                        log_file = open("query_log_errors.txt", "a+")
                        log_file.write(f"{command}\n")
                        print(e)
                        log_file.close()
                    else:
                        print(f"Problem found. Skipping command...")

    def execute_key_query(self, df: pd.DataFrame, key: str = "primary", logging: bool = False):
        for row in range(df.__len__()):
            if key == "primary":
                if df.iloc[row, 2] != "":
                    drop_key_query = f"ALTER TABLE {df.iloc[row, 0]}.{df.iloc[row, 1]} DROP PRIMARY KEY;"
                    key_query = f"ALTER TABLE {df.iloc[row, 0]}.{df.iloc[row, 1]} ADD PRIMARY KEY ({df.iloc[row, 2]});"
                    skip = False
                else:
                    skip = True

            elif key == "unique":
                if (df.iloc[row, 3] != "") and (df.iloc[row, 3] != df.iloc[row, 2]):
                    drop_key_query = f"ALTER TABLE {df.iloc[row, 0]}.{df.iloc[row, 1]} DROP UNIQUE ({df.iloc[row, 3]});"
                    key_query = f"ALTER TABLE {df.iloc[row, 0]}.{df.iloc[row, 1]} ADD UNIQUE ({df.iloc[row, 3]});"
                    skip = False
                else:
                    skip = True

            if not skip:
                try:
                    self.conn.cursor().execute(key_query)
                except snowflake.connector.errors.ProgrammingError as e:
                    if "already exists" in str(e):
                        self.conn.cursor().execute(drop_key_query)
                        self.conn.cursor().execute(key_query)
                    else:
                        if ("does not exist or not authorized" not in str(e)) or ("Empty SQL statement" not in str(e)):
                            if logging:
                                print(f"Problem found. Skipping command. "
                                      f"Check the query_log_errors.txt for more details.")
                                log_file = open("query_log_errors.txt", "a+")
                                log_file.write(f"{key_query}\n")
                                print(e)
                                log_file.close()
                            else:
                                print(f"Problem found. Skipping command...")
