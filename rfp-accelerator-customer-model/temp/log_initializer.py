import sys
import google.cloud.logging
project_name = sys.argv[1]
client = google.cloud.logging.Client(project=project_name)
logger = client.logger(name="Req-Prop-Application-runtime")
logger.log("A simple entry")