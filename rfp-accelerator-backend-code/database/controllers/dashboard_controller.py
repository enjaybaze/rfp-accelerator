"""
Class to help run dashboard searches
"""
from datetime import datetime
import sys
import traceback
import sqlalchemy

sys.path.append('../')
from connection import Connection
from timer_controller import TimerController


class DashboardController(Connection):
    ''' Class to provide backend support for RFP dashboard pages '''

    def __init__(self):
        self.table_name = 'rfp_upload'
        self.pool = self.connect()

    def soft_remove(self, expert_request_id):
        ''' Set 'active' status to false to hide from dashboard '''
        try:

            pool = self.connect()
            with pool.connect() as con:

                sql = f"""
                UPDATE {self.table_name}
                SET status = FALSE
                WHERE expert_request_id = "{expert_request_id}"
                """

                query = sqlalchemy.text(sql)
                con.execute(query)

                con.commit()
                con.close()
                return True
        except sqlalchemy.exc.SQLAlchemyError:
            print('Error removing rfp')
            return False

    def create_search_string(self, search_dictionary):
        ''' Helper method for dashboard search. Creates sql for the requested search params'''
        # Parse dict
        search_params = search_dictionary.keys()
        search_restrictions = ''

        for key in search_params:
            value = search_dictionary.get(key)
            sql_string = ''

            # If searching by dates, convert to datetime object
            print(key == 'from_date')
            date_format = '%Y-%m-%d'
            if key == 'from_date':
                datetime_date = datetime.strptime(value, date_format)
                search_dictionary[key] = datetime_date
                sql_string = 'AND upload_time >= :from_date '
            elif key == 'to_date':
                datetime_date = datetime.strptime(value, date_format)
                search_dictionary[key] = datetime_date
                sql_string = 'AND upload_time <= :to_date '
            else:
                sql_string = f'AND {key} = :{key} '
            search_restrictions += sql_string

        search_restrictions += 'AND status = TRUE'

        return search_dictionary, search_restrictions

    def process_timeout(self, expert_request_id):
        ''' Update the DB with responses and status changes on timeout '''
        try:
            with self.pool.connect() as con:

                sql = f"""
                UPDATE {self.table_name}
                SET run_model = "error", process_status = "pa_review", result1 = "Model timed out. Please rerun again"
                WHERE expert_request_id = "{expert_request_id}" AND (run_model = "waiting" OR run_model = "processing")
                """
                query = sqlalchemy.text(sql)
                con.execute(query)

                # Deactivate Timer
                tc = TimerController()
                tc.end_model_timer(expert_request_id)
                print('Timeout. Deactivated timer')

                con.commit()

                con.close()
                return True
        except sqlalchemy.exc.SQLAlchemyError:
            traceback.print_exc()
            print('Error updating rfp on model timeout')
            return False

    # Helper function for processing rfp_dict from dashboard search
    def process_dashboard_dict(self, rfp_dict, dashboard='PA'):

        ''' Process rfp data to identify buttons to be enabled for dashboard '''

        num_rfps = 0
        num_completed = 0
        del_list = []

        # Iterate over rfps one by one
        for key in rfp_dict:
            # Do not process the summary statistics
            if key == 'stats':
                continue
            sub_dict = rfp_dict[key]

            num_rfps += 1
            # Turn sets into list for jsonify method later
            sub_dict['process_status'] = list(sub_dict['process_status'])
            sub_dict['run_model_status'] = list(sub_dict['run_model_status'])

            process_status = sub_dict['process_status']
            run_model_status = sub_dict['run_model_status']
            print(key)
            print(run_model_status)

            v1 = 'pa_review' in process_status
            v2 = 'uploaded' in process_status
            v3 = 'processing' in run_model_status
            v4 = 'staged' in run_model_status
            v5 = 'processed' in run_model_status
            v6 = 'sme_review' in process_status
            v7 = 'pa_final_review' in process_status
            v8 = 'completed' in process_status
            p_len = len(process_status)
            rm_len = len(run_model_status)
            v9 = dashboard == 'PA'
            v10 = dashboard == 'SME'
            v11 = 'error' in run_model_status
            v12 = 'waiting' in run_model_status
            v13 = 'rfp_uploaded' in run_model_status
            v14 = 'exported' in run_model_status

            dashboard_status = 'Default/Messed Up'
            review_button = 'enabled'
            search_refinement_button = 'disabled'
            upload_button = 'disabled'
            # Priority 1 is processing status
            if v3 or (v12 and (v11 or v5 or v3)):
                dashboard_status = 'In Progress'
                review_button = 'disabled'
                search_refinement_button = 'disabled'

                # if RFP is timed out, set all responses to default response
                tc = TimerController()
                timeout = tc.get_timeout(sub_dict['expert_request_id'])
                if timeout:
                    self.process_timeout(sub_dict['expert_request_id'])
                    dashboard_status = 'Completed'
                    review_button = 'enabled'
                    search_refinement_button = 'disabled'


            # Priority 2 staged
            elif v12 and rm_len == 1:
                dashboard_status = 'In Progress'
                review_button = 'disabled'
                search_refinement_button = 'disabled'

                # Can timeout in Queued. if timed out, set all responses to default response
                tc = TimerController()
                timeout = tc.get_timeout(sub_dict['expert_request_id'])
                if timeout:
                    self.process_timeout(sub_dict['expert_request_id'])
                    dashboard_status = 'Completed'
                    review_button = 'enabled'
                    search_refinement_button = 'disabled'



            elif (v4 and p_len == 1 and rm_len == 1):
                dashboard_status = 'In Progress'
                review_button = 'disabled'
                search_refinement_button = 'enabled'

            elif v13:
                dashboard_status = 'In Progress'
                review_button = 'disabled'
                search_refinement_button = 'disabled'
                upload_button = 'enabled'
            elif v14:
                dashboard_status = 'Completed'
                review_button = 'enabled'
                search_refinement_button = 'disabled'
                upload_button = 'enabled'

            elif ((not v3) and (not v4) and (v1)):
                dashboard_status = 'Completed'
                review_button = 'enabled'
                search_refinement_button = 'disabled'
                if v10:
                    review_button = 'disabled'
            elif (v4 and v2 and p_len == 1):
                dashboard_status = 'Completed'
                review_button = 'enabled'
                search_refinement_button = 'disabled'
                if v10:
                    review_button = 'disabled'
            elif (v1 and p_len == 1 and v5):
                dashboard_status = 'Completed'
                review_button = 'enabled'
                search_refinement_button = 'disabled'
                if v10:
                    # review_button = 'disabled'
                    # If SME, dont allow edits to this rfp
                    review_button = 'disabled'
            # Uploaded, staged, PA Review, processed
            elif (v1 and v5 and v2 and v4):
                dashboard_status = 'Completed'
                review_button = 'enabled'
                search_refinement_button = 'disabled'
                if v10:
                    review_button = 'disabled'

            # PA review, processed, waiting, waiting
            elif (v6 and p_len == 1):
                dashboard_status = 'Ready for SME Review'
                review_button = 'enabled'
                search_refinement_button = 'disabled'
                if v9:
                    review_button = 'disabled'

            elif (v7 and p_len == 1):
                dashboard_status = 'Ready for PA Final Review'
                review_button = 'enabled'
                search_refinement_button = 'disabled'
                if v10:
                    review_button = 'disabled'

            elif (v8 and p_len == 1):

                num_completed += 1
                dashboard_status = 'Completed'
                review_button = 'enabled'
                search_refinement_button = 'disabled'

            sub_dict['review_button'] = review_button
            sub_dict['dashboard_status'] = dashboard_status
            sub_dict['search_refinement_button'] = search_refinement_button
            sub_dict['upload_button'] = upload_button
            del sub_dict['run_model_status']
            del sub_dict['process_status']
        for key in del_list:
            del rfp_dict[key]
        return rfp_dict, num_rfps, num_completed

    def new_dashboard_search(self, search_dictionary, upload_user_id):
        ''' Gets data for PA Dashboard '''
        try:

            pool = self.connect()
            # Execute DB as one interaction
            with pool.connect() as con:

                # Create sql for search restrictions and update dict with datetime vales
                search_dictionary, search_restrictions = self.create_search_string(search_dictionary)

                # Create sql query for return values of PA dashboard search
                sql = f"""
                SELECT expert_request_id, upload_time, account_name, process_status, run_model,
                 dashboard_status, review_button, search_refinement_button, name FROM {self.table_name}
                WHERE upload_user_id = "{upload_user_id}" AND status = TRUE """

                sql += search_restrictions

                sql += """
                ORDER BY upload_time DESC
                LIMIT 10000
                """

                query = sqlalchemy.text(sql)
                print(query)
                results = con.execute(query, search_dictionary)

                # Process output from search, and determine UI fields
                # Set of rfp data by expert request id
                rfp_dict = {}

                sort_val = 0
                # For each question
                for row in results:

                    rfp = list(row)
                    expert_request_id = rfp[0]
                    row_run_model = rfp[4]
                    row_process_status = rfp[3]

                    # If new rfp, add to dict
                    if not expert_request_id in rfp_dict:
                        sort_val += 1

                        # Determine UI 'processed' status
                        rfp_dict[expert_request_id] = {
                            "expert_request_id": expert_request_id,
                            "upload_time": rfp[1].date().strftime("%Y-%m-%d"),
                            "account_name": rfp[2],
                            "process_status": set(),
                            "run_model_status": set(),
                            "sort_val": sort_val,
                            "dashboard_status": rfp[5],
                            "review_button": rfp[6],
                            "search_refinement_button": rfp[7],
                            "rfp_name": rfp[8]
                        }

                    rfp_dict[expert_request_id]['process_status'].add(row_process_status)
                    rfp_dict[expert_request_id]['run_model_status'].add(row_run_model)

                sql2 = f"""SELECT COUNT(a.expert_request_id) AS total_uploaded_rfps, SUM(b.num_questions) AS total_generated_responses, AVG(b.runtime_seconds) AS avg_response_time FROM (SELECT DISTINCT expert_request_id FROM rfp_upload WHERE upload_user_id = "{upload_user_id}" AND status = TRUE {search_restrictions}) AS a JOIN (SELECT expert_request_id, MAX(TIMESTAMPDIFF(SECOND, model_start, model_end)) AS runtime_seconds, MAX(num_questions) AS num_questions FROM rfp_timing WHERE model_end IS NOT NULL AND model_start IS NOT NULL GROUP BY expert_request_id) AS b ON a.expert_request_id = b.expert_request_id;
"""

                print(sql2)
                query2 = sqlalchemy.text(sql2)
                results2 = con.execute(query2, search_dictionary)
                for stats in results2:
                    turfp, tgr, art = list(stats)

                    # Check if art is None
                    if art is not None:
                        # Convert art to MM:SS format
                        minutes, seconds = divmod(art, 60)
                        art_formatted = f"{int(minutes):02}:{int(seconds):02}"
                    else:
                        art_formatted = "00:00"  # Default value if art is None

                rfp_dict['stats'] = {}
                rfp_dict['stats']['total_uploaded_rfps'] = turfp
                rfp_dict['stats']['total_generated_responses'] = tgr
                rfp_dict['stats']['avg_response_time'] = art_formatted

                rfp_dict = self.process_dashboard_dict(rfp_dict)

            con.commit()
            con.close()
            return True, rfp_dict
        except Exception as e:
            traceback.print_exc()
            print('Error searching for pa dashboard data')
            return False, []