# Importing required modules for Flask and SQLAlchemy
from flask import Flask, request, render_template, url_for, redirect, send_file, flash
import os
import matplotlib
matplotlib.use('Agg')  # Forcer Matplotlib à utiliser un backend non-GUI
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import pandas as pd
from flask_debugtoolbar import DebugToolbarExtension
from flask import session 
import matplotlib.pyplot as plt
import numpy as np
import io
from werkzeug.utils import secure_filename
import openai
import gradio as gr

# Étape 1 : Conception du modèle de base de données
client = openai.OpenAI(api_key='')
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

# Créez le dossier de téléchargement s'il n'existe pas
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
app.debug = True
app.config['SECRET_KEY'] = '<replace with a secret key>'
toolbar = DebugToolbarExtension(app)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Définir les modèles SQLAlchemy pour le tableau 1 (données initiales), le tableau 2 (station de recharge) et le 
# tableau 3 (véhicules électriques).
class VehicleData(db.Model):
    numvehicle = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(50))
    categorie_thermique = db.Column(db.String(50)) 
    nbre_km = db.Column(db.Float)
    trajet_matin = db.Column(db.Float)
    fin_trajet_matin = db.Column(db.Float)
    trajet_aprs_midi = db.Column(db.Float)
    fin_trajet_aprs_midi = db.Column(db.Float)
    recharge_midi_hre = db.Column(db.Float)
    annee = db.Column(db.Float)
    type_util = db.Column(db.String(50))
    type_vehicl = db.Column(db.String(50))
    circuit = db.Column(db.String(50))
    carburant = db.Column(db.String(50))
    val_carburant = db.Column(db.Float)
    conso_L_100km = db.Column(db.Float)
    batiment = db.Column(db.String(50))
    stationnement = db.Column(db.String(50))
    cout_vehicl_therm = db.Column(db.Float)
    cout_entre_annuel = db.Column(db.Float)
    nbre_jrs = db.Column(db.Float)
    annee_conversion  = db.Column(db.Integer)
    nbre_km_max = db.Column(db.Float)
    nbre_km_annuel = db.Column(db.Float)
    trajet_nuit = db.Column(db.Float)
    recharge_hre_ouvr = db.Column(db.Float)
    capacite_charge = db.Column(db.Float)
    capacite_remork = db.Column(db.Float)
    catego_vehcl_thermik = db.Column(db.String(50))
    hre_ouvr_jour = db.Column(db.Float)
    terme_finan = db.Column(db.Float)
    taux_finan = db.Column(db.Float)
    puiss_borne_recharg = db.Column(db.Float)
    modeleVE = db.Column(db.String(50))
    conso_kWh_100km_hiver = db.Column(db.Float)
    capacite_batterie = db.Column(db.Float)
    cout_vehicl_elect = db.Column(db.Float)
    subvention = db.Column(db.Float)
    autono_batterie = db.Column(db.Float)
    Autonomie_KM_ete = db.Column(db.Float)
    Autonomie_KM_hiver = db.Column(db.Float)
    Conso_kWh_100km_ete = db.Column(db.Float)
    port_charg_n2 = db.Column(db.Float)
    port_charg_n3 = db.Column(db.Float)
    cout_entre_km_elec = db.Column(db.Float)
    conso_diesel_heure = db.Column(db.Float)
    annee_dispo_VE = db.Column(db.Float)
    categorie_electrique = db.Column(db.String(50))
    residuel_90_pm = db.Column(db.Float)
    capacite_batterie_90 = db.Column(db.Float)
    conso_kwh_jrs_hiver = db.Column(db.Float)
    conso_kwh_jrs_ete = db.Column(db.Float)
    residuel_90_am = db.Column(db.Float)
    recharge_midi_kwh = db.Column(db.Float)
    pourc_am = db.Column(db.Float)
    pourc_pm = db.Column(db.Float)
    reduction_GES = db.Column(db.Float)
    conso_gaz_annee = db.Column(db.Float)
    prix_gaz = db.Column(db.Float)
    cout_kwh = db.Column(db.Float)
    cout_litre = db.Column(db.Float)
    entretien_elec = db.Column(db.Float)
    economy = db.Column(db.Float)
    recharge_soir_h = db.Column(db.Float)


class ChargingStation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    categorie = db.Column(db.String(50))
    puiss_borne_recharg = db.Column(db.Float)

class ElectricVehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    modeleVE = db.Column(db.String(50))
    conso_kWh_100km_hiver = db.Column(db.Float)
    capacite_batterie = db.Column(db.Float)
    cout_vehicl_elect = db.Column(db.Float)
    subvention = db.Column(db.Float)
    autono_batterie = db.Column(db.Float)
    Autonomie_KM_ete = db.Column(db.Float)
    Autonomie_KM_hiver = db.Column(db.Float)
    Conso_kWh_100km_ete = db.Column(db.Float)
    port_charg_n2 = db.Column(db.Float)
    port_charg_n3 = db.Column(db.Float)
    cout_entre_km_elec = db.Column(db.Float)
    conso_diesel_heure = db.Column(db.Float)
    annee_dispo_VE = db.Column(db.Float)
    categorie_electrique = db.Column(db.String(50))


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/acceuil', methods=['GET', 'POST'])
def acceuil():
    vehicles = VehicleData.query.all()
    selected_vehicle = None

    if request.method == 'POST':
        # Sauvegarder l'ID du véhicule sélectionné dans la session
        session['selected_vehicle_id'] = request.form.get('vehicle-select')
    
    # Récupérer l'ID du véhicule sélectionné de la session si disponible
    selected_vehicle_id = session.get('selected_vehicle_id')
    if selected_vehicle_id:
        selected_vehicle = VehicleData.query.get(selected_vehicle_id)

    return render_template('acceuil.html', vehicles=vehicles, selected_vehicle=selected_vehicle)

@app.route('/importer', methods=['GET', 'POST'])
def importer():
    return render_template('upload.html')




@app.route('/upload', methods=['POST'])
def upload():
    # Upload and save VehicleData
    vehicle_data_file = request.files['vehicle_data']
    if vehicle_data_file:
        df_vehicle = pd.read_excel(vehicle_data_file)
        for _, row in df_vehicle.iterrows():
            vehicle = VehicleData(model=row['model'], categorie_thermique=row['categorie_thermique'], prix_gaz = row['prix_gaz'], nbre_km=row['nbre_km'], trajet_matin=row['trajet_matin'], fin_trajet_matin=row['fin_trajet_matin'], trajet_aprs_midi=row['trajet_aprs_midi'], fin_trajet_aprs_midi=row['fin_trajet_aprs_midi'], recharge_midi_hre=row['recharge_midi_hre'], annee=row['annee'], type_util=row['type_util'], type_vehicl=row['type_vehicl'], circuit=row['circuit'], carburant=row['carburant'], val_carburant=row['val_carburant'], conso_L_100km=row['conso_L_100km'], batiment=row['batiment'], stationnement=row['stationnement'], cout_vehicl_therm=row['cout_vehicl_therm'], cout_entre_annuel=row['cout_entre_annuel'], nbre_jrs=row['nbre_jrs'], nbre_km_max=row['nbre_km_max'], nbre_km_annuel=row['nbre_km_annuel'], trajet_nuit=row['trajet_nuit'], recharge_hre_ouvr=row['recharge_hre_ouvr'], capacite_charge=row['capacite_charge'], capacite_remork=row['capacite_remork'], catego_vehcl_thermik=row['catego_vehcl_thermik'], hre_ouvr_jour=row['hre_ouvr_jour'], terme_finan=row['terme_finan'], taux_finan=row['taux_finan'])
            db.session.add(vehicle)
        
    # Upload and save ChargingStation data
    charging_station_file = request.files['charging_station_data']
    if charging_station_file:
        df_charging_station = pd.read_excel(charging_station_file)
        for _, row in df_charging_station.iterrows():
            station = ChargingStation(puiss_borne_recharg=row['puiss_borne_recharg'], categorie=row['categorie'])
            db.session.add(station)
        
    # Upload and save ElectricVehicle data
    electric_vehicle_file = request.files['electric_vehicle_data']
    if electric_vehicle_file:
        df_electric_vehicle = pd.read_excel(electric_vehicle_file)
        for _, row in df_electric_vehicle.iterrows():
            ev = ElectricVehicle(modeleVE=row['modeleVE'], categorie_electrique = row['categorie_electrique'], conso_kWh_100km_hiver=row['conso_kWh_100km_hiver'], capacite_batterie=row['capacite_batterie'], cout_vehicl_elect=row['cout_vehicl_elect'], subvention=row['subvention'], autono_batterie=row['autono_batterie'], Autonomie_KM_ete=row['Autonomie_KM_ete'], Autonomie_KM_hiver=row['Autonomie_KM_hiver'], Conso_kWh_100km_ete=row['Conso_kWh_100km_ete'], port_charg_n2=row['port_charg_n2'], port_charg_n3=row['port_charg_n3'], cout_entre_km_elec=row['cout_entre_km_elec'], conso_diesel_heure=row['conso_diesel_heure'], annee_dispo_VE=row['annee_dispo_VE'])
            db.session.add(ev)
    
    db.session.commit()
    return redirect(url_for('calculate'))

@app.route('/calculate')
def calculate():
    all_vehicles = VehicleData.query.order_by(VehicleData.nbre_km.desc()).all()
    # charging_stations = ChargingStation.query.order_by(ChargingStation.puiss_borne_recharg).all()

    # Calculer l'année de conversion
    total_vehicles = len(all_vehicles)
    group_size = total_vehicles // 10
    current_group = 1
    count = 0
    print(f"Total vehicles: {total_vehicles}, Group size: {group_size}")

    for index, vehicle in enumerate(all_vehicles):
        # Assigner l'année de conversion
        vehicle.annee_conversion = current_group
        print(f"Vehicle ID: {vehicle.numvehicle}, KM: {vehicle.nbre_km}, Assigned year: {vehicle.annee_conversion}")

        count += 1
        if count >= group_size and current_group < 10:
            count = 0
            current_group += 1

    db.session.commit()

    for vehicle in all_vehicles:
        # Filtrer les véhicules électriques par catégorie correspondant à celle du véhicule thermique
        electric_vehicles = ElectricVehicle.query.filter_by(categorie_electrique=vehicle.categorie_thermique).all()
        found_valid_ev = False  # Variable pour vérifier si un VE valide a été trouvé
        conso_gaz_annee = (vehicle.conso_L_100km/100) * vehicle.nbre_km_annuel
        vehicle.reduction_GES = round((conso_gaz_annee * vehicle.val_carburant)/1000, 2)
        cout_litre = conso_gaz_annee * vehicle.prix_gaz
        

        for ev in electric_vehicles:
            capacite_batterie_90 = round(ev.capacite_batterie * 0.9, 2)
            conso_kwh_jrs_hiver = (ev.conso_kWh_100km_hiver/100) * vehicle.nbre_km
            conso_kwh_jrs_ete = round((ev.Conso_kWh_100km_ete/100) * vehicle.nbre_km, 2)
            cout_kwh = (conso_kwh_jrs_hiver * (vehicle.nbre_jrs*0.5) + conso_kwh_jrs_ete * (vehicle.nbre_jrs*0.5)) * 0.11
            entretien_elec = vehicle.cout_entre_annuel * 0.5
            economy = round((cout_litre + vehicle.cout_entre_annuel) - (cout_kwh + entretien_elec))
            pourc_am = (vehicle.fin_trajet_matin - vehicle.trajet_matin) / \
                       ((vehicle.fin_trajet_matin - vehicle.trajet_matin) + (vehicle.fin_trajet_aprs_midi - vehicle.trajet_aprs_midi))
            pourc_pm = 1 - pourc_am
            residuel_90_am = capacite_batterie_90 - (conso_kwh_jrs_hiver * pourc_am)


            # Filtrer les bornes de recharge par catégorie correspondant à celle du véhicule
            charging_stations = ChargingStation.query.filter_by(categorie=vehicle.categorie_thermique).order_by(ChargingStation.puiss_borne_recharg).all()
            # Trouver une borne de recharge qui peut recharger le véhicule pendant la pause de midi
            for station in charging_stations:
                recharge_midi_kwh = station.puiss_borne_recharg * 0.9 * vehicle.recharge_midi_hre
                if recharge_midi_kwh > capacite_batterie_90:
                    recharge_midi_kwh = capacite_batterie_90
                residuel_90_pm = round(capacite_batterie_90 if (recharge_midi_kwh + residuel_90_am) > capacite_batterie_90 \
                                 else (recharge_midi_kwh + residuel_90_am) - (conso_kwh_jrs_hiver * pourc_pm), 2)
                
                if residuel_90_pm > 0:
                    found_valid_ev = True
                    # If a valid charging station is found, break the loop
                    break
            
            if found_valid_ev:
                # Update the vehicle data with the calculated values
                vehicle.modeleVE = ev.modeleVE
                vehicle.capacite_batterie = ev.capacite_batterie
                vehicle.Autonomie_KM_hiver = round(ev.Autonomie_KM_hiver)
                vehicle.Autonomie_KM_ete = round(ev.Autonomie_KM_ete)
                vehicle.cout_vehicl_elect = ev.cout_vehicl_elect
                vehicle.capacite_batterie_90 = round(capacite_batterie_90, 2)
                vehicle.conso_kwh_jrs_hiver = round(conso_kwh_jrs_hiver, 2)
                vehicle.residuel_90_am = round(residuel_90_am, 2)
                vehicle.recharge_midi_kwh = round(recharge_midi_kwh, 2)
                vehicle.residuel_90_pm = residuel_90_pm
                vehicle.pourc_am = pourc_am
                vehicle.pourc_pm = pourc_pm
                vehicle.puiss_borne_recharg = station.puiss_borne_recharg
                vehicle.economy = economy
                vehicle.recharge_soir_h = round((capacite_batterie_90 - residuel_90_pm)/station.puiss_borne_recharg, 2)
                db.session.commit()
                break  # Break the loop if the calculations are successful for this EV model

        if not found_valid_ev:
            # Si aucun véhicule électrique valide n'a été trouvé
            vehicle.modeleVE = "Non electrifiable"
            vehicle.capacite_batterie = 0
            vehicle.capacite_batterie_90 = 0
            vehicle.conso_kwh_jrs_hiver = 0
            vehicle.residuel_90_am = 0
            db.session.commit()

    return redirect(url_for('display'))



@app.route('/plot.png1')
def plot_png1():
    # Récupérer les données de la base de données
    vehicles = VehicleData.query.all()
    # Transformer les données en DataFrame
    data = []
    for vehicle in vehicles:
        data.append({
            'numvehicle': vehicle.numvehicle,
            'nbre_km': vehicle.nbre_km
        })
    df = pd.DataFrame(data)
    # Trier les données par consommation de kWh/jour
    df = df.sort_values(by='nbre_km', ascending=True)

    # Création du diagramme en barres ordonné
    fig, ax = plt.subplots(figsize=(15, 8))
    ax.bar(df['numvehicle'], df['nbre_km'], color='skyblue')

    # Ajout des labels et du titre
    ax.set_xlabel('Numéro du véhicule')
    ax.set_ylabel('Distance en Km/jour')
    ax.set_title('Distance parcourue en Km/jour')
    ax.set_xticklabels(df['numvehicle'], rotation=45)

    # Sauvegarder le graphique dans un tampon
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    
    return send_file(buf, mimetype='image1/png')




@app.route('/plot.png')
def plot_png():
    # Récupérer les données de la base de données
    vehicles = VehicleData.query.all()
    # Transformer les données en DataFrame
    data = []
    for vehicle in vehicles:
        data.append({
            'numvehicle': vehicle.numvehicle,
            'conso_kwh_jrs_hiver': vehicle.conso_kwh_jrs_hiver,
            'puiss_borne_recharg': vehicle.puiss_borne_recharg,
            'capacite_batterie_90': vehicle.capacite_batterie_90
        })
    df = pd.DataFrame(data)

        # Création du graphique
    fig, ax1 = plt.subplots(figsize=(15, 8))

    # Graphique en barres pour la consommation kWh/jour
    ax1.bar(df['numvehicle'], df['conso_kwh_jrs_hiver'], color='skyblue', label='Consommation kWh/jour (hiver)')
    ax1.set_xlabel('# Unité')
    ax1.set_ylabel('Consommation kWh/jour', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    # Ajout de la légende pour ax1
    ax1.legend(loc='upper left')
    # Deuxième axe Y pour les lignes de capacité et de puissance
    ax2 = ax1.twinx()
    ax2.plot(df['numvehicle'], df['capacite_batterie_90'], color='red', marker='o', label='Capacité de la batterie (90%)')
    ax2.plot(df['numvehicle'], df['puiss_borne_recharg'], color='purple', marker='o', label='Puissance de la borne (kW)')
    ax2.set_ylabel('Capacité et Puissance', color='black')
    ax2.tick_params(axis='y', labelcolor='black')
    # Ajout de la légende pour ax2
    ax2.legend(loc='upper right')
    fig.tight_layout()

    #fig.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=3)
    


    # Sauvegarder le graphique dans un tampon
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    
    return send_file(buf, mimetype='image/png')


@app.route('/plot.png2')
def plot_png2():
    # Récupérer les données de la base de données
    vehicles = VehicleData.query.all()
    # Transformer les données en DataFrame
    data = []
    for vehicle in vehicles:
        data.append({
            'numvehicle': vehicle.numvehicle,
            'trajet_matin': vehicle.trajet_matin,
            'fin_trajet_aprs_midi': vehicle.fin_trajet_aprs_midi,
            'recharge_soir_h': vehicle.recharge_soir_h
        })
    df = pd.DataFrame(data)
    df['heure_dispo'] = 24 - df['fin_trajet_aprs_midi'] + df['trajet_matin']

    # Position des barres sur l'axe des x
    bar_width = 0.35
    r1 = np.arange(len(df['numvehicle']))
    r2 = [x + bar_width for x in r1]

    # Création du graphique
    fig, ax = plt.subplots(figsize=(15, 8))

    # Barres
    ax.bar(r1, df['heure_dispo'], color='limegreen', width=bar_width, edgecolor='grey', label='Temps de recharge possible soir (heure)')
    ax.bar(r2, df['recharge_soir_h'], color='deepskyblue', width=bar_width, edgecolor='grey', label='Temps de recharge nécessaire Soir hiver (Heure)')

    # Ajouter les labels, titre et légende
    ax.set_xlabel('Numero vehicule', fontweight='bold')
    ax.set_ylabel('Temps de recharge (heures)', fontweight='bold')
    ax.set_title('Temps de recharge', fontweight='bold')
    ax.set_xticks([r + bar_width/2 for r in range(len(df['numvehicle']))])
    ax.set_xticklabels(df['numvehicle'], rotation=45, ha="right")

    # Ajouter la légende
    ax.legend()

    # Sauvegarder le graphique dans un tampon
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    
    return send_file(buf, mimetype='image2/png')


@app.route('/download')
def download():
    vehicles = VehicleData.query.all()
    data = [{
        'Numero': v.numvehicle,
        'Marque Modele': v.model,
        'Distance Moyen': v.nbre_km,
        'Vehicule electrique Eq': v.modeleVE,
        'Debut Trajet AM': v.trajet_matin,
        'Fin Trajet AM': v.fin_trajet_matin,
        'Debut Trajet PM': v.trajet_aprs_midi,
        'Fin Trajet PM': v.fin_trajet_aprs_midi,
        'Batiment Attitre': v.batiment,
        'Conso (kWh/jour) ete': v.conso_kwh_jrs_ete,
        'Conso (kWh/jour) hiver': v.conso_kwh_jrs_hiver,
        'Annee de Conversion': v.annee_conversion,
        'Temps de Recharge Midi': v.recharge_midi_hre,
        'Puissance Borne': v.puiss_borne_recharg,
        'Residuel PM (kWh)': v.residuel_90_pm,
        'Temps de recharge soir (h)': v.recharge_soir_h
    } for v in vehicles]
    df = pd.DataFrame(data)
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='VehicleData')
    writer.save()
    output.seek(0)
    return send_file(output, download_name='vehicle_data.xlsx', as_attachment=True)

@app.route('/download_tab1')
def download_tab1():
    vehicles = VehicleData.query.all()
    data = [{
        'Numero': v.numvehicle,
        'Marque Modele': v.model,
        'Annee du Vehicule': v.annee,
        'Carburant': v.carburant,
        'Distance Moyen': v.nbre_km,
        'Debut trajet AM': v.trajet_matin,
        'Fin trajet PM': v.fin_trajet_aprs_midi
    } for v in vehicles]
    df = pd.DataFrame(data)
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='tableau1')
    writer.save()
    output.seek(0)
    return send_file(output, download_name='tableau1.xlsx', as_attachment=True)

@app.route('/download_tab2')
def download_tab2():
    vehicles = VehicleData.query.all()
    data = [{
        'Numero': v.numvehicle,
        'Marque Modele': v.model,
        'Vehicule electrique Eq': v.modeleVE,
        'Conso en kWh hiver': v.conso_kwh_jrs_hiver,
        'Autonomie(Km) hiver': v.Autonomie_KM_hiver,
        'Autonomie(Km) ete': v.Autonomie_KM_ete

    } for v in vehicles]
    df = pd.DataFrame(data)
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='tableau2')
    writer.save()
    output.seek(0)
    return send_file(output, download_name='tableau2.xlsx', as_attachment=True)

@app.route('/download_tab3')
def download_tab3():
    vehicles = VehicleData.query.all()
    data = [{
        'Numero': v.numvehicle,
        'Marque Modele': v.model,
        'Vehicule electrique Eq': v.modeleVE,
        'Annee du vehicule': v.annee,
        'kilometrage annuel': v.nbre_km_annuel,
        'Annee de conversion': v.annee_conversion,
        'Puissance de la borne': v.puiss_borne_recharg
    } for v in vehicles]
    df = pd.DataFrame(data)
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='tableau3')
    writer.save()
    output.seek(0)
    return send_file(output, download_name='tableau3.xlsx', as_attachment=True)

@app.route('/download_tab4')
def download_tab4():
    vehicles = VehicleData.query.all()
    data = [{
        'Numero': v.numvehicle, 
            'Marque Modele': v.model, 
            'Vehicule electrique Eq': v.modeleVE, 
            'Reduction de GES(CO2 teq': v.reduction_GES
    } for v in vehicles]
    df = pd.DataFrame(data)
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='tableau4')
    writer.save()
    output.seek(0)
    return send_file(output, download_name='tableau4.xlsx', as_attachment=True)

@app.route('/scenariotab')
def scenariotab():
    vehicles = VehicleData.query.all()
    data = [{
        'Numero': v.numvehicle, 
            'Marque Modele': v.model, 
            'Vehicule electrique Eq': v.modeleVE, 
            'Reduction de GES(CO2 teq': v.reduction_GES
    } for v in vehicles]
    df = pd.DataFrame(data)
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='scenario')
    writer.save()
    output.seek(0)
    return send_file(output, download_name='scenario.xlsx', as_attachment=True)

@app.route('/graph')
def graph():
    return render_template('graph.html')

@app.route('/scenario')
def scenario():
    vehicle_data = VehicleData.query.all()
    return render_template('scenario.html', vehicle_data=vehicle_data)

@app.route('/optimisation')
def optimisation():
    vehicle_data = VehicleData.query.all()
    return render_template('optimisation.html', vehicle_data=vehicle_data)

@app.route('/comparateur')
def comparateur():
    vehicle_data = VehicleData.query.all()
    return render_template('comparateur.html', vehicle_data=vehicle_data)

@app.route('/display')
def display():
    vehicle_data = VehicleData.query.all()
    return render_template('display.html', vehicle_data=vehicle_data)

@app.route('/test')
def test():
    return render_template('test.html')



@app.route('/save-text', methods=['POST'])
def save_text():
    text = request.form['text']
    # Définir un chemin de fichier pour enregistrer le texte
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'analysis.txt')

    # Enregistrer le texte dans un fichier
    with open(file_path, 'w') as f:
        f.write(text)

    # Optionnel : permettre à l'utilisateur de télécharger le fichier après sauvegarde
    return send_file(file_path, as_attachment=True)


@app.route('/rapport', methods=['GET', 'POST'])
def rapport():
    if request.method == 'POST':
        # Récupération du fichier CSV
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and file.filename.endswith('.csv'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Lecture du fichier CSV
            df = pd.read_csv(filepath)

            # Récupération de l'invite personnalisée
            custom_prompt = request.form['prompt']
            table_text = df.to_string(index=False)
            prompt = f"{custom_prompt}\n\n{table_text}\n\nDonne une analyse détaillée de ce tableau."

            # Analyse du tableau avec GPT
            analysis_text = analyze_table(prompt)

            return render_template('rapport.html', analysis_text=analysis_text)

    return render_template('rapport.html')
from openai import OpenAI

def analyze_table(prompt):
    """
    Cette fonction prend un dataframe pandas comme entrée, le convertit en un format textuel
    et envoie une requête à l'API OpenAI pour obtenir une analyse du tableau.
    """
    # Convertir le dataframe en un format textuel lisible
    #table_text = dataframe.to_string(index=False)

    # Construire l'invite pour ChatGPT
    #prompt = f"Analyse ce tableau qui comporte les données suivantes :\n\n{table_text}\n\nDonne une analyse détaillée de ce tableau. Faite une analyse comme si vous etes un analyste de donnees et vous faite un rapport pour un client"

    try:
        # Appel à l'API OpenAI pour obtenir une analyse
        response = client.chat.completions.create(
            model="gpt-4o",  # Ou "gpt-4" si vous avez accès à ce modèle
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )

        # Extraire le texte de la réponse en utilisant directement l'attribut 'content'
        analysis_text = response.choices[0].message.content.strip()
        
    except Exception as e:
        analysis_text = f"Une erreur s'est produite lors de l'analyse du tableau: {e}"

    return analysis_text


@app.route('/gradio')
def gradio_interface():
    def display_table():
        # Extraire les données nécessaires
        all_vehicles = VehicleData.query.all()
        data = {
            'numvehicle': [v.numvehicle for v in all_vehicles],
            'conso_kwh_jrs_hiver': [v.conso_kwh_jrs_hiver for v in all_vehicles],
            'puiss_borne_recharg': [v.puiss_borne_recharg for v in all_vehicles],
            'capacite_batterie_90': [v.capacite_batterie_90 for v in all_vehicles]
        }
        df = pd.DataFrame(data)
        return df

    def plot_graph():
        all_vehicles = VehicleData.query.all()
        df = pd.DataFrame({
            'numvehicle': [v.numvehicle for v in all_vehicles],
            'conso_kwh_jrs_hiver': [v.conso_kwh_jrs_hiver for v in all_vehicles],
        })
        fig, ax = plt.subplots()
        ax.plot(df['numvehicle'], df['conso_kwh_jrs_hiver'], label='Conso KWh hiver')
        ax.set_xlabel('Num Vehicle')
        ax.set_ylabel('Conso KWh Hiver')
        ax.legend()
        return fig

    # Interface Gradio pour afficher le tableau et le graphique
    with gr.Blocks() as demo:
        with gr.Tab("Tableau"):
            gr.Interface(fn=display_table, inputs=[], outputs=gr.DataFrame()).launch(inline=False)
        with gr.Tab("Graphique"):
            gr.Interface(fn=plot_graph, inputs=[], outputs="plot").launch(inline=False)

    return gr.mount_gradio_app(app, demo, path="/gradio")


if __name__ == '__main__':
    app.run(debug=True)
