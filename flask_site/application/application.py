
import pathlib
import os
import folium
import numpy as np
import pandas as pd
from flask import render_template, send_file, jsonify, request, Blueprint, flash, g

from .auth import login_required, admin_required

# default settings for created folium maps
default_location = [34.716000, 137.747887]
default_zoom_start_vaccine = 13
default_zoom_start_pcr = 11

bp = Blueprint('map', __name__, template_folder='templates')


@bp.route("/")
@bp.route("/index")
def index():
    return render_template("index.html")


@bp.route("/maps/vaccine.html")
def default_map():
    return send_file("maps\\vaccine.html")


@bp.route("/maps/pcr.html")
def extra_map():
    return send_file("maps\\pcr.html")


@bp.route("/static/styles.css")
def send_stylesheet():
    return send_file("static/styles.css")


@bp.route("/csv", methods=["GET", "POST"])
@admin_required
def csv_update_interface():
    if request.method == 'POST':
        csv_path = pathlib.Path('data/pcr.csv')
        if 'csv' not in request.files:
            with csv_path.open(mode='w', encoding='utf-8') as csv_file:
                form_text = request.form["csvtext"]
                # for some reason updating the csv like this adds extra newlines, so we remove them here
                to_write = form_text.replace("\r\n", '\n')
                csv_file.write(to_write)
                update_maps()
            return render_template("index.html")

        else:
            file = request.files['csv']
            if file.filename == '':
                flash('no file in file upload')
            else:
                if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() == 'csv':
                    filename = 'vaccine.csv' if request.form['csvselect'] == 'vaccine' else 'pcr.csv'
                    file.save(pathlib.Path('temp.csv'))
                    with open('temp.csv', mode='r', encoding='utf-8') as infile:
                        with open((pathlib.Path('data') / filename), mode='w', encoding='utf-8') as outfile:
                            for line in infile:
                                outfile.write(line)
                    os.remove('temp.csv')
                    flash('success')
                    return render_template('index.html')
                else:
                    flash('unspecified failure while uploading file')

    else:
        infile_path = pathlib.Path("data/pcr.csv")
        with infile_path.open(mode='r', encoding='utf-8') as infile:
            csv_content = infile.read()
            return render_template('csv.html', csv_content=csv_content)


@bp.route("/filter", methods=["POST"])
def filter_map():
    # get desired weekdays from post data
    wanted_days = request.form.getlist('days[]')
    translation_dict = {"monday": '月曜日',
                        "tuesday": '火曜日',
                        "wednesday": '水曜日',
                        "thursday": '木曜日',
                        "friday": '金曜日',
                        "saturday": '土曜日',
                        "sunday": '日曜日'
                        }

    wanted_days = set([translation_dict[i] for i in wanted_days])

    vaccine_df = pd.read_csv("data\\vaccine.csv", encoding="utf-8")
    pcr_df = pd.read_csv("data\\pcr.csv", encoding="utf-8")
    # filter out all locations where all desired weekdays are in　定休日
    contains = [~vaccine_df['定休日'].str.contains(day) for day in wanted_days]
    contains2 = [~pcr_df['定休日'].str.contains(day) for day in wanted_days]
    filtered = vaccine_df[np.any(contains, axis=0)]
    filtered2 = pcr_df[np.any(contains2, axis=0)]
    vaccine_data = filtered[["緯度", "経度", "病院名", "電話番号", "住所", "定休日"]].values
    pcr_data = filtered2[["緯度", "経度", "病院名", "電話番号", "所在地", "定休日"]].values
    # make map with the filtered points
    vaccine_map = folium.Map(location=default_location, zoom_start=default_zoom_start_vaccine)
    pcr_map = folium.Map(location=default_location, zoom_start=default_zoom_start_pcr)
    add_markers_to_map(vaccine_data, vaccine_map, color='green')
    add_markers_to_map(pcr_data, pcr_map, color='green')
    # save and send to client
    vaccine_map.save("application/maps/filteredvaccine.html")
    pcr_map.save('application/maps/filteredpcr.html')

    vaccine_map_html = pathlib.Path("application/maps/filteredvaccine.html").read_text(encoding='utf-8')
    pcr_map_html = pathlib.Path("application/maps/filteredpcr.html").read_text(encoding='utf-8')
    return jsonify(html1=vaccine_map_html, html2=pcr_map_html)


def update_maps():
    # Open vaccine CSV
    df = pd.read_csv("data\\vaccine.csv", encoding="utf-8")
    pcr_df = pd.read_csv("data\\pcr.csv", encoding="utf-8")
    vaccine_data = df[["緯度", "経度", "病院名", "電話番号", "住所", "定休日"]].values
    pcr_data = pcr_df[["緯度", "経度", "病院名", "電話番号", "所在地", "定休日"]].values

    # initialize maps
    vaccine_map = folium.Map(location=default_location, zoom_start=default_zoom_start_vaccine)
    pcr_map = folium.Map(location=default_location, zoom_start=default_zoom_start_pcr)

    # add markers to vaccine map
    add_markers_to_map(vaccine_data, vaccine_map)
    add_markers_to_map(pcr_data, pcr_map)

    # update vaccine map html file
    vaccine_map.save("application/maps/vaccine.html")
    pcr_map.save("application/maps/pcr.html")


def add_markers_to_map(row_list, folium_map, color='red'):
    """Takes list of 5-tuples from csv and adds them to a folium map as markers"""
    for row in row_list:
        folium.Marker(
            [row[0], row[1]], tooltip=[row[2], row[3], row[4], row[5]],
            icon=folium.Icon(color=color)
        ).add_to(folium_map)




