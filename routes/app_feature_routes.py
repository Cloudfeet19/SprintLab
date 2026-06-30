from database.models import db, AthleteTable
from forms.forms import ResultForm, AthleteForm
from flask import render_template, request, Blueprint, url_for, redirect
from flask_login import login_required, current_user
from sqlalchemy import select
from helpers.helpers import *


features_bp = Blueprint("feature", __name__)

# Complete -- May need upgrading
@features_bp.route("/add-result", methods=["GET", "POST"])
@login_required
def add_result():
    result_form = ResultForm()
    athlete_form = AthleteForm()

    athletes = db.session.execute(
        select(AthleteTable).where(AthleteTable.user_id == current_user.id)
    ).scalars().all()

    selected_athlete_id = request.form.get("athlete_id")

    if request.method == "POST":
        if selected_athlete_id == "new":
            valid = athlete_form.validate() and result_form.validate()
        else:
            valid = result_form.validate()

        if valid:
            if selected_athlete_id == "new":
                athlete = create_new_athlete(athlete_form, current_user)
                db.session.add(athlete)
                db.session.flush()
            else:
                athlete = db.session.get(
                    AthleteTable, selected_athlete_id
                )

            print(athlete.id, athlete.name)

            if athlete is None:
                flash("That athlete no longer exists. Please select another athlete.", "error")
                return redirect(url_for("feature.add_result"))

            result = get_result_data(result_form, athlete, current_user)

            db.session.add(result)
            db.session.commit()

            return redirect(url_for("feature.add_result"))

    return render_template("add_result.html", result_form=result_form, athlete_form=athlete_form, athletes=athletes)