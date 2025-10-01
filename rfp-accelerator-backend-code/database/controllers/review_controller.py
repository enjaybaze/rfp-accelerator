''' Module for managing review related operations '''
import sys
import sqlalchemy
sys.path.append('../')
from connection import Connection
from datetime import datetime


class ReviewController(Connection):
    ''' Operations on the RFPUpload Table '''

    def __init__(self):
        self.table_name = 'rfp_upload'
        self.pool = self.connect()

    def new_save_review_demo(self, dict_list, user_ldap, expert_request_id):
        ''' Saves data from PA review table row by row
        Also updates last_updated_user '''
        try:
            pool = self.connect()
            #Execute DB as one interaction
            with pool.connect() as con:
                #maybe many documents to be processed
                for dictionary in dict_list:
                    dictionary['user_ldap'] = user_ldap
                    dictionary['expert_request_id'] = expert_request_id



                    sql = f"""
                    UPDATE {self.table_name}
                    SET expert_request_id = :expert_request_id,
                    result1 = :response,
                    pa_feedback = :pa_feedback,
                    last_updated_user = :user_ldap,
                    pa_reviewer = :user_ldap,
                    pa_approve_reject_override = :pa_approve_reject_override
                    WHERE document_id = :question_id
                    """

                    query = sqlalchemy.text(sql)
                    con.execute(query, dictionary)


                con.commit()
                con.close()
                return True
        except sqlalchemy.exc.SQLAlchemyError:
            print('Error saving search refinements')
            return False


    def new_load_review_demo(self, expert_request_id, final_hit):
        ''' Gets review page data by expert request id. Has data for all review pages '''
        try:
            
            review_data = {}
            review_data['processed_data'] = []
            review_data['error_data'] = []
            review_data['waiting_data'] = []


            with self.pool.connect() as con:
                sql = f"""
                SELECT document_id, expert_request_id, account_name, question, search_refinement, page_name, result1, result2, result3, pa_final_response, pa_feedback, pa_approve_reject_override, sme_final_response, sme_feedback, sme_approve_reject_override, run_model FROM {self.table_name}
                WHERE expert_request_id = "{expert_request_id}"
                ORDER BY document_id
                """

                query = sqlalchemy.text(sql)
                results = con.execute(query)

                q_id = 0
                for row in results:
                    q_id +=1
                    quest = list(row)
                    data = {
                            "q_id": q_id,
                            "id":quest[0],
                            "expert_request_id":quest[1],
                            "account_name":quest[2],
                            "question":quest[3],
                            "search_refinement":quest[4],
                            "page_name":quest[5],
                            "result1":quest[6],
                            "result2": quest[7],
                            "result3":quest[8],
                            "pa_final_response": quest[9],
                            "pa_feedback": quest[10],
                            "pa_approve_reject_override": quest[11],
                            "sme_final_response":quest[12],
                            "sme_feedback":quest[13],
                            "sme_approve_reject_override":quest[14], 
                            "run_model_status": quest[15]
                        }

                    #Sort data by run_model_status
                    if quest[15] == 'processed' or quest[15] == 'exported' or quest[15] == 'downloaded':
                        review_data['processed_data'].append(data)
                    if quest[15] == 'error':
                        review_data['error_data'].append(data)
                    if quest[15] == 'waiting' or quest[15] == 'processing' or quest[15] == 'staged':
                        data['result1'] = 'Model is not responding for this question'
                        review_data['waiting_data'].append(data)

                sql2 = f"""
                SELECT model_start, model_end FROM rfp_timing
                WHERE expert_request_id = "{expert_request_id}" and rfp_timing.model_start IS NOT NULL
                """

                # Initialize variables
                model_start = datetime.now()
                model_end = datetime.now()

                query2 = sqlalchemy.text(sql2)
                results2 = con.execute(query2)

                record = results2.fetchone()

                # Check if the record exists
                if record:
                
                    model_start, model_end  = record

                # Convert to datetime objects if they are not already
                if model_start is not None and isinstance(model_start, str):
                    model_start = datetime.fromisoformat(model_start.replace('Z', '+00:00'))
                if model_end is None:
                    model_end = datetime.now()  # Use current time if model_end is null
                elif isinstance(model_end, str):
                    model_end = datetime.fromisoformat(model_end.replace('Z', '+00:00'))

                # Ensure both model_start and model_end are valid before calculating processing time
                print("modelstart: " + (model_start.strftime('%H:%M:%S') if model_start is not None else "empty"))
                print("modelend: " + (model_end.strftime('%H:%M:%S') if model_end is not None else "empty"))
                if model_start is not None and model_end is not None:
                    # Calculate processing time
                    process_time = model_end - model_start

                    # Convert processing time to MM:SS format
                    total_seconds = int(process_time.total_seconds())
                    minutes, seconds = divmod(total_seconds, 60)
                    processing_time = f"{minutes:02}:{seconds:02}"

                else:
                    processing_time = "00:00"  # Default value if model_start or model_end is None

            #Analyze data for payload output
            lwd = len(review_data['waiting_data'])
            led = len(review_data['error_data'])
            lpd = len(review_data['processed_data'])

            progress = 0
            if(led > 0 or lwd > 0 or lpd > 0):
                progress = 100 * (1- (lwd/(lwd+led+lpd)))

            model_failed = False
            error = led > 0
            model_finished = False

            if progress == 100:
                model_finished = True

            if final_hit:
                model_failed = progress < 100
                progress = 100
                model_finished = True

            metadata = {"progress": progress,
                        "model_failed": model_failed,
                        "error": error,
                        "model_finished": model_finished
                        }

            con.commit()
            con.close()

            #If it is the final hit, return all data, even waiting
            return review_data, metadata, processing_time
        except sqlalchemy.exc.SQLAlchemyError:
            print('Error loading review data')
            return [], {}


if __name__ == '__main__':
    r = ReviewController()
