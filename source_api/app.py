
from flask import Flask, request, send_from_directory, jsonify
import os
import threading
from Scraper import main
import time

app = Flask(__name__)

@app.route('/download-data', methods=['POST'])
def download_data():
    year = request.json.get('year')
    print(year)
    if not year:
        return jsonify({"error": "Year parameter is missing"}), 400

    # Run the Selenium script in a separate thread to avoid blocking the Flask server
    print("year")
    thread = threading.Thread(target=main, args=(year,))
    thread.start()

    # Assuming the script will take some time to download the file
    download_directory = os.path.join(os.getcwd(), "data")
    new_filename = f"{year}.csv"

    # Wait until the file exists
    while not os.path.exists(os.path.join(download_directory, new_filename)):
        time.sleep(1)

    # Return the file as a response
    return send_from_directory(directory=download_directory, path=new_filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)