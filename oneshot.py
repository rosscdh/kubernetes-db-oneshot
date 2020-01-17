import os
import yaml
import psycopg2
import sqlalchemy as sa
from urllib.parse import urlparse
from sqlalchemy_utils import database_exists, create_database

from pathlib import Path

MAKER_YAML = os.getenv('MAKER_YAML', 'oneshot.yaml')
MASTER_DB_URL = os.getenv('MASTER_DB_URL', 'postgres://postgres:postgres@localhost:5432/postgres')

MASTER_DB = urlparse(MASTER_DB_URL)
MASTER_DB_NAME = MASTER_DB.path.split('/')[1]
user_pass, host_port = MASTER_DB.netloc.split('@')
MASTER_DB_USER, MASTER_DB_PASSWD = user_pass.split(':')
MASTER_DB_HOST, MASTER_DB_PORT = host_port.split(':')

master_engine = sa.create_engine(MASTER_DB_URL)
master_conn = master_engine.connect()
master_conn.execute("commit")

data = yaml.load(Path(MAKER_YAML).read_bytes(), Loader=yaml.BaseLoader)


for db in data.get('dbs', []):
    url = urlparse(db.get('url'))

    db_name = url.path.split('/')[1]
    user_pass, host_port = url.netloc.split('@')

    user, passwd = user_pass.split(':')
    host, port = host_port.split(':')

    new_db_url = f"{MASTER_DB.scheme}://{MASTER_DB_USER}:{MASTER_DB_PASSWD}@{MASTER_DB_HOST}:{MASTER_DB_PORT}/{db_name}"

    print(new_db_url)
    engine = sa.create_engine(new_db_url)

    # create user access
    permissions = ','.join(db.get('permissions', ['ALL PRIVILEGES']))
    try:
        create_database(engine.url)
    except Exception as e:
        pass
    conn = engine.connect()
    sql_set = (f"create user \"{user}\" with encrypted password '{passwd}';",
                f"grant {permissions} on database \"{db_name}\" to \"{user}\";")
    for sql in sql_set:
        # print(f"HERE: {sql}")
        try:
            master_engine.execute(sql)
            master_conn.execute("commit")
        except psycopg2.errors.DuplicateObject as e:
            print(e)
            # import pdb;pdb.set_trace()
        except sa.exc.ProgrammingError as e:
            print(e)
            # import pdb;pdb.set_trace()
        except Exception as e:
            # import pdb;pdb.set_trace()
            print(e)


    new_db_url = f"{MASTER_DB.scheme}://{user}:{passwd}@{host}:{port}/{db_name}"

    try:
        engine = sa.create_engine(new_db_url)
        conn = engine.connect()
        print(f"Success, Connected to {new_db_url}, yay")
    except:
        print(f"Could not connect to {new_db_url}, sorry")
