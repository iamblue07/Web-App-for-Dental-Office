from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional

class PacientForm(FlaskForm):
    nume = StringField('Nume', validators=[
        DataRequired(message='Numele este obligatoriu.'),
        Length(min=2, max=50, message='Numele trebuie să aibă între 2 și 50 de caractere.')
    ])
    prenume = StringField('Prenume', validators=[
        DataRequired(message='Prenumele este obligatoriu.'),
        Length(min=2, max=50, message='Prenumele trebuie să aibă între 2 și 50 de caractere.')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email-ul este obligatoriu.'),
        Email(message='Introduceți un email valid.')
    ])
    telefon = StringField('Telefon', validators=[
        DataRequired(message='Telefonul este obligatoriu.'),
        Length(min=10, max=15, message='Telefonul trebuie să aibă între 10 și 15 caractere.')
    ])
    data_nasterii = DateField('Data nașterii', validators=[Optional()], format='%Y-%m-%d')
    adresa = StringField('Adresă', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Salvează')


class MedicForm(FlaskForm):
    nume = StringField('Nume', validators=[
        DataRequired(message='Numele este obligatoriu.'),
        Length(min=2, max=50, message='Numele trebuie să aibă între 2 și 50 de caractere.')
    ])
    prenume = StringField('Prenume', validators=[
        DataRequired(message='Prenumele este obligatoriu.'),
        Length(min=2, max=50, message='Prenumele trebuie să aibă între 2 și 50 de caractere.')
    ])
    specialitate = StringField('Specialitate', validators=[
        DataRequired(message='Specialitatea este obligatorie.'),
        Length(min=2, max=100)
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email-ul este obligatoriu.'),
        Email(message='Introduceți un email valid.')
    ])
    telefon = StringField('Telefon', validators=[
        Optional(),
        Length(min=10, max=15, message='Telefonul trebuie să aibă între 10 și 15 caractere.')
    ])
    submit = SubmitField('Salvează')


class ProgramareForm(FlaskForm):
    pacient_id = SelectField('Pacient', coerce=int, validators=[
        DataRequired(message='Selectați un pacient.')
    ])
    medic_id = SelectField('Medic', coerce=int, validators=[
        DataRequired(message='Selectați un medic.')
    ])
    data = DateField('Data', validators=[
        DataRequired(message='Data este obligatorie.')
    ], format='%Y-%m-%d')
    ora = SelectField('Ora', choices=[
        ('08:00', '08:00'), ('08:30', '08:30'),
        ('09:00', '09:00'), ('09:30', '09:30'),
        ('10:00', '10:00'), ('10:30', '10:30'),
        ('11:00', '11:00'), ('11:30', '11:30'),
        ('12:00', '12:00'), ('12:30', '12:30'),
        ('13:00', '13:00'), ('13:30', '13:30'),
        ('14:00', '14:00'), ('14:30', '14:30'),
        ('15:00', '15:00'), ('15:30', '15:30'),
        ('16:00', '16:00'), ('16:30', '16:30'),
    ], validators=[DataRequired()])
    motiv = TextAreaField('Motiv', validators=[
        DataRequired(message='Motivul este obligatoriu.'),
        Length(min=3, max=200)
    ])
    status = SelectField('Status', choices=[
        ('Programat', 'Programat'),
        ('Confirmat', 'Confirmat'),
        ('Anulat', 'Anulat'),
    ], validators=[DataRequired()])
    submit = SubmitField('Salvează')