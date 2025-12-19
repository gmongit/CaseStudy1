# src/mockup_ui.py
import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Case Study I – Geräteverwaltung (Mockup)", layout="wide")

# Platzhalterdaten in Session State (Mockup)
if "devices" not in st.session_state:
    st.session_state.devices = [
        {"device_name": "Gerät_A", "managed_by_user_id": "user_001", "is_active": True,  "end_of_life": date(2028, 6, 30)},
        {"device_name": "Gerät_B", "managed_by_user_id": "user_002", "is_active": True,  "end_of_life": date(2027, 12, 31)},
        {"device_name": "Gerät_C", "managed_by_user_id": "user_003", "is_active": False, "end_of_life": date(2025, 3, 15)},
    ]

st.write("# Gerätemanagement")
st.write("## Geräteauswahl")

device_names = [d["device_name"] for d in st.session_state.devices]
current_name = st.selectbox("Gerät auswählen", options=device_names, key="sb_current_device")  # Selectbox wie in den Beispielen :contentReference[oaicite:5]{index=5}
current_device = next(d for d in st.session_state.devices if d["device_name"] == current_name)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Gerätename", current_device["device_name"])
with col2:
    st.metric("Verantwortlich (User-ID)", current_device["managed_by_user_id"])
with col3:
    st.metric("Aktiv", "Ja" if current_device["is_active"] else "Nein")

st.write("## Gerät bearbeiten")

# Form :contentReference[oaicite:6]{index=6}
with st.form("device_edit_form"):
    managed_by = st.text_input("Geräte-Verantwortlicher (User-ID)", value=current_device["managed_by_user_id"])
    is_active = st.checkbox("Gerät aktiv", value=current_device["is_active"])
    eol = st.date_input("End of Life", value=current_device["end_of_life"])

    submitted = st.form_submit_button("Änderungen übernehmen")
    if submitted:
        current_device["managed_by_user_id"] = managed_by
        current_device["is_active"] = is_active
        current_device["end_of_life"] = eol
        st.success("Mockup: Änderungen übernommen (nur Session State).")
        st.rerun()

st.write("## Geräteübersicht (Mockup)")
df = pd.DataFrame(st.session_state.devices)
st.dataframe(df, use_container_width=True)

with st.expander("Neues Gerät anlegen (Mockup)"):
    with st.form("device_create_form"):
        new_name = st.text_input("Gerätename", placeholder="Gerät_X")
        new_user = st.text_input("Verantwortlicher (User-ID)", placeholder="user_999")
        new_active = st.checkbox("Aktiv", value=True)
        new_eol = st.date_input("End of Life", value=date(2030, 1, 1))
        create = st.form_submit_button("Gerät hinzufügen")
        if create and new_name:
            st.session_state.devices.append({
                "device_name": new_name,
                "managed_by_user_id": new_user,
                "is_active": new_active,
                "end_of_life": new_eol
            })
            st.success("Mockup: Gerät hinzugefügt (nur Session State).")
            st.rerun()
