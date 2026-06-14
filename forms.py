from wsgiref.validate import validator
import numpy as np
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, SelectField, PasswordField, EmailField, BooleanField, DateField
from wtforms.validators import DataRequired, InputRequired, NumberRange, Email, EqualTo, Length
import json

events = ["60m", "60mH", "100m", "100mH", "110mH", "200m", "300mH", "400m", "800m", "1600m", "3200m", "Long Jump", "Triple Jump", "High Jump", "Javelin", "Pole Vault", "Shot Put", "Discus"]
genders = ["Male", "Female"]
athletes_class = str(list(np.arange(2006,2035)))

class ResultForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    gender = SelectField("Gender", choices=["Male", "Female"], validators=[DataRequired()])
    athlete_class = SelectField("Graduation Class", choices=athletes_class, validators=[DataRequired()])
    event = SelectField("Event", choices=events, validators=[DataRequired()])
    result = StringField("Result", validators=[DataRequired()])
    wind = StringField("Wind Reading")
    placement = StringField("Place")
    date = DateField("Date", format="%Y-%m-%d", validators=[DataRequired()])
    meet = StringField("Meet", validators=[DataRequired()])
    atmosphere = SelectField("Atmosphere", choices=["Indoor", "Outdoor"], validators=[DataRequired()])
    race_type = SelectField("Result Type", choices=["Finals", "Prelims"], validators=[DataRequired()])
    season = StringField("Season", validators=[DataRequired()])
    performance_type = SelectField(
        "Performance Type",
        choices=["Official", "Practice", "Split - Official"],
        validators=[DataRequired()]
    )
    submit = SubmitField("Submit Result")