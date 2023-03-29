# API

The API was developed fully in Python using Python 3.10. Older versions may have compatibility issues and as such, it is strongly recommended you use the same version.

The project has the following packages as dependencies:

- Flask, installed using "pip install Flask"
- Flask-RESTx, installed using "pip install flask-restx"
- Flask-CORS, installed using "pip install -U flask-cors"
- OpenPyXL, installed using "pip install openpyxl"
  Once all of those packages are installed, you're ready to go.

The API folder contains the Excel spreadsheet and 5 Python Files, all of which are required to run the app. The main 'driver' of the project is the **'flask_app.py'** file and as such, to run the project you can either do so with the GUI of your IDE of choice, or you can navigate to the folder in your command line or terminal and execute **"python flask_app.py"**.

The documentation for the API should open at both "http://127.0.0.1:5000/" and "http://localhost:5000", and any HTTP requests can be made to the URLs detailed in the documentation.

## Testing

To run the unit tests, you can execute the command **"python -m unittest helper_tests"** in the terminal within the directory of the python files, and it will run all 14 unit tests for the helper functions.
