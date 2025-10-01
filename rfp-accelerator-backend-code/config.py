from google.cloud import secretmanager
import json


class Config:

    def __init__(self):
        self.config = self.load_config()

    def load_jwt_secret_key(self):
        client = secretmanager.SecretManagerServiceClient()
        config = self.load_config()
        name = f"projects/{config['project_id']}/secrets/{config['secret_name']}/versions/1"
        request = {"name": name}
        # Make the request
        response = client.access_secret_version(request=request)
        payload = response.payload.data.decode("UTF-8")
        return payload

    def load_config(self):
        ''' reads config file '''
        FILE_NAME = 'config.txt'
        file = open(FILE_NAME, "r")
        config = {}
        while True:
            content = file.readline()
            if not content:
                break
            key_val_pair = content.split('=')
            key = key_val_pair[0]
            val = key_val_pair[1].strip()  # Ignore newline character
            config[key] = val

        file.close()
        return config


if __name__ == '__main__':
    c = Config()
    print(c.config)
