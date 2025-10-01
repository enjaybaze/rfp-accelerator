''' Module working with the rfp_upload table '''
import sys
import sqlalchemy
# import requests
import datetime
import random
import traceback
import string

from database.controllers.sheets_controller_v2 import read_sheet_v2, create_sheet_new_v2

sys.path.append('../')
from connection import Connection
from timer_controller import TimerController
from sqlalchemy.exc import SQLAlchemyError


class RFPUploadController(Connection):
    '''Methods controlling the rfp_upload table'''

    def __init__(self):
        '''Set table name'''
        self.table_name = 'rfp_upload'
        self.pool = self.connect()

    def test(self):
        '''Return all table objects to test connection to db'''
        pool = self.connect()
        sql = 'SHOW TABLES'
        query = sqlalchemy.text(sql)
        data = []
        with pool.connect() as con:
            results = con.execute(query)

            for row in results:
                data.append(row[0])

        print(data)
        return data

    def download_file_new(self, expert_request_id, user_ldap, sheets_controller):
        ''' Create excel spreadsheet of finished RFP '''
        try:
            download_data = {}
            # Name to save google sheet as. Is updated to account-name-date
            name = expert_request_id
            with self.pool.connect() as con:
                sql = f"""
                SELECT document_id, expert_request_id, account_name, question, search_refinement, page_name, result1, result2, result3, pa_final_response, pa_feedback, pa_approve_reject_override, sme_final_response, sme_feedback, sme_approve_reject_override, run_model, rfp_owner FROM {self.table_name}
                WHERE expert_request_id = "{expert_request_id}"
                """

                sheet_owner = ''

                query = sqlalchemy.text(sql)
                results = con.execute(query)

                for row in results:
                    quest = list(row)
                    print(str(quest).encode(encoding='UTF-8', errors='ignore'))
                    page_name = quest[5]

                    # If any question not in 'error' or 'processed' state , skip question
                    if not (quest[15] == 'error' or quest[15] == 'processed' or quest[15] == 'completed' or quest[
                        15] == 'exported'):
                        # return False, 'incomplete'
                        continue

                    if not page_name in download_data:
                        download_data[page_name] = []
                    download_data[page_name].append([quest[3], quest[4], quest[6], quest[10]])

                    name = self.create_name(quest[2])

                    sheet_owner = quest[16]
                    print("sheet Own", sheet_owner)

                    '''
                        print(download_data)
                        download_data[page_name][-1][2] = 'I cannot determine the answer to that.'
                    '''

                sql2 = f"""
                UPDATE {self.table_name}
                SET run_model = "exported"
                WHERE expert_request_id = "{expert_request_id}"
                """

                query2 = sqlalchemy.text(sql2)
                con.execute(query2)
                print('Status Updatedd')

                if sheet_owner == '':
                    return False, ''

                finished, url = create_sheet_new_v2(name, sheet_owner, download_data)
                con.commit()
                con.close()

            return finished, url
        except sqlalchemy.exc.SQLAlchemyError:
            traceback.print_exc()
            print('Failed ')
            return False, ''

    def create_name(self, account_name):
        ''' Creates sheets title based on exp_req_id name '''
        time = datetime.datetime.now().strftime("%Y/%m/%d_%H:%M:%S")
        # -%H:%M:%S

        name = account_name + '_' + time
        print(name)
        return name

    def process_file(self, file_url, sheets_controller):
        ''' Helper function to read RFP data from sheet file '''
        print('File Processing')
        file_id = file_url.split('/d/')[1].split('/')[0]
        print("file_id: ", file_id)
        data, msg, owner = read_sheet_v2(file_id)
        print("File Processed")
        return data, msg, owner

    def rfp_refinement(self, document):
        ''' Depricated rfp_refinement method '''
        try:
            pool = self.connect()
            # Fetch questions with credentials
            sql = f"""
            SELECT document_id, expert_request_id, account_name, question, search_refinement, page_name FROM {self.table_name}
            WHERE expert_request_id = "{document.expert_request_id}"
            """
            query = sqlalchemy.text(sql)
            questions = []

            # Execute DB as one interaction
            with pool.connect() as con:
                results = con.execute(query)

                for row in results:
                    quest = list(row)

                    questions.append({
                        "id": quest[0],
                        "expect_requ_id": quest[1],
                        "account_name": quest[2],
                        "question": quest[3],
                        "search_refinement": quest[4],
                        "page_name": quest[5]
                    })
                con.close()
            return questions
        except sqlalchemy.exc.SQLAlchemyError:
            print('Error loading questions')
            return questions

    # RFP Refinement 2 sorted by page for easier front end
    def rfp_refinement2(self, document):
        ''' rfp refinement by page to help front end '''

        # Fetch questions with credentials
        sql = f"""
        SELECT document_id, expert_request_id, account_name, question, search_refinement, page_name FROM {self.table_name}
        WHERE expert_request_id = "{document.expert_request_id}"
        """

        query = sqlalchemy.text(sql)
        rfp = {}

        account_name = ''
        try:

            pool = self.connect()
            # Execute DB as one interaction
            with pool.connect() as con:
                results = con.execute(query)

                for row in results:
                    quest = list(row)
                    account_name = quest[2]
                    data = {
                        "id": quest[0],
                        "question": quest[3],
                        "search_refinement": quest[4],
                    }

                    page_name = quest[5]

                    # add new key if not in keys
                    if not page_name in rfp.keys():
                        rfp[page_name] = []

                    question_number = len(rfp[page_name]) + 1
                    data['question_number'] = question_number
                    rfp[page_name].append(data)

                con.close()

            # alternate_response_format = self.modified_rfp2_dict(rfp)
            return account_name, rfp
        except sqlalchemy.exc.SQLAlchemyError:
            print('Error loading questions')
            return None, rfp

    def rfp_refinement3(self, document):
        ''' RFP refinement by page, listed as 'name' to help front end '''
        account_name, rfp2_dict = self.rfp_refinement2(document)
        list_of_sheets = []

        sheet_names = rfp2_dict.keys()

        for name in sheet_names:
            data = rfp2_dict.get(name)
            sheet_dict = {'name': name, 'data': data}
            list_of_sheets.append(sheet_dict)

        return account_name, list_of_sheets

    def get_num_questions(self, expert_request_id):
        ''' Get number of questions for expert_request_id '''
        # Also update rfp_timing table for timing spreadsheet
        try:
            with self.pool.connect() as con:
                sql = f"""
                SELECT * FROM {self.table_name}
                WHERE expert_request_id = "{expert_request_id}" AND run_model = "waiting"
                """

                results = con.execute(sqlalchemy.text(sql))

                count = 0
                for x in results:
                    count += 1

                con.commit()
                con.close()
                return count
        except sqlalchemy.exc.SQLAlchemyError:
            traceback.print_exc()
            print('Error counting questions')
            return 0

    def advance_stage(self, data_dict, run_model_update, process_status_update):
        ''' Updates run_status and process_status by expert request id '''

        print('hello')
        try:
            pool = self.connect()
            # Execute DB as one interaction

            # If specific questions are listed, load them. Otherwise, have a dummy question for looping
            questions_specified = 'questions' in data_dict
            questions = [1]
            num_questions = -1

            if questions_specified:
                questions = data_dict['questions']
                num_questions = len(questions)
                print(num_questions)

            with self.pool.connect() as con:
                expert_request_id = data_dict['expert_request_id']
                sql = f"""
                    UPDATE {self.table_name}
                    SET run_model = "{run_model_update}", process_status='{process_status_update}'"""

                # If starting model run
                if run_model_update == 'waiting':
                    sql += ", pa_approve_reject_override = ''"

                sql += f"""
                WHERE expert_request_id = "{expert_request_id}"
                        """
                if questions_specified:
                    sql += f' AND document_id = :question'

                # Execute stmt for each question
                for question in questions:
                    d = {"question": question}
                    query = sqlalchemy.text(sql)
                    print(query, d)
                    con.execute(query, d)

                con.commit()
                con.close()

                # Start timer if we just advanced the stage to waiting
                if run_model_update == 'waiting':

                    if num_questions < 1:
                        num_questions = self.get_num_questions(expert_request_id)
                    tc = TimerController()
                    tc.start_timer(expert_request_id, num_questions)

                return True
        except sqlalchemy.exc.SQLAlchemyError:
            traceback.print_exc()
            print('Error advancing stage of model')
            return False

    def check_duplicate_erid(self, erid):
        ''' Helper function for document_upload. Verifies erid is unique '''

        try:

            pool = self.connect()
            with pool.connect() as con:

                sql = f"""
                SELECT expert_request_id from {self.table_name}
                WHERE expert_request_id = "{erid}"
                """
                print(sql)
                query = sqlalchemy.text(sql)

                # Execute the SQL statement
                results = con.execute(query)
                con.commit()

                # count how many rows have the expert request id
                count = len(list(results))
                con.close()
                if count > 0:
                    return True
                return False
        except sqlalchemy.exc.SQLAlchemyError:
            return True

    def preprocess_text(self, text):
        ''' Function to preprocess text fields for additional safety '''
        if text is None:
            return ''

        text = text.replace("''", "'")
        text = text.replace('""', '"')
        text = text.replace("\\", "")

        return text

    def save_model_response(self, dict_list, expert_request_id, action):
        ''' Method called by model API while running to update db '''
        try:
            # Debugging information
            print(f'Data list: {dict_list}')
            print(f'Expert Request ID: {expert_request_id}')
            print(f'Action: {action}')

            # Get the model run state. If it is started, start the model run timer
            tc = TimerController()
            model_run_state = self.get_model_run_state(expert_request_id)
            if model_run_state == 'started':
                tc.start_model_timer(expert_request_id, self.get_num_questions(expert_request_id))

            # Execute DB as one interaction
            with self.pool.connect() as con:
                for dictionary in dict_list:
                    document_id = dictionary.get('question_id')
                    answer = self.preprocess_text(dictionary.get('response'))  # Use class method
                    # target_column = 'result' + dictionary.get('response_type', '')
                    process_status = self.preprocess_text(dictionary.get('process_status'))  # Use class method
                    run_status = self.preprocess_text(dictionary.get('run_status'))  # Use class method

                    if action == 'update_dependency':
                        dependency = self.preprocess_text(dictionary.get('dependency'))  # Use class method
                        sql = f"""UPDATE {self.table_name}
                                SET dependency = :dependency,
                                    run_model = :run_status
                                WHERE document_id = :document_id
                                AND expert_request_id = :expert_request_id"""
                        params = {
                            'dependency': dependency,
                            'run_status': run_status,
                            'document_id': document_id,
                            'expert_request_id': expert_request_id
                        }

                    elif action == 'update_model_response':
                        # If a context is provided
                        context = self.preprocess_text(dictionary.get('context', ''))  # Use class method

                        sql = f"""UPDATE {self.table_name}
                                                        SET result1 = :answer,
                                                            run_model = :run_status,
                                                            process_status = :process_status,
                                                            pa_final_response = '',
                                                            pa_feedback = '',
                                                            context = :context
                                                        WHERE document_id = :document_id
                                                        AND expert_request_id = :expert_request_id"""
                        params = {
                            'answer': answer,
                            'run_status': run_status,
                            'process_status': process_status,
                            'context': context,
                            'document_id': document_id,
                            'expert_request_id': expert_request_id
                        }

                    else:
                        print('Invalid request')
                        continue

                    # Debugging output
                    print(f'Executing SQL: {sql}')
                    print(f'Parameters: {params}')

                    query = sqlalchemy.text(sql)
                    con.execute(query, params)

                con.commit()

                # Get the model run state. If done, end the model run timer
                model_run_state = self.get_model_run_state(expert_request_id)
                if model_run_state == 'done':
                    tc.end_model_timer(expert_request_id)

            return True

        except SQLAlchemyError as e:
            # Enhanced error handling
            print('Error saving model response')
            traceback.print_exc()  # Print detailed traceback
            return False

    def get_model_run_state(self, expert_request_id):
        ''' get state of model run for timer processing '''
        try:
            with self.pool.connect() as con:

                # Execute query
                sql = f"""
                SELECT DISTINCT run_model FROM {self.table_name}
                WHERE expert_request_id = "{expert_request_id}"
                """
                query = sqlalchemy.text(sql)
                results = con.execute(query)
                con.commit()
                con.close()

                # Find run state from results
                our_results = results.fetchall()
                statuses = [r[0] for r in our_results]
                # If run model status has no 'waiting' or 'processing' states, it is done
                print('Calculating state response')
                print(statuses)
                if not 'waiting' in statuses and not 'processing' in statuses:
                    print('Done')
                    return 'done'

                # If run model status has only 'waiting' states, it just started
                elif 'waiting' in statuses and not 'processing' in statuses:
                    print('Started')
                    return 'started'

                print('Processing')
                return 'processing'

        except sqlalchemy.exc.SQLAlchemyError:
            traceback.print_exc()
            return 'error'

    def model_run_question(self, data_dict):
        ''' Method called by model API to fetch all questions in specific run_status state '''

        try:
            pool = self.connect()

            sql2 = 'WHERE '
            run_status = data_dict['run_status']
            if 'expert_request_id' in data_dict.keys():
                expert_request_id = data_dict.get('expert_request_id')

                sql2 = f"""
                WHERE expert_request_id = "{expert_request_id}" AND 
                """

            sql2 += f'run_model = "{run_status}"'

            sql = f"""
            SELECT document_id, expert_request_id, account_name, question, search_refinement, page_name, dependency FROM {self.table_name}
            """

            sql = sql + sql2

            query = sqlalchemy.text(sql)
            rfp = []

            account_name = ''
            with pool.connect() as con:
                results = con.execute(query)

                for row in results:
                    quest = list(row)
                    account_name = quest[2]
                    data = {
                        "id": quest[0],
                        "question": quest[3],
                        "search_refinement": quest[4],
                        "expert_request_id": quest[1],
                        "dependency": quest[6]
                    }
                    rfp.append(data)

                con.close()

            return account_name, rfp
        except sqlalchemy.exc.SQLAlchemyError:
            print('Error loading questions from db')
            return None, rfp

    def create_expert_request_id(self):
        erid_length = int(self.load_config()['erid_length'])

        erid = ''.join(random.choices(string.digits, k=erid_length))
        return 'ER-' + erid

    def new_upload_document(self, data_payload, sheets_controller=None):
        ''' Add rfp question object to database '''

        # ERID auto generated
        duplicate = True
        expert_request_id = 'ER-111111'
        while duplicate:
            expert_request_id = self.create_expert_request_id()
            duplicate = self.check_duplicate_erid(expert_request_id)

        # Load in data from payload
        account_name = data_payload['account_name']
        name = data_payload['name']
        file_url = data_payload['file_url']
        user_ldap = data_payload['user_ldap']

        excel_data = None
        try:
            excel_data, msg, owner = self.process_file(file_url, sheets_controller)
            print(msg)
            if msg == 'formatting':
                return False, 'formatting', 0, None
            if msg == 'access':
                return False, 'access', 0, None
            if msg == 'url':
                print('file url payload')
                return False, 'url', 0, None
            if msg == 'general':
                return False, 'general', 0, None
            if msg == 'empty':
                return False, 'empty', 0, None
            if msg == 'loading':
                return False, 'loading', 0, None
            if msg == 'tabs':
                return False, 'tabs', 0, None
            if msg == 'hidden':
                return False, 'hidden', 0, None
        except:
            traceback.print_exc()
            return False, 'exception', 0, None

        # Upload excel_data to db
        try:
            # Execute DB as one interaction
            with self.pool.connect() as con:
                num_questions = 0
                for sheet_data in excel_data:
                    page_name = sheet_data['page_name']
                    sheet = sheet_data['rfp']

                    # print(page_name)
                    for row in sheet:
                        num_questions += 1
                        question = row[0]
                        search_refinement = row[1]

                        data = {
                            "expert_request_id": expert_request_id,
                            "account_name": account_name,
                            "name": name,
                            "page_name": page_name,
                            "question": question,
                            "search_refinement": search_refinement,
                            "upload_user_id": user_ldap,
                            "pa_reviewer": user_ldap,
                            "rfp_owner": owner
                        }

                        sql = f"""
                        INSERT into {self.table_name} (expert_request_id, account_name, name, page_name, question, search_refinement, upload_user_id, pa_reviewer, rfp_owner)
                        VALUES (:expert_request_id, :account_name, :name, :page_name, :question, :search_refinement, :upload_user_id, :pa_reviewer, :rfp_owner)
                        """

                        con.execute(sqlalchemy.text(sql), data)

                        con.commit()
                con.close()
                return True, 'success', num_questions, expert_request_id
        except sqlalchemy.exc.SQLAlchemyError:
            traceback.print_exc()
            return False, 'sql', 0, None


if __name__ == '__main__':
    uc = RFPUploadController()
