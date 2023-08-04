from flask import Flask, render_template, request
from .perform_queries import perform_query, VarAIException

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')


@app.route('/bysql', methods=['POST'])
def query_by_sql():
    return 'Not implemented yet', 501


@app.route('/bynl', methods=['POST'])
def query_by_nl():
    data = request.get_data()
    if not data:
        return "No data passed", 400

    try:
        return perform_query(data.decode())
    except VarAIException as err:
        return str(err), err.error_code
    except Exception as err:
        return "An unknown error occurred: " + str(err), 500
