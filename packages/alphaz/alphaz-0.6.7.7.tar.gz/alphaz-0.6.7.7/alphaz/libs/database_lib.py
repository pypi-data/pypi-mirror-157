import datetime, glob, os, importlib
from typing import Dict

from sqlalchemy import MetaData

from . import flask_lib, io_lib

from ..models.main import AlphaException
"""
try:
    from core import core 
except:
    from .. import core
    
LOG = core.get_logger("database")"""

def convert_value(value):
    if type(value) == str and len(value) > 7 and value[4] == "/" and value[7] == "/":
        return datetime.datetime.strptime(value, "%Y/%m/%d")
    if value == "now()":
        return datetime.datetime.now()
    return value


def init_databases(db, bind, table_name, drop=False, LOG=None):
    """if core.configuration != 'local':
        if log: log.error('Configuration must be <local>')
        return"""
    bind = bind.upper()
    is_database_names_in_lib = any([x for x in flask_lib.TABLES if x.upper() == bind])
    if not is_database_names_in_lib:
        raise AlphaException("cannot_find_schema", parameters={"schema": bind})

    is_tablenames_in_lib = any([ x for x in flask_lib.TABLES[bind]["tables"] if x.upper() == table_name.upper()])
    if not is_tablenames_in_lib:
        raise AlphaException("cannot_find_table", parameters={"table": table_name})

    table = flask_lib.TABLES[bind]["tables"][table_name.upper()]

    init_databases_config = db.config.get("databases")
    if init_databases_config is None:
        raise AlphaException(
                "No initialisation configuration has been set in <databases> entry"
            )

    database_names_in_configs = [x for x in init_databases_config if x.upper() == bind.upper()]
    if not len(database_names_in_configs):
        raise AlphaException(
                "No initialisation configuration has been set in <databases> entry for database <%s>"
                % bind
            )
        return False
    database_name_in_configs = database_names_in_configs[0]

    #db = core.db

    if drop:
        if LOG:
            LOG.info("Drop table <%s> on <%s> database" % (table, bind))
        #db.metadata.drop_all(db.engine, tables=[table.__table__])
        table.drop()

    #db.metadata.create_all(db.engine, tables=[table.__table__])
    table.create()
    if LOG:
        LOG.info("Create table <%s> on <%s> database" % (table, bind))
    #db.commit()

    cf = init_databases_config[database_name_in_configs]
    if not len(cf):
        if LOG:
            LOG.error(
                "No initialisation configuration has been set in <databases> entry for database <%s>"
                % bind
            )
        return False
        
    if type(cf) == str:
        cf = init_databases_config[cf]

    # json ini
    if "init_database_dir_json" in cf:
        json_ini = cf["init_database_dir_json"]
        files = glob.glob(json_ini + os.sep + "*.json")

        # if log: log.info('Initiating table %s from json files (%s): \n%s'%(bind,json_ini,'\n'.join(['   - %s'%x for x in files])))
        for file_path in files:
            __process_databases_init(
                db, bind, table_name, file_path, file_type="json"
            )

    # python ini
    if "init_database_dir_py" in cf:
        py_ini = cf["init_database_dir_py"]
        files = [x for x in glob.glob(py_ini + os.sep + "*.py") if not "__init__" in x]

        # if log: log.info('Initiating table %s from python files (%s): \n%s'%(bind,py_ini,'\n'.join(['   - %s'%x for x in files])))
        for file_path in files:
            __process_databases_init(
                db, bind, table_name, file_path
            )

def __process_databases_init(
    db, bind, table_name, file_path, file_type="py"
):
    if file_type == "py":
        current_path = os.getcwd()
        module_path = (
            file_path.replace(current_path, "")
            .replace("/", ".")
            .replace("\\", ".")
            .replace(".py", "")
        )

        if module_path[0] == ".":
            module_path = module_path[1:]

        module = importlib.import_module(module_path)

        if hasattr(module, "ini"):
            ini = module.__dict__["ini"]
            if type(ini) != dict:
                raise AlphaException(
                        "In file %s <ini> configuration must be of type <dict>"
                        % (file_path)
                    )

            __get_entries(db, bind, table_name, file_path, ini)
    elif file_type == "json":
        try:
            ini = io_lib.read_json(file_path)
        except Exception as ex:
            raise AlphaException("Cannot read file %s: %s" % (file_path, ex))

        __get_entries(db, bind, table_name, file_path, ini)


def __get_entries(db, bind, table_name, file_path, configuration):
    # models_sources = [importlib.import_module(x) if type(x) == str else x for x in models_sources]
    for database, tables_config in configuration.items():
        if type(database) == str:
            if database != bind:
                continue

            if not bind in db.db_cnx:
                raise AlphaException(
                        "In file %s configuration database <%s> is not recognized"
                        % (file_path, database)
                    )

        if type(tables_config) != dict:
            raise AlphaException(
                    "In file %s configuration of database <%s> must be of type <dict>"
                    % (file_path, database)
                )

        for table, config in tables_config.items():
            if table != table_name:
                continue

            found = False
            for schema, tables in flask_lib.TABLES.items():
                if table in tables["tables"]:
                    found = True
                    table = tables["tables"][table]

            if not found:
                raise AlphaException(
                        "In file %s configuration of database <%s> the table <%s> is not found"
                        % (file_path, database, table)
                    )

            if "headers" in config and "values" in config:
                if type(config["values"]) != list:
                    raise AlphaException(
                            'In file %s "values" key from table <%s> and database <%s> must be of type <list>'
                            % (file_path, table_name, database)
                        )

                if type(config["headers"]) != list:
                    raise AlphaException(
                            'In file %s "headers" key from table <%s> and database <%s> must be of type <list>'
                            % (file_path, table_name, database)
                        )

                headers_size = len(config["headers"])

                entries = []
                for entry in config["values"]:
                    if type(entry) != list:
                        raise AlphaException(
                                "In file %s from table <%s> and database <%s> entry <%s> must be of type <list>"
                                % (file_path, table_name, database, entry)
                            )
                        
                    entries.append(entry)

                """if LOG:
                    LOG.info(
                        "Adding %s entries from <list> for table <%s> in database <%s> from file %s"
                        % (len(entries), table_name, database, file_path)
                    )"""
                db.process_entries(
                    bind, table, headers=config["headers"], values=entries
                )

            if "objects" in config:
                entries = config["objects"]
                """if LOG:
                    LOG.info(
                        "Adding %s entries from <objects> for table <%s> in database <%s> from file %s"
                        % (len(entries), table_name, database, file_path)
                    )"""
                db.process_entries(bind, table,  values=entries)


def get_databases_tables_dict(core) -> Dict[str, str]:
    return {} #TODO: update
    return {x: list(y.metadata.tables.keys()) for x, y in core.databases.items()}

def __get_table_model(schema: str, tablename: str):
    module = importlib.import_module(f"models.databases.{schema}")
    model = None
    for el in module.__dict__.values():
        if hasattr(el, "__tablename__") and el.__tablename__ == tablename:
            model = el
    if model is None:
        raise AlphaException(f"Cannot find {tablename=} in {schema=}")
    return model


def get_table_columns(schema: str, tablename: str):
    model = __get_table_model(schema, tablename)
    return model.get_columns()

def get_table_model(schema:str, tablename:str):
    model = __get_table_model(schema, tablename)
    return model.get_model()

def get_table_content(
    schema: str,
    tablename: str,
    order_by: str,
    direction: str,
    page_index: int,
    page_size: int,
):
    from core import core
    model = __get_table_model(schema, tablename)
    return core.db.select(
        model,
        page=page_index,
        per_page=page_size,
        order_by=order_by,
        order_by_direction=direction,
    )