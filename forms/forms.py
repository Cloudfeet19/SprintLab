from wsgiref.validate import validator
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, FloatField, SelectField, PasswordField, EmailField, BooleanField, DateField
from wtforms.validators import DataRequired, NumberRange, Email, EqualTo, Length

TRACK_EVENTS = ["60m", "60mH", "100m", "100mH", "110mH", "200m", "300mH", "400m", "800m", "1600m", "3200m"]
FIELD_EVENTS = ["Long Jump", "Triple Jump", "High Jump", "Javelin", "Pole Vault", "Shot Put", "Discus"]
ALL_EVENTS = TRACK_EVENTS + FIELD_EVENTS

genders = ["Male", "Female"]

athletes_class = list(range(2035, 1960, -1))
grades = list(range(6,13))

class AthleteForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    gender = SelectField("Gender", choices=["Male", "Female"], validators=[DataRequired()])
    athlete_class = SelectField("Graduation Class", choices=athletes_class, validators=[DataRequired()])

class ResultForm(FlaskForm):
    grade = SelectField("Grade", choices=grades, validators=[DataRequired()])
    event = SelectField("Event", choices=ALL_EVENTS, validators=[DataRequired()])
    result = StringField("Result", validators=[DataRequired()])
    wind = FloatField("Wind Reading")
    placement = IntegerField("Place", validators=[DataRequired()])
    date = DateField("Date", format="%Y-%m-%d", validators=[DataRequired()])
    meet = StringField("Meet", validators=[DataRequired()])
    atmosphere = SelectField("Atmosphere", choices=["Indoor", "Outdoor"], validators=[DataRequired()])
    race_type = SelectField("Result Type", choices=["Finals", "Prelims"], validators=[DataRequired()])
    performance_type = SelectField(
        "Performance Type",
        choices=["Official", "Practice", "Split - Official"],
        validators=[DataRequired()]
    )
    submit = SubmitField("Submit Result")
