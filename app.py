import streamlit as st
import zipfile
import io
import datetime
import re

# ==========================================
# 1. BAZA DE DATE (Extrasă din App.jsx)
# ==========================================
DOSAR_RAW_DATA = """
R|1|REFERINȚA 1: MANAGEMENTUL STRATEGIC ȘI ORGANIZAȚIONAL
S|01.01|01.01. Strategia şi managementul strategic al organizației sunt concordante cu nevoia de îngrijiri.
C|01.01.01|01.01.01. Planul strategic se bazează pe analiza nevoilor de îngrijire a populaţiei.
I|01.01.01.01|01.01.01.01. Organizația a realizat/utilizat o analiză privind nevoile de îngrijire a populaţiei.|Realizarea periodică a analizei nevoilor de îngrijire a populaţiei/comunităţii deservite, precum şi analiza gradului de acoperire a acestora pe plan local/judeţean/regional.
I|01.01.01.02|01.01.01.02. Rezultatele analizei privind nevoile medicale sunt utilizate în stabilirea obiectivelor.|Obiectivele care duc la satisfacerea nevoii de servicii de sănătate sunt fundamentate pe baza rezultatelor analizei privind nevoile de îngrijire a populaţiei.
C|01.01.02|01.01.02. Planul strategic elaborat de către spital este asumat la toate nivelurile de decizie.
I|01.01.02.01|01.01.02.01. Planul strategic este fundamentat în conformitate cu resursele disponibile.|Formalizarea şi asumarea de către autoritatea tutelară a planului strategic.
I|01.01.02.02|01.01.02.02. Planul strategic vizează îmbunătățirea calității serviciilor şi a siguranței pacienților.|Elaborarea unor politici de calitate realiste pe baza analizei strategice.
I|01.01.02.03|01.01.02.03. Obiectivele planului strategic sunt cunoscute şi asumate la nivelul structurilor.|Planificarea activităților necesare îndeplinirii obiectivelor planului strategic se realizează cu stabilirea responsabilităților persoanelor implicate.
C|01.01.03|01.01.03. Planul strategic se implementează cu participarea tuturor sectoarelor de activitate.
I|01.01.03.01|01.01.03.01. La nivelul spitalului funcționează o echipă activă responsabilă cu evaluările periodice.|Efectuarea analizelor periodice ale nivelului de realizare a obiectivelor.
I|01.01.03.02|01.01.03.02. Şefii tuturor sectoarelor de activitate analizează periodic nivelul de realizare.|Analiza stadiului de îndeplinire a activităţilor specifice fiecărui sector de activitate.
I|01.01.03.03|01.01.03.03. Planificarea anuală a activităților are în vedere obiectivele strategice stabilite.|Planificarea anuală a activităților unităţii sanitare trebuie să cuprindă activităţile specifice pentru realizarea obiectivelor din Planul strategic.
C|01.01.04|01.01.04. Strategia institutelor clinice şi a spitalelor clinice include dezvoltarea cercetării.
I|01.01.04.01|01.01.04.01. Cercetarea științifică vizează obiectivele de dezvoltare a spitalului.|Temele abordate în cercetarea ştiinţifică trebuie să ţină cont și de obiectivele de dezvoltare ale acestuia.
I|01.01.04.02|01.01.04.02. Inovația adusă prin cercetare îmbunătățește calitatea și performanța actului medical.|Identificarea, în cadrul activităţii de cercetare, a soluțiilor care duc la îmbunătățirea permanentă a calităţii actului medical.
I|01.01.04.03|01.01.04.03. Institutul medical coordonează activitatea de inovare/cercetare a spitalelor cu activitate.|Unităţile sanitare din categoria institut coordonează activitatea de cercetare a spitalelor cu preocupări similare.
S|01.02|01.02. Structura organizatorică şi managementul organizaţional asigură derularea optimă a proceselor.
C|01.02.01|01.02.01. Spitalul funcţionează cu toate avizele şi autorizaţiile prevăzute de actele normative.
I|01.02.01.01|01.02.01.01. Spitalul a luat toate măsurile pentru obţinerea şi actualizarea autorizaţiilor și avizelor.|Autorizație sanitară de funcționare, Autorizație farmacie, CNCAN, Mediu, ISU.
I|01.02.01.02|01.02.01.02. Spitalul a luat toate măsurile pentru menținerea condițiilor de autorizare.|Monitorizarea activităților pentru menținerea condițiilor de obținere a autorizațiilor și avizelor.
C|01.02.02|01.02.02. Structura organizatorică este fundamentată, documentată, analizată şi actualizată periodic.
I|01.02.02.01|01.02.02.01. Fundamentarea structurii organizatorice are în vedere cererea de servicii medicale.|-
I|01.02.02.02|01.02.02.02. Conducerea evaluează periodic structura organizației în raport cu cererea.|-
I|01.02.02.03|01.02.02.03. Conducerea analizează periodic modul de desfăşurare a proceselor organizației.|-
C|01.02.03|01.02.03. Structurile funcţionale (comisii, comitete, consilii) sunt operaţionale.
I|01.02.03.01|01.02.03.01. Structurile funcționale (comisii, comitete, consilii) sunt constituite şi active.|-
I|01.02.03.02|01.02.03.02. Activitatea structurilor funcţionale asigură fundamentarea procesului decizional.|-
S|01.06|01.06. Sistemul de comunicare existent la nivelul spitalului răspunde nevoilor organizaţiei.
C|01.06.02|01.06.02. Comunicarea internă răspunde nevoilor pacienților și ale spitalului.
I|01.06.02.03|01.06.02.03. Regulile interne sunt comunicate personalului şi pacienţilor.|Regulile interne trebuie să fie accesibile și clare pentru toți membrii organizației.
R|2|REFERINȚA 2: MANAGEMENTUL CLINIC
S|02.11|02.11. Managementul infecţiilor asociate asistenţei medicale respectă bunele practici.
C|02.11.04|02.11.04. Managementul clinic al structurilor medicale previne şi limitează riscul infecţios.
I|02.11.04.07|02.11.04.07. Spitalul de specialitate sau cu secție de obstetrică adoptă măsuri de prevenie a riscului infecțios prenatal.|Implementarea protocoalelor specifice pentru prevenirea infecțiilor la nou-născut și mamă.
"""

@st.cache_data
def parse_dosar_data(raw_data):
    dosar = []
    current_ref = None
    current_std = None
    current_crit = None

    lines = raw_data.strip().split('\n')
    for line in lines:
        if not line.strip():
            continue
        parts = line.split('|')
        item_type = parts[0]
        item_id = parts[1]
        text = parts[2].strip() if len(parts) > 2 else ""
        ghid = '|'.join(parts[3:]).strip() if len(parts) > 3 else "Consultați Manualul Standardelor de Acreditare (Ediția II)."

        if item_type == 'R':
            current_ref = {'id': f'REF_{item_id}', 'titlu': text, 'standarde': []}
            dosar.append(current_ref)
        elif item_type == 'S':
            current_std = {'id': f'STD_{item_id.replace(".", "_")}', 'titlu': text, 'criterii': []}
            if current_ref:
                current_ref['standarde'].append(current_std)
        elif item_type == 'C':
            current_crit = {'id': f'CRIT_{item_id.replace(".", "_")}', 'titlu': text, 'cerinte': []}
            if current_std:
                current_std['criterii'].append(current_crit)
        elif item_type == 'I':
            if current_crit:
                current_crit['cerinte'].append({
                    'id': f'CER_{item_id.replace(".", "_")}',
                    'nume': text,
                    'ghid': ghid
                })
    return dosar

DOSAR_IERARHIC = parse_dosar_data(DOSAR_RAW_DATA)

# Funcție pentru a curăța numele de fișiere/foldere
def sanitize_name(name):
    return re.sub(r'[^a-zA-Z0-9 ]', '', name).strip().replace(' ', '_')

# Generare Fișier ZIP
def generate_zip_file(hospital_info):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        # Fișier info
        info_text = f"DOSAR ACREDITARE ANMCS\n========================\nUnitate: {hospital_info.get('nume','')}\nCUI: {hospital_info.get('cui','')}\nManager: {hospital_info.get('manager','')}\nAdresa: {hospital_info.get('adresa','')}\nData: {datetime.datetime.now().strftime('%d.%m.%Y')}"
        z.writestr("00_Date_Identificare.txt", info_text)
        
        # Generare foldere și adăugare fișiere din session_state
        for ref in DOSAR_IERARHIC:
            ref_folder = f"{ref['id']}_{sanitize_name(ref['titlu'])[:40]}"
            for std in ref['standarde']:
                std_folder = f"{ref_folder}/{std['id']}_{sanitize_name(std['titlu'])[:40]}"
                for crit in std['criterii']:
                    crit_folder = f"{std_folder}/{crit['id']}_{sanitize_name(crit['titlu'])[:40]}"
                    for cer in crit['cerinte']:
                        file_key = f"file_{cer['id']}"
                        # Verificăm dacă există un fișier încărcat pentru această cerință
                        if file_key in st.session_state and st.session_state[file_key] is not None:
                            uploaded_file = st.session_state[file_key]
                            ext = uploaded_file.name.split('.')[-1]
                            safe_name = sanitize_name(cer['nume'][:40])
                            full_path = f"{crit_folder}/{cer['id']}_{safe_name}.{ext}"
                            z.writestr(full_path, uploaded_file.getvalue())
    return buf.getvalue()

# ==========================================
# 2. INTERFAȚA STREAMLIT
# ==========================================
st.set_page_config(page_title="Platformă Acreditare ANMCS", layout="wide", page_icon="🏥")

# Calcul total cerințe
TOTAL_CERINTE = sum(len(crit['cerinte']) for ref in DOSAR_IERARHIC for std in ref['standarde'] for crit in std['criterii'])

# Configurare state pentru info spital
if 'hospital_info' not in st.session_state:
    st.session_state.hospital_info = {"nume": "", "manager": "", "cui": "", "adresa": ""}

# --- BARA LATERALĂ ---
with st.sidebar:
    st.title("🏥 Portal ANMCS")
    st.markdown("**Pregătire Dosar Ciclul II**")
    st.divider()
    
    st.markdown("### 1. Date Unitate Sanitară")
    st.session_state.hospital_info["nume"] = st.text_input("Nume Spital *", value=st.session_state.hospital_info["nume"])
    st.session_state.hospital_info["cui"] = st.text_input("CUI", value=st.session_state.hospital_info["cui"])
    st.session_state.hospital_info["manager"] = st.text_input("Manager / Reprezentant", value=st.session_state.hospital_info["manager"])
    st.session_state.hospital_info["adresa"] = st.text_area("Adresă Sediu", value=st.session_state.hospital_info["adresa"])
    
    st.divider()
    st.markdown("### 2. Progres Dosar")
    
    # Calculăm progresul: numărăm câte chei "file_..." din session_state au o valoare reală (fișier încărcat)
    uploaded_count = sum(1 for k in st.session_state.keys() if k.startswith('file_') and st.session_state[k] is not None)
    progress_pct = int((uploaded_count / TOTAL_CERINTE) * 100) if TOTAL_CERINTE > 0 else 0
    
    st.progress(progress_pct / 100.0)
    st.markdown(f"**{uploaded_count} din {TOTAL_CERINTE} documente** ({progress_pct}%)")
    
    st.divider()
    st.markdown("### 3. Finalizare Dosar")
    if uploaded_count > 0:
        zip_data = generate_zip_file(st.session_state.hospital_info)
        safe_hosp_name = sanitize_name(st.session_state.hospital_info['nume']) or 'Spital'
        st.download_button(
            label="⬇️ Descarcă Arhiva ZIP",
            data=zip_data,
            file_name=f"Dosar_ANMCS_{safe_hosp_name}.zip",
            mime="application/zip",
            use_container_width=True,
            type="primary"
        )
    else:
        st.info("Încărcați cel puțin un document pentru a genera arhiva ZIP.")

# --- ZONA PRINCIPALĂ ---
st.header("Structura Dosarului de Acreditare")
st.markdown("Navigați prin ierarhia standardelor de mai jos pentru a citi ghidul evaluării și a încărca documentele justificative corespunzătoare fiecărei cerințe.")

# Generare tab-uri pentru Referințe
tab_titles = [ref['titlu'].split(':')[0] for ref in DOSAR_IERARHIC]
tabs = st.tabs(tab_titles)

for ref_idx, ref in enumerate(DOSAR_IERARHIC):
    with tabs[ref_idx]:
        st.subheader(ref['titlu'])
        
        # Standarde
        for std in ref['standarde']:
            st.markdown(f"### {std['titlu']}")
            
            # Criterii (Expandere)
            for crit in std['criterii']:
                with st.expander(f"📁 {crit['titlu']}", expanded=False):
                    
                    # Cerințe
                    for cer in crit['cerinte']:
                        file_key = f"file_{cer['id']}"
                        is_uploaded = st.session_state.get(file_key) is not None
                        
                        # Container vizual distinct pentru fiecare cerință
                        with st.container(border=True):
                            # Afișare nume cerință
                            status_icon = "✅" if is_uploaded else "📄"
                            st.markdown(f"**{status_icon} {cer['nume']}**")
                            
                            col1, col2 = st.columns([1, 1])
                            
                            # Stânga: Ghidul
                            with col1:
                                with st.expander("📖 Vezi Ghid / Evaluare ANMCS"):
                                    ghid_text = cer['ghid'].replace("<br/>", "\n\n")
                                    st.info(ghid_text)
                                    
                            # Dreapta: Upload
                            with col2:
                                st.file_uploader(
                                    "Încărcați documentul scanat", 
                                    key=file_key, 
                                    label_visibility="collapsed"
                                )
                                if is_uploaded:
                                    st.success(f"Fișier salvat în memorie: {st.session_state[file_key].name}")
