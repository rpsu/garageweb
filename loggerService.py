import os.path, threading, datetime
from datetime import datetime
from flask import Flask, request, jsonify

fileName = os.path.basename(__file__)
verboseConsole = True
debug = True

lock = threading.Lock()
logFilePath = "/home/pi/GarageWeb/static/log.txt"
app = Flask(__name__)
listen_to_ip = '127.0.0.1'
listen_to_port = 5081

def write(msg, fileName):
    global verboseConsole, logFilePath

    with lock:
        try:
          logfile = open(logFilePath, "a")
          msg = (datetime.now().strftime("%Y-%m-%d %H:%M:%S [" + fileName + "] - - " + msg + "\n"))
          charsWritten = logfile.write(msg)
          logfile.close()

          if verboseConsole:
              print(msg)
          if charsWritten < len(msg):
              raise Exception('Mismatch in msg len provided and written')
        except Exception as e:
          raise e

    return charsWritten > 0



@ app.route('/new', methods=['POST'])
def addLogEntry():
    msg = request.form['log_entry']
    fileName = request.form['source']
    try:
        write(msg, fileName)
        return jsonify({'message': 'success'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    msg= f'Starting logger service from {fileName} '
    msg=msg + "(debug: " + str(debug) + ")!"
    write(msg, fileName)
    app.run(host=listen_to_ip, port=listen_to_port, debug=debug)
