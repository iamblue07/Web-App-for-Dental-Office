from app import create_app
from extensions import db
from models import Pacient, Medic, Programare
from datetime import date

app = create_app()

with app.app_context():
    db.create_all()
    print("Tabele create cu succes!")

    m1 = Medic(nume='Ionescu', prenume='Alexandru', specialitate='Ortodontie', email='alex.ionescu@stoma.ro', telefon='0721000001')
    m2 = Medic(nume='Popescu', prenume='Maria', specialitate='Chirurgie Orala', email='maria.popescu@stoma.ro', telefon='0721000002')

    p1 = Pacient(nume='Georgescu', prenume='Ion', email='ion.georgescu@email.com', telefon='0740000001', data_nasterii=date(1990, 5, 15))
    p2 = Pacient(nume='Dumitrescu', prenume='Ana', email='ana.dumitrescu@email.com', telefon='0740000002', data_nasterii=date(1985, 3, 22))

    db.session.add_all([m1, m2, p1, p2])
    db.session.flush()

    pr1 = Programare(data=date(2026, 5, 10), ora='10:00', motiv='Detartraj', status='Programat', pacient_id=p1.id, medic_id=m1.id)
    pr2 = Programare(data=date(2026, 5, 12), ora='14:00', motiv='Extractie', status='Programat', pacient_id=p2.id, medic_id=m2.id)

    db.session.add_all([pr1, pr2])
    db.session.commit()
    print("Date de test adăugate cu succes!")