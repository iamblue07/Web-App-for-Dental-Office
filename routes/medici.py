from flask import Blueprint, render_template, redirect, url_for, flash
from extensions import db
from models import Medic
from forms import MedicForm

medici_bp = Blueprint('medici', __name__, url_prefix='/medici')


@medici_bp.route('/')
def lista():
    medici = Medic.query.order_by(Medic.nume).all()
    return render_template('medici/lista.html', medici=medici)


@medici_bp.route('/<int:id>')
def profil(id):
    medic = Medic.query.get_or_404(id)
    return render_template('medici/profil.html', medic=medic)


@medici_bp.route('/nou', methods=['GET', 'POST'])
def nou():
    form = MedicForm()
    if form.validate_on_submit():
        medic = Medic(
            nume=form.nume.data,
            prenume=form.prenume.data,
            specialitate=form.specialitate.data,
            email=form.email.data,
            telefon=form.telefon.data
        )
        db.session.add(medic)
        db.session.commit()
        flash('Medic adăugat cu succes!', 'success')
        return redirect(url_for('medici.profil', id=medic.id))
    return render_template('medici/form.html', form=form, titlu='Medic nou')


@medici_bp.route('/<int:id>/editeaza', methods=['GET', 'POST'])
def editeaza(id):
    medic = Medic.query.get_or_404(id)
    form = MedicForm(obj=medic)
    if form.validate_on_submit():
        medic.nume = form.nume.data
        medic.prenume = form.prenume.data
        medic.specialitate = form.specialitate.data
        medic.email = form.email.data
        medic.telefon = form.telefon.data
        db.session.commit()
        flash('Date medic actualizate cu succes!', 'success')
        return redirect(url_for('medici.profil', id=medic.id))
    return render_template('medici/form.html', form=form, titlu='Editează medic')


@medici_bp.route('/<int:id>/sterge', methods=['POST'])
def sterge(id):
    medic = Medic.query.get_or_404(id)
    db.session.delete(medic)
    db.session.commit()
    flash('Medic șters cu succes!', 'success')
    return redirect(url_for('medici.lista'))