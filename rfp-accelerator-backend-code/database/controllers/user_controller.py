''' Module to interact with user_details table '''
import sys
import sqlalchemy

sys.path.append('../')
sys.path.append('../models')
from connection import Connection


class UserController(Connection):
    ''' Class to interact with user_details table '''

    def __init__(self):
        self.table_name = 'user_details'
        super().__init__(self.table_name)

    # If user's ldap is in DB return True
    def get_user(self, user, pwd):
        ''' Checks if user ldap is in database '''
        sql = f"""
        SELECT * FROM {self.table_name} 
        WHERE user_ldap = 
        """

        search_string = '"' + user.ldap + '" AND password = :pwd '
        query_dict = {"pwd": pwd}

        sql += search_string

        print(search_string)
        print(sql)

        # Create db connection
        pool = self.connect()

        query = sqlalchemy.text(sql)
        try:
            # Execute the SQL statement
            with pool.connect() as con:
                results = con.execute(query, query_dict)
                all_users = []
                for row in results:
                    all_users.append(row)

                con.close()

            if len(all_users) == 1:
                return True, all_users[0]
            print('Unique user not found')
            return False, None
        except sqlalchemy.exc.SQLAlchemyError as e:
            print(str(e))
            return None, None


if __name__ == '__main__':
    uc = UserController()
