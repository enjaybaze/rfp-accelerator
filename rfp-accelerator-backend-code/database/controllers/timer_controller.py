import os
from google.cloud.sql.connector import Connector, IPTypes
import pymysql
import sqlalchemy
import sys 
import datetime
import traceback
sys.path.append('../')
from connection import Connection


class TimerController(Connection):

    def __init__(self):
        super().__init__('timer_controller')

    def get_metadata(self):
        return sqlalchemy.MetaData()

    def get_timer_table(self):
        ''' get sqlalchemy table object for rfp_timing table '''

        #Setup statement
        metadata_obj = self.get_metadata()
        table = sqlalchemy.Table(
        "rfp_timing",
        metadata_obj,
        sqlalchemy.Column("expert_request_id", sqlalchemy.String(255)),
        sqlalchemy.Column("start_time", sqlalchemy.DateTime),
        sqlalchemy.Column("expected_end_time", sqlalchemy.DateTime),
        sqlalchemy.Column("num_questions", sqlalchemy.Integer),
        sqlalchemy.Column("active", sqlalchemy.Boolean),
        sqlalchemy.Column("update_time", sqlalchemy.Boolean),
        sqlalchemy.Column("tracked_time", sqlalchemy.DateTime),
        sqlalchemy.Column("model_end", sqlalchemy.DateTime),
        sqlalchemy.Column("model_start", sqlalchemy.DateTime),
        )
        return table



    def start_timer(self, expert_request_id, num_questions):
        ''' start tracking time for how long the model has been running '''

        #Get time per question from config file
        config = self.load_config()
        time_per_question = int(config['time_per_question'])

        time_for_run = datetime.timedelta(0,time_per_question*num_questions)
        now = datetime.datetime.now()

        try:
            with self.pool.connect() as con:
                #sql2_dict = {"expert_request_id": expert_request_id, "num_questions": num_questions, "start_time": now}
                table = self.get_timer_table()
                stmt = (
                    sqlalchemy.insert(table).
                    values(expert_request_id=expert_request_id, num_questions=num_questions, start_time=now, expected_end_time=now+time_for_run)
                )
                con.execute(stmt)
                con.commit()
                con.close()
                return True#Successfully saved

        except sqlalchemy.exc.SQLAlchemyError:
            traceback.print_exc()
            return False

    def start_model_timer(self, expert_request_id, num_questions):
        ''' tell database to start model run timer'''

        #Will update expected_end_time as well
        config = self.load_config()
        time_per_question = int(config['time_per_question_running'])
        time_for_run = datetime.timedelta(0,time_per_question*num_questions)
        now = datetime.datetime.now()

        try:

            with self.pool.connect() as con:
                table = self.get_timer_table()
                stmt = (
                    sqlalchemy.update(table).
                    where(table.c.expert_request_id == expert_request_id and active == 1).
                    values(model_start=now, expected_end_time = now+time_for_run)
                )
                con.execute(stmt)
                con.commit()
                con.close()
                return True #Successfully saved

        except sqlalchemy.exc.SQLAlchemyError:
            traceback.print_exc()
            return False

    def end_model_timer(self, expert_request_id):
        ''' tell the database to end the model run timer for the rfp'''
        now = datetime.datetime.now()
        try:
            with self.pool.connect() as con:
                #sql2_dict = {"expert_request_id": expert_request_id, "num_questions": num_questions, "start_time": now}
                table = self.get_timer_table()
                stmt = (
                    sqlalchemy.update(table).
                    where(table.c.expert_request_id == expert_request_id and active == 1).
                    values(model_end=now, active=0)
                )
                con.execute(stmt)
                con.commit()
                con.close()
                return True#Successfully saved


        except sqlalchemy.exc.SQLAlchemyError:
            traceback.print_exc()
            return False

    def get_timeout(self, expert_request_id):
        ''' Access rfp_timing table to identify if the model is timed out '''
        now = datetime.datetime.now()
        try:
            with self.pool.connect() as con:
                #Get expected_end_time
                table = self.get_timer_table()
                stmt = sqlalchemy.select(table.c.expected_end_time).where(table.c.expert_request_id == expert_request_id and table.active == 1)
                results = list(con.execute(stmt))
                con.commit()
                con.close()

                #If no results return false. Need this for old records
                if len(results) < 1:
                    return False

                #If expected_end_time passed, return True - RFP timed out
                expected_end_time = list(results)[0][0]
                print(expected_end_time)
                print(now)

                if expected_end_time is None:
                    return False

                if(expected_end_time < now):
                    print('Timeout')
                    return True
                return False 
        except Exception as e:
            traceback.print_exc()
            print('Error calculating rfp timeout')
            return False
