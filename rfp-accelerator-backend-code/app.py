import sys

sys.path.append('./database/')
sys.path.append('./database/controllers')
sys.path.append('./database/models')

import os
import flask
import traceback
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import jwt
from rfp_upload_controller import RFPUploadController
from dashboard_controller import DashboardController
from review_controller import ReviewController
from user_controller import UserController
from document import Document
from user import User
from config import Config

c = Config()
config = c.load_config()
app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": [config['frontend_url'], 'http://localhost:4200', 'http://localhost:3000']}})


@app.route("/")
def hello_world():
    return "Hello World"


def get_secret_key_v2():
    ''' Load secret key from secretmanager '''
    print('Getting secret key')
    config_obj = Config()
    secret_key = config_obj.load_jwt_secret_key()

    return secret_key


@app.route("/run_model", methods=['POST'])
def run_model():
    # Parse POST request
    entry = json.loads(request.data)
    data = entry['run']

    token = entry['token']
    auth, rsp = check_auth(token)
    if not auth:
        return process_auth()

    uc = get_rfp_upload_controller()

    updated = uc.advance_stage(data, "waiting", "waiting")

    model_called = True

    response_data = None
    try:
        if (updated and model_called):

            response_data = {'model_requested': True, 'message': 'Model run requested', 'status': 200,
                             'mimetype': 'application/json'}

        else:
            response_data = {'model_requested': False,
                             'message': 'Model run stayed in waiting stage. Try running the model again.',
                             'status': 401, 'mimetype': 'application/json'}


    except:
        response_data = {'model_requested': False, 'message': 'Error running model', 'status': 500,
                         'mimetype': 'application/json'}
    return jsonify(response_data)


@app.route("/new_save_review_demo", methods=['POST'])
def new_save_review_demo():
    # Parse POST request
    entry = json.loads(request.data)
    data_list = entry['save']
    user_ldap = entry['user_name']
    expert_request_id = entry['expert_request_id']

    token = entry['token']
    auth, rsp = check_auth(token)
    if not auth:
        return process_auth()

    rc = get_review_controller()
    updated = rc.new_save_review_demo(data_list, user_ldap, expert_request_id)

    response_data = None
    try:
        if (updated):

            response_data = {'Saved': True, 'message': 'Save Successful.', 'status': 200,
                             'mimetype': 'application/json'}

        else:
            response_data = {'Saved': False, 'message': 'Try Saving Again.', 'status': 401,
                             'mimetype': 'application/json'}


    except:
        response_data = {'Saved': False, 'message': 'Error saving', 'status': 500, 'mimetype': 'application/json'}
    return jsonify(response_data)


@app.route("/soft_remove", methods=['POST'])
def soft_remove():
    # Parse POST request
    entry = json.loads(request.data)
    erid = entry['expert_request_id']

    token = entry['token']
    auth, rsp = check_auth(token)
    if not auth:
        return process_auth()

    dc = get_dashboard_controller()

    removed = dc.soft_remove(erid)

    response_data = None
    try:
        if (removed):

            response_data = {'removed': True, 'message': 'Rfp status set to inactive', 'status': 200,
                             'mimetype': 'application/json'}

        else:
            response_data = {'removed': False, 'message': 'Rfp status unchanged. Try again', 'status': 401,
                             'mimetype': 'application/json'}


    except:
        response_data = {'removed': False, 'message': 'Error removing Rfp', 'status': 500,
                         'mimetype': 'application/json'}
    return jsonify(response_data)


@app.route("/new_load_review_demo", methods=['POST'])
def new_load_review_demo():
    # Parse POST request
    entry = json.loads(request.data)
    eid = entry['expert_request_id']
    final_hit = entry['final_hit']

    token = entry['token']
    auth, rsp = check_auth(token)
    if not auth:
        return process_auth()

    # Load the review
    rc = get_review_controller()
    review_data, metadata, processing_time = rc.new_load_review_demo(eid, final_hit)

    print(metadata)
    processed = metadata['model_finished']
    progress = metadata['progress']
    error = metadata['error']
    model_failed = metadata['model_failed']
    processing_time = processing_time

    response_data = None
    try:
        if (len(review_data) > 0):

            response_data = {'fetched': True, "Model_Finished": processed, "Model_Progress": progress,
                             "Model_Error": error, "Model_Failed": model_failed, "live_sec": processing_time,
                             "data": review_data, 'message': 'Review details fetched', 'status': 200,
                             'mimetype': 'application/json'}

        else:
            response_data = {'fetched': False, "Model_Finished": processed, "Model_Progress": progress,
                             "Model_Error": error, "Model_Failed": model_failed, "live_sec": processing_time,
                             "data": review_data, 'message': 'Data with that rfp_id not found in the database',
                             'status': 401, 'mimetype': 'application/json'}


    except:
        response_data = {'model_requested': False, "Model_Finished": processed, "Model_Progress": progress,
                         "Model_Error": error, "Model_Failed": model_failed, "live_sec": processing_time,
                         "data": review_data, 'message': 'Error fetching review details', 'status': 500,
                         'mimetype': 'application/json'}
    return jsonify(response_data)


@app.route("/new_dashboard_search", methods=['POST'])
def new_dashboard_search():
    ''' New dashboard search for new UI '''
    # Parse POST request
    entry = json.loads(request.data)

    data_list = entry['search']
    upload_user_id = entry['user_name']

    # Authorize
    token = entry['token']
    authed, rsp = check_auth(token)
    if not authed:
        return process_auth()
    del entry['token']

    dc = DashboardController()
    successful_search, search_results = dc.new_dashboard_search(data_list, upload_user_id)

    response_data = None
    try:
        if (successful_search):

            response_data = {'Searched': True, "data": search_results, 'message': 'search executed', 'status': 200,
                             'mimetype': 'application/json'}

        else:
            response_data = {'fetched': False, "data": search_results, 'message': 'Error Searching', 'status': 401,
                             'mimetype': 'application/json'}


    except:
        response_data = {'model_requested': False, "data": search_results,
                         'message': 'Error fetching PA review details', 'status': 500, 'mimetype': 'application/json'}
    # print(response_data)
    return jsonify(response_data)


@app.route('/new_upload_document', methods=['POST'])
def new_upload_document():
    ''' Upload document for new payload. Payload requires token, name, account_name, file_url, user_ldap '''
    # Parse POST request
    entry = json.loads(request.data)

    # #Authenticate
    token = entry['token']
    authed, rsp = check_auth(token)
    if not authed:
        return process_auth()

    uc = RFPUploadController()

    sheets_controller = None

    uploaded, msg, num_questions, expert_request_id = uc.new_upload_document(entry, sheets_controller)

    response_data = None
    try:
        if (uploaded):

            response_data = {'Uploaded': True, 'message': 'Upload Successful.', 'status': 200,
                             'num_questions': num_questions, 'expert_request_id': expert_request_id,
                             'mimetype': 'application/json'}

        elif (msg == 'duplicate'):
            response_data = {'Uploaded': False,
                             'message': 'The Request ID you have entered has already been utilized in a prior request. Please provide a unique Request ID.',
                             'status': 401, 'mimetype': 'application/json'}
        elif (msg == 'general'):
            response_data = {'Uploaded': False, 'message': 'An unknown error occured while uploading your RFP.',
                             'status': 401, 'mimetype': 'application/json'}

        elif (msg == 'access'):
            response_data = {'Uploaded': False,
                             'message': 'File is not accessible. Please clear your browser cache, and give consent to RFP-bot to manage google spreadsheets.',
                             'status': 401, 'mimetype': 'application/json'}

        elif (msg == 'sql'):
            response_data = {'Uploaded': False, 'message': 'Error loading data', 'status': 401,
                             'mimetype': 'application/json'}
        elif (msg == 'url'):
            response_data = {'Uploaded': False, 'message': 'Invalid file URL. Please enter a URL to a google sheet.',
                             'status': 401, 'mimetype': 'application/json'}
        elif (msg == 'formatting'):
            response_data = {'Uploaded': False,
                             'message': 'Formatting error. Make sure column A1 is "Question" and B1 is "Search Refinement" exactly for each sheet.',
                             'status': 401, 'mimetype': 'application/json'}
        elif (msg == 'empty'):
            response_data = {'Uploaded': False,
                             'message': 'There seems to be one or more empty tabs in the RFP file you are trying to upload. Please delete the same and retry.',
                             'status': 401, 'mimetype': 'application/json'}
        elif (msg == 'loading'):
            response_data = {'Uploaded': False,
                             'message': 'File is not accessible. Please clear your browser cache and give consent to RFP-bot to manage google spreadsheets, and ensure the sheet is not in .xlsx format.',
                             'status': 401, 'mimetype': 'application/json'}
        elif (msg == 'tabs'):
            response_data = {'Uploaded': False,
                             'message': 'RFP Accelerator can support files with a maximum of 20 tabs. Please reduce the number of tabs to proceed.',
                             'status': 401, 'mimetype': 'application/json'}
        elif (msg == 'hidden'):
            response_data = {'Uploaded': False,
                             'message': 'There seems to be one or more hidden tabs in the RFP file you are trying to upload. Please delete or unhide the tabs and retry.',
                             'status': 401, 'mimetype': 'application/json'}




        else:
            response_data = {'Uploaded': False, 'message': 'Error uploading. Try Again.', 'status': 401,
                             'mimetype': 'application/json'}


    except:
        response_data = {'Uploaded': False, 'message': 'Error uploading. Try Again', 'status': 500,
                         'mimetype': 'application/json'}
    return jsonify(response_data)


# Modified output of rfp_refinement for easier use with front end
@app.route('/rfp_refinement3', methods=['POST'])
def rfp_refinement3():
    # Parse POST request
    entry = json.loads(request.data)
    expert_request_id = list(entry.values())[0]

    # Auth Check
    token = entry['token']
    auth, rsp = check_auth(token)
    if not auth:
        return process_auth()

    uc = get_rfp_upload_controller()
    d = Document(expert_request_id=expert_request_id)

    account_name, questions = uc.rfp_refinement3(d)
    print(questions)

    response_data = None
    try:
        if (len(questions) > 0):
            response_data = {'Fetched': True, 'account_name': account_name, 'expert_request_id': expert_request_id,
                             'questions': questions, 'message': 'Questions and refinement retrieved successfully.',
                             'status': 200, 'mimetype': 'application/json'}

        else:
            response_data = {'Fetched': False, 'questions': None,
                             'message': 'No questions found. Try fetching questions and refinements again.',
                             'status': 401, 'mimetype': 'application/json'}


    except:
        response_data = {'Fetched': False, 'questions': None, 'message': 'Error fetching questions and refinements',
                         'status': 500, 'mimetype': 'application/json'}
    return jsonify(response_data)


@app.route('/welcome', methods=['POST'])
def check_user():
    # Parse ldap from POST request (json)
    entry = json.loads(request.data)

    ldap = list(entry.values())[0]
    pwd = list(entry.values())[1]

    uc = get_user_controller()
    user = User(ldap=ldap)

    # Boolean, user data
    in_db, user_data = uc.get_user(user, pwd)

    response_data = None

    print("userdata", user_data)

    try:
        # If user is in database, login
        if in_db:
            active = user_data[3]
            role = user_data[2]

            if active:
                print('getting token')
                token = get_auth_token(ldap)
                # token = "Disabled"
                print('Token got')
                # When successfully logged in, load session

                response_data = {'exists': True, 'message': 'User exists in the database.', 'status': 201,
                                 'mimetype': 'application/json', 'role': role, 'username': ldap, 'token': token}
            else:
                response_data = {'exists': False, 'message': 'User needs an active account to login.', 'status': 403,
                                 'mimetype': 'application/json', 'role': None, 'username': ldap}



        # Otherwise fail to login
        else:
            response_data = {'exists': False, 'message': 'User not found', 'status': 403,
                             'mimetype': 'application/json', 'role': None, 'ldap': ldap}



    except:
        response_data = {'exists': False, 'message': 'Error fetching user', 'status': 500,
                         'mimetype': 'application/json', 'role': None, 'ldap': ldap}

    return jsonify(response_data)


@app.route("/save_model_response", methods=['POST'])
def save_model_response():
    response_data = None

    try:
        # Parse POST request
        entry = json.loads(request.data, strict=False)
        data_list = entry['data']
        erid = entry['expert_request_id']
        action = entry['action']

        uc = get_rfp_upload_controller()

        print('hello')
        updated = uc.save_model_response(data_list, erid, action)

        if (updated):

            response_data = {'Saved': True, 'message': 'Save Successful.', 'status': 200,
                             'mimetype': 'application/json'}

        else:
            response_data = {'Saved': False, 'message': 'Error saving to SQL db.', 'status': 401,
                             'mimetype': 'application/json'}


    except Exception as e:
        response_data = {'Saved': False, 'message': 'Error saving', 'status': 500, 'mimetype': 'application/json'}
        traceback.print_exc()
    return jsonify(response_data)


@app.route('/download_file', methods=['POST'])
def download_file():
    ''' Download file button. This is /download_file_new in main api'''

    # Parse POST request
    entry = json.loads(request.data)
    expert_request_id = entry['expert_request_id']
    print('EXPERT REQ ID')
    print(expert_request_id)
    user_ldap = entry['user_name']
    token = entry['token']
    authed, rsp = check_auth(token)
    if not authed:
        return process_auth()

    sheets_controller = None

    uc = get_rfp_upload_controller()
    downloaded, url = uc.download_file_new(expert_request_id, user_ldap, sheets_controller)

    response_data = None
    try:
        if (downloaded):

            response_data = {'Downloaded': True, 'Link_to_sheet': url, 'message': 'Download Successful.', 'status': 200,
                             'mimetype': 'application/json'}
        elif url == 'incomplete':
            response_data = {'Downloaded': False,
                             'message': 'File not ready to export. One or more questions is incomplete.', 'status': 400,
                             'mimetype': 'application/json'}

        else:
            response_data = {'Downloaded': False, 'message': 'Try downloading again.', 'status': 401,
                             'mimetype': 'application/json'}


    except:
        response_data = {'Downloaded': False, 'message': 'Error downloading', 'status': 500,
                         'mimetype': 'application/json'}
    return jsonify(response_data)


@app.route('/run_model_question', methods=['POST'])
def run_model_question():
    # Parse POST request
    entry = json.loads(request.data)

    token = entry['token']
    auth, rsp = check_auth(token)
    if not auth:
        return process_auth()

    data_dict = entry
    print(data_dict)

    response_data = None

    uc = get_rfp_upload_controller()

    account_name, questions = uc.model_run_question(data_dict)

    try:
        if (len(questions) > 0):
            response_data = {'Fetched': True, 'account_name': account_name, 'questions': questions,
                             'message': 'Questions and refinement retrieved successfully.', 'status': 200,
                             'mimetype': 'application/json'}

        else:
            response_data = {'Fetched': False, 'questions': None,
                             'message': 'No questions found. Try fetching questions and refinements again.',
                             'status': 401, 'mimetype': 'application/json'}


    except:
        response_data = {'Fetched': False, 'questions': None, 'message': 'Error fetching questions and refinements',
                         'status': 500, 'mimetype': 'application/json'}
    return jsonify(response_data)


def check_auth(token):
    # Decode (verify) JWT
    secret_key = get_secret_key_v2()
    try:
        decoded_payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        # print("Decoded Payload:", decoded_payload)
        return True, 'Verified'
    except jwt.ExpiredSignatureError:
        print("Token has expired.")
        return False, 'Expired'
    except jwt.InvalidTokenError:
        print("Invalid token.")
        return False, 'Invalid'


def process_auth():
    response_data = {'Response': False, 'message': 'User not authenticated', 'status': 500,
                     'mimetype': 'application/json'}
    return response_data


def get_auth_token(ldap):
    try:
        payload = {
            'user_id': ldap,
        }

        secret_key = get_secret_key_v2()
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        return token
    except Exception as e:
        traceback.print_exc()


def get_dashboard_controller():
    ''' Load dashboard_controller into session. One to avoid memory leaking '''
    dc = None
    if not 'dashboard_controller' in flask.session:
        dc = DashboardController()
    return dc


def get_review_controller():
    ''' Load review_controller into session. One to avoid memory leaking '''
    if not 'review_controller' in flask.session:
        rc = ReviewController()
    return rc


def get_user_controller():
    ''' Load user_controller into session. One to avoid memory leaking '''
    uc = None
    if not 'user_controller' in flask.session:
        uc = UserController()
    return uc


def get_rfp_upload_controller():
    ''' Load rfp_upload_controller into session. One to avoid memory leaking '''
    rc = None
    if not 'rfp_upload_controller' in flask.session:
        rc = RFPUploadController()
    return rc


if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(host='localhost', port='8000', debug=True)
