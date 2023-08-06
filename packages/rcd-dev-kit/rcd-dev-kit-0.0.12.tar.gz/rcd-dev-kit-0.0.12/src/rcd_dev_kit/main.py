from typing import List, Optional

import pandas as pd
from dotenv import load_dotenv, find_dotenv
import os

from rcd_dev_kit.database_manager.s3_operator import S3Operator
from rcd_dev_kit.database_manager.redshift_operator import RedshiftOperator, send_to_redshift, \
    send_metadata_to_redshift, find_tables_by_column_name, read_from_redshift
from rcd_dev_kit.database_manager.snowflake_operator import SnowflakeOperator
from sqlalchemy import text

from sqlalchemy.engine.default import DefaultDialect
import sqlalchemy
import snowflake.connector
import sqlparse
import re
import json


def migrate_metadata_from_redshift(
        rs_db: str,
        sf_db: str,
        schemas_list: List = [],
        tables_list: List = [],
        create_tables: bool = False,
        logging: bool = True,
        verbose: bool = True,
        not_include: Optional = None,
        schema_migration_dict: Optional[dict] = None
):
    print("Starting the metadata migration process | Redshift -> Snowflake")
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

    print("Connecting to Snowflake...")
    sf = SnowflakeOperator(snowflake_database=sf_db.upper())
    print("Done!")

    if schema_migration_dict is not None:
        ddl_model.replace(schema_migration_dict, regex=True, inplace=True)

    if logging:
        if os.path.exists("query_log_errors.txt"):
            os.remove("query_log_errors.txt")

    if create_tables:
        print("Creating tables if they don't already exist...")
        # Some of these corrections below must be done because 'year', 'level', 'region', 'names' are SQL Syntax Names
        # and AWS parse them as strings when creating the column names. However, Snowflake parses it otherwise because
        # it can distinguish the column names and the SQL Variables as different things.
        ddl_model.create_query = ddl_model.create_query.str.replace('"year"', "year ").str.replace('"level" ', "level ") \
            .str.replace('"region" ', "region ") \
            .str.replace('"names" ', "names ") \
            .str.replace('"type" ', "type ") \
            .str.replace('"role" ', "role ") \
            .str.replace('"provider" ', "provider ") \
            .str.replace('"location" ', "location ")
        sf.execute_metadata_query(ddl_model.create_query.values, logging=logging, correct_syntax=True)

    print("Migrating Table Descriptions...")
    sf.execute_metadata_query(ddl_model.table_description.values, logging=logging)

    print("Migrating Columns Descriptions...")
    ddl_model.columns_description = ddl_model.columns_description.str.replace('."year"', ".year") \
        .str.replace('."level"', ".level") \
        .str.replace('."region"', ".region") \
        .str.replace('."names"', ".names") \
        .str.replace('."type"', ".type") \
        .str.replace('."role"', ".role") \
        .str.replace('."provider"', ".provider") \
        .str.replace('."location"', ".location ")
    sf.execute_metadata_query(ddl_model.columns_description.values, logging=logging)

    print("Migrating Primary Keys...")
    sf.execute_key_query(ddl_model, key="primary", logging=logging)

    print("Migrating Unique Keys...")
    sf.execute_key_query(ddl_model, key="unique", logging=logging)

    print("Migrating Foreign Keys...")
    sf.execute_metadata_query(ddl_model.foreign_keys.values, logging=logging)

    sf.conn.cursor().close()
    sf.conn.close()
    print("✅ All metadata have been migrated successfully !")


def test_sf_operator():
    load_dotenv(find_dotenv())

    so = S3Operator()
    s3 = so.s3.Bucket('oip-openinnovationprogram-datamart')
    [obj.key for obj in s3.objects.all() if obj.key.endswith('csv')]  # .filter(Prefix="emea_customer/")

    so.bucket = os.environ.get("S3_BUCKET_DATAMART")
    so.prefix = "pv_intermediary_tables/"

    so.detect_prefix()
    list_obj = so.list_s3_obj()
    list_tables = [obj.split("/")[-1].split(".")[0] for obj in list_obj if
                   ((len(obj.split("/")[-1]) > 0) and (obj.split(".")[-1] == "csv"))]

    migrate_metadata_from_redshift(rs_db="oip",
                                   sf_db="oip",
                                   schemas_list=["pv_intermediary_tables"],
                                   create_tables=True,
                                   not_include=[],
                                   schema_migration_dict={"pv_intermediary_tables": "emea_sales"})

    sf = SnowflakeOperator()
    for table in list_tables:
        sf.copy_from_S3("pv_intermediary_tables", f"{table}.csv", "OIP", "emea_sales".upper(), table)
    print("finished")


def test_rs_operator():
    load_dotenv(find_dotenv())

    ro = RedshiftOperator(database="oip")
    ddl_model = ro.get_DDL(verbose=True, not_include=["platform", "pg_catalog", "information_schema"])

    ddl_model.table_description.values[0]

    send_to_redshift(database="staging", schema="test_schema", table="ddl_model", df=ddl_model, check=False)


def test_function_columns_desc():
    load_dotenv(find_dotenv())
    send_metadata_to_redshift(database="staging", file_path="./table_metadata.json")


def test_tables_checkup():
    load_dotenv(find_dotenv())

    ro = RedshiftOperator(database="oip")
    ddl_model = ro.get_DDL(verbose=True)

    schemas_list = ['emea_environment', 'emea_customer', 'emea_sales',
                    'amer_environment', 'amer_customer', 'amer_sales',
                    'apac_environment', 'apac_customer', 'apac_sales',
                    'reference', 'pv_reference',
                    'latam_environment',
                    'global_environment',
                    'pv_intermediary_tables']

    so = S3Operator()
    s3 = so.s3.Bucket('oip-openinnovationprogram-datamart')

    objs_list_list = []
    for schema in schemas_list:
        objs_list_list.append(obj.key for obj in s3.objects.filter(Prefix=f"{schema}/") if
                              obj.key.endswith('csv'))  # .filter(Prefix="emea_customer/")
    objs_list = [x for xx in objs_list_list for x in xx]

    for obj in objs_list:
        table_name = obj.split("/")[-1].split(".")[0]
        if len(ddl_model[ddl_model["table_name"] == table_name]) == 0:
            print(obj)


def test_list_comments():
    load_dotenv(find_dotenv())
    df__by_column = find_tables_by_column_name(database="oip", column_name="index_id", verbose=False)

    ro = RedshiftOperator(database="oip")
    ddl_model = ro.get_DDL(verbose=True)
    ro.conn.close()

    col_name = "id"

    df_filtered = ddl_model[ddl_model.create_query.str.contains(f'[\s,"]{col_name}[\s"]')]

    opa = df_filtered["create_query"].values
    schema_names_lst = df_filtered["schema_name"].values
    table_names_lst = df_filtered["table_name"].values
    columns_description = df_filtered["columns_description"].apply(lambda x:
                                                                   re.findall(f"\\.{col_name} IS '(.*)';", x)[0] if
                                                                   len(re.findall(f"\\.{col_name} IS '(.*)';", x)) > 0
                                                                   else "").values

    # for value in columns_description:
    #     print(value)
    #     print("\n")

    data = {'opa': opa, 'schema_name': schema_names_lst, 'table_name': table_names_lst, 'column_name': col_name,
            "column_description": columns_description}
    df = pd.DataFrame(data=data)


def main():
    load_dotenv(find_dotenv())

    ro = RedshiftOperator(database="oip")
    ddl_model = ro.get_DDL(verbose=True)

    query = open('/opt/project/rcd_pyutils/database_manager/v_generate_tbl_ddl.sql', 'r').read().replace("%", "%%")

    result = ro.conn.execution_options(autocommit=True).execute(sqlalchemy.text(query))
    result.close()

    print(f"🥳Table is copied to redshift from S3.\n")

    # query = f"select * " \
    #        f"from admin.v_generate_tbl_ddl " \
    #        f"where tablename='fr__definition_disorder__orphanet' and schemaname='reference';"

    query = f"select * " \
            f"from admin.v_generate_tbl_ddl"

    try:
        query = f"select * " \
                f"from admin.v_generate_tbl_ddl"

        ro = RedshiftOperator(database="oip")
        result = ro.conn.execute(sqlalchemy.text(query)).all()
        ro.conn.close()
        schema_names = list(set([record.schemaname for record in result]))

        # #result = ro.conn.execute(sqlalchemy.text(query)).all()
        # dfs = []
        # verbose = True
        # schema_names = None
        # table_names = None
        #
        # if not schema_names:
        #     schema_names = list(set([record.schemaname for record in result]))
        #
        # for schema in set(schema_names).difference(['pv_reference', 'platform', 'pv_intermediary_tables', 'pg_catalog', 'information_schema']):
        #     if verbose:
        #         print(schema)
        #     if not table_names:
        #         table_names = list(set([record.tablename for record in result if record.schemaname == schema]))
        #     for table in table_names:
        #         if verbose:
        #             print(f" - {table}")
        #         corrected_query = ""
        #         for record in result:
        #             if (record.schemaname == schema) and (record.tablename == table):
        #                 line = record.ddl.replace(" ", " ").replace("\'\"", "'").replace("\"\'", "'")
        #                 corrected_query += f"{line}"
        #         corrected_query = corrected_query.replace('\";\"', "semicolon").split(";")
        #
        #         create_sql = ";\n".join(statement.strip() for statement in corrected_query if "CREATE TABLE IF NOT EXISTS".lower() in statement.lower())
        #         comment_table_sql = ";\n".join(statement.strip() for statement in corrected_query if "COMMENT ON table".lower() in statement.lower())
        #         comment_columns_sql = ";\n".join([statement.strip() for statement in corrected_query if "COMMENT ON column".lower() in statement.lower()])
        #         foreign_key_sql = ";\n".join([statement.strip() for statement in corrected_query if "FOREIGN KEY".lower() in statement.lower()])
        #
        #         df = pd.DataFrame({"schema_name": schema,
        #                            "table_name": table,
        #                            "create_query": create_sql,
        #                            "table_description": comment_table_sql,
        #                            "columns_description": comment_columns_sql,
        #                            "foreign_keys": foreign_key_sql}, index=[1])
        #         dfs.append(df)
        #
        # print("DDL Data Model generated.")
        # ddl_model = pd.concat(dfs, ignore_index=True)

        verbose = True
        dfs = []
        for schema in set(schema_names).difference(
                ['pv_reference', 'platform', 'pv_intermediary_tables', 'pg_catalog', 'information_schema']):
            if verbose:
                print(schema)
            table_names = list(set([record.tablename for record in result if record.schemaname == schema]))
            # for table in table_names:
            for table in ['be__retail_patient__atc4__inami']:
                if verbose:
                    print(f" - {table}")
                corrected_query = ""
                for record in result:
                    if (record.schemaname == schema) and (record.tablename == table):
                        # line = record.ddl.replace(" ", " ").replace("\'\"", "'").replace("\"\'", "'")
                        # line = record.ddl.replace(" ", " ").replace("\'\"", "__aux__").replace("\"\'", "__aux__").replace("'", "\\'").replace("__aux__", "'")
                        line = record.ddl.replace(" ", " ").replace("\'\"", "'").replace("\"\'", "'").replace("\"\"",
                                                                                                              '"')
                        if line.count("'") > 2:
                            line = "'".join([line.split("'")[0], "''".join(line.split("'")[1:-1]), line.split("'")[-1]])
                        corrected_query += f"{line}\n"

                corrected_query = corrected_query.replace(".year ", '."year" ').replace(".level ", '."level" ') \
                    .replace(".region ", '."region" ').replace(".names ", '."names" ').replace(".type ", '."type" ') \
                    .replace(".role ", '."role" ').replace(".provider ", '."provider" ').replace(".location ",
                                                                                                 '."location" ')
                corrected_query = sqlparse.split(corrected_query)

                create_sql = "".join([statement for statement in corrected_query if
                                      "CREATE TABLE IF NOT EXISTS".lower() in statement.lower()])
                create_sql = ";\n".join(create_sql.split(";\n")[1:])
                primary_key = re.findall(",PRIMARY KEY \((\w+)\)", create_sql)[-1] if len(
                    re.findall(",PRIMARY KEY \((\w+)\)", create_sql)) > 0 else ""
                comment_table_sql = "".join(
                    [statement for statement in corrected_query if "COMMENT ON table".lower() in statement.lower()])
                comment_columns_sql = "\n".join(
                    [statement for statement in corrected_query if "COMMENT ON column".lower() in statement.lower()])
                foreign_key_sql = "\n".join(
                    [statement for statement in corrected_query if "FOREIGN KEY".lower() in statement.lower()])

                # Check if the column names agree with the SQL standards. It must not have accented letters or any special character.
                # For some reason, when we retrieve the DDL from Redshift, it gives the CREATE TABLE Sql correctly but not
                # the COMMENT ON Sql script. Whenever a column name has a non-ASCII name, we must parse it as string (under quotes).
                # This script down below corrects the COMMENT ON string with the quotes notation.
                sql_columns = re.findall("\n\t[,]*\"([.\S]+)\"\s+", create_sql)
                string_check = re.compile('[@\-!#$%^&*+()<>?/\|}{~:]')
                for var in sql_columns:
                    if not var.isascii() or (string_check.search(var) is not None):
                        comment_columns_sql = comment_columns_sql.replace(f".{var} IS", f'."{var}" IS')

                teste = f'CREATE TABLE IF NOT EXISTS emea_environment.fr__drug_directory\n(\n\tcip13_code VARCHAR(1000) NOT NULL  ENCODE lzo\n\t,cis_code+++ VARCHAR(1000)   ENCODE lzo\n\t,cis-label VARCHAR(1000)   ENCODE lzo\n\t,presentation_label VARCHAR(1000)   ENCODE lzo\n\t,brand VARCHAR(1000)   ENCODE lzo\n\t,brand_regroup VARCHAR(1000)   ENCODE lzo\n\t,owner_regroup VARCHAR(1000)   ENCODE lzo\n\t,atc5_code VARCHAR(1000)   ENCODE lzo\n\t,atc4_code VARCHAR(1000)   ENCODE lzo\n\t,atc3_code VARCHAR(1000)   ENCODE lzo\n\t,atc2_code VARCHAR(1000)   ENCODE lzo\n\t,atc1_code VARCHAR(1000)   ENCODE lzo\n\t,atc5_french_label VARCHAR(1000)   ENCODE lzo\n\t,atc4_french_label VARCHAR(1000)   ENCODE lzo\n\t,atc3_french_label VARCHAR(1000)   ENCODE lzo\n\t,atc2_french_label VARCHAR(1000)   ENCODE lzo\n\t,atc1_french_label VARCHAR(1000)   ENCODE lzo\n\t,atc5_english_label VARCHAR(1000)   ENCODE lzo\n\t,atc4_english_label VARCHAR(1000)   ENCODE lzo\n\t,atc3_english_label VARCHAR(1000)   ENCODE lzo\n\t,atc2_english_label VARCHAR(1000)   ENCODE lzo\n\t,atc1_english_label VARCHAR(1000)   ENCODE lzo\n\t,generic_type_code VARCHAR(1000)   ENCODE lzo\n\t,generic_type_label VARCHAR(1000)   ENCODE lzo\n\t,is_retail VARCHAR(1000)   ENCODE lzo\n\t,is_hospital VARCHAR(1000)   ENCODE lzo\n\t,is_brand VARCHAR(1000)   ENCODE lzo\n\t,PRIMARY KEY (cip13_code)\n)\nDISTSTYLE AUTO\n DISTKEY (cip13_code)\n;'
                teste = f'CREATE TABLE IF NOT EXISTS emea_environment.fr__medical_devices__region__yearly__sniiram\n(\n\tcode_lpp VARCHAR(259) NOT NULL  ENCODE lzo\n\t,label_lpp VARCHAR(259)   ENCODE lzo\n\t,categorie VARCHAR(259)   ENCODE lzo\n\t,label_categorie VARCHAR(259)   ENCODE lzo\n\t,sous_categorie_1 VARCHAR(259)   ENCODE lzo\n\t,label_sous_categorie_1 VARCHAR(259)   ENCODE lzo\n\t,sous_categorie_2 VARCHAR(259)   ENCODE lzo\n\t,label_sous_categorie_2 VARCHAR(259)   ENCODE lzo\n\t,label_region VARCHAR(259)   ENCODE lzo\n\t,periode VARCHAR(259)   ENCODE lzo\n\t,nombre_de_beneficiaires DOUBLE PRECISION   ENCODE RAW\n\t,"montant_remboursé" DOUBLE PRECISION   ENCODE RAW\n\t,base_de_remboursement DOUBLE PRECISION   ENCODE RAW\n\t,"quantité_rembousée" DOUBLE PRECISION   ENCODE RAW\n)\nDISTSTYLE AUTO\n DISTKEY (code_lpp)\n;'
                teste = f'CREATE TABLE IF NOT EXISTS emea_sales.be__retail_patient__atc4__inami\r\n(\r\n\tregistry_year VARCHAR(259)   ENCODE RAW\r\n\t,atc4_code VARCHAR(255) NOT NULL  ENCODE RAW\r\n\t,\"atc4-en\" VARCHAR(258)   ENCODE RAW\r\n\t,\"atc4_reimbursed-inami\" DOUBLE PRECISION   ENCODE RAW\r\n\t,\"atc4_reimbursed-patient\" DOUBLE PRECISION   ENCODE RAW\r\n\t,\"atc4_reimbursed-total\" DOUBLE PRECISION   ENCODE RAW\r\n\t,atc4_unit DOUBLE PRECISION   ENCODE RAW\r\n\t,atc4_patient DOUBLE PRECISION   ENCODE RAW\r\n\t,atc3_code VARCHAR(255)   ENCODE RAW\r\n\t,atc3_en VARCHAR(258)   ENCODE RAW\r\n\t,\"atc3_reimbursed-inami\" DOUBLE PRECISION   ENCODE RAW\r\n\t,\"atc3_reimbursed-patient\" DOUBLE PRECISION   ENCODE RAW\r\n\t,\"atc3_reimbursed-total\" DOUBLE PRECISION   ENCODE RAW\r\n\t,atc3_unit DOUBLE PRECISION   ENCODE RAW\r\n\t,atc3_ddd DOUBLE PRECISION   ENCODE RAW\r\n\t,atc3_patient DOUBLE PRECISION   ENCODE RAW\r\n\t,atc2_code VARCHAR(255)   ENCODE RAW\r\n\t,\"atc2-en\" VARCHAR(258)   ENCODE RAW\r\n\t,\"atc2_reimbursed-inami\" DOUBLE PRECISION   ENCODE RAW\r\n\t,\"atc2_reimbursed-patient\" DOUBLE PRECISION   ENCODE RAW\r\n\t,\"atc2_reimbursed-total\" DOUBLE PRECISION   ENCODE RAW\r\n\t,atc2_unit DOUBLE PRECISION   ENCODE RAW\r\n\t,atc2_ddd DOUBLE PRECISION   ENCODE RAW\r\n\t,atc2_patient DOUBLE PRECISION   ENCODE RAW\r\n\t,atc1_code VARCHAR(255)   ENCODE RAW\r\n\t,atc1_en VARCHAR(258)   ENCODE RAW\r\n\t,\"atc1_reimbursed-inami\" DOUBLE PRECISION   ENCODE RAW\r\n\t,\"atc1_reimbursed-patient\" DOUBLE PRECISION   ENCODE RAW\r\n\t,\"atc1_reimbursed-total\" DOUBLE PRECISION   ENCODE RAW\r\n\t,atc1_unit DOUBLE PRECISION   ENCODE RAW\r\n\t,atc1_ddd DOUBLE PRECISION   ENCODE RAW\r\n\t,atc1_patient DOUBLE PRECISION   ENCODE RAW\r\n\t,atc4_ddd DOUBLE PRECISION   ENCODE RAW\r\n\t,\"atc3_reimbursed-inami-avg\" DOUBLE PRECISION   ENCODE RAW\r\n\t,\"atc3_reimbursed-patient-avg\" DOUBLE PRECISION   ENCODE RAW\r\n\t,\"atc3_reimbursed-total-avg\" DOUBLE PRECISION   ENCODE RAW\r\n\t,\"atc3_unit-avg\" DOUBLE PRECISION   ENCODE RAW\r\n\t,\"atc3_ddd-avg\" DOUBLE PRECISION   ENCODE RAW\r\n\t,\"atc3_patient-avg\" DOUBLE PRECISION   ENCODE RAW\r\n\t,\"atc2_reimbursed-inami-avg\" DOUBLE PRECISION   ENCODE RAW\r\n\t,\"atc2_reimbursed-patient-avg\" DOUBLE PRECISION   ENCODE RAW\r\n\t,\"atc2_reimbursed-total-avg\" DOUBLE PRECISION   ENCODE RAW\r\n\t,\"atc2_unit-avg\" DOUBLE PRECISION   ENCODE RAW\r\n\t,\"atc2_ddd-avg\" DOUBLE PRECISION   ENCODE RAW\r\n\t,\"atc2_patient-avg\" DOUBLE PRECISION   ENCODE RAW\r\n\t,\"atc1_reimbursed-inami-avg\" DOUBLE PRECISION   ENCODE RAW\r\n\t,\"atc1_reimbursed-patient-avg\" DOUBLE PRECISION   ENCODE RAW\r\n\t,\"atc1_reimbursed-total-avg\" DOUBLE PRECISION   ENCODE RAW\r\n\t,\"atc1_unit-avg\" DOUBLE PRECISION   ENCODE RAW\r\n\t,\"atc1_ddd-avg\" DOUBLE PRECISION   ENCODE RAW\r\n\t,\"atc1_patient-avg\" DOUBLE PRECISION   ENCODE RAW\r\n\t,PRIMARY KEY (atc4_code)\r\n)\r\nDISTSTYLE EVEN\r\n;'

                print(re.findall(",PRIMARY KEY \((\w+)\)", teste)[-1])

                sql_columns = re.findall("\n\t[,]*([.\S]+)\s+", teste)

                # Check if the column names agree with the SQL standards. It must not have accented letters or any special character.
                string_check = re.compile('[@\-!#$%^&*+()<>?/\|}{~:]')
                for col_name in sql_columns:
                    if not col_name.isascii() or (string_check.search(col_name) is not None):
                        teste = teste.replace(col_name, f'"{col_name}"')

                print(re.findall("\n\t,({\w*[@\-!#$%^&*+<>?/\|~:]+\w*}+)\s+", teste))

                print(re.findall("\n\t,({\w*[@\-!#$%^&*+()<>?/\|}{~:]+\w*}+)\s+", teste))

                string_check = re.compile('[@\-!#$%^&*+123456789()<>?/\|}{~:]')

                # create_sql = "".join([statement for statement in corrected_query if "CREATE TABLE IF NOT EXISTS".lower() in statement.lower()])
                # create_sql = re.sub("\s\s\s\s*", "\n\t", sqlparse.format(create_sql, reindent=True, keyword_case='upper', strip_comments=True, comma_first=True, wrap_after=1))
                #
                # comment_table_sql = "".join([statement for statement in corrected_query if "COMMENT ON table".lower() in statement.lower()])
                # comment_table_sql = re.sub("\s\s\s\s*", "\n\t", sqlparse.format(comment_table_sql, reindent=True, keyword_case='upper', strip_comments=True, comma_first=True, wrap_after=1))
                #
                # comment_columns_sql = "".join([statement for statement in corrected_query if "COMMENT ON column".lower() in statement.lower()])
                # comment_columns_sql = re.sub("\s\s\s\s*", "\n\t", sqlparse.format(comment_columns_sql, reindent=True, keyword_case='upper', strip_comments=True, comma_first=True, wrap_after=1))
                #
                # foreign_key_sql = "".join([statement for statement in corrected_query if "FOREIGN KEY".lower() in statement.lower()])
                # foreign_key_sql = re.sub("\s\s\s\s*", "\n\t", sqlparse.format(foreign_key_sql, reindent=True, keyword_case='upper', strip_comments=True, comma_first=True, wrap_after=1))
                df = pd.DataFrame({"schema_name": schema,
                                   "table_name": table,
                                   "create_query": create_sql,
                                   "table_description": comment_table_sql.strip(),
                                   "columns_description": comment_columns_sql.strip(),
                                   "foreign_keys": foreign_key_sql.strip()}, index=[1])
                dfs.append(df)

        print("Concatenating")
        ddl_model = pd.concat(dfs, ignore_index=True)

        print("Exporting model to file...")
        ddl_model.to_csv("/opt/project/rcd_pyutils/ddl_model.txt", sep="\t", encoding="utf-8", index=False)
        print("Finished!")

        ddl_model = pd.read_csv("/opt/project/rcd_pyutils/ddl_output/ddl_model.txt", sep="\t", encoding="utf-8")
        ctx = snowflake.connector.connect(user='DAVIBARRETO',
                                          password='Ecclesiasancta!1',
                                          account='xg19634.europe-west4.gcp',
                                          warehouse="COMPUTE_WH",
                                          role="ACCOUNTADMIN",
                                          database="OIP_TEST")
        cs = ctx.cursor()

        # table_description_query = ddl_model[ddl_model.schema_name == "reference"].fillna("").table_description.values
        #
        # table_description_query = [convert_to_snowflake_syntax(command) for command in table_description_query if not re.match(r'^\s*$', command)]
        #
        # col_description_query = ddl_model[ddl_model.schema_name == "reference"].fillna("").columns_description.values
        #
        # col_description_query = ";".join(convert_to_snowflake_syntax(command) for command in col_description_query if not re.match(r'^\s*$', command)).split(";")

        # for command in col_description_query.split(";"):
        #    cs.execute(f"{command};")

        command = f"create or replace TABLE OIP_TEST.ijbfzouefb.PL__DRUGS_MARKET__CHEMOTHERAPY__ACTIVE_SUBSTANCE_AGE__NFZ (" \
                  f"YEAR VARCHAR(8)," \
                  f"MOLECULE VARCHAR(64)," \
                  f"ACTSUB_NAME VARCHAR(128)," \
                  f"ACTSUB_CODE VARCHAR(16)," \
                  f"AGE VARCHAR(16)," \
                  f"PATIENT_NUMBER FLOAT," \
                  f"REFUND FLOAT);"

        command = '--DROP TABLE latam_environment.br__projection_census__ibge;\nCREATE TABLE IF NOT EXISTS latam_environment.br__projection_census__ibge\n(\n\tcode DOUBLE PRECISION   ENCODE RAW\n\t,"year" DOUBLE PRECISION   ENCODE RAW\n\t,age_group VARCHAR(8)   ENCODE lzo\n\t,gender VARCHAR(8)   ENCODE lzo\n\t,population DOUBLE PRECISION   ENCODE RAW\n)\nDISTSTYLE AUTO\n;'

        sqlparse.split(command)

        re.sub("\s\s\s\s*", "\n\t",
               sqlparse.format(command, reindent=True, keyword_case='upper', strip_comments=True, comma_first=True,
                               wrap_after=1))

        sqlparse.parse(command)

        ifile = open("inputfile.txt", mode='w+')
        ifile.write(sqlparse.split(command)[-1])
        ifile.close()

        command = convert_to_snowflake_syntax(ddl_model.table_description.values[0], no_comments=True)
        try:
            cs.execute(command)
        except snowflake.connector.errors.ProgrammingError as e:
            if "does not exist or not authorized" not in str(e):
                print("oi")

        df = cs.fetch_pandas_all()

        for ddl in ["", "foreign_keys"]:
            queries = ddl_model[ddl_model.schema_name == "reference"].fillna("")[ddl].values
            queries_list = ";".join(
                convert_to_snowflake_syntax(command) for command in queries if not re.match(r'^\s*$', command)).split(
                ";")

            index = 0
            for command in queries_list:
                log = open("query_log_errors.txt", "a+")
                index += 1
                try:
                    print(index)
                    cs.execute(f"{command.strip()};")
                except snowflake.connector.errors.ProgrammingError as e:
                    print(f"Skipping: {index}")
                    log.write(f"{command}\n")
            log.close()

            aux = 0
            cs.execute("use database OIP_TEST;")
            for command in table_description_query:
                log = open("log_2.txt", "w+")
                aux += 1
                print(aux)
                log.write(command)
                log.close()
                cs.execute(f"{command.strip()};")

            print("Comments done !")

        aux = 0
        cs.execute("use database OIP_TEST;")
        for command in col_description_query:
            log = open("log_2.txt", "a")
            aux += 1
            print(aux)
            try:
                cs.execute(f"{command.strip()};")
            except snowflake.connector.errors.ProgrammingError as e:
                print("skipping")
                log.write(f"{command}\n")

        log.close()

        print("Comments done !")

        corrected_query = ""
        for record in result:
            print(record.tablename)

            line = record.ddl.replace(" ", " ").replace("\'\"", "'").replace("\"\'", "'")
            corrected_query += f"{line}\n"
            print(line)

        output_file = open("/opt/project/rcd_pyutils/database_manager/redshift_2.sql", "w+")
        output_file.write(corrected_query)
        output_file.close()

        queries = [q.strip() for q in corrected_query.split(";") if len(q) > 0]

        commented_lines = [q.strip() for q in queries if "--" in q[:5]]
        create_table_lines = [q.strip() for q in queries if "--" in q[:5]]

        result.close()
    except Exception as msg:
        print("Command skipped: ", msg)

    print(f"🥳Table is copied to redshift from S3.\n")


if __name__ == "__main__":
    main()

# class MyDialect(DefaultDialect):
#    supports_statement_cache = True
