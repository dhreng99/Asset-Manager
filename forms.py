from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=150)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    
    def validate_username(self, username):
        from app import User
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class AssetForm(FlaskForm):
    name = StringField('Asset Name', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Length(max=500)])

    def validate_name(self, field):
        from app import Asset
        if Asset.query.filter_by(name=field.data).first():
            raise ValidationError('An asset with this name already exists.')