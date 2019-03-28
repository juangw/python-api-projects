from common.utils.get_api_data import api_post_req
from flask import render_template

import connexion
import logging
import ast

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

logger.debug("Start of Program, Testing Debugger")

# Create the application instance
app = connexion.FlaskApp(__name__, specification_dir='openapi/')


@app.route("/")
def home():
    """
    This function just responds to the browser URL
    localhost:5000/

    :return:        the rendered template "home.html"
    """
    default_filter = [
        {
            "fieldName": "animalSpecies",
            "operation": "equals",
            "criteria": "cat"
        },
        {
            "fieldName": "animalLocation",
            "operation": "equals",
            "criteria": "48105"
        }
    ]
    default_fields = [
        "animalID",
        "animalOrgID",
        "locationPhone",
        "animalName",
        "animalThumbnailUrl",
        "animalPictures",
        "animalSex",
        "animalAdoptionFee",
        "animalBreed",
        "animalColor",
        "animalEyeColor",
        "animalAgeString",
        "animalLocation",
        "animalAffectionate",
        "animalApartment",
        "animalIntelligent",
        "animalLap",
        "animalActivityLevel"
    ]

    results = api_post_req("rescue_group", default_filter, default_fields)
    result_dict = ast.literal_eval(results)
    return render_template("home.html", results=result_dict)


def run():
    app.run(debug=True, host="0.0.0.0", port=8090)