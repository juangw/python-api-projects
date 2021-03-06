from rescue_groups.utils.call_rescue_group import api_post_req
from rescue_groups.models.parser import strip_tags
from rescue_groups.utils.all_fields import ALL_FIELDS
from rescue_groups.utils.db_ops import save_animal, remove_animal, list_saved_animals

from flask import current_app as app
from rescue_groups.utils.logger import log
from flask import render_template, request, redirect
from flask_login import current_user, login_required
from datetime import datetime
from dateutil.relativedelta import relativedelta
from collections import OrderedDict

import json

HALF_YEAR = datetime.now() + relativedelta(months=-6)
HALF_YEAR_FILTER = datetime.strftime(HALF_YEAR, "%m/%d/%y")

default_fields = [
    "animalName",
    "animalThumbnailUrl",
    "animalSex",
    "animalGeneralAge",
    "animalLocation",
    "locationAddress",
]


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect("/animals")
    return redirect("/login")


@app.route("/animals")
@login_required
def animals_home(page=1):
    error = ""
    default_filter = [
        {"fieldName": "animalSpecies", "operation": "equals", "criteria": "cat"},
        {"fieldName": "animalLocation", "operation": "equals", "criteria": "48105"},
        {"fieldName": "animalAdoptedDate", "operation": "blank"},
        {
            "fieldName": "animalUpdatedDate",
            "operation": "greaterthan",
            "criteria": HALF_YEAR_FILTER,
        },
    ]
    log.debug("Attempting to gather API data")
    start = (int(page) - 1) * 20
    results = api_post_req("rescue_group", start, default_filter, default_fields)
    if results is not None:
        result_dict = json.loads(results, object_pairs_hook=OrderedDict)
        return render_template(
            "animals.html",
            results=result_dict,
            page=page,
            adopted=None,
            save_animal=save_animal,
            limits=[start, start + 20],
        )
    else:
        return render_template("error.html", error=error)


@app.route("/saved-animals")
@login_required
def animals_saved():
    try:
        saved_animals = list_saved_animals()
        return render_template(
            "saved.html", results=saved_animals, count=len(saved_animals),
        )
    except Exception as e:
        return render_template("error.html", error=e)


@app.route("/animals/<page>", methods=["GET", "POST"])
@login_required
def animals_page_filter(page):
    gender = request.args.get("gender", request.form.get("gender"))
    location = request.args.get("location", request.form.get("location"))
    age = request.args.get("age", request.form.get("age"))
    distance = request.args.get("distance", request.form.get("distance"))
    adopted = request.args.get("adopted", request.form.get("adopted"))

    error = ""
    default_filter = [
        {"fieldName": "animalSpecies", "operation": "equals", "criteria": "cat"},
        {
            "fieldName": "animalUpdatedDate",
            "operation": "greaterthan",
            "criteria": HALF_YEAR_FILTER,
        },
    ]
    if age not in [None, "None"]:
        age_filter = {
            "fieldName": "animalGeneralAge",
            "operation": "equals",
            "criteria": age,
        }
        default_filter.append(age_filter)
    if gender not in [None, "None"]:
        gender_filter = {
            "fieldName": "animalSex",
            "operation": "equals",
            "criteria": gender,
        }
        default_filter.append(gender_filter)
    if adopted is None:
        adopted_filter = {"fieldName": "animalAdoptedDate", "operation": "blank"}
        default_filter.append(adopted_filter)
    if location not in ["", None]:
        location_filter = {
            "fieldName": "animalLocation",
            "operation": "equals",
            "criteria": location,
        }
        default_filter.append(location_filter)
    else:
        location_filter = {
            "fieldName": "animalLocation",
            "operation": "equals",
            "criteria": "48105",
        }
        default_filter.append(location_filter)
    if distance not in ["", "0", None]:
        distance_filter = {
            "fieldName": "animalLocationDistance",
            "operation": "equals",
            "criteria": distance,
        }
        default_filter.append(distance_filter)
    log.info(f"FILTER: {default_filter}\nPAGE: {page}")
    log.debug("Attempting to gather API data")
    start = (int(page) - 1) * 20
    results = api_post_req("rescue_group", start, default_filter, default_fields, True)
    if results is not None:
        result_dict = json.loads(results, object_pairs_hook=OrderedDict)
        return render_template(
            "animals.html",
            results=result_dict,
            page=page,
            age=age,
            gender=gender,
            adopted=adopted,
            location=location,
            distance=distance,
            save_animal=save_animal,
            limits=[start, start + 20],
        )
    else:
        return render_template("error.html", error=error)


@app.route("/animal/<animal_id>")
@login_required
def animal(animal_id):
    animal_filter = [
        {"fieldName": "animalID", "operation": "equals", "criteria": animal_id}
    ]
    default_fields = ALL_FIELDS
    log.debug("Attempting to gather API data")
    results = api_post_req("rescue_group", 0, animal_filter, default_fields)
    if results is not None:
        result_dict = json.loads(results, object_pairs_hook=OrderedDict)
        return render_template(
            "animal.html",
            results=result_dict,
            animal_id=animal_id,
            save_animal=save_animal,
            strip_tags=strip_tags,
        )
    else:
        return render_template("error.html")


@app.route("/save-animal/<animal_id>", methods=["GET"])
@login_required
def save_animals(animal_id):
    save_animal(animal_id)
    return "ok", 200


@app.route("/remove-animal/<animal_id>")
@login_required
def remove_animals(animal_id):
    remove_animal(animal_id)
    return "ok", 200
