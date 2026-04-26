from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from extensions import db
from models import Programare, Pacient, Medic
from forms import ProgramareForm
import json

programari_bp = Blueprint('programari', __name__, url_prefix='/programari')

@programari_bp.route('/')
def lista():
    filtru_status = request.args.get('status', '')
    filtru_medic = request.args.get('medic_id', '')

    query = Programare.query

    if filtru_status:
        query = query.filter(Programare.status == filtru_status)
    if filtru_medic:
        query = query.filter(Programare.medic_id == int(filtru_medic))

    programari = query.order_by(Programare.data.desc(), Programare.ora).all()
    medici = Medic.query.order_by(Medic.nume).all()

    programari_json = json.dumps([{
    'id': pr.id,
    'data': pr.data.strftime('%Y-%m-%d'),
    'ora': pr.ora,
    'ora_sfarsit': pr.ora_sfarsit or pr.ora,
    'medic_id': pr.medic_id,
    'medic': f'Dr. {pr.medic.nume} {pr.medic.prenume}',
    'pacient': f'{pr.pacient.nume} {pr.pacient.prenume}',
    'motiv': pr.motiv,
    'status': pr.status
    } for pr in programari])

    return render_template('programari/lista.html',
                           programari=programari,
                           medici=medici,
                           filtru_status=filtru_status,
                           filtru_medic=filtru_medic,
                           programari_json=programari_json)

@programari_bp.route('/nou', methods=['GET', 'POST'])
def nou():
    form = ProgramareForm()
    form.pacient_id.choices = [
        (p.id, f'{p.nume} {p.prenume}')
        for p in Pacient.query.order_by(Pacient.nume).all()
    ]
    form.medic_id.choices = [
        (m.id, f'Dr. {m.nume} {m.prenume} - {m.specialitate}')
        for m in Medic.query.order_by(Medic.nume).all()
    ]

    if form.validate_on_submit():
        ora_sfarsit = request.form.get('ora_sfarsit') or None
        programare = Programare(
            pacient_id=form.pacient_id.data,
            medic_id=form.medic_id.data,
            data=form.data.data,
            ora=form.ora.data,
            ora_sfarsit=ora_sfarsit,
            motiv=form.motiv.data,
            status=form.status.data
        )
        db.session.add(programare)
        db.session.commit()
        flash('Programare adăugată cu succes!', 'success')
        return redirect(url_for('programari.lista'))
    return render_template('programari/form.html', form=form, titlu='Programare nouă')

@programari_bp.route('/<int:id>/editeaza', methods=['GET', 'POST'])
def editeaza(id):
    programare = Programare.query.get_or_404(id)
    form = ProgramareForm(obj=programare)
    form.pacient_id.choices = [
        (p.id, f'{p.nume} {p.prenume}')
        for p in Pacient.query.order_by(Pacient.nume).all()
    ]
    form.medic_id.choices = [
        (m.id, f'Dr. {m.nume} {m.prenume} - {m.specialitate}')
        for m in Medic.query.order_by(Medic.nume).all()
    ]

    if form.validate_on_submit():
        ora_sfarsit = request.form.get('ora_sfarsit') or None
        programare.pacient_id = form.pacient_id.data
        programare.medic_id = form.medic_id.data
        programare.data = form.data.data
        programare.ora = form.ora.data
        programare.ora_sfarsit = ora_sfarsit
        programare.motiv = form.motiv.data
        programare.status = form.status.data
        db.session.commit()
        flash('Programare actualizată cu succes!', 'success')
        return redirect(url_for('programari.lista'))
    return render_template('programari/form.html', form=form, titlu='Editează programare',
                           programare=programare)

@programari_bp.route('/<int:id>/sterge', methods=['POST'])
def sterge(id):
    programare = Programare.query.get_or_404(id)
    db.session.delete(programare)
    db.session.commit()
    flash('Programare ștearsă cu succes!', 'success')
    return redirect(url_for('programari.lista'))


@programari_bp.route('/api/programari')
def api_programari():
    medic_id = request.args.get('medic_id', '')
    programari = Programare.query.all()
    rezultat = []
    for pr in programari:
        rezultat.append({
            'id': pr.id,
            'data': pr.data.strftime('%Y-%m-%d'),
            'ora': pr.ora,
            'ora_sfarsit': pr.ora_sfarsit or pr.ora,
            'medic_id': pr.medic_id,
            'medic': f'Dr. {pr.medic.nume} {pr.medic.prenume}',
            'pacient': f'{pr.pacient.nume} {pr.pacient.prenume}',
            'motiv': pr.motiv,
            'status': pr.status
        })
    return jsonify(rezultat)

from sqlalchemy import func

@programari_bp.route('/statistici')
def statistici():
    # Numar programari per medic
    programari_per_medic = db.session.query(
        Medic.nume,
        Medic.prenume,
        Medic.specialitate,
        func.count(Programare.id).label('total')
    ).join(Programare, Medic.id == Programare.medic_id)\
     .group_by(Medic.id, Medic.nume, Medic.prenume, Medic.specialitate)\
     .order_by(func.count(Programare.id).desc()).all()

    # Numar programari per status
    programari_per_status = db.session.query(
        Programare.status,
        func.count(Programare.id).label('total')
    ).group_by(Programare.status).all()

    # Top 5 pacienti cu cele mai multe programari
    top_pacienti = db.session.query(
        Pacient.nume,
        Pacient.prenume,
        func.count(Programare.id).label('total')
    ).join(Programare, Pacient.id == Programare.pacient_id)\
     .group_by(Pacient.id, Pacient.nume, Pacient.prenume)\
     .order_by(func.count(Programare.id).desc())\
     .limit(5).all()

    # Programari ordonate cronologic (urmatoarele 10)
    from datetime import date
    urmatoarele = Programare.query\
        .filter(Programare.data >= date.today())\
        .filter(Programare.status != 'Anulat')\
        .order_by(Programare.data.asc(), Programare.ora.asc())\
        .limit(10).all()

    return render_template('programari/statistici.html',
                           programari_per_medic=programari_per_medic,
                           programari_per_status=programari_per_status,
                           top_pacienti=top_pacienti,
                           urmatoarele=urmatoarele)