import os
import yaml
import psycopg2
import sqlalchemy as sa
from urllib.parse import urlparse
from sqlalchemy_utils import database_exists, create_database

from pathlib import Path

ONESHOT_YAML = os.getenv("ONESHOT_YAML", "oneshot.yaml")

data = yaml.load(Path(ONESHOT_YAML).read_bytes(), Loader=yaml.BaseLoader)

MASTER_DB_URL = data.get(
    "MASTER_DB_URL", "postgres://postgres:postgres@localhost:5432/postgres"
)

MASTER_DB = urlparse(MASTER_DB_URL)
MASTER_DB_NAME = MASTER_DB.path.split("/")[1]
user_pass, host_port = MASTER_DB.netloc.split("@")
MASTER_DB_USER, MASTER_DB_PASSWD = user_pass.split(":")
MASTER_DB_HOST, MASTER_DB_PORT = host_port.split(":")

master_engine = sa.create_engine(MASTER_DB_URL)
master_conn = master_engine.connect()
master_conn.execute("commit")


class BaseUserPrivCreator:
    def create_user(self, user: str, passwd: str, **kwargs:dict) -> str:
        raise NotImplemented

    def create_privs(self, db_name: str, user: str, **kwargs:dict) -> str:
        raise NotImplemented

    def get_sql(self, **kwargs):
        return set([self.create_user(**kwargs), self.create_privs(**kwargs)])


class PostgresUserCreator(BaseUserPrivCreator):
    def create_user(self, user: str, passwd: str, **kwargs:dict) -> str:
        return f"create user \"{user}\" with encrypted password '{passwd}';"

    def create_privs(self, db_name: str, user: str, **kwargs:dict) -> str:
        return f"grant ALL PRIVILEGES on database \"{db_name}\" to \"{user}\";"


class MysqlUserCreator(BaseUserPrivCreator):
    def create_user(self, user: str, host: str, passwd: str, **kwargs:dict) -> str:
        return f"CREATE USER '{user}'@'{host}' IDENTIFIED BY '{passwd}';"

    def create_privs(self, db_name: str, user: str, host: str, **kwargs:dict) -> str:
        return f"GRANT ALL PRIVILEGES ON {db_name}.* TO '{user}'@'{host}';FLUSH PRIVILEGES;"


class UserPrivCreator:
    @staticmethod
    def factory(scheme: str, *args, **kwargs):
        if scheme == "postgres":
            return PostgresUserCreator()
        elif scheme == "mysql":
            return MysqlUserCreator()
        else:
            raise NotImplementedError("onyl mysql and postgres at the moment")


def parse_db_url(url: str, use_master: bool = True) -> tuple:
    url = urlparse(db.get("url"))

    db_name = url.path.split("/")[1]
    user_pass, host_port = url.netloc.split("@")

    user, passwd = user_pass.split(":")
    host, port = host_port.split(":")

    if use_master:
        new_db_url = f"{MASTER_DB.scheme}://{MASTER_DB_USER}:{MASTER_DB_PASSWD}@{MASTER_DB_HOST}:{MASTER_DB_PORT}/{db_name}"
    else:
        new_db_url = f"{url.scheme}://{user}:{passwd}@{host}:{port}/{db_name}"

    return db_name, user, passwd, host, port, new_db_url, url.scheme


if __name__ == "__main__":
    for statement in data.get("pre_statements", []):
        print(f"PRE-STATEMENT: {statement}")
        try:
            master_engine.execute(sql)
            master_conn.execute("commit")
        except Exception as e:
            print(e)

    for db in data.get("create_dbs", []):
        db_name, user, passwd, host, port, new_db_url, scheme = parse_db_url(
            url=db.get("url")
        )
        engine = sa.create_engine(new_db_url)

        # create user access
        try:
            create_database(engine.url)
        except Exception as e:
            pass
        conn = engine.connect()

        db_factory = UserPrivCreator.factory(scheme=scheme)
        sql_set = db_factory.get_sql(
            user=user, passwd=passwd, host=host, db_name=db_name
        )

        for sql in sql_set:
            try:
                master_engine.execute(sql)
                master_conn.execute("commit")
            except Exception as e:
                print(e)

        new_db_url = f"{MASTER_DB.scheme}://{user}:{passwd}@{host}:{port}/{db_name}"

        try:
            engine = sa.create_engine(new_db_url)
            conn = engine.connect()
            print(f"Success, Connected to {new_db_url}, yay")
        except:
            print(f"Could not connect to {new_db_url}, sorry")

    # Iterate over statements
    db_name, user, passwd, host, port, new_db_url, scheme = parse_db_url(
        url=MASTER_DB_URL
    )
    engine = sa.create_engine(new_db_url)
    conn = engine.connect()

    for statement in data.get("statements", []):
        print(f"STATEMENT: {statement}")
        try:
            master_engine.execute(sql)
            master_conn.execute("commit")
        except Exception as e:
            print(e)
