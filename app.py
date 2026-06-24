import streamlit as st
import zipfile
import io
import datetime
import re

# ==========================================
# 0. CONFIGURARE SPITAL FICTIV PENTRU MODELE
# ==========================================
SPITAL_FICTIV = {
    "nume": "Spitalul Municipal 'Sf. Ioan'",
    "manager": "Dr. Popescu Andrei",
    "cui": "RO12345678",
    "adresa": "Str. Sănătății nr. 1, Municipiul Exemplu, Județul Test",
    "tip": "Spital general, categoria III",
    "paturi": "150",
    "sectii": "Medicină Internă (40 paturi), Chirurgie Generală (30 paturi), ATI (10 paturi), Pediatrie (40 paturi), Obstetrică-Ginecologie (30 paturi)"
}

# ==========================================
# 1. BAZA DE DATE (Structura și Cerințele)
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
C|01.01.03|01.01.03. Planul strategic se implementează cu participarea tuturor sectoarelor de activitate.
I|01.01.03.01|01.01.03.01. La nivelul spitalului funcționează o echipă activă responsabilă cu evaluările periodice.|Efectuarea analizelor periodice ale nivelului de realizare a obiectivelor.
S|01.02|01.02. Structura organizatorică şi managementul organizaţional asigură derularea optimă a proceselor.
C|01.02.01|01.02.01. Spitalul funcţionează cu toate avizele şi autorizaţiile prevăzute de actele normative.
I|01.02.01.01|01.02.01.01. Spitalul a luat toate măsurile pentru obţinerea şi actualizarea autorizaţiilor și avizelor.|Autorizație sanitară de funcționare, Autorizație farmacie, CNCAN, Mediu, ISU.
C|01.02.03|01.02.03. Structurile funcţionale (comisii, comitete, consilii) sunt operaţionale.
I|01.02.03.01|01.02.03.01. Structurile funcționale (comisii, comitete, consilii) sunt constituite şi active.|Există decizii de constituire pentru toate consiliile și comisiile reglementate legal.
S|01.06|01.06. Sistemul de comunicare existent la nivelul spitalului răspunde nevoilor organizaţiei.
C|01.06.02|01.06.02. Comunicarea internă răspunde nevoilor pacienților și ale spitalului.
I|01.06.02.03|01.06.02.03. Regulile interne sunt comunicate personalului şi pacienţilor.|Regulile interne trebuie să fie accesibile și clare pentru toți membrii organizației.
R|2|REFERINȚA 2: MANAGEMENTUL CLINIC
S|02.02|02.02. Evaluarea inițială urmăreşte identificarea nevoilor pacienţilor în contextul factorilor de risc.
C|02.02.01|02.02.01. Procesul de evaluare a nevoilor pacientului este bine definit la nivelul spitalului.
I|02.02.01.01|02.02.01.01. În funcție de starea inițială se decide dacă spitalul poate prelua pacientul.|Medicul din UPU sau gardă consemnează fișa de evaluare și decide internarea.
S|02.03|02.03. Practica medicală abordează integrat și specific pacientul cu asigurarea continuității.
C|02.03.01|02.03.01. Managementul cazului este bazat pe utilizarea protocoalelor de diagnostic şi tratament.
I|02.03.01.02|02.03.01.02. Elaborarea protocoalelor de diagnostic și tratament este făcută pe baza dovezilor (EBM).|Protocoale medicale avizate pe secție cu sursa bibliografică de la comisii de specialitate.
S|02.11|02.11. Managementul infecţiilor asociate asistenţei medicale respectă bunele practici în domeniu.
C|02.11.04|02.11.04. Managementul clinic al structurilor medicale previne şi limitează riscul infecţios.
I|02.11.04.04|02.11.04.04. SSPLIAAM/CSPLIAAM supraveghează respectarea regulilor de igienă a mâinilor.|Monitorizarea consumului de dezinfectant la mia de zile spitalizare. Implementarea celor 5 Momente OMS.
S|02.12|02.12. Spitalul dezvoltă și implementează o politică de asigurare şi îmbunătățire a siguranței pacientului.
C|02.12.01|02.12.01. Spitalul are o politică proactivă de prevenire a riscurilor clinice.
I|02.12.01.04|02.12.01.04. Spitalul are un sistem funcțional de identificare a pacientului bazat pe cel puțin două elemente.|Folosirea brățărilor cu cod de bare/nume si cnp - verificarea încrucișată verbală înaintea intervenției.
C|02.12.04|02.12.04. Spitalul urmăreşte creşterea siguranţei actului chirurgical şi anestezic.
I|02.12.04.01|02.12.04.01. În practica chirurgicală și anestezică sunt utilizate liste de verificare specifice (Check-list).|Checklist-ul OMS privind siguranța chirurgicală ("Sign-in, Time-out, Sign-out") implementat în mod real.
C|02.12.07|02.12.07. Spitalul urmăreşte identificarea şi diminuarea cauzelor generatoare de vătămări corporale prin cădere/lovire.
I|02.12.07.01|02.12.07.01. Spitalul identifică pacienții cu risc de cădere și ia măsuri pentru prevenirea şi diminuarea consecințelor.|Evaluare a riscului de cădere Scala Morse completată la internare, atașare pictogramă la capătul patului.
S|02.14|02.14. Auditul clinic evaluează eficacitatea și eficienţa asistenţei medicale.
C|02.14.01|02.14.01. Activitatea de audit clinic este organizată.
I|02.14.01.01|02.14.01.01. Misiunile de audit clinic intern sunt planificate anual.|Există un program anual la nivelul spitalului / secțiilor aprobat.
R|3|REFERINȚA 3: ETICA MEDICALĂ ȘI DREPTURILE PACIENTULUI
S|03.01|03.01. Spitalul promovează respectul pentru autonomia pacientului.
C|03.01.01|03.01.01. Spitalul asigură conformitatea practicii medicale cu normele etice care se aplică consimţământului (CI).
I|03.01.01.01|03.01.01.01. Spitalul reglementează obținerea consimțământului informat.|Existența unui consimțământ la internare, dar și al consimțământelor individuale procedurale (ex. chirurgie, endoscopie etc).
"""

# ==========================================
# 2. GENERATOARE DE ȘABLOANE (Documente Oficiale)
# ==========================================
def get_template_for_requirement(cerinta_id, spital_info):
    """Returnează un șablon HTML complex în funcție de ID-ul cerinței."""
    nume_spital = spital_info.get("nume", SPITAL_FICTIV["nume"])
    manager = spital_info.get("manager", SPITAL_FICTIV["manager"])
    
    templates = {
        "01.01.01.01": f"""
        <h2 style='text-align: center;'>RAPORT DE ANALIZĂ A NEVOILOR DE ÎNGRIJIRE A POPULAȚIEI<br/>Anul {datetime.datetime.now().year}</h2>
        <p><strong>Aprobat,</strong><br/>Manager: {manager}</p>
        <h3>1. Introducere</h3>
        <p>Prezenta analiză a fost realizată la nivelul <strong>{nume_spital}</strong> pentru a fundamenta Planul Strategic de Dezvoltare. Spitalul nostru, de tip {SPITAL_FICTIV['tip']}, cu un număr de {SPITAL_FICTIV['paturi']} paturi, deservește o populație estimată la 120.000 de locuitori din municipiu și zonele limitrofe.</p>
        <h3>2. Date Demografice și de Morbiditate</h3>
        <ul>
            <li><strong>Structura populației:</strong> 55% mediul urban, 45% mediul rural. Procentul persoanelor peste 65 de ani este în creștere (aprox. 18%).</li>
            <li><strong>Morbiditate spitalizată (Top 3):</strong>
                <ul>
                    <li>Boli ale aparatului circulator (hipertensiune arterială, cardiopatie ischemică) - 35% din internări pe secția Medicină Internă.</li>
                    <li>Afecțiuni chirurgicale acute (apendicită, colecistită, hernii) - Secția Chirurgie ({SPITAL_FICTIV['sectii'].split(',')[1]}).</li>
                    <li>Afecțiuni respiratorii (pneumonii, BPOC) - predominant în sezonul rece la Pediatrie și Medicină Internă.</li>
                </ul>
            </li>
        </ul>
        <h3>3. Analiza cererii de servicii medicale (Anul precedent)</h3>
        <p>Spitalul a înregistrat un număr de 12.500 de internări continue și 18.000 de prezentări în CPU/Cameră de Gardă. Se observă o presiune crescută pe secția de ATI ({SPITAL_FICTIV['sectii'].split(',')[2]}) și necesitatea dezvoltării serviciilor de spitalizare de zi pentru a degreva paturile de acuți.</p>
        <h3>4. Concluzii și Recomandări pentru Planul Strategic</h3>
        <p>Având în vedere îmbătrânirea populației și incidența bolilor cardiovasculare, se recomandă:
        <br/>- Creșterea numărului de paturi pentru cronici/paliație (reorganizare viitoare).
        <br/>- Dotarea compartimentului de Cardiologie cu un ecograf Doppler performant.
        <br/>- Extinderea capacității ambulatoriului integrat pentru specialitățile deficitare.</p>
        <br/><br/>
        <p><strong>Întocmit de:</strong> Consiliul Medical / Biroul de Management al Calității</p>
        <p><strong>Data:</strong> {datetime.datetime.now().strftime('%d.%m.%Y')}</p>
        """,
        
        "01.02.03.01": f"""
        <h2 style='text-align: center;'>DECIZIA Nr. 45 / {datetime.datetime.now().year}<br/>privind constituirea și funcționarea structurilor funcționale (Comisii/Consilii)</h2>
        <p>Managerul <strong>{nume_spital}</strong>, domnul/doamna {manager}, numit prin Dispoziția/Ordinul nr. ..., în temeiul prevederilor Legii 95/2006 privind reforma în domeniul sănătății și ale Ordinului MS nr. 446/2017,</p>
        <h3>DECIDE:</h3>
        <p><strong>Art. 1.</strong> Începând cu data prezentei, se actualizează componența și regulamentele de funcționare pentru următoarele structuri obligatorii la nivelul spitalului:</p>
        <ol>
            <li><strong>Consiliul Medical</strong> - coordonat de Directorul Medical.</li>
            <li><strong>Consiliul Etic</strong> - constituit conform prevederilor legale, având rol în analiza reclamațiilor și protejarea drepturilor pacienților.</li>
            <li><strong>Comisia Medicamentului</strong> - formată din farmaciști și medici șefi de secție (Chirurgie, Boli Interne, ATI).</li>
            <li><strong>Serviciul/Compartimentul de Prevenire a Infecțiilor Asociate Asistenței Medicale (SPIAAM)</strong> - coordonat de un medic epidemiolog.</li>
            <li><strong>Comisia de Audit Clinic</strong> - coordonată de Responsabilul SMC.</li>
            <li><strong>Comitetul de Securitate și Sănătate în Muncă (CSSM)</strong>.</li>
        </ol>
        <p><strong>Art. 2.</strong> Fiecare comisie/consiliu va funcționa în baza unui Regulament Intern aprobat și va prezenta rapoarte de activitate semestriale/anuale către Comitetul Director.</p>
        <p><strong>Art. 3.</strong> Structura de Management al Calității (SMC) va monitoriza activitatea acestor comisii și va colecta procesele-verbale ale ședințelor ca dovezi pentru procesul de acreditare ANMCS.</p>
        <p><strong>Art. 4.</strong> Prezenta decizie se aduce la cunoștință persoanelor nominalizate (anexa 1) și șefilor de secții ({SPITAL_FICTIV['sectii']}).</p>
        <br/><br/>
        <div style="display: flex; justify-content: flex-end;">
            <div style="text-align: center;">
                <p><strong>MANAGER,</strong></p>
                <p>{manager}</p>
            </div>
        </div>
        """,
        
        "02.12.01.04": f"""
        <h2 style='text-align: center;'>PROCEDURĂ OPERAȚIONALĂ<br/>Identificarea Corectă a Pacientului</h2>
        <p><strong>Aprobat, Manager:</strong> {manager} | <strong>Unitate:</strong> {nume_spital}</p>
        <h3>1. Scop</h3>
        <p>Prevenirea erorilor medicale (administrare greșită de tratament, intervenții chirurgicale pe pacienți greșiți, recoltări eronate de analize) prin stabilirea unui sistem standardizat, funcțional, bazat pe minimum două elemente de identificare.</p>
        <h3>2. Domeniu de aplicare</h3>
        <p>Se aplică în toate secțiile cu paturi ({SPITAL_FICTIV['sectii']}), în CPU/UPU și în Ambulatoriul Integrat. Personalul vizat: medici, asistenți medicali, infirmieri, brancardieri.</p>
        <h3>3. Descrierea Procedurii</h3>
        <h4>3.1. Elementele de identificare</h4>
        <p>În <strong>{nume_spital}</strong>, identificarea se va face OBLIGATORIU folosind următoarele două elemente:</p>
        <ul>
            <li><strong>Numele și Prenumele pacientului</strong> (elementul 1)</li>
            <li><strong>Data nașterii (sau CNP-ul)</strong> (elementul 2)</li>
        </ul>
        <p><span style="color: red;"><strong>INTERZIS:</strong> Este strict interzisă identificarea pacientului după numărul salonului, numărul patului sau diagnosticul medical! (ex. "pacientul de la patul 3" sau "apendicita din salonul 2").</span></p>
        <h4>3.2. Brățara de identificare</h4>
        <ul>
            <li>La momentul internării (în UPU/CPU sau Biroul de Internări), fiecărui pacient i se atașează o <strong>brățară de identificare</strong>.</li>
            <li>Brățara va conține, tipărit sau scris clar, cele două elemente de identificare și un cod de bare (dacă sistemul informatic permite).</li>
            <li>Dacă brățara se deteriorează sau este îndepărtată pentru o procedură medicală, asistentul medical de salon are obligația de a o înlocui imediat.</li>
        </ul>
        <h4>3.3. Verificarea încrucișată (Cross-checking)</h4>
        <p>Înainte de orice manevră cu risc (recoltare sânge, administrare medicație orală sau IV, transfuzie, intervenție chirurgicală, transport pentru investigații), personalul medical <strong>va efectua o dublă verificare</strong>:</p>
        <ol>
            <li>Va citi datele de pe brățară și le va confrunta cu Foaia de Observație / Eprubeta / Fișa de medicație.</li>
            <li>Va întreba pacientul activ: <em>"Vă rog să îmi spuneți cum vă numiți și care este data dumneavoastră de naștere?"</em> (Nu se va folosi întrebarea "Sunteți domnul Popescu?", la care un pacient confuz ar putea răspunde afirmativ).</li>
        </ol>
        <h4>3.4. Situații excepționale</h4>
        <p>Pentru pacienții comatoși, afazici, cu patologie psihiatrică sau copiii mici (Pediatrie), identificarea se va face prin citirea brățării și confirmarea datelor cu aparținătorul prezent sau cu un alt cadru medical care cunoaște cazul.</p>
        <h3>4. Monitorizare și Audit</h3>
        <p>Respectarea acestei proceduri va fi auditată lunar de către asistenții șefi de secție și trimestrial de către SMC prin metoda "pacientului trasor".</p>
        """,
        
        "02.12.04.01": f"""
        <h2 style='text-align: center;'>LISTĂ DE VERIFICARE PRIVIND SIGURANȚA CHIRURGICALĂ (Check-list OMS)</h2>
        <p><strong>Spital:</strong> {nume_spital} | <strong>Secție:</strong> Chirurgie Generală / Bloc Operator</p>
        <p><em>Acest document se anexează obligatoriu la Foaia de Observație a fiecărui pacient supus unei intervenții chirurgicale.</em></p>
        
        <table border="1" cellpadding="5" cellspacing="0" style="width: 100%; border-collapse: collapse; margin-top: 20px;">
            <tr style="background-color: #f0f0f0;">
                <th style="width: 33%;">ÎNAINTE DE INDUCEREA ANESTEZIEI (Sign In)</th>
                <th style="width: 33%;">ÎNAINTE DE INCIZIA PIELII (Time Out)</th>
                <th style="width: 33%;">ÎNAINTE DE IEȘIREA DIN SALA DE OPERAȚIE (Sign Out)</th>
            </tr>
            <tr>
                <td valign="top">
                    <p><strong>A participat: Asistent / Anestezist</strong></p>
                    <p>☐ Pacientul a confirmat identitatea, locul operației, procedura și și-a dat consimțământul?</p>
                    <p>☐ Locul operației este marcat?</p>
                    <p>☐ A fost verificată siguranța anesteziei și funcționarea aparatului?</p>
                    <p>☐ Pulsoximetrul este pus pacientului și funcționează?</p>
                    <p><strong>Pacientul are:</strong></p>
                    <p>☐ Alergii cunoscute?</p>
                    <p>☐ Risc de aspirare / dificultăți căi aeriene? Dacă da, sunt echipamentele necesare la dispoziție?</p>
                    <p>☐ Risc de sângerare &gt; 500ml? Dacă da, există acces IV adecvat și sânge planificat/disponibil?</p>
                </td>
                <td valign="top">
                    <p><strong>A participat: Toată echipa (Chirurg, Anestezist, Asistent instrumentar)</strong></p>
                    <p>☐ Toți membrii echipei s-au prezentat (nume și rol)?</p>
                    <p>☐ Echipa a confirmat verbal pacientul, locul intervenției și procedura?</p>
                    <p><strong>Evenimente critice anticipate:</strong></p>
                    <p><strong>Chirurgul:</strong><br/>☐ Care sunt pașii critici/neașteptați?<br/>☐ Cât va dura?<br/>☐ Ce pierdere de sânge e estimată?</p>
                    <p><strong>Anestezistul:</strong><br/>☐ Există preocupări specifice privind pacientul?</p>
                    <p><strong>Asistentul:</strong><br/>☐ S-a confirmat sterilitatea echipamentelor (indicatori valabili)?</p>
                    <p>☐ S-a administrat profilaxia antibiotică în ultimele 60 de minute?</p>
                    <p>☐ Sunt expuse imagini/radiografii esențiale?</p>
                </td>
                <td valign="top">
                    <p><strong>A participat: Toată echipa</strong></p>
                    <p><strong>Asistentul instrumentar confirmă verbal:</strong></p>
                    <p>☐ Numele procedurii efectuate</p>
                    <p>☐ Că numărătoarea instrumentelor, compreselor și acelor a ieșit CORECTĂ (sau nu se aplică).</p>
                    <p>☐ Etichetarea corectă a probelor biologice extrase (inclusiv numele pacientului pe flacon).</p>
                    <p>☐ Există probleme cu echipamentul care trebuie raportate?</p>
                    <p><strong>Chirurg, Anestezist și Asistent:</strong></p>
                    <p>☐ Care sunt preocupările cheie privind recuperarea și managementul pacientului în perioada post-operatorie (ex. ATI)?</p>
                </td>
            </tr>
        </table>
        """,

        "02.12.07.01": f"""
        <h2 style='text-align: center;'>FIȘĂ DE EVALUARE A RISCULUI DE CĂDERE (Scala MORSE)</h2>
        <p><strong>Unitate:</strong> {nume_spital} | Se completează de către asistentul medical la internare și la orice modificare a stării pacientului.</p>
        
        <table border="1" cellpadding="5" cellspacing="0" style="width: 100%; border-collapse: collapse; margin-top: 15px;">
            <tr style="background-color: #d1e8ff;">
                <th>Criteriu de evaluare</th>
                <th>Scala</th>
                <th>Scor Acordat</th>
            </tr>
            <tr>
                <td><strong>1. Istoric de căderi</strong><br/>(A mai căzut în ultimele 3 luni?)</td>
                <td>Nu = 0<br/>Da = 25</td>
                <td></td>
            </tr>
            <tr>
                <td><strong>2. Diagnostice secundare</strong><br/>(Are mai mult de un diagnostic medical pe fișă?)</td>
                <td>Nu = 0<br/>Da = 15</td>
                <td></td>
            </tr>
            <tr>
                <td><strong>3. Dispozitive de sprijin pentru mers</strong></td>
                <td>Niciunul / Repaus la pat / Se sprijină de asistent = 0<br/>Cârjă / Baston / Cadru = 15<br/>Se sprijină de mobilă pentru a merge = 30</td>
                <td></td>
            </tr>
            <tr>
                <td><strong>4. Terapie intravenoasă / Perfuzie</strong><br/>(Este conectat la un stativ IV?)</td>
                <td>Nu = 0<br/>Da = 20</td>
                <td></td>
            </tr>
            <tr>
                <td><strong>5. Mers / Mod de deplasare</strong></td>
                <td>Normal / Repaus la pat / Imobilizat = 0<br/>Slab (obosit, pași scurți) = 10<br/>Afectat (se dezechilibrează, nu poate merge fără sprijin) = 20</td>
                <td></td>
            </tr>
            <tr>
                <td><strong>6. Stare mentală</strong></td>
                <td>Orientat / Conștient de propriile limite = 0<br/>Supraestimează abilitățile sale / Uită că are restricții = 15</td>
                <td></td>
            </tr>
            <tr style="background-color: #f9f9f9; font-weight: bold;">
                <td colspan="2" align="right">SCOR TOTAL:</td>
                <td></td>
            </tr>
        </table>
        
        <h3>Interpretarea Scorului și Măsuri:</h3>
        <ul>
            <li><strong>0 - 24 (Risc Scăzut):</strong> Măsuri de bază. Mențineți patul în poziție joasă, asigurați acces facil la butonul de chemare și la lumina de veghe.</li>
            <li><strong>25 - 44 (Risc Mediu):</strong> Măsuri preventive. Ridicați barele laterale ale patului. Instruiti pacientul să solicite asistență la coborârea din pat. Asigurați prezența încălțămintei antiderapante.</li>
            <li><strong>≥ 45 (Risc Înalt):</strong> Măsuri stricte de prevenție. Se aplică obligatoriu picrograma <span style="color:red;">[RISC DE CĂDERE]</span> la capătul patului / pe brățara pacientului. Barele patului ridicate permanent. Pacientul va fi însoțit OBLIGATORIU la grupul sanitar de către infirmieră/brancardier.</li>
        </ul>
        <p><strong>Semnătura asistent medical:</strong> ________________________  <strong>Data:</strong> ____________</p>
        """,

        "03.01.01.01": f"""
        <h2 style='text-align: center;'>FORMULAR CONSIMȚĂMÂNT INFORMAT AL PACIENTULUI<br/>LA INTERNARE</h2>
        <p><strong>Spitalul:</strong> {nume_spital} | <strong>Secția:</strong> _____________________</p>
        <p>Subsemnatul/a ____________________________________________, identificat cu CI seria _____ nr. ____________, CNP _________________________, având calitatea de PACIENT / REPREZENTANT LEGAL al pacientului ________________________________,</p>
        <p>Declar că am fost informat clar, într-un limbaj pe care l-am înțeles, de către Dr. ______________________________, cu privire la:</p>
        <ol>
            <li><strong>Diagnosticul prezumtiv/cert:</strong> ______________________________________________________________</li>
            <li><strong>Scopul internării, investigațiile și procedurile diagnostice/terapeutice propuse.</strong></li>
            <li><strong>Riscurile și complicațiile posibile:</strong> Mi s-au explicat riscurile inerente oricărei proceduri medicale (inclusiv reacții alergice, sângerări, infecții nosocomiale) și riscurile specifice afecțiunii mele.</li>
            <li><strong>Alternativele terapeutice:</strong> Mi s-au prezentat opțiunile alternative de tratament (inclusiv lipsa tratamentului) și riscurile asociate acestora.</li>
        </ol>
        
        <h3>ACORD / REFUZ</h3>
        <p>☐ <strong>CONSIMT</strong> în mod liber și voluntar la internare, la efectuarea investigațiilor recomandate și a tratamentului propus (medicamentos / perfuzabil / îngrijiri generale).</p>
        <p>☐ <strong>REFUZ</strong> efectuarea procedurilor medicale propuse, asumându-mi pe proprie răspundere consecințele asupra stării mele de sănătate (care pot duce la agravarea bolii sau deces).</p>
        
        <h3>ALTE DECLARAȚII OBLIGATORII:</h3>
        <p><strong>1. Transfuzia de sânge:</strong><br/>
        În caz de urgență sau necesitate medicală pe parcursul internării: <br/>
        ☐ SUNT DE ACORD cu transfuzia de sânge/produse derivate.<br/>
        ☐ NU SUNT DE ACORD cu transfuzia de sânge din motive personale/religioase.</p>
        
        <p><strong>2. Desemnarea persoanelor care pot primi informații medicale (Confidențialitate):</strong><br/>
        Conform Legii Drepturilor Pacientului (Legea 46/2003), doresc ca informații despre starea mea de sănătate și diagnostic să fie comunicate:<br/>
        ☐ Doar mie personal.<br/>
        ☐ Și următoarelor persoane (Nume, Prenume, Grad de rudenie, Telefon):<br/>
        1. ________________________________________________________<br/>
        2. ________________________________________________________</p>
        
        <br/><br/>
        <table width="100%">
            <tr>
                <td><strong>Data și Ora:</strong><br/>__________________</td>
                <td><strong>Semnătură Pacient / Reprezentant Legal:</strong><br/>______________________________</td>
                <td><strong>Semnătură Medic Curant:</strong><br/>______________________________</td>
            </tr>
        </table>
        """
    }
    
    # Returnăm șablonul dacă există, altfel un mesaj generic adaptat contextului spitalului
    if cerinta_id in templates:
        return create_printable_template(f"Model Document / Procedură: {cerinta_id}", templates[cerinta_id], spital_info)
    else:
        return create_printable_template(
            f"Draft / Planificare Procedură: {cerinta_id}", 
            f"""
            <h3 style="color: #2563eb;">DOCUMENT ÎN LUCRU</h3>
            <p>Această cerință vizează documentația pentru <strong>{nume_spital}</strong>.</p>
            <p><strong>Obiectiv:</strong> Reglementarea modului de lucru specific cerinței {cerinta_id}, adaptat la structura spitalului ({SPITAL_FICTIV['paturi']} paturi, secții: {SPITAL_FICTIV['sectii']}).</p>
            <p><strong>Responsabilități:</strong> Managerul ({manager}), Consiliul Medical și Structura de Management al Calității (SMC).</p>
            <hr>
            <p><em>INSTRUCȚIUNI PENTRU ECHIPA DE CALITATE:</em></p>
            <ul>
                <li>Definiți clar scopul și domeniul de aplicare al acestei reglementări.</li>
                <li>Identificați resursele necesare (umane și materiale) din cadrul spitalului.</li>
                <li>Redactați pașii concreți, responsabilii și indicatorii de monitorizare (cine controlează implementarea).</li>
                <li>Supuneți documentul avizării Consiliului Medical și aprobării finale a Managerului.</li>
            </ul>
            <p>Puteți utiliza asistentul AI integrat în platformă pentru a genera un draft amănunțit al acestei reglementări, oferindu-i ca instrucțiune detalii specifice modului în care procedați efectiv pe secție.</p>
            """, 
            spital_info
        )

# ==========================================
# 3. FUNCȚII DE PARSARE ȘI UI
# ==========================================
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
        ghid = '|'.join(parts[3:]).strip() if len(parts) > 3 else ""

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
                    'ghid': ghid,
                    'raw_id': item_id # salvam id-ul curat gen "01.01.01.01" pt cautare template
                })
    return dosar

DOSAR_IERARHIC = parse_dosar_data(DOSAR_RAW_DATA)

def create_printable_template(title, content, hospital_info):
    html = f"""
    <!DOCTYPE html>
    <html lang="ro">
    <head>
        <meta charset="UTF-8">
        <title>{title}</title>
        <style>
            body {{ font-family: 'Times New Roman', Times, serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 40px; color: #000; font-size: 12pt; }}
            h1 {{ text-align: center; margin-bottom: 20px; font-size: 14pt; font-weight: bold; text-transform: uppercase;}}
            h2 {{ font-size: 12pt; margin-top: 15px; margin-bottom: 10px; border-bottom: 1px solid #ccc; padding-bottom: 5px;}}
            .header {{ margin-bottom: 40px; border-bottom: 2px solid #000; padding-bottom: 10px;}}
            .footer {{ margin-top: 60px; display: flex; justify-content: space-between; }}
            .signature-box {{ width: 250px; text-align: center; border-top: 1px dashed #000; padding-top: 10px; margin-top: 40px;}}
            .text-justify {{ text-align: justify; }}
            .bold {{ font-weight: bold; }}
            @media print {{ body {{ padding: 0; }} button.no-print {{ display: none; }} }}
        </style>
    </head>
    <body onload="window.print()">
        <button class="no-print" onclick="window.print()" style="padding: 12px 24px; background: #2563eb; color: white; border: none; cursor: pointer; margin-bottom: 20px; border-radius: 6px; font-weight: bold;">Salvează PDF / Printează</button>
        <div class="header">
            <p class="bold" style="font-size: 14pt; margin:0;">{hospital_info.get('nume', SPITAL_FICTIV['nume'])}</p>
            <p style="margin:0;">CUI: {hospital_info.get('cui', SPITAL_FICTIV['cui'])} | Adresa: {hospital_info.get('adresa', SPITAL_FICTIV['adresa'])}</p>
        </div>
        
        {content}

    </body>
    </html>
    """
    return html

# Funcție pentru a curăța numele de fișiere/foldere
def sanitize_name(name):
    return re.sub(r'[^a-zA-Z0-9 ]', '', name).strip().replace(' ', '_')

def generate_zip_file(hospital_info):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        info_text = f"DOSAR ACREDITARE ANMCS\n========================\nUnitate: {hospital_info.get('nume','')}\nCUI: {hospital_info.get('cui','')}\nManager: {hospital_info.get('manager','')}\nAdresa: {hospital_info.get('adresa','')}\nData: {datetime.datetime.now().strftime('%d.%m.%Y')}"
        z.writestr("00_Date_Identificare.txt", info_text)
        
        for ref in DOSAR_IERARHIC:
            ref_folder = f"{ref['id']}_{sanitize_name(ref['titlu'])[:40]}"
            for std in ref['standarde']:
                std_folder = f"{ref_folder}/{std['id']}_{sanitize_name(std['titlu'])[:40]}"
                for crit in std['criterii']:
                    crit_folder = f"{std_folder}/{crit['id']}_{sanitize_name(crit['titlu'])[:40]}"
                    for cer in crit['cerinte']:
                        file_key = f"file_{cer['id']}"
                        if file_key in st.session_state and st.session_state[file_key] is not None:
                            uploaded_file = st.session_state[file_key]
                            ext = uploaded_file.name.split('.')[-1]
                            safe_name = sanitize_name(cer['nume'][:40])
                            full_path = f"{crit_folder}/{cer['id']}_{safe_name}.{ext}"
                            z.writestr(full_path, uploaded_file.getvalue())
    return buf.getvalue()


st.set_page_config(page_title="Platformă Acreditare ANMCS", layout="wide", page_icon="🏥")

TOTAL_CERINTE = sum(len(crit['cerinte']) for ref in DOSAR_IERARHIC for std in ref['standarde'] for crit in std['criterii'])

if 'hospital_info' not in st.session_state:
    st.session_state.hospital_info = {"nume": SPITAL_FICTIV["nume"], "manager": SPITAL_FICTIV["manager"], "cui": SPITAL_FICTIV["cui"], "adresa": SPITAL_FICTIV["adresa"]}

with st.sidebar:
    st.title("🏥 Portal ANMCS")
    st.markdown("**Pregătire Dosar Ciclul II**")
    st.divider()
    
    st.markdown("### 1. Date Unitate Sanitară (Editable)")
    st.session_state.hospital_info["nume"] = st.text_input("Nume Spital *", value=st.session_state.hospital_info["nume"])
    st.session_state.hospital_info["cui"] = st.text_input("CUI", value=st.session_state.hospital_info["cui"])
    st.session_state.hospital_info["manager"] = st.text_input("Manager / Reprezentant", value=st.session_state.hospital_info["manager"])
    st.session_state.hospital_info["adresa"] = st.text_area("Adresă Sediu", value=st.session_state.hospital_info["adresa"])
    
    st.divider()
    st.markdown("### 2. Progres Dosar")
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

st.header("Structura Dosarului de Acreditare (Template-uri incluse)")
st.markdown("Acum puteți genera modele oficiale (șabloane) pre-completate cu datele spitalului pentru cerințele cheie.")

tab_titles = [ref['titlu'].split(':')[0] for ref in DOSAR_IERARHIC]
tabs = st.tabs(tab_titles)

for ref_idx, ref in enumerate(DOSAR_IERARHIC):
    with tabs[ref_idx]:
        st.subheader(ref['titlu'])
        
        for std in ref['standarde']:
            st.markdown(f"### {std['titlu']}")
            
            for crit in std['criterii']:
                with st.expander(f"📁 {crit['titlu']}", expanded=False):
                    
                    for cer in crit['cerinte']:
                        file_key = f"file_{cer['id']}"
                        is_uploaded = st.session_state.get(file_key) is not None
                        
                        with st.container(border=True):
                            status_icon = "✅" if is_uploaded else "📄"
                            st.markdown(f"**{status_icon} {cer['nume']}**")
                            
                            col1, col2, col3 = st.columns([1.5, 1, 1])
                            
                            # Buton Generare Model / Draft
                            with col1:
                                if st.button(f"📄 Generează Model Document", key=f"btn_tpl_{cer['id']}"):
                                    html_draft = get_template_for_requirement(cer['raw_id'], st.session_state.hospital_info)
                                    st.download_button(
                                        label="⬇️ Descarcă Documentul (HTML/PDF)",
                                        data=html_draft,
                                        file_name=f"Document_{cer['raw_id']}.html",
                                        mime="text/html",
                                        key=f"dl_{cer['id']}",
                                        type="primary"
                                    )
                                    st.components.v1.html(html_draft, height=400, scrolling=True)

                            # Ghid ANMCS
                            with col2:
                                with st.expander("📖 Info/Ghid"):
                                    ghid_text = cer['ghid'].replace("<br/>", "\n\n")
                                    st.info(ghid_text if ghid_text else "Consultați Manualul Standardelor.")
                                    
                            # Upload
                            with col3:
                                st.file_uploader(
                                    "Încărcare Variantă Semnată", 
                                    key=file_key, 
                                    label_visibility="collapsed"
                                )
                                if is_uploaded:
                                    st.success("Salvat!")
