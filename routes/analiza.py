import os
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import io
import base64

from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename

analiza_bp = Blueprint('analiza', __name__, url_prefix='/analiza')

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'csv'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=120)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_base64

def get_df():
    path = os.path.join(UPLOAD_FOLDER, 'instrumente.csv')
    if not os.path.exists(path):
        return None
    try:
        df = pd.read_csv(path, encoding='utf-8-sig')
        return df
    except Exception:
        return None

@analiza_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'fisier' not in request.files:
            flash('Nu a fost selectat niciun fișier.', 'danger')
            return redirect(url_for('analiza.index'))
        file = request.files['fisier']
        if file.filename == '':
            flash('Nu a fost selectat niciun fișier.', 'danger')
            return redirect(url_for('analiza.index'))
        if file and allowed_file(file.filename):
            path = os.path.join(UPLOAD_FOLDER, 'instrumente.csv')
            file.save(path)
            flash('Fișier CSV încărcat cu succes!', 'success')
            return redirect(url_for('analiza.sumar'))
        else:
            flash('Doar fișiere CSV sunt acceptate.', 'danger')
    df = get_df()
    return render_template('analiza/index.html', fisier_exista=df is not None)


@analiza_bp.route('/sumar')
def sumar():
    df = get_df()
    if df is None:
        flash('Te rugăm să încarci mai întâi un fișier CSV.', 'warning')
        return redirect(url_for('analiza.index'))

    # Statistici generale
    stats = {
        'total_randuri': len(df),
        'total_coloane': len(df.columns),
        'coloane': list(df.columns),
        'valori_lipsa': df.isnull().sum().to_dict(),
        'tipuri': df.dtypes.astype(str).to_dict(),
    }

    # Statistici numerice
    numerice = df.select_dtypes(include='number')
    desc = numerice.describe().round(2).to_dict() if not numerice.empty else {}

    # Previzualizare primele 10 randuri
    preview = df.head(10).to_dict(orient='records')
    coloane = list(df.columns)

    return render_template('analiza/sumar.html',
                           stats=stats,
                           desc=desc,
                           preview=preview,
                           coloane=coloane)


@analiza_bp.route('/grafic', methods=['GET', 'POST'])
def grafic():
    df = get_df()
    if df is None:
        flash('Te rugăm să încarci mai întâi un fișier CSV.', 'warning')
        return redirect(url_for('analiza.index'))

    coloane_numerice = list(df.select_dtypes(include='number').columns)
    coloane_categorice = list(df.select_dtypes(include='object').columns)
    coloane_toate = list(df.columns)

    img = None
    tip_grafic = request.form.get('tip_grafic', '')
    col_x = request.form.get('col_x', '')
    col_y = request.form.get('col_y', '')
    eroare = None

    tipuri_grafice = [
        ('histograma', 'Histogramă'),
        ('boxplot', 'Box Plot'),
        ('bar_medie', 'Bar Chart - Medie pe categorie'),
        ('bar_total', 'Bar Chart - Total pe categorie'),
        ('scatter', 'Scatter Plot'),
        ('pie', 'Pie Chart'),
        ('linie_timp', 'Evoluție în timp'),
    ]

    if request.method == 'POST' and tip_grafic and col_x:
        try:
            sns.set_theme(style='whitegrid')
            fig, ax = plt.subplots(figsize=(12, 6))

            if tip_grafic == 'histograma':
                if col_x not in coloane_numerice:
                    eroare = f'Coloana "{col_x}" trebuie să fie numerică pentru histogramă.'
                else:
                    sns.histplot(df[col_x].dropna(), bins=30, kde=True, ax=ax, color='steelblue')
                    ax.set_title(f'Distribuția valorilor — {col_x}', fontsize=14)
                    ax.set_xlabel(col_x)
                    ax.set_ylabel('Frecvență')

            elif tip_grafic == 'boxplot':
                if col_x not in coloane_numerice:
                    eroare = f'Coloana "{col_x}" trebuie să fie numerică pentru box plot.'
                else:
                    if col_y and col_y in coloane_categorice:
                        top_cat = df[col_y].value_counts().head(10).index
                        df_f = df[df[col_y].isin(top_cat)]
                        sns.boxplot(data=df_f, x=col_y, y=col_x, ax=ax, palette='Set2')
                        ax.set_title(f'Box Plot — {col_x} pe {col_y}', fontsize=14)
                        plt.xticks(rotation=30, ha='right')
                    else:
                        sns.boxplot(y=df[col_x].dropna(), ax=ax, color='steelblue')
                        ax.set_title(f'Box Plot — {col_x}', fontsize=14)

            elif tip_grafic == 'bar_medie':
                if not col_y or col_y not in coloane_numerice:
                    eroare = 'Selectează o coloană numerică pentru axa Y.'
                elif col_x not in coloane_categorice:
                    eroare = 'Selectează o coloană categorică pentru axa X.'
                else:
                    data = df.groupby(col_x)[col_y].mean().sort_values(ascending=False).head(15)
                    bars = ax.bar(data.index, data.values, color=sns.color_palette('Set2', len(data)))
                    ax.bar_label(bars, fmt='%.1f', padding=3, fontsize=9)
                    ax.set_title(f'Media {col_y} pe {col_x}', fontsize=14)
                    ax.set_xlabel(col_x)
                    ax.set_ylabel(f'Media {col_y}')
                    plt.xticks(rotation=30, ha='right')

            elif tip_grafic == 'bar_total':
                if col_x not in coloane_categorice:
                    eroare = 'Selectează o coloană categorică pentru axa X.'
                elif col_y and col_y in coloane_numerice:
                    data = df.groupby(col_x)[col_y].sum().sort_values(ascending=False).head(15)
                    bars = ax.bar(data.index, data.values, color=sns.color_palette('Set3', len(data)))
                    ax.bar_label(bars, fmt='%.0f', padding=3, fontsize=9)
                    ax.set_title(f'Total {col_y} pe {col_x}', fontsize=14)
                    ax.set_xlabel(col_x)
                    ax.set_ylabel(f'Total {col_y}')
                    plt.xticks(rotation=30, ha='right')
                else:
                    data = df[col_x].value_counts().head(15)
                    bars = ax.bar(data.index, data.values, color=sns.color_palette('Set3', len(data)))
                    ax.bar_label(bars, padding=3, fontsize=9)
                    ax.set_title(f'Număr înregistrări pe {col_x}', fontsize=14)
                    ax.set_xlabel(col_x)
                    ax.set_ylabel('Număr')
                    plt.xticks(rotation=30, ha='right')

            elif tip_grafic == 'scatter':
                if not col_y:
                    eroare = 'Selectează o coloană pentru axa Y.'
                elif col_x not in coloane_numerice or col_y not in coloane_numerice:
                    eroare = 'Ambele coloane trebuie să fie numerice pentru scatter plot.'
                else:
                    sns.scatterplot(data=df, x=col_x, y=col_y, ax=ax,
                                    alpha=0.6, color='steelblue')
                    ax.set_title(f'Scatter: {col_x} vs {col_y}', fontsize=14)

            elif tip_grafic == 'pie':
                if col_x not in coloane_categorice:
                    eroare = 'Selectează o coloană categorică pentru pie chart.'
                else:
                    data = df[col_x].value_counts().head(10)
                    ax.pie(data.values, labels=data.index, autopct='%1.1f%%',
                           colors=sns.color_palette('Set2', len(data)),
                           startangle=90)
                    ax.set_title(f'Distribuție — {col_x}', fontsize=14)
                    ax.axis('equal')

            elif tip_grafic == 'linie_timp':
                col_data = [c for c in df.columns if 'data' in c.lower() or 'date' in c.lower()]
                if not col_data:
                    eroare = 'Nu s-a găsit o coloană de tip dată în CSV.'
                else:
                    col_dt = col_data[0]
                    df_t = df.copy()
                    df_t[col_dt] = pd.to_datetime(df_t[col_dt], errors='coerce')
                    df_t = df_t.dropna(subset=[col_dt])
                    df_t['Luna'] = df_t[col_dt].dt.to_period('M')
                    if col_x in coloane_numerice:
                        data = df_t.groupby('Luna')[col_x].sum().reset_index()
                        data['Luna'] = data['Luna'].astype(str)
                        ax.plot(data['Luna'], data[col_x], marker='o', color='steelblue', linewidth=2)
                        ax.set_title(f'Evoluție {col_x} în timp', fontsize=14)
                        ax.set_ylabel(col_x)
                    else:
                        data = df_t.groupby('Luna').size().reset_index(name='count')
                        data['Luna'] = data['Luna'].astype(str)
                        ax.plot(data['Luna'], data['count'], marker='o', color='steelblue', linewidth=2)
                        ax.set_title('Număr achiziții pe lună', fontsize=14)
                        ax.set_ylabel('Număr')
                    plt.xticks(rotation=45, ha='right')
                    ax.set_xlabel('Luna')

            if not eroare:
                img = fig_to_base64(fig)
            else:
                plt.close(fig)

        except Exception as e:
            eroare = f'Eroare la generarea graficului: {str(e)}'
            plt.close('all')

    return render_template('analiza/grafic.html',
                           coloane_numerice=coloane_numerice,
                           coloane_categorice=coloane_categorice,
                           coloane_toate=coloane_toate,
                           tipuri_grafice=tipuri_grafice,
                           img=img,
                           tip_grafic=tip_grafic,
                           col_x=col_x,
                           col_y=col_y,
                           eroare=eroare)


@analiza_bp.route('/preturi')
def preturi():
    df = get_df()
    if df is None:
        flash('Te rugăm să încarci mai întâi un fișier CSV.', 'warning')
        return redirect(url_for('analiza.index'))

    sns.set_theme(style='whitegrid')
    grafice = {}

    # 1. Pret mediu per categorie
    if 'Categorie' in df.columns and 'Pret_Unitar_EUR' in df.columns:
        fig, ax = plt.subplots(figsize=(12, 5))
        data = df.groupby('Categorie')['Pret_Unitar_EUR'].mean().sort_values(ascending=False)
        bars = ax.bar(data.index, data.values, color=sns.color_palette('Set2', len(data)))
        ax.bar_label(bars, fmt='%.0f EUR', padding=3, fontsize=9)
        ax.set_title('Preț mediu per categorie (EUR)', fontsize=14)
        ax.set_ylabel('Preț mediu (EUR)')
        plt.xticks(rotation=30, ha='right')
        grafice['pret_mediu_categorie'] = fig_to_base64(fig)

    # 2. Valoare totala achizitii per furnizor
    if 'Furnizor' in df.columns and 'Valoare_Totala_EUR' in df.columns:
        fig, ax = plt.subplots(figsize=(12, 5))
        data = df.groupby('Furnizor')['Valoare_Totala_EUR'].sum().sort_values(ascending=False).head(10)
        bars = ax.bar(data.index, data.values, color=sns.color_palette('Set3', len(data)))
        ax.bar_label(bars, fmt='%.0f', padding=3, fontsize=8)
        ax.set_title('Top 10 furnizori după valoare totală achiziții (EUR)', fontsize=14)
        ax.set_ylabel('Valoare totală (EUR)')
        plt.xticks(rotation=30, ha='right')
        grafice['valoare_furnizor'] = fig_to_base64(fig)

    # 3. Distributie preturi (histograma)
    if 'Pret_Unitar_EUR' in df.columns:
        fig, ax = plt.subplots(figsize=(12, 5))
        sns.histplot(df['Pret_Unitar_EUR'].dropna(), bins=40, kde=True,
                     ax=ax, color='steelblue')
        ax.set_title('Distribuția prețurilor instrumentelor (EUR)', fontsize=14)
        ax.set_xlabel('Preț (EUR)')
        ax.set_ylabel('Frecvență')
        grafice['distributie_preturi'] = fig_to_base64(fig)

    # 4. Box plot pret per categorie
    if 'Categorie' in df.columns and 'Pret_Unitar_EUR' in df.columns:
        fig, ax = plt.subplots(figsize=(13, 6))
        sns.boxplot(data=df, x='Categorie', y='Pret_Unitar_EUR',
                    palette='Set2', ax=ax)
        ax.set_title('Variația prețurilor pe categorie (EUR)', fontsize=14)
        ax.set_ylabel('Preț (EUR)')
        plt.xticks(rotation=30, ha='right')
        grafice['boxplot_categorie'] = fig_to_base64(fig)

    # 5. Pie chart - ponderea valorii pe tara de origine
    if 'Tara_Origine' in df.columns and 'Valoare_Totala_EUR' in df.columns:
        fig, ax = plt.subplots(figsize=(9, 9))
        data = df.groupby('Tara_Origine')['Valoare_Totala_EUR'].sum().sort_values(ascending=False)
        ax.pie(data.values, labels=data.index, autopct='%1.1f%%',
               colors=sns.color_palette('Set2', len(data)), startangle=90)
        ax.set_title('Ponderea valorii achizițiilor pe țară de origine', fontsize=14)
        ax.axis('equal')
        grafice['pie_tara'] = fig_to_base64(fig)

    # 6. Evolutie achizitii in timp
    if 'Data_Achizitie' in df.columns and 'Valoare_Totala_EUR' in df.columns:
        fig, ax = plt.subplots(figsize=(12, 5))
        df_t = df.copy()
        df_t['Data_Achizitie'] = pd.to_datetime(df_t['Data_Achizitie'], errors='coerce')
        df_t['Luna'] = df_t['Data_Achizitie'].dt.to_period('M')
        data = df_t.groupby('Luna')['Valoare_Totala_EUR'].sum().reset_index()
        data['Luna'] = data['Luna'].astype(str)
        ax.plot(data['Luna'], data['Valoare_Totala_EUR'],
                marker='o', color='steelblue', linewidth=2)
        ax.fill_between(range(len(data)), data['Valoare_Totala_EUR'],
                        alpha=0.15, color='steelblue')
        ax.set_xticks(range(len(data)))
        ax.set_xticklabels(data['Luna'], rotation=45, ha='right', fontsize=8)
        ax.set_title('Evoluția valorii achizițiilor pe luni', fontsize=14)
        ax.set_ylabel('Valoare totală (EUR)')
        grafice['evolutie_timp'] = fig_to_base64(fig)

    # Statistici sumar preturi
    stat_preturi = {}
    if 'Pret_Unitar_EUR' in df.columns:
        stat_preturi = {
            'minim': round(df['Pret_Unitar_EUR'].min(), 2),
            'maxim': round(df['Pret_Unitar_EUR'].max(), 2),
            'medie': round(df['Pret_Unitar_EUR'].mean(), 2),
            'mediana': round(df['Pret_Unitar_EUR'].median(), 2),
            'std': round(df['Pret_Unitar_EUR'].std(), 2),
            'total_investit': round(df['Valoare_Totala_EUR'].sum(), 2) if 'Valoare_Totala_EUR' in df.columns else 0,
        }

    return render_template('analiza/preturi.html',
                           grafice=grafice,
                           stat_preturi=stat_preturi)