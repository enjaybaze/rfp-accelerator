'''Module helps controllers get database connections'''
import json
import sqlalchemy
from config import Config
from google.cloud.sql.connector import Connector
from google.cloud import secretmanager



class Connection(Config):
    '''Superclass for controllers that need to access the database'''

    def __init__(self, table_name = None):
        self.table_name = table_name
        self.pool = self.connect()

    def connect(self):
        '''Function to get a connection pool with the database we are using'''

        # Load DB creds from SM
        client = secretmanager.SecretManagerServiceClient()
        config = self.load_config()
        name = f"projects/{config['project_id']}/secrets/{config['database_details']}/versions/1"
        request = {"name": name}
        # Make the request
        response = client.access_secret_version(request=request)
        payload = response.payload.data.decode("UTF-8")
        payload.encode('unicode_escape')
        db_cred = json.loads(payload)

        # Init connection variables
        instance_connection_name = db_cred['instance_connection_name']
        db_name = db_cred['db_name']
        db_user = db_cred['db_user']
        db_pass = db_cred['db_pass']

        connector = Connector()

        # helper method to connect to db
        def get_conn():
            conn = connector.connect(
                instance_connection_name,
                "pymysql",
                user=db_user,
                password=db_pass,
                db=db_name,
            )
            return conn


        #Create connection pool
        pool = sqlalchemy.create_engine(
                "mysql+pymysql://",
                creator=get_conn,
                )
        return pool

    def execute(self, sql):
        ''' Development method to execute a sql query '''

        pool = self.connect()
        query = sqlalchemy.text(sql)
        try:
            # Execute the SQL statement
            with pool.connect() as con:
                results = con.execute(query)
                con.commit()
                con.close()
            print('Done')
            return True
        except sqlalchemy.exc.SQLAlchemyError:
            print('error')
            return False


if __name__ == '__main__':
    c = Connection()
