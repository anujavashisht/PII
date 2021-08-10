from flask import Flask
from flask import request
from flask.helpers import send_from_directory
from flask_cors import CORS, cross_origin
import shutil
import stat
import os

from helper import *


app = Flask(__name__, static_folder='./frontend/build', static_url_path='')
cors = CORS(app)


def removing_git(path):
    for root, dirs, files in os.walk(path):
        for dir in dirs:
            os.chmod(os.path.join(root, dir), stat.S_IRWXU)
        for file in files:
            os.chmod(os.path.join(root, file), stat.S_IRWXU)
    shutil.rmtree(path)


@app.route('/')
@cross_origin()
def index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/get_pii', methods=['POST'])
@cross_origin()
def get_pii():
    if request.method == 'POST':
        url = request.json['url']
        print(url)
        repo_path = clone_repo(url)
        data = get_text_from_repo_files(repo_path)
        data = get_pii_data(data)

        row_count = data.shape[0]
        column_count = data.shape[1]
        column_names = data.columns.tolist()
        row_data = []

        for index, rows in data.iterrows():
            row_data.append(rows.to_dict())

        json_result = {'rows': row_count, 'cols': column_count,
                       'columns': column_names, 'rowData': row_data}

        removing_git(repo_path)
        return json_result


if __name__ == '__main__':
    app.run()
