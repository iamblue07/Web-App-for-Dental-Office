from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db
from models import Pacient, Programare
from forms import PacientForm

pacienti_bp = Blueprint('pacienti', __name__, url_prefix='/pacienti')


@pacienti_bp.route('/')
def lista():
    cautare = request.args.get('cautare', '')
    if cautare:
        pacienti = Pacient.query.filter(
            (Pacient.nume.ilike(f'%{cautare}%')) |
            (Pacient.prenume.ilike(f'%{cautare}%')) |
            (Pacient.email.ilike(f'%{cautare}%'))
        ).order_by(Pacient.nume).all()
    else:
        pacienti = Pacient.query.order_by(Pacient.nume).all()
    return render_template('pacienti/lista.html', pacienti=pacienti, cautare=cautare)


@pacienti_bp.route('/<int:id>')
def profil(id):
    pacient = Pacient.query.get_or_404(id)
    programari = Programare.query.filter_by(pacient_id=id)\
        .order_by(Programare.data.desc(), Programare.ora.desc()).all()
    return render_template('pacienti/profil.html', pacient=pacient, programari=programari)


@pacienti_bp.route('/nou', methods=['GET', 'POST'])
def nou():
    form = PacientForm()
    if form.validate_on_submit():
        pacient = Pacient(
            nume=form.nume.data,
            prenume=form.prenume.data,
            email=form.email.data,
            telefon=form.telefon.data,
            data_nasterii=form.data_nasterii.data,
            adresa=form.adresa.data
        )
        db.session.add(pacient)
        db.session.commit()
        flash('Pacient adăugat cu succes!', 'success')
        return redirect(url_for('pacienti.profil', id=pacient.id))
    return render_template('pacienti/form.html', form=form, titlu='Pacient nou')


@pacienti_bp.route('/<int:id>/editeaza', methods=['GET', 'POST'])
def editeaza(id):
    pacient = Pacient.query.get_or_404(id)
    form = PacientForm(obj=pacient)
    if form.validate_on_submit():
        pacient.nume = form.nume.data
        pacient.prenume = form.prenume.data
        pacient.email = form.email.data
        pacient.telefon = form.telefon.data
        pacient.data_nasterii = form.data_nasterii.data
        pacient.adresa = form.adresa.data
        db.session.commit()
        flash('Date pacient actualizate cu succes!', 'success')
        return redirect(url_for('pacienti.profil', id=pacient.id))
    return render_template('pacienti/form.html', form=form, titlu='Editează pacient')


@pacienti_bp.route('/<int:id>/sterge', methods=['POST'])
def sterge(id):
    pacient = Pacient.query.get_or_404(id)
    db.session.delete(pacient)
    db.session.commit()
    flash('Pacient șters cu succes!', 'success')
    return redirect(url_for('pacienti.lista'))