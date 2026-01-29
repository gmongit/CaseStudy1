# user_interface.py
import streamlit as st
from datetime import datetime, timezone, date

from users import User
from devices import Device
from repositories import UserRepo, DeviceRepo
from db import now_utc, DB_FILE

import inspect
import streamlit as st


st.set_page_config(page_title="Geräte- & Nutzerverwaltung", layout="wide")

st.sidebar.caption(f"DB: {DB_FILE}")

user_repo = UserRepo()
device_repo = DeviceRepo()

st.sidebar.title("Navigation")
page = st.sidebar.radio("Bereich", ["Nutzerverwaltung", "Geräteverwaltung"])

# Nutzerverwaltung

if page == "Nutzerverwaltung":
    st.header("Nutzerverwaltung")

    with st.form("create_user"):
        email = st.text_input("E-Mail (ID)", placeholder="max.mustermann@fh.at")
        name = st.text_input("Name", placeholder="Max Mustermann")
        submitted = st.form_submit_button("Nutzer speichern")

    if submitted:
        email = email.strip()
        name = name.strip()
        if not email or "@" not in email:
            st.error("Bitte eine gültige E-Mail eingeben.")
        elif not name:
            st.error("Bitte einen Namen eingeben.")
        else:
            user_repo.upsert(User(id=email, name=name))
            st.success("Nutzer gespeichert.")
            st.rerun()

    st.subheader("Alle Nutzer")
    users = user_repo.list_all()
    if not users:
        st.info("Noch keine Nutzer vorhanden.")
    else:
        for u in users:
            cols = st.columns([4, 6, 2])
            cols[0].write(u.id)
            cols[1].write(u.name)
            if cols[2].button("Löschen", key=f"del_user_{u.id}"):
                user_repo.delete(u.id)
                st.rerun()

# Geräteverwaltung
elif page == "Geräteverwaltung":
    st.header("Geräteverwaltung")

    users = user_repo.list_all()
    if not users:
        st.warning("Lege zuerst mindestens einen Nutzer an (Verantwortliche Person).")
        st.stop()

    MAX_IDS = 20

    # Geräte laden + freie IDs 1..20 berechnen
    devices = device_repo.list_all()
    existing_ids = {int(d.id) for d in devices if d.id is not None}
    free_ids = [i for i in range(1, MAX_IDS + 1) if i not in existing_ids]

    # Auswahl: neu oder bestehend
    device_ids = ["(neu)"] + [str(d.id) for d in sorted(devices, key=lambda x: int(x.id))]
    selected = st.selectbox("Gerät auswählen", device_ids)

    if selected == "(neu)":
        current = Device(
            id="0",
            name="",
            responsible_user_id=users[0].id,
            is_active=True,
            end_of_life=None,
        )
        is_new = True
    else:
        current = device_repo.get(int(selected))
        is_new = False

    has_eol_default = current.end_of_life is not None
    eol_default_date = current.end_of_life.date() if current.end_of_life else date.today()

    user_map = {f"{u.name} ({u.id})": u.id for u in users}
    user_labels = list(user_map.keys())
    user_values = list(user_map.values())
    resp_index = user_values.index(current.responsible_user_id) if current.responsible_user_id in user_values else 0


    has_eol = st.checkbox("EOL setzen", value=has_eol_default, key="has_eol")
    eol_date = st.date_input("End of Life", value=eol_default_date, disabled=not has_eol, key="eol_date")

    with st.form("device_form"):
        # Inventarnummer: beim Anlegen nur freie IDs 1..20 auswählbar
        if is_new:
            if not free_ids:
                st.error("Alle Inventarnummern 1–20 sind bereits vergeben.")
                st.stop()

            inv = st.selectbox(
                "Inventarnummer (ID) – frei (1–20)",
                options=free_ids,
                index=0,
                help="Es werden nur freie IDs aus 1–20 angezeigt.",
            )
        else:
            inv = st.number_input(
                "Inventarnummer (ID)",
                min_value=1,
                max_value=MAX_IDS,
                step=1,
                value=int(current.id),
                disabled=True,
            )

        name = st.text_input("Gerätename", value=current.name or "")

        responsible_label = st.selectbox(
            "Verantwortliche Person",
            options=user_labels,
            index=resp_index,
        )
        responsible_id = user_map[responsible_label]

        save = st.form_submit_button("Gerät speichern")

    if save:
        inv_int = int(inv)

        if not (1 <= inv_int <= MAX_IDS):
            st.error("Inventarnummer muss zwischen 1 und 20 liegen.")
            st.stop()

        # Doppelte ID beim Neuanlegen verhindern
        if is_new and inv_int in existing_ids:
            st.error("Inventarnummer bereits vergeben. Speichern abgebrochen.")
            st.stop()

        if not name.strip():
            st.error("Bitte Gerätenamen eingeben.")
            st.stop()

        end_of_life_dt = None
        if has_eol:
            end_of_life_dt = datetime(eol_date.year, eol_date.month, eol_date.day, tzinfo=timezone.utc)

        updated = Device(
            id=str(inv_int),
            name=name.strip(),
            responsible_user_id=responsible_id,
            is_active=True,
            end_of_life=end_of_life_dt,
        )

        try:
            device_repo.upsert(updated)
            st.success("Gerät gespeichert.")
            st.rerun()
        except ValueError as e:
            st.error(str(e))


    st.subheader("Alle Geräte")
    devices = device_repo.list_all()
    if not devices:
        st.info("Noch keine Geräte vorhanden.")
    else:
        for d in sorted(devices, key=lambda x: int(x.id)):
            st.write(f"**{d.id}** – {d.name} | Verantwortlich: {d.responsible_user_id}")
