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


"""
class AuthBaseForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired("password required"),
                                                     Length(min=8, message="Password must be at least 8 characters long.")])
class LoginForm(AuthBaseForm):
    remember_me = BooleanField()
    submit = SubmitField("Log In")

class RegistrationForm(AuthBaseForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    confirm_password = PasswordField("Re-Type Password", validators=[DataRequired(), EqualTo(fieldname="password", message="Passwords must match.")])
    register_button = SubmitField("Sign Up")

class BaseRatingForm(FlaskForm):
    title = SelectField("Title", validators=[DataRequired("Select A Title")])
    character_quality = FloatField('Character Quality', validators=[InputRequired("Choose a number from 0 to 10"), NumberRange(min=0.0, max=11.0)])
    plot_quality = FloatField('Plot Quality', validators=[InputRequired("Choose a number from 0 to 10"), NumberRange(min=0.0, max=11.0)])
    submit = SubmitField(label="Submit Rating")

    def __init__(self, *args, mode: str = "create", **kwargs):
        super().__init__(*args, **kwargs)
        if mode == "update":
            # remove title for update forms
            if hasattr(self, "title"):
                del self.title

class MarvelMovieRatingForm(BaseRatingForm):
    title = SelectField("Title", choices=[(json.dumps(movie), movie["title"]) for movie in all_mcu_movies], validators=[DataRequired("Select A Title")])
    mcu_relevance = FloatField('MCU Relevance', validators=[InputRequired("Choose a number from 0 to 10"), NumberRange(min=0.0, max=11.0)])

    def __init__(self):
        self.franchise = "marvel"

    def get_franchise(self):
        return self.franchise

class XMenRatingForm(BaseRatingForm):
    title = SelectField("Title", choices=[(movie,movie.title()) for movie in all_xmen_movies], validators=[DataRequired("Select A Title")])
    action_quality = FloatField('Action Quality', validators=[InputRequired("Choose a number from 0 to 10"), NumberRange(min=0.0, max=11.0)])

    def __init__(self):
        self.franchise = "xmen"

    def get_franchise(self):
        return self.franchise
"""