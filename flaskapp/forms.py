from wtforms import Form, BooleanField, StringField, PasswordField, SubmitField, validators

class AddForm(Form):
    username = StringField('Book title')
    confirm = SubmitField('Add Book')
