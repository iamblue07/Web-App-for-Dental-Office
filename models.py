from extensions import db

class Pacient(db.Model):
    __tablename__ = 'pacienti'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nume = db.Column(db.String(50), nullable=False)
    prenume = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telefon = db.Column(db.String(15), nullable=False)
    data_nasterii = db.Column(db.Date, nullable=True)
    adresa = db.Column(db.String(200), nullable=True)

    programari = db.relationship('Programare', backref='pacient', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Pacient {self.nume} {self.prenume}>'


class Medic(db.Model):
    __tablename__ = 'medici'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nume = db.Column(db.String(50), nullable=False)
    prenume = db.Column(db.String(50), nullable=False)
    specialitate = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telefon = db.Column(db.String(15), nullable=True)

    programari = db.relationship('Programare', backref='medic', lazy=True)

    def __repr__(self):
        return f'<Medic Dr. {self.nume} {self.prenume}>'


class Programare(db.Model):
    __tablename__ = 'programari'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data = db.Column(db.Date, nullable=False)
    ora = db.Column(db.String(5), nullable=False)
    ora_sfarsit = db.Column(db.String(5), nullable=True)
    motiv = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Programat')

    pacient_id = db.Column(db.Integer, db.ForeignKey('pacienti.id'), nullable=False)
    medic_id = db.Column(db.Integer, db.ForeignKey('medici.id'), nullable=False)

    def __repr__(self):
        return f'<Programare {self.data} {self.ora} - {self.status}>'