from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Regexp

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=150)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long.'),
        Regexp(r'(?=.*[A-Z])(?=.*[0-9])(?=.*[@$!%*?&])', message='Password must contain at least one uppercase letter, one number, and one special character.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    
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

    def __init__(self, *args, **kwargs):
        self.original_name = kwargs.pop('original_name', None)
        super(AssetForm, self).__init__(*args, **kwargs)

    def validate_name(self, field):
        if field.data != self.original_name:
            from app import Asset
            asset = Asset.query.filter_by(name=field.data).first()
            if asset:
                raise ValidationError('An asset with this name already exists.')