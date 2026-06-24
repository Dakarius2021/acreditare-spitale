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
# 1. BAZA DE DATE COMPLETA (Toate Cerințele ANMCS)
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
I|01.02.02.01|01.02.02.01. Fundamentarea structurii organizatorice are în vedere cererea de servicii medicale.|Se evaluează organigrama spitalului şi documentele care stau la baza cererii de modificare a acesteia.
I|01.02.02.02|01.02.02.02. Conducerea evaluează periodic structura organizației în raport cu cererea.|Se analizează rapoartele periodice de activitate și modul în care sunt adaptate structurile.
I|01.02.02.03|01.02.02.03. Conducerea analizează periodic modul de desfăşurare a proceselor organizației.|Analiza proceselor organizaționale interne.
C|01.02.03|01.02.03. Structurile funcţionale (comisii, comitete, consilii) sunt operaţionale.
I|01.02.03.01|01.02.03.01. Structurile funcționale (comisii, comitete, consilii) sunt constituite şi active.|Există decizii de constituire pentru toate consiliile și comisiile reglementate legal.
I|01.02.03.02|01.02.03.02. Activitatea structurilor funcţionale asigură fundamentarea procesului decizional.|Procesele-verbale ale şedinţelor dovedesc funcționalitatea acestora.
S|01.03|01.03. Managementul resurselor umane asigură nevoile de personal conform misiunii asumate.
C|01.03.01|01.03.01. Politica de resurse umane este documentată și adaptată nevoilor.
I|01.03.01.01|01.03.01.01. Conducerea spitalului stabileşte necesarul de personal în raport cu volumul de activitate.|Statul de funcții este aprobat, corelat cu nevoile de resurse umane.
I|01.03.01.02|01.03.01.02. Conducerea spitalului analizează anual structura posturilor şi dispune măsuri.|Planificarea fluctuațiilor de personal, pensionărilor.
I|01.03.01.03|01.03.01.03. Conducerea spitalului asigură elaborarea planului de selecție, recrutare şi dezvoltare.|Procedură clară de recrutare.
I|01.03.01.04|01.03.01.04. Formarea profesională continuă este realizată în baza unui plan de formare.|Există un plan anual de formare continuă pentru tot personalul.
C|01.03.02|01.03.02. Nevoia de personal este stabilită conform capacității tehnice, hoteliere, normativului.
I|01.03.02.01|01.03.02.01. Nevoia de personal medical şi auxiliar în secţii este stabilită în funcţie de gradul de dependență.|Planificarea turelor ține cont de normativul legal.
I|01.03.02.02|01.03.02.02. Nevoia de personal este estimată pentru a asigura utilizarea resurselor tehnice.|Aparatura medicală are personal instruit pentru a o utiliza.
I|01.03.02.03|01.03.02.03. Personalul care desfăşoară activitate în unitate este calificat şi autorizat.|Verificarea autorizațiilor de liberă practică la zi.
C|01.03.03|01.03.03. Politica de personal motivează angajații și determină îmbunătățirea calității.
I|01.03.03.01|01.03.03.01. Armonizarea relaţiilor dintre nivelurile managementului şi angajaţi se realizează prin dialog.|Dialog structurat și transparent cu sindicatele și reprezentanții salariaților.
I|01.03.03.02|01.03.03.02. Nivelul de satisfacţie al angajaţilor este evaluat periodic.|Chestionare periodice aplicate angajaților privind satisfacția la locul de muncă.
I|01.03.03.03|01.03.03.03. Spitalul asigură respectarea cerințelor privind calitatea vieţii profesionale.|Condiții optime de muncă conform normelor de sănătate ocupațională.
S|01.04|01.04. Managementul financiar şi administrativ răspunde obiectivelor strategice şi operaţionale.
C|01.04.01|01.04.01. Spitalul are o strategie financiară privind dezvoltarea.
I|01.04.01.01|01.04.01.01. Investiţiile sunt stabilite în conformitate cu obiectivele strategice.|Lista de investiții asumată și aprobată de autoritatea competentă.
I|01.04.01.02|01.04.01.02. Spitalul asigură realizarea planului anual de investiții conform bugetului.|Execuția bugetară reflectă investițiile planificate.
C|01.04.02|01.04.02. Bugetul de venituri şi cheltuieli al spitalului susţine realizarea planului anual de servicii.
I|01.04.02.01|01.04.02.01. Bugetul de venituri şi cheltuieli al spitalului este întocmit cu fundamentarea cheltuielilor.|Bugetul este corelat cu estimarea veniturilor de la CJAS și alte surse.
I|01.04.02.02|01.04.02.02. Spitalul analizează periodic veniturile realizate, în raport cu cheltuielile efectuate.|Analiza financiară la nivel de secție și spital.
C|01.04.03|01.04.03. Bugetul este actualizat periodic din perspectiva eficientizării furnizării serviciilor.
I|01.04.03.01|01.04.03.01. Spitalul are implementată o metodologie de monitorizare a costurilor serviciilor.|Spitalul implementează contabilitatea de gestiune pe centre de cost.
I|01.04.03.02|01.04.03.02. Spitalul analizează periodic procesul de furnizare a serviciilor cu participarea managementului.|Șefii de secție sunt informați despre cheltuielile secției lor.
C|01.04.04|01.04.04. Aprovizionarea sectoarelor de activitate asigură continuitatea în furnizarea serviciilor.
I|01.04.04.01|01.04.04.01. Spitalul asigură evidența și monitorizarea produselor şi serviciilor critice.|Proceduri de stabilire a stocurilor optime de siguranță.
I|01.04.04.02|01.04.04.02. Spitalul realizează analiza periodică a stocurilor.|Prevenirea expirării medicamentelor și materialelor sanitare.
I|01.04.04.03|01.04.04.03. Aprovizionarea sectoarelor de activitate este corelată cu consumul.|Referatele de necesitate sunt justificate pe baza consumurilor anterioare.
I|01.04.04.04|01.04.04.04. Spitalul asigură aprovizionarea cu produse şi servicii pentru cazuri excepţionale.|Existența fondurilor sau a contractelor pentru achiziții în regim de urgență.
S|01.05|01.05. Sistemul informațional răspunde necesităților de informații și stabilește utilizarea lor eficientă.
C|01.05.01|01.05.01. Sistemul informaţional asigură datele necesare documentării activităților spitalului.
I|01.05.01.01|01.05.01.01. Sistemul informațional integrează nevoia de informații și solicitările externe.|Raportările către DSP, CAS, MS și alte instituții.
I|01.05.01.02|01.05.01.02. Administrarea sistemului informatic asigură adaptarea acestuia la cerințele spitalului.|Existența personalului dedicat IT și contracte de mentenanță.
C|01.05.02|01.05.02. Circuitele şi fluxurile informaționale susțin desfăşurarea activităților și procesul decizional.
I|01.05.02.01|01.05.02.01. Circuitele și fluxurile informaționale asigură transmiterea datelor în formatul necesar.|Existența unui manual al circuitului documentelor în unitate.
I|01.05.02.02|01.05.02.02. Circuitele și fluxurile informaționale conțin sisteme de alertare care previn erorile.|Alerte pentru lipsă stoc, validări, interacțiuni medicamentoase.
C|01.05.03|01.05.03. Procesele informaționale fundamentează eficient deciziile la nivelul spitalului.
I|01.05.03.01|01.05.03.01. Suportul de informații caracteristic fiecărei activități este definit și respectat.|Existența indicatorilor și raportărilor de performanță la zi.
I|01.05.03.02|01.05.03.02. Operaționalitatea procedurilor informaționale utilizate permit eficientizarea activității.|Timpul de procesare a datelor este monitorizat.
C|01.05.04|01.05.04. Sistemul informatic asigură confidențialitatea, integritatea şi securitatea datelor.
I|01.05.04.01|01.05.04.01. Spitalul respectă legislația în vigoare cu privire la securitatea datelor.|Implementarea GDPR la nivelul spitalului și fișelor medicale.
I|01.05.04.02|01.05.04.02. Accesul la informații, prelucrarea și protecţia acestora sunt reglementate.|Parole individuale, nivele diferite de acces pe module.
I|01.05.04.03|01.05.04.03. Spitalul asigură sisteme de back-up al informației.|Salvarea copiilor de siguranță ale bazei de date periodic.
I|01.05.04.04|01.05.04.04. Spitalul asigură monitorizarea și controlul utilizării sistemelor informaționale.|Jurnal (log) al modificărilor făcute în sistem.
I|01.05.04.05|01.05.04.05. Păstrarea şi arhivarea documentelor asigură confidențialitatea, integritatea și securitatea datelor.|Arhiva fizică a spitalului este securizată împotriva accesului neautorizat, distrugerii, incendiului.
I|01.05.04.06|01.05.04.06. Distrugerea documentelor/înregistrarilor se realizează cu păstrarea confidențialității.|Există procedură specifică pentru tocarea / arderea documentelor confidentiale.
C|01.05.05|01.05.05. Sistemul informațional asigură documentarea și susține procesul educațional al angajaţilor.
I|01.05.05.01|01.05.05.01. Sistemul informațional asigură documentarea și informarea angajaților din spital.|Accesul la legislație, proceduri, protocoale este facil.
I|01.05.05.02|01.05.05.02. Sistemul informațional susține procesul de instruire și dezvoltare profesională.|Existența bibliotecilor medicale / abonamente baze de date (Pubmed etc).
S|01.06|01.06. Sistemul de comunicare existent la nivelul spitalului răspunde nevoilor organizaţiei.
C|01.06.01|01.06.01. Comunicarea externă răspunde nevoilor beneficiarilor și ale spitalului.
I|01.06.01.01|01.06.01.01. Spitalul pune la dispoziția publicului canale de comunicare variate.|Telefon, e-mail, registru sesizări, program audiențe.
I|01.06.01.02|01.06.01.02. Pagina de internet a spitalului asigură comunicarea eficientă.|Site actualizat conform Legii transparenței decizionale și nevoilor pacientului.
I|01.06.01.03|01.06.01.03. Spitalul asigură condițiile necesare orientării cu uşurinţă.|Pancarte, indicatoare clare, hărți în spital.
I|01.06.01.04|01.06.01.04. Spitalul asigură condițiile necesare identificării personalului.|Purtarea ecusoanelor standardizate și vizibile (Nume, Funcție).
I|01.06.01.05|01.06.01.05. Comunicarea cu mass-media asigură informarea publicului şi promovarea spitalului.|Există purtător de cuvânt desemnat.
I|01.06.01.06|01.06.01.06. Spitalul oferă informații privind activitatea medicală prestată.|Materiale informative privind pachetele de servicii oferite.
I|01.06.01.07|01.06.01.07. Comunicarea externă se realizează având în vedere continuitatea procesului de îngrijire.|Colaborare documentată cu medicii de familie și asistența comunitară.
I|01.06.01.08|01.06.01.08. Spitalul are organizată comunicarea cu alte unități sanitare şi alte structuri.|Protocoale de transfer și servicii medicale externe.
C|01.06.02|01.06.02. Comunicarea internă răspunde nevoilor pacienților și ale spitalului.
I|01.06.02.01|01.06.02.01. Spitalul are implementate modele de comunicare profesională între membrii echipelor.|Ședințe raport de gardă, comitete directoare.
I|01.06.02.02|01.06.02.02. Spitalul are stabilite şi utilizează protocoale de comunicare specifică între profesionişti.|Transmiterea valorilor critice de laborator, protocoale la limită de schimb (predare-primire gardă).
I|01.06.02.03|01.06.02.03. Regulile interne sunt comunicate personalului şi pacienţilor.|Regulile interne trebuie să fie accesibile și clare pentru toți membrii organizației.
C|01.06.03|01.06.03. Comunicarea cu pacientul urmăreşte implicarea acestuia în procesul de îngrijire.
I|01.06.03.01|01.06.03.01. Comunicarea personalului cu pacientul urmăreşte educarea în vederea implicării terapeutice.|Materiale scrise sau explicații privind regimul de viață după boală.
I|01.06.03.02|01.06.03.02. Spitalul analizează anual eficiența și eficacitatea comunicării.|Audit privind percepția pacienților despre comunicarea cu medicul curant.
S|01.07|01.07. Sistemul de management al calității serviciilor este operațional și asigură desfăşurarea proceselor.
C|01.07.01|01.07.01. Sistemul de management al calității vizează optimizarea continuă a proceselor organizației.
I|01.07.01.01|01.07.01.01. Managementul spitalului asigură organizarea sistemului de management al calității serviciilor.|Există un nucleu/birou SMC (Structura de Management al Calității).
I|01.07.01.02|01.07.01.02. Structura de management al calității serviciilor coordonează procesul de îmbunătățire a calității.|Plan de acțiuni și program pentru calitatea serviciilor.
I|01.07.01.03|01.07.01.03. Spitalul se preocupă de certificarea de calitate a activităților desfășurate.|Certificare tip ISO (opțional/recomandat).
C|01.07.02|01.07.02. Structura de management al calității (SMC) asigură dezvoltarea culturii calității în spital.
I|01.07.02.01|01.07.02.01. Spitalul are stabilite şi urmărește respectarea principiilor și valorilor calității.|Sunt diseminate obiectivele în materie de calitate.
I|01.07.02.02|01.07.02.02. Spitalul se preocupă de implementarea și dezvoltarea culturii calității în spital.|Instruirea continuă a personalului pe standardele ANMCS.
C|01.07.03|01.07.03. Spitalul elaborează și implementează un plan de acțiuni privind asigurarea calității.
I|01.07.03.01|01.07.03.01. Planificarea anuală a activităților SMC asigură conformarea la cerințele standardelor de acreditare.|Planul de conformare la standarde.
I|01.07.03.02|01.07.03.02. Planul de acțiuni pentru implementarea managementul calității serviciilor este asumat de conducere.|Managementul spitalului alocă resursele necesare.
I|01.07.03.03|01.07.03.03. SMC monitorizează implementarea planului de acțiuni pentru asigurarea calității serviciilor.|Rapoarte de evaluare a conformității.
I|01.07.03.04|01.07.03.04. Pe baza recomandărilor SMC spitalul ia măsuri de îmbunătățire a calității serviciilor.|Adoptarea și actualizarea procedurilor.
C|01.07.04|01.07.04. Spitalul urmăreşte creşterea nivelului de satisfacţie a pacienţilor.
I|01.07.04.01|01.07.04.01. Spitalul elaborează şi actualizează periodic chestionare de satisfacţie a pacienţilor.|Chestionare anonime prelucrate periodic.
I|01.07.04.02|01.07.04.02. SMC analizează sistematic informaţiile rezultate din prelucrarea chestionarelor şi emite recomandări.|Rapoarte de analiză a gradului de satisfacție a pacienților.
I|01.07.04.03|01.07.04.03. Spitalul utilizează analiza periodică a reclamaţiilor primite pentru a îmbunătăţi serviciile medicale.|Registru pentru reclamații, petiții și sesizări, analizat în consiliul etic și comitetul director.
C|01.07.05|01.07.05. Programul de îmbunătățire a calității prevede eficientizarea activităţii spitalului.
I|01.07.05.01|01.07.05.01. Este stabilită o modalitate de evaluare a eficienţei proceselor de îmbunătățire a calității derulate.|Auditul clinic și analiza indicatorilor de performanță (ICM).
I|01.07.05.02|01.07.05.02. Rezultatele evaluărilor SMC sunt utilizate pentru eficientizarea activităţilor.|Măsuri aplicate post-evaluare.
S|01.08|01.08. Managementul riscurilor neclinice previne apariția prejudiciilor și fundamentează procesul decizional.
C|01.08.01|01.08.01. Toate nivelurile de management au implementat o modaliatate de management al riscurilor.
I|01.08.01.01|01.08.01.01. Managerii de la toate nivelurile au organizate identificarea, analiza şi tratarea riscurilor.|Responsabil management riscuri desemnat la nivelul spitalului.
I|01.08.01.02|01.08.01.02. Spitalul are un registru al riscurilor şi monitorizează eficacitatea măsurilor de prevenţie.|Registrul general de riscuri este actualizat anual.
I|01.08.01.03|01.08.01.03. Managementul spitalului efectuează analizele de risc pe tipuri, probabilitate și impact.|Scala probabilitate-impact aplicată în proceduri.
C|01.08.02|01.08.02. Managementul riscurilor neclinice asigură protecţia pacienților, angajaţilor și vizitatorilor.
I|01.08.02.01|01.08.02.01. Sunt identificate locurile și condițiile cu potențial de risc fizic pentru securitatea persoanelor.|Marcarea corespunzătoare a zonelor periculoase (podea umedă, etc).
I|01.08.02.02|01.08.02.02. Managementul deșeurilor respectă regulile pentru prevenirea contaminării toxice și infecțioase.|Contract cu firmă autorizată pentru preluarea deșeurilor biologice și a recipientelor pentru tăietoare.
I|01.08.02.03|01.08.02.03. Funcționarea serviciilor vitale ale spitalului este asigurată.|Grup electrogen (generator), rezervă de apă potabilă.
I|01.08.02.04|01.08.02.04. Capacitatea şi numărul lifturilor asigură volumul, tipurile și fluxurile de transport în spital.|Service ISCIR la zi pentru ascensoare, separarea fluxurilor de pacient vs materiale murdare dacă este posibil.
I|01.08.02.05|01.08.02.05. La nivelul spitalului sunt adoptate măsuri de protecție, pază și securitate pentru bunuri și persoane.|Pază proprie sau externalizată, sistem de supraveghere video pe holuri.
I|01.08.02.06|01.08.02.06. Spitalul implementează măsuri de gestionare a riscurilor la seism.|Planul de evacuare și acțiune în caz de cutremur afișat.
I|01.08.02.07|01.08.02.07. Spitalul implementează măsuri de gestionare a riscului de incendiu.|Instruire PSI/SU, extinctoare cu revizia la zi, hidranți funcționali.
I|01.08.02.08|01.08.02.08. Spitalul implementeaza măsuri de gestionare a riscului de explozie.|Depozitarea conformă a buteliilor de oxigen și a gazelor medicale.
I|01.08.02.09|01.08.02.09. Spitalul implementează măsuri de gestionare a riscului de contaminare chimică și biologică.|Existența kiturilor antiversare pentru substanțe toxice/citostatice/produse biologice.
I|01.08.02.10|01.08.02.10. Spitalul implementează măsuri de gestionare a riscului de iradiere.|Aprobări CNCAN și dosimetrie individuală pentru personalul de la radiologie.
I|01.08.02.11|01.08.02.11. Spitalul are prevăzute măsuri pentru siguranța fizică a angajaţilor.|Control de medicina muncii anual și evaluarea stării de sănătate a personalului.
I|01.08.02.12|01.08.02.12. Responsabilii cu prevenirea riscurilor tehnologice sunt nominalizați prin decizie și instruiți.|RSVTI, responsabil protecția mediului, responsabil PSI, Protecția muncii.
I|01.08.02.13|01.08.02.13. Personalul expus la risc este instruit periodic cu privire la măsurile de prevenire.|Fișe de instructaj SSM și PSI semnate la zi.
I|01.08.02.14|01.08.02.14. Sunt organizate evaluări periodice ale modului de respectare a măsurilor de prevenire a riscurilor.|Rapoarte referitoare la numărul de accidente de muncă.
C|01.08.03|01.08.03. Modul de acțiune, responsabilitățile și rezerva de resurse utilizabile în caz de situații excepționale.
I|01.08.03.01|01.08.03.01. Echipele de intervenție pentru situații de dezastre naturale sau catastrofă sunt actualizate.|Planul Alb aplicabil situațiilor de urgență / aflux masiv de pacienți.
I|01.08.03.02|01.08.03.02. La nivelul spitalului este constituită rezerva de resurse utilizabile în caz de dezastru.|Există un stoc de medicamente de urgență blocat pentru situații de catastrofă.
I|01.08.03.03|01.08.03.03. Spitalul are organizată evidența resurselor vizate de sarcini specifice la mobilizare şi razboi.|Aprobat prin organele abilitate ale structurii județene / ministeriale.
S|01.09|01.09. Mediul de îngrijire asigură condițiile necesare pentru desfăşurarea asistenței medicale.
C|01.09.01|01.09.01. Organizarea mediului de îngrijire respectă condițiile privind capacitatea și competenţele asumate.
I|01.09.01.01|01.09.01.01. Condiţiile hoteliere răspund particularităților fiecărui pacient.|Numărul de paturi din salon corespunde normativelor de spațiu pe pat (mp/pat).
I|01.09.01.02|01.09.01.02. Îngrijirile sunt acordate cu respectarea dreptului la intimitate.|Existența paravanelor în saloane la momentul examinării clinice a pacientului.
I|01.09.01.03|01.09.01.03. Deplasarea pacienţilor în spital se realizează în condiții de siguranță și comfort, respectând circuitele.|Existența tărgilor/cărucioarelor și a rampelor pentru persoanele cu dizabilități.
I|01.09.01.04|01.09.01.04. Curăţenia și dezinfecția spațiilor şi a echipamentelor sunt reglementate și monitorizate.|Planurile de curățenie și dezinfecție sunt afișate și bifate zilnic de infirmiere.
I|01.09.01.05|01.09.01.05. Instituţia asigură și îşi asumă calitatea sterilizării.|Respectarea ciclurilor de sterilizare, existența testelor chimice/biologice din autoclav în registrele de sterilizare.
I|01.09.01.06|01.09.01.06. Alimentația pacientului este stabilită în concordanţă cu recomandările igieno-dietetice.|Tabel cu regimurile alimentare (1-10 sau specific) prescris de medicul curant și dietetician.
I|01.09.01.07|01.09.01.07. Instituţia asigură calitativ şi cantitativ hrana, în condiții de siguranță a alimentului.|Analize de laborator pe probe de alimente gătite pastrate la frigider (48 de ore).
I|01.09.01.08|01.09.01.08. Instituţia asigură circuitele alimentelor cu respectarea regulilor de igienă.|Circuitul blocului alimentar, transportul în recipiente izoterme către secții.
I|01.09.01.09|01.09.01.09. Instituţia asigură calitativ și cantitativ lenjerie şi efecte pentru pacienţi şi personal medical.|Existența schimbului optim de lenjerie pentru rulaj.
I|01.09.01.10|01.09.01.10. Instituția asigură circuitul lenjeriei cu respectarea regulilor de igienă.|Spălătoria are bariera igienică separând curatul de murdar; transport în saci dedicați.
C|01.09.02|01.09.02. Mediul de îngrijire este evaluat şi adaptat permanent la necesitățile asistenței medicale.
I|01.09.02.01|01.09.02.01. Instituţia evaluează şi îmbunătăţeşte constant condiţiile hoteliere.|Modernizări periodice ale saloanelor, grupurilor sanitare.
I|01.09.02.02|01.09.02.02. Instituţia evaluează şi îmbunătăţeşte constant serviciile de alimentație.|Monitorizarea calității hranei de către medicii sau SMC.
I|01.09.02.03|01.09.02.03. Instituţia evaluează şi îmbunătăţeşte constant serviciul de spălătorie.|Controale igienico-sanitare privind curățenia lenjeriei de pat.
I|01.09.02.04|01.09.02.04. Instituția evaluează şi îmbunătățește constant mediului ambiant.|Iluminat optim, ventilație adecvată a secțiilor, climatizare.
R|2|REFERINȚA 2: MANAGEMENTUL CLINIC
S|02.01|02.01. Preluarea în îngrijire a pacienţilor se face conform nevoilor acestora, misiunii şi resurselor disponibile.
C|02.01.01|02.01.01. Spitalul şi-a stabilit gradul de compentență tehnic și profesional.
I|02.01.01.01|02.01.01.01. Spitalul evaluează grupurile populaționale cu particularități clinico-biologice.|Pacienții cronici sau specifici sunt evaluați în baza protocolului (vârstnici, copii, gravide).
I|02.01.01.02|02.01.01.02. Spitalul a identificat patologiile pentru care dispune de resurse.|Criteriile de internare exclud transferurile nejustificate ale pacienților pentru care spitalul nu are profil/competentă.
C|02.01.02|02.01.02. Preluarea în îngrijire a pacienților este organizată pentru a facilita accesul.
I|02.01.02.01|02.01.02.01. Primirea și consultul pacientului programat sunt reglementate la nivelul spitalului.|Există listă de așteptare pentru pacienții cronici și criterii de prioritizare.
I|02.01.02.02|02.01.02.02. Sistemul de programare a pacienților este organizat astfel încât să nu afecteze urgențele.|Circuit separat la internări / ambulatoriu de circuitul de primire Urgențe / Gardă.
C|02.01.03|02.01.03. Spitalul are organizat serviciul de urgenţe medicale.
I|02.01.03.01|02.01.03.01. Spitalul asigură asistența medicală de urgență, în limitele competențelor sale, permanent.|Program de gardă 24/7 asigurat la nivel de medic și asistent.
I|02.01.03.02|02.01.03.02. Personalul medical angajat în UPU/CPU/Gardă este calificat conform prevederilor legale.|Medicii care asigură garda au specialitatea corespunzătoare conform liniei de gardă.
I|02.01.03.03|02.01.03.03. Serviciul de urgenţă (camera de gardă/UPU/CPU) este organizat eficace şi eficient.|Timpul de așteptare la triaj și în zona de asistență de urgență este monitorizat permanent.
C|02.01.04|02.01.04. Spitalul asigură servicii adaptate și pentru persoanele cu dizabilități, nevoi speciale.
I|02.01.04.01|02.01.04.01. Pacientul cu dizabilități sau nevoi speciale beneficiază de condiții adecvate de preluare.|Persoane cu deficiențe de auz/văz/locomotorii beneficiază de acces cu rampe/translatori de semne (după caz).
I|02.01.04.02|02.01.04.02. Spitalul este pregătit pentru managementul pacientului cu manifestări agresive.|Există o procedură pentru pacienții recalcitranți și colaborare cu paza/poliția.
C|02.01.05|02.01.05. Spitalele de psihiatrie sau spitalele cu secții de psihiatrie asigură servicii adaptate.
I|02.01.05.01|02.01.05.01. Spitalul de psihiatrie reglementează internarea nevoluntară a pacientului psihiatric.|Există procedură cu respectarea legii Sănătății Mintale (Legea 487).
I|02.01.05.02|02.01.05.02. Spitalul de psihiatrie reglementează internarea pacienților în vederea expertizei medico-legale.|Camere specifice și colaborare cu IML / Politie.
I|02.01.05.03|02.01.05.03. Spitalul de psihiatrie reglementează preluarea în îngrijire a pacientului psihiatric arestat.|Zone cu paza poliției asigurate.
I|02.01.05.04|02.01.05.04. Spitalul de psihiatrie are prevăzute măsuri speciale, de prevenire si limitare a manifestărilor violente.|Aparatură specifică sau medicație sedativă la îndemână, conform protocolului de contenționare.
I|02.01.05.05|02.01.05.05. Externarea pacientului psihiatric este reglementată și adaptată modalității de internare.|Avizarea externării nevoluntare conform comisiei.
S|02.02|02.02. Evaluarea inițială urmăreşte identificarea nevoilor pacienţilor în contextul factorilor de risc.
C|02.02.01|02.02.01. Procesul de evaluare a nevoilor pacientului este bine definit la nivelul spitalului.
I|02.02.01.01|02.02.01.01. În funcție de starea inițială se decide dacă spitalul poate prelua pacientul.|Medicul din UPU sau gardă consemnează fișa de evaluare și decide internarea.
I|02.02.01.02|02.02.01.02. Spitalul are organizată o modalitate de orientare a pacienților care depășesc competențele.|Există protocol clar de transfer interclinic al pacientului critic către eșaloane superioare.
I|02.02.01.03|02.02.01.03. Recunoaşterea rezultatelor investigațiilor efectuate în alte unități sanitare sunt reglementate.|Medicii iau în considerare analizele aduse de pacient (din ultimele zile).
C|02.02.02|02.02.02. Evaluarea iniţială a pacientului include factorii psihocomportamentali și socioeconomici.
I|02.02.02.01|02.02.02.01. Spitalul se implică în rezolvarea cazurilor cu particularități psihoemoționale și socioeconomice.|Identificarea persoanelor fără adăpost sau victimelor violenței domestice. Implicarea asistentului social.
I|02.02.02.02|02.02.02.02. Traseul pacientului este stabilit în raport și cu profilul psihocomportamental și socioeconomic.|Implicarea psihologului, după caz.
I|02.02.02.03|02.02.02.03. Managementul durerii acute sau cronice începe din etapa evaluării inițiale.|Durererea se scalează la internare (Scala vizuală analoagă 0-10) de către asistent sau medic.
S|02.03|02.03. Practica medicală abordează integrat și specific pacientul cu asigurarea continuității.
C|02.03.01|02.03.01. Managementul cazului este bazat pe utilizarea protocoalelor de diagnostic şi tratament.
I|02.03.01.01|02.03.01.01. Acordarea asistenței medicale se face conform unei planificării stabilite de către medic.|Plan de tratament menționat în Foaia de Observație (FOCG) la internare și evoluție.
I|02.03.01.02|02.03.01.02. Elaborarea protocoalelor de diagnostic și tratament este făcută pe baza dovezilor (EBM).|Protocoale medicale avizate pe secție cu sursa bibliografică de la comisii de specialitate.
I|02.03.01.03|02.03.01.03. Protocoalele de diagnostic şi tratament sunt utilizate individualizat.|Pacientul nu este standardizat, ci adaptat afecțiunilor cronice concomitente.
I|02.03.01.04|02.03.01.04. Evaluarea eficienței și eficacității protocoalelor se efectuează periodic.|Auditul clinic evaluează dacă s-au urmat protocoalele pe cazuri randomizate.
I|02.03.01.05|02.03.01.05. Actualizarea protocoalelor se face când evaluările periodice o impun.|Protocoale modificate în funcție de noile ghiduri terapeutice și avizate de Directorul Medical.
C|02.03.02|02.03.02. Abordarea integrată a pacientului este o uzanță a practicii medicale.
I|02.03.02.01|02.03.02.01. Spitalul asigură o abordare multidisciplinară a practicii medicale, completă și personalizată.|Abordare multi-sistemică prin utilizarea de echipe mixte în secții (ex. chirurg + cardiolog).
I|02.03.02.02|02.03.02.02. Consulturile interdisciplinare sunt fundamentate şi consemnate în foaia de observaţie.|Fișa consultului interclinic este semnată de medicul specialist solicitat.
I|02.03.02.03|02.03.02.03. A doua opinie medicală este analizată şi utilizată de către spital.|Pacientul are dreptul să solicite a 2-a opinie, conform reglementărilor scrise.
I|02.03.02.04|02.03.02.04. Spitalul se preocupă de depistarea pacienților cu boală cronică de rinichi (BCR).|Laboratorul semnalează valorile reduse ale eGFR (Rata filtrării glomerulare).
I|02.03.02.05|02.03.02.05. Comisia multidisciplinară oncologică decide tratamentul pacientului oncologic.|Funcționarea Tumor Board-ului, cu rapoarte semnate de oncolog, chirurg, radioterapeut.
C|02.03.03|02.03.03. Spitalul asigură continuitatea actului medical ulterior evaluării iniţiale.
I|02.03.03.01|02.03.03.01. Spitalul asigură condițiile necesare pentru continuitatea actului medical.|Preluarea de pe secția ATI pe secția de pacienți de tip cronici / acuți se face cursiv.
I|02.03.03.02|02.03.03.02. Spitalul asigură condiții pentru accesul pacientului la serviciile de recuperare/reabilitare.|Kinetoterapie oferită pe parcursul spitalizării pentru reducerea duratelor de spitalizare.
C|02.03.04|02.03.04. Planul de îngrijire a pacientului este parte integrantă din managementul cazului.
I|02.03.04.01|02.03.04.01. Personalul medical asigură îngrijirea completă și personalizată a pacientului.|Asistentul medical efectuează proceduri pe baza evaluării sale autonome.
I|02.03.04.02|02.03.04.02. Planul de îngrijire individualizat este întocmit de către asistentul medical, pe baza recomandărilor.|Fișele de plan de îngrijire completate pe ture de către asistentul de salon.
I|02.03.04.03|02.03.04.03. Planul de îngrijire este adaptat în funcţie de evoluţia pacientului.|Re-evaluarea nevoilor (ex. aparitia escarelor) pe parcursul internării.
I|02.03.04.04|02.03.04.04. La externare se întocmeşte un plan de îngrijiri care se comunică pacientului şi medicului de familie.|Scrisoare medicală clară, bilet de externare semnat la plecare.
I|02.03.04.05|02.03.04.05. Necesarul de personal medical de îngrijire este stabilit în funcţie de nevoia de îngrijire.|Repartizarea uniformă a sarcinilor și preluarea turelor.
C|02.03.05|02.03.05. Datele medicale sunt înregistrate corect, complet, în timp real şi evitând redundanţele.
I|02.03.05.01|02.03.05.01. Spitalul stabilește datele necesare a fi culese, consemnate şi monitorizate pe întreaga durată.|Completarea FO se realizează zilnic (evoluție zilnică).
I|02.03.05.02|02.03.05.02. Personalul medical consemnează informațiile privind îngrijirile acordate şi rezultatele investigaţiilor.|Asistenta consemnează funcțiile vitale grafic la indicația medicului (TA, Puls, Temp, Respiratii).
S|02.04|02.04. Spitalul promoveză conceptul de "prieten al copilului".
C|02.04.01|02.04.01. Spitalul a adoptat o politică de promovare a alimentației la sân în secțiile de neonatologie.
I|02.04.01.01|02.04.01.01. Spitalul susține un program de alăptare ca metodă sănătoasă de alimentaţie a nou-născutului.|Existența politicii "Baby Friendly Hospital".
I|02.04.01.02|02.04.01.02. Mamele internate sunt informate în privința beneficiilor alăptării.|Materiale vizuale sau educație față în față pentru lăuze.
I|02.04.01.03|02.04.01.03. Personalul medical din obstetrică-ginecologie şi neonatologie este format continuu în domeniu.|Certificări pe consultanță în alăptare (recomandat).
I|02.04.01.04|02.04.01.04. Spitalul asigură facilități pentru promovarea şi susţinerea alăptării.|Sistem "rooming-in" pentru mamă-copil.
C|02.04.02|02.04.02. Spitalul se preocupă de identificarea și prevenirea cazurilor de îmbolnăvire la nou-născut.
I|02.04.02.01|02.04.02.01. Spitalul previne bolile infectocontagioase ale nou-născutului.|Măsuri stricte de izolare în caz de focar.
I|02.04.02.02|02.04.02.02. Spitalul identifică malformațiile/deficienţele nou-născutului.|Screening obligatoriu: auditiv, metabolic, etc. conform PNN.
C|02.04.03|02.04.03. Spitalul se preocupă de asigurarea unui climat prietenos, adaptat copilului.
I|02.04.03.01|02.04.03.01. Spitalul asigură condiții adaptate îngrijirii copilului.|Decorare saloane pediatrie, spații de joacă (acolo unde secția o permite).
I|02.04.03.02|02.04.03.02. Spitalul asigură servicii de susținere a asistenței medicale pentru copii.|Posibilitatea internării cu însoțitor.
S|02.05|02.05. Serviciile paraclinice corespund nevoilor de investigare.
C|02.05.01|02.05.01. Întreaga activitate a serviciilor paraclinice este efectuată în colaborare cu medicii clinicieni.
I|02.05.01.01|02.05.01.01. Secțiile definesc și estimează nevoia de servicii paraclinice în funcție de nivelul de competență.|Se transmit lunar numărul de seturi de analize / examinări CT/RMN necesare.
I|02.05.01.02|02.05.01.02. Specialiştii din serviciile paraclinice fac parte din echipa multidisciplinară pentru rezolvarea cazurilor.|Medicul imagist / de laborator participă la deciziile pe cazurile complexe.
C|02.05.02|02.05.02. Serviciile paraclinice răspund necesităţilor de investigare a pacienţilor (acces, calitate, timp).
I|02.05.02.01|02.05.02.01. Monitorizarea și analiza neconformităților sunt utilizate pentru îmbunătațirea activității paraclinice.|În laborator se înregistrează probele respinse și motivele respingerii.
I|02.05.02.02|02.05.02.02. Intervalele de referință ale rezultatelor examinărilor, valorile de alertă şi valorile critice sunt comunicate.|Procedura de raportare "Valoare Critică" de la laborator către secție se face telefonic/sistem IT de urgență.
I|02.05.02.03|02.05.02.03. Practicile de radiodiagnostic, radiologie intervenţională şi explorări funcţionale sunt centrate pe nevoile pacientului.|Protocol pentru utilizarea substanței de contrast și gestionarea reacțiilor adverse.
C|02.05.03|02.05.03. Laboratorul se preocupă de satisfacerea în condiții optime a nevoilor de investigare.
I|02.05.03.01|02.05.03.01. Laboratorul stabileşte soluțiile de satisfacere a nevoilor de investigații în condiții de eficiență.|Participarea la programe de Control Extern al Calității Laboratorului (RENAR, etc).
I|02.05.03.02|02.05.03.02. Spitalul reglementează condițiile necesare desfăşurării proceselor de preexaminare și postexaminare de laborator.|Transportul corect al probelor de la secție la laborator (temperatură și timp controlate).
S|02.06|02.06. Spitalul de nefrologie sau cu secții de nefrologie asigură continuitatea asistenței pentru pacienții cu BCR.
C|02.06.01|02.06.01. Spitalul asigură accesul pacienților cu BCR la tratamentul de supleere a funcției renale (TSFR).
I|02.06.01.01|02.06.01.01. Pacienții aflați în evidența de nefrologie sunt tratați în vederea reducerii ratei de progresie a BCR.|Evidență corectă a valorilor de eGFR pe perioadă lungă.
I|02.06.01.02|02.06.01.02. Spitalul se preocupă de pregătirea pacienților cu BCR pentru tratamentul de supleere renală.|Montarea fistulei arteriovenoase în stadiile predializă.
C|02.06.02|02.06.02. Eficacitatea şi eficienţa TSFR (tratamentelor de supleere renală) sunt preocupări constante.
I|02.06.02.01|02.06.02.01. Unitatea care inițiază dializa decide asupra modalității de TSFR de comun acord cu pacienții.|Informare hemodializă versus dializă peritoneală.
I|02.06.02.02|02.06.02.02. Unitatea care inițiază dializa colaborează cu secțiile de nefrologie şi cu centrele ambulatorii de dializă.|Scrisoare și transfer medical la inițierea tratamentului de lungă durată.
C|02.06.03|02.06.03. Unitatea de dializă în regim de spitalizare de zi monitorizează evoluția pacienţilor dializați.
I|02.06.03.01|02.06.03.01. Unitatea de dializă transmite on-line toți parametri de monitorizare către Registrul Renal Român.|Raportări în platforma RRR la zi.
I|02.06.03.02|02.06.03.02. Unitatea de dializă în regim de spitalizare de zi controlează anemia pacienților dializați.|Verificare nivel de Hb, feritină și prescriere Erytropoietină (EPO).
I|02.06.03.03|02.06.03.03. Unitatea de dializă în regim de spitalizare de zi controlează metabolismul mineral.|Monitorizarea PTH, fosforului seric.
I|02.06.03.04|02.06.03.04. Unitatea de dializă în regim de spitalizare de zi controlează acidoza.|Modificarea soluțiilor de dializă corespunzător cu gazele sanguine.
I|02.06.03.05|02.06.03.05. Unitatea de dializă, în regim de spitalizare de zi monitorizează riscul infecțios specific pacientului dializat.|Vaccinări contra virus hepatitic B la cei neresponderi, teste periodice de virusologie HIV/AgHBs/HCV.
I|02.06.03.06|02.06.03.06. Unitatea de dializă în regim de spitalizare de zi monitorizează starea de nutriție a pacienților dializați.|Urmărirea greutății uscate la ieșirea din dializă și aportului proteic.
I|02.06.03.07|02.06.03.07. Unitatea de dializă în regim de spitalizare de zi monitorizează eficiența dializei (HD/DP).|Calcularea parametrilor Kt/V lunar.
I|02.06.03.08|02.06.03.08. Unitatea de dializă în regim de spitalizare de zi se preocupă de creșterea calității vieții pacienților.|Grupuri de suport, evaluări psihologice.
I|02.06.03.09|02.06.03.09. Unitatea de dializă are o politică de creştere a autonomiei pacienților.|Pacienții sunt încurajați să participe activ la conectarea/deconectarea din APD (dializa peritoneală).
S|02.07|02.07. Radioterapia şi/sau medicină nucleară asigură nevoile de tratament specifice.
C|02.07.01|02.07.01. Practica de radioterapie/medicină nucleară este adaptată nevoilor specifice ale pacientului.
I|02.07.01.01|02.07.01.01. Dotarea serviciului de radioterapie/medicină nucleară asigură nevoile de tratament specifice.|Echipamente și dozimetrie calibrate de fizicianul medical.
I|02.07.01.02|02.07.01.02. Radioterapia/medicina nucleară respectă regulile de bună practică specifice.|Protocol standard pentru conturarea leziunilor înainte de iradiere.
C|02.07.02|02.07.02. Practica de radioterapie/medicină nucleară este monitorizată şi evaluată periodic.
I|02.07.02.01|02.07.02.01. Radioterapia/medicina nucleară utitizată în tratamentul pacientului oncologic este monitorizată.|Managementul iradierii și urmăririi efectelor secundare cutanate/sistemice.
I|02.07.02.02|02.07.02.02. Practica de radioterapie/medicină nucleară este evaluată și îmbunătățită constant.|Audit pe baza evoluției pacienților (remisiune, complicații).
S|02.08|02.08. Îngrijirile paliative şi terminale se adresează pacienţilor cu boli cronice progresive şi familiilor.
C|02.08.01|02.08.01. Managementul pacienţilor cu boli cronice progresive şi nevoi de îngrijiri paliative se face individualizat.
I|02.08.01.01|02.08.01.01. Nevoile de îngrijiri paliative la pacienții cu boală cronică progresivă sunt identificate prompt.|Utilizarea de instrumente (ex. SPICT) pentru identificarea pacienților eligibili.
I|02.08.01.02|02.08.01.02. Internarea pacienţilor cu boală cronică se face pe baza deciziei unei comisii multidisciplinare.|Cazurile depășite terapeutic din alte secții sunt evaluate pentru paliație.
I|02.08.01.03|02.08.01.03. Personalul implicat în îngrijirea pacienților are pregătire recunoscută în îngrijiri paliative.|Atestat în Îngrijiri Paliative pentru medicii titulari.
I|02.08.01.04|02.08.01.04. Durerea şi celelalte simptome specifice bolilor cronice progresive sunt controlate prin metode adecvate.|Protocol de terapie cu analgezice majore (opioide) / plasturi antialgici asigurați continuu.
I|02.08.01.05|02.08.01.05. Pacienții cu boli cronice progresive "cazuri complexe" primesc îngrijire paliativă specializată.|Îngrijire holistică.
C|02.08.02|02.08.02. Îngrijirile paliative sunt oferite într-un mediu adecvat, cât mai apropiat de mediul familial.
I|02.08.02.01|02.08.02.01. Infrastructura de îngrijire paliativă este adaptată nevoilor speciale ale pacientului cu grad ridicat de dependenţă.|Saloane cu maxim 2 paturi/cameră de izolare, fotolii extensibile pentru însoțitori, condiții pentru pacient care nu se poate deplasa.
I|02.08.02.02|02.08.02.02. Infrastructura permite desfăşurarea serviciilor conexe de îngrijire paliativă.|Spații de liniște / discuție pentru familii, capelă / suport spiritual pe secție.
C|02.08.03|02.08.03. Serviciile de îngrijiri paliative asigură îmbunătățirea calităţii vieţii pentru pacient şi familie.
I|02.08.03.01|02.08.03.01. La primirea pacientului se efectuează o evaluare comprehensivă a pacientului/familiei/aparţinătorilor.|Planificare anticipată și discutarea dorințelor pacientului.
I|02.08.03.02|02.08.03.02. Obiectivele îngrijirii paliative, înţelegerea diagnosticului şi prognosticului sunt evaluate împreună cu familia.|Se stabilește "goals of care".
I|02.08.03.03|02.08.03.03. Semnele şi simptomele stării terminale se evaluează folosind scale standardizate şi se documentează.|Notarea grafică a declinului (ESAS, PPS).
I|02.08.03.04|02.08.03.04. Planul de management al pacientului cu nevoie de îngrijiri paliative este elaborat de echipa pluridisciplinară.|Ședință cu psiholog, asistent social, preot/pastor.
I|02.08.03.05|02.08.03.05. Comunicarea echipei medicale cu pacientul/familia/aparţinătorii este permanentă.|Ora de vizită adaptată / lărgită pentru rudele apropiate.
I|02.08.03.06|02.08.03.06. La externare, continuitatea îngrijirilor se face luând în considerare opțiunile pacientului.|Referire la echipe de îngrijiri paliative la domiciliu dacă pacientul dorește plecarea.
C|02.08.04|02.08.04. Asistenţa medicală paliativă este acordată de o echipă pluridisciplinară.
I|02.08.04.01|02.08.04.01. Structura minimă este compusă din: medic cu competență în paleație, farmacist, asistenţi, asistent social.|Organigrama acoperă specialitățile enumerate ca obligatorii.
I|02.08.04.02|02.08.04.02. Echipa include şi alţi specialişti, precum: kinetoterapeut, terapeut ocupaţional, terapeut prin joc.|Colaborări opționale pentru îmbunătățirea rezultatelor.
I|02.08.04.03|02.08.04.03. Membrii echipei pluridisciplinare din serviciile de îngrijire paliativă participă la instruire continuă.|Participare la conferințe, prevenirea Sindromului Burnout pentru angajați.
I|02.08.04.04|02.08.04.04. Instituţia are un program coerent de monitorizare şi menţinere a sănătății muncii personalului.|Servicii de suport psihologic / consiliere pentru cadrele medicale expuse la stresul end-of-life.
C|02.08.05|02.08.05. Managementul stării terminale respectă demnitatea şi confortul pacientului, asigurând suport familiei.
I|02.08.05.01|02.08.05.01. Starea terminală este identificată şi comunicată familiei/aparţinătorilor.|Procedură clară de anunțare a apropierii decesului, în timp util pentru ca familia să se prezinte.
I|02.08.05.02|02.08.05.02. Personalul medical respectă protocolul de stare terminală.|Măsuri paliative finale: toaletarea pacientului decedat, consilierea familiei.
S|02.09|02.09. Managementul farmaceutic și al medicației asigură continuitatea tratamentului și siguranța pacientului.
C|02.09.01|02.09.01. La nivelul spitalului sunt utilizate reguli de prescriere a medicamentelor şi monitorizare.
I|02.09.01.01|02.09.01.01. Condiţiile de prescriere ale medicației în spital sunt stabilite şi cunoscute la nivel de secție și farmacie.|Aprobarea referatelor și fișelor condică.
I|02.09.01.02|02.09.01.02. Farmacologul/Farmacistul clinician este implicat activ în activitatea de prescriere şi monitorizare.|Semnalarea neconformităților / asocierilor medicamentoase periculoase către medic.
I|02.09.01.03|02.09.01.03. Farmacia asigură medicamentele necesare susținerii continuității actului medical.|Nu există întreruperi in tratamentul cu antibiotice vitale sau tratamente cronice pe perioada internării pacientului.
C|02.09.02|02.09.02. Infrastructura şi organizarea activităţii farmaceutice susţin trasabilitatea medicamentelor uzuale.
I|02.09.02.01|02.09.02.01. Activităţile şi responsabilităţile specifice farmaceutice sunt consemnate corespunzător legislaţiei.|Personal cu drept de liberă practică care verifică trasabilitatea medicamentului.
I|02.09.02.02|02.09.02.02. Organizarea activității farmaceutice se face pe baza unor proceduri şi instrucţiuni de lucru specifice.|Recepția produselor, respingerea medicamentelor neconforme.
I|02.09.02.03|02.09.02.03. Organizarea şi dotarea spaţiului de lucru al farmaciei sunt conforme cu legislaţia specifică.|Spații separate pentru preparare, receptură, depozitare și aparatură cu înregistrare a temperaturii.
I|02.09.02.04|02.09.02.04. Circuitul informaţional al produselor farmaceutice este respectat.|Trasabilitate din momentul intrării în magazie până la administrarea pe pacient în sistem (FO).
I|02.09.02.05|02.09.02.05. Medicaţia din studiile clinice este păstrată şi gestionată în condiții optime de farmacia spitalului.|Dacă spitalul desfășoară studii, medicamentele de investigație sunt în seifuri / dulapuri cu circuit separat.
S|02.10|02.10. Spitalul a implementat bunele practici de antibioticoterapie.
C|02.10.01|02.10.01. Spitalul are organizată activitatea de prescriere şi monitorizare a antibioterapiei.
I|02.10.01.01|02.10.01.01. Spitalul a stabilit structurile funcţionale cu atribuţii în monitorizarea bunelor practici.|Există o comisie care se ocupă cu supravegherea consumului de antibiotice cu spectru larg.
I|02.10.01.02|02.10.01.02. Structurile implicate în implementarea şi monitorizarea bunelor practici au stabilit modalităţile de lucru.|Tabel de clasificare al antibioticelor conform OMS (AWaRe: Access, Watch, Reserve).
C|02.10.02|02.10.02. Prescrierea de antibiotice este fundamentată medical şi asigură trasabilitatea utilizării acestora.
I|02.10.02.01|02.10.02.01. Prescrierea antibioticelor se face conform ghidurilor recunoscute și rezultatului antibiogramei.|La 48-72h se face revizuirea de către medic: de-escaladarea (trecerea de pe perfuzabil pe pastile) bazată pe culturi.
I|02.10.02.02|02.10.02.02. Durata prescrierii se stabileşte în funcție de evoluţie şi este documentată.|Mențiunea motivului prelungirii terapiei peste 7 zile direct în Foia de Observație.
I|02.10.02.03|02.10.02.03. Înregistrările prescrierii unui antibiotic permit trasabilitatea utilizării acestuia.|Medicul este menționat la antibiotice de rezervă și aprobate eventual de medicul infecționist.
C|02.10.03|02.10.03. Farmacia spitalului este implicată direct în respectarea bunelor practici de antibioticoterapie.
I|02.10.03.01|02.10.03.01. Farmacia asigură necesarul de antibiotice, luând în considerare evoluția antibioticorezistenței.|Se asigură aprovizionarea continuă cu antibiotice de linia 1.
I|02.10.03.02|02.10.03.02. Farmacia verifică respectarea bunelor practici în prescrierea şi utilizarea antibioticelor.|Semnalizarea consumurilor excesive sau iraționale de Colistin, Meropenem etc.
I|02.10.03.03|02.10.03.03. Farmacia informează periodic prescriptorii cu privire la antibioticele disponibile şi consumul.|Avertizări pentru medici de la farmacie când un antibiotic intră în stoc limitat.
C|02.10.04|02.10.04. Activitatea laboratorului de microbiologie susţine respectarea bunelor practici în utilizarea antibioticelor.
I|02.10.04.01|02.10.04.01. Compartimentul de microbiologie are proceduri de control intern pentru detectarea antibioticorezistenţei.|Screening pentru germeni Multidrog Rezistenți (MRSA, VRE, CRE, ESBL).
I|02.10.04.02|02.10.04.02. Compartimentul de microbiologie colaborează cu SPLIAAM, farmacia, clinicienii şi managementul spitalului.|Raportări și hărți epidemiologice elaborate împreună cu medicul epidemiolog.
C|02.10.05|02.10.05. Serviciile clinice au reglementat utilizarea antibioticelor, conform bunelor practici.
I|02.10.05.01|02.10.05.01. Serviciile clinice au implementat reglementări de antibioticoterapie şi antibioticoprofilaxie.|Profilaxia perioperatorie documentată: la inducție, 1 doză, întreruptă în 24h.
I|02.10.05.02|02.10.05.02. Monitorizarea consumul de antibiotice și trasabilitatea prescrierii şi utilizării sunt asigurate.|Formulare de prescriere specifică pt. antibiotice speciale avizate pe secții.
S|02.11|02.11. Managementul infecţiilor asociate asistenţei medicale respectă bunele practici în domeniu.
C|02.11.01|02.11.01. Managementul spitalului are organizată activitatea de supraveghere şi limitare a IAAM.
I|02.11.01.01|02.11.01.01. Managementul spitalului adoptă măsuri pentru constituirea structurilor implicate în prevenire.|Există SPIAAM/CPLIAAM condusă de un medic epidemiolog / boli infecțioase.
I|02.11.01.02|02.11.01.02. Managementul spitalului asigură implementarea planului anual pentru supravegherea şi prevenirea IAAM.|Buget dedicat conform planului pentru cumpărarea de materiale de dezinfecție premium și teste.
I|02.11.01.03|02.11.01.03. Activitatea de supraveghere şi limitare a IAAM şi a bolilor transmisibile este organizată pe fiecare structură.|În fiecare secție s-a desemnat un medic și o asistentă ca responsabili.
C|02.11.02|02.11.02. Supravegherea mediului de îngrijire reduce gradul de risc infecţios.
I|02.11.02.01|02.11.02.01. Zonele cu risc infecțios sunt identificate şi supravegheate pentru a preveni şi limita IAAM.|Exemplu: Blocul operator, Terapia Intensivă (ATI), sălile de tratament, sunt delimitate corespunzător.
I|02.11.02.02|02.11.02.02. SSPLIAAM monitorizează calitatea aerului şi adoptă măsuri pentru a limita infecțiile aerogene.|Filtre HEPA monitorizate; mentenanța centralelor de tratare aer (CTA) din bloc operator.
I|02.11.02.03|02.11.02.03. Impactul lucrărilor de demolare, construcție asupra calității aerului şi controlului infecțiilor este gestionat.|Pancarte izolatoare și monitorizarea prafului pe durata renovărilor interioare ale spitalului.
I|02.11.02.04|02.11.02.04. Calitatea sterilizării este verificată și supravegheată.|Registru sterilizare completat fără erori de către asistent, teste Bowie-Dick conforme.
I|02.11.02.05|02.11.02.05. SSPLIAAM/CSPLIAAM monitorizează circuitul lenjeriei.|Prelevări sanitare recoltate de pe mâinile angajaților din spălătorie și lenjeria proaspăt curățată.
C|02.11.03|02.11.03. Politica de calitate a spitalului referitoare la siguranţa alimentului are în vedere controlul riscului infecţios.
I|02.11.03.01|02.11.03.01. Activitatea sectorului alimentar al spitalului este controlată (bloc alimentar, biberoneria).|Testări bacteriologice lunare pentru bucătărese/veselă.
I|02.11.03.02|02.11.03.02. Respectarea regulilor de siguranță a alimentului pentru prevenirea infecțiilor este evaluată.|Analize coprocultură și exsudat angajat la blocul alimentar.
C|02.11.04|02.11.04. Managementul clinic al structurilor medicale previne şi limitează riscul infecţios.
I|02.11.04.01|02.11.04.01. Structurile medicale (secții/compartimente, laboratoare) identifică, evaluează și tratează riscul infecțios.|Politici de screening pacienți cronici cu escare (risc purtător MRSA la internare).
I|02.11.04.02|02.11.04.02. Medicii curanți identifică pacienții cu risc infecţios şi adoptă măsuri pentru limitarea acestuia.|Sistem de izolare a pacientului confirmat cu Clostridium (Clostridioides) Difficile – igienă cu clor.
I|02.11.04.03|02.11.04.03. Trasabilitatea privind buna utilizare a dispozitivelor medicale şi materialelor sanitare este asigurată.|Materialele de unică folosință NU sunt resterilizate; eticheta de la cateter este trecută pe fișă.
I|02.11.04.04|02.11.04.04. SSPLIAAM/CSPLIAAM supraveghează respectarea regulilor de igienă a mâinilor.|Monitorizarea consumului de dezinfectant la mia de zile spitalizare. Implementarea celor 5 Momente OMS.
I|02.11.04.05|02.11.04.05. Spitalul respectă metodologiile naţionale de supraveghere a bolilor transmisibile cu potențial nosocomial.|Raportarea către DSP în interval de 24h a bolilor cu grad de IAAM / Focare.
I|02.11.04.06|02.11.04.06. Spitalul gestionează riscul infecțios al personalului.|Raportarea expunerii accidentale profesionale (înțeparea în ac): evaluare protocol HIV/VHC.
I|02.11.04.07|02.11.04.07. Spitalul de specialitate sau cu secție de obstetrică adoptă măsuri de prevenie a riscului infecțios prenatal.|Implementarea protocoalelor specifice pentru prevenirea infecțiilor la nou-născut și mamă.
S|02.12|02.12. Spitalul dezvoltă și implementează o politică de asigurare şi îmbunătățire a siguranței pacientului.
C|02.12.01|02.12.01. Spitalul are o politică proactivă de prevenire a riscurilor clinice.
I|02.12.01.01|02.12.01.01. La nivelul fiecărui sector de activitate medicală sunt documentate şi evaluate periodic riscurile clinice.|Identificarea reacțiilor nedorite în timpul actului medical și raportarea lor.
I|02.12.01.02|02.12.01.02. Spitalul dezvoltă și implementează un sistem de gestionare a evenimentelor santinelă.|Cultura blamării este eliminată, se analizează "Ce a generat" eroare (RCA Root Cause Analysis).
I|02.12.01.03|02.12.01.03. Spitalul a elaborat și aplică o procedură de gestionare a evenimentelor "near miss".|Incidentele care "ar fi putut să se întâmple" dar s-au prevenit la limită sunt înregistrate pentru a schimba sistemul.
I|02.12.01.04|02.12.01.04. Spitalul are un sistem funcțional de identificare a pacientului bazat pe cel puțin două elemente.|Folosirea brățărilor cu cod de bare/nume si cnp - verificarea încrucișată verbală înaintea intervenției.
C|02.12.02|02.12.02. Spitalul urmăreşte identificarea și prevenirea riscurilor și a erorilor legate de medicație.
I|02.12.02.01|02.12.02.01. Înregistrarea şi comunicarea informaţiilor legate de medicaţia pacientului contribuie la evitarea asocierilor.|Medicamentul prescris în FO și în foaia de temperatură coincide, alerte IT de alergii (la penicilină, etc).
I|02.12.02.02|02.12.02.02. Depozitarea şi manipularea medicamentelor cu risc înalt sau asemănătoare sunt reglementate.|Medicamente cu nume similare dar indicații diferite (LASA - Look Alike Sound Alike) sunt stocate pe rafturi distincte, cu avertizare colorată.
I|02.12.02.03|02.12.02.03. Reglementările specifice privind depozitarea şi eliberarea medicamentelor pshihotrope sunt respectate.|Condica pentru stupefiante se închide în dulap încuiat, cheia se predă conform protocol.
I|02.12.02.04|02.12.02.04. Reglementările specifice privind depozitarea şi eliberarea citostaticelor sunt respectate.|Preparare se face în hotă laminară, kit-uri de protecție purtate de asistent.
I|02.12.02.05|02.12.02.05. Reglementările specifice privind depozitarea şi eliberarea soluțiilor concentrate de electroliți sunt respectate.|Soluțiile de KCl concentrat nu se păstrează pe raft liber, ci controlat pentru a preveni administrarea letală accidentală (în bolus).
C|02.12.03|02.12.03. Transferul informaţiei şi al responsabilităţilor privind pacientul asigură continuitatea îngrijirilor.
I|02.12.03.01|02.12.03.01. Predarea-preluarea cazului se face aplicând o modalitate de transfer a informaţiilor stabilită.|Fișa de transfer Inter-secții cuprinde scoruri, linii venoase active și parametrii principali la momentul plecării.
I|02.12.03.02|02.12.03.02. Modul de transfer a informațiilor şi responsabilităţilor la predarea-preluarea cazului se monitorizează.|Predare preluare pacienți la ieșire din tura de noapte.
C|02.12.04|02.12.04. Spitalul urmăreşte creşterea siguranţei actului chirurgical şi anestezic.
I|02.12.04.01|02.12.04.01. În practica chirurgicală și anestezică sunt utilizate liste de verificare specifice (Check-list).|Checklist-ul OMS privind siguranța chirurgicală ("Sign-in, Time-out, Sign-out") implementat în mod real.
I|02.12.04.02|02.12.04.02. În practica medicală sunt aplicate și respectate protocoalele chirurgicale și anestezice.|Formular de evaluare preanestezică semnat, inclusiv riscuri (Mallampati, risc ASA).
I|02.12.04.03|02.12.04.03. Incidentele apărute în practica chirurgicală și anestezică sunt recunoscute și se iau măsuri imediate.|Numărarea compreselor post-operator, managementul echipamentului anestezic critic.
C|02.12.05|02.12.05. La nivelul spitalul sunt asigurate condiții pentru radioprotecția pacienților și a personalului.
I|02.12.05.01|02.12.05.01. Principiile generale privind radioprotecția în radiodiagnostic și medicină nucleară sunt aplicate corect.|Utilizarea șorțurilor de plumb și colierelor de tiroidă la persoana care imobilizează copilul.
I|02.12.05.02|02.12.05.02. Principiile de radioprotecție privind procedurile de radiodiagnostic urmăresc calitatea imaginii și minimum de expunere.|Principiul ALARA "As Low As Reasonably Achievable" implementat pe softul aparatelor.
I|02.12.05.03|02.12.05.03. Principiile de radioprotecție privind radioterapie/medicină nucleară urmăresc stabilirea planului de tratament.|Buncăre și dosimetrie asigurată.
I|02.12.05.04|02.12.05.04. Principiile de radioprotecție privind radiologia intervențională urmăresc optimizarea timpului de intervenție.|Timpul de flouroscopie limitat, raport de doză înregistrat per pacient.
I|02.12.05.05|02.12.05.05. Persoanele care ajută voluntar un pacient sunt informate asupra riscurilor asociate expunerii.|Declarații de luare la cunoștință a rudelor ce stau cu pacientul la pat.
C|02.12.06|02.12.06. Spitalul urmăreşte identificarea şi diminuarea riscurilor asociate procesului investigaţional.
I|02.12.06.01|02.12.06.01. Laboratorul clinic identifică şi evaluează riscurile microbiologice.|Manipularea probelor (în special respiratorii suspecte BK) se face doar în hota de risc biologic.
I|02.12.06.02|02.12.06.02. Riscurile microbiologice ale laboratorului clinic sunt analizate şi se stabilesc reguli de bună practică.|Evitarea formării aerosolilor la centrifugare (utilizarea eprubetelor cu capac etanș).
C|02.12.07|02.12.07. Spitalul urmăreşte identificarea şi diminuarea cauzelor generatoare de vătămări corporale prin cădere/lovire.
I|02.12.07.01|02.12.07.01. Spitalul identifică pacienții cu risc de cădere și ia măsuri pentru prevenirea şi diminuarea consecințelor.|Evaluare a riscului de cădere Scala Morse completată la internare, atașare pictogramă la capătul patului.
I|02.12.07.02|02.12.07.02. Informarea şi educarea pacientului/aparţinătorilor şi personalului contribuie la diminuarea riscurilor de cădere.|Ridicarea barilor la pat. Atenționarea în vederea deplasării doar cu însoțitor.
I|02.12.07.03|02.12.07.03. Spitalul asigură resursele necesare desfăşurării activității de prelevare și/sau transplant.|-
I|02.12.07.04|02.12.07.04. Spitalul asigură condițiile necesare pentru desfăşurarea activităților de prelevare de organe/țesuturi/celule.|Declararea morții cerebrale conform algoritmului național, existând echipamentele de confirmare (EEG, doppler TCD etc).
I|02.12.07.05|02.12.07.05. Spitalul asigură condițiile necesare pentru desfăşurarea activităților de transplant de organe/țesuturi.|Avizare de către Agenția Națională de Transplant (ANT).
I|02.12.07.06|02.12.07.06. La nivelul spitalului este organizată monitorizarea activității de prelevare şi/sau transplant conform ANT.|Coordonatorul de transplant pe spital completează lunar fișa KIP.
S|02.13|02.13. Spitalul a implementat bunele practici transfuzionale și de hemovigilență.
C|02.13.01|02.13.01. Spitalul are organizată activitatea de prescriere și monitorizare a terapiei transfuzionale şi hemovigilența.
I|02.13.01.02|02.13.01.02. Spitalul îndeplineşte condițiile pentru asigurarea terapiei transfuzionale în condiții de siguranță.|Unitatea de Transfuzie Sanguină (UTS) este autorizată, dispune de frigidere avizate, combine pentru plasmă la -30 gr C.
I|02.13.01.03|02.13.01.03. Structurile funcţionale cu atribuţii în monitorizarea terapiei transfuzionale respectă modalitățile de lucru.|Comisia de transfuzie elaborează politica transfuzională din spital.
C|02.13.02|02.13.02. Prescrierea de sânge și derivate este fundamentată medical şi asigură trasabilitatea utilizării.
I|02.13.02.01|02.13.02.01. Prescrierea sângelui și derivatelor se face conform Ghidului Național de utilizare terapeutică raţională.|Se urmărește raportul beneficiu/risc pentru evitarea transfuziei excesive "over-transfusion" (ex: acceptarea anemiei la praguri sigure).
I|02.13.02.02|02.13.02.02. Înregistrările aferente activității de transfuzie sanguină permit trasabilitatea procesului.|Efectuarea grupei de sânge la patul bolnavului înaintea transfuziei (Testul Beth-Vincent la pat) și notarea completă pe pungă.
I|02.13.02.03|02.13.02.03. Spitalul asigură necesarul de sânge și componente sanguine și monitorizează consumul şi traseul produselor.|Recuperarea pungilor goale timp de 24h după procedură în caz de eveniment advers sever.
S|02.14|02.14. Auditul clinic evaluează eficacitatea și eficienţa asistenţei medicale.
C|02.14.01|02.14.01. Activitatea de audit clinic este organizată.
I|02.14.01.01|02.14.01.01. Misiunile de audit clinic intern sunt planificate anual.|Există un program anual la nivelul spitalului / secțiilor aprobat.
I|02.14.01.02|02.14.01.02. Echipa de audit clinic este parte funcțională a structurii de management al calităţii.|Echipa cuprinde medici / profesioniști instruiți.
I|02.14.01.03|02.14.01.03. În situațiile în care se produc evenimentele indezirabile, echipa de audit propune misiuni suplimentare.|Se demarează audit "la cald" în cazul incidenței bruste a IAAM.
C|02.14.02|02.14.02. Îmbunătățirea activității medicale se face utilizând rezultatele auditării clinice.
I|02.14.02.01|02.14.02.01. Recomandările rezultate în urma auditului clinic sunt utilizate pentru îmbunătățirea protocoalelor.|Se redactează note de propunere, iar Directorul Medical le aprobă.
I|02.14.02.02|02.14.02.02. Spitalul urmăreşte îmbunătățirea activității medicale, utilizând protocoale de diagnostic şi terapeutice.|Concluziile rapoartelor de audit sunt diseminate medicilor curanți.
S|02.15|02.15. Externarea şi transferul pacientului se organizează specific, în funcție de starea acestuia.
C|02.15.01|02.15.01. Externarea este planificată, coordonată și documentată.
I|02.15.01.01|02.15.01.01. Estimarea momentului externării se face la internarea pacientului şi se actualizează în funcţie de evoluţie.|În FO se prognozează zilele de internare.
I|02.15.01.02|02.15.01.02. Spitalul îndeplineşte procedurile necesare externării şi asigurării continuității îngrijirilor.|Programarea pacientului pentru controale ulterioare / rețetă compensată / scrisoare medicală.
C|02.15.02|02.15.02. Spitalul are proceduri legate de stări critice sau deces.
I|02.15.02.01|02.15.02.01. Aparţinătorii sunt alertaţi în caz de degradare a stării pacientului, inclusiv de iminența/survenirea decesului.|Anotarea pe foaia de observație a orei la care a fost anunțat aparținătorul declarat la internare de către pacient.
I|02.15.02.02|02.15.02.02. Demnitatea pacientului aflat în stare critică/fază terminală și convingerile sale spirituale sunt luate în considerare.|Posibilitatea asistenței spirituale conform religiei la patul pacientului.
I|02.15.02.03|02.15.02.03. Spitalul are reglementate activitățile necesar a fi desfășurate în situațiile de deces al pacientului.|Procedura menționează 2 ore la pat înainte de transfer la anatomie patologică / morgă, reguli necropsie etc.
R|3|REFERINȚA 3: ETICA MEDICALĂ ȘI DREPTURILE PACIENTULUI
S|03.01|03.01. Spitalul promovează respectul pentru autonomia pacientului.
C|03.01.01|03.01.01. Spitalul asigură conformitatea practicii medicale cu normele etice care se aplică consimţământului (CI).
I|03.01.01.01|03.01.01.01. Spitalul reglementează obținerea consimțământului informat.|Existența unui consimțământ la internare, dar și al consimțământelor individuale procedurale (ex. chirurgie, endoscopie etc).
I|03.01.01.02|03.01.01.02. Identificarea vulnerabilităţilor în procesul obţinerii consimţământului informat al pacienţilor este o preocupare.|Verificarea discernământului, starea cognitivă la vârstnici (scor MMSE eventual).
I|03.01.01.03|03.01.01.03. Sunt aplicate măsuri pentru diminuarea efectelor vulnerabilităţilor identificate referitoare la consimţământ.|Preluarea consimțământului de la tutore legal la copii, persoană numită legal.
C|03.01.02|03.01.02. Spitalul prevede măsuri pentru conformitatea practicii cu normele privind confidenţialitatea datelor medicale.
I|03.01.02.01|03.01.02.01. Spitalul utilizează proceduri unitare privind asigurarea confidențialității și verifică respectarea acestora.|Documente GDPR (Acord pacient cu nominalizarea strictă a persoanelor care pot afla informații despre starea de sănătate).
I|03.01.02.03|03.01.02.03. Spitalul aplică măsuri pentru diminuarea efectelor vulnerabilităţilor identificate cu privire la confidenţialitate.|Paravan sau loc retras pentru a purta discuții private despre diagnostic.
S|03.02|03.02. Spitalul respectă principiul echității și justiției sociale şi drepturile pacienților.
C|03.02.01|03.02.01. Spitalul are politici de prevenire a discriminării în acordarea serviciilor medicale.
I|03.02.01.01|03.02.01.01. Spitalul reglementează prevenirea discriminării.|Acces necondiționat de etnie, sex, religie. Fără tratament preferențial vizibil.
I|03.02.01.02|03.02.01.02. Consiliul etic este constituit, este funcțional și are reglementată activitatea la nivelul spitalului.|Membrii consiliului sunt numiți și organizează ședințe lunare, postând rapoarte pe site.
C|03.02.02|03.02.02. Spitalul asigură accesul la informaţiile medicale personale.
I|03.02.02.01|03.02.02.01. Spitalul reglementează modalitatea prin care se pun la dispoziţia pacientului documentele medicale solicitate.|Procedură pentru cerere eliberare copii din FO (contra cost sau gratuit în condițiile legii).
I|03.02.02.02|03.02.02.02. Spitalul reglementează modalitatea prin care se pun la dispoziția autorităților datele medicale personale.|Eliberarea datelor către procurori / poliție în mod reglementat și vizat de conducere.
C|03.02.03|03.02.03. Spitalul asigură conditii pentru exercitarea dreptului pacientului la a doua opinie medicală.
I|03.02.03.01|03.02.03.01. Spitalul reglementează condițiile în care pacienţii pot beneficia de a doua opinie de la medici neangajaţi.|Facilitarea accesului unui expert extern vizitator, reglementat contractual / formal.
I|03.02.03.02|03.02.03.02. Spitalul reglementează condiţiile în care pacienții pot beneficia de a doua opinie de la medici angajaţi.|Fără reticențe între colegi (pacientul internat poate cere să fie consultat de un alt specialist din spital).
C|03.02.04|03.02.04. Spitalul este preocupat de protecția pacienților în relația cu mediul extern.
I|03.02.04.01|03.02.04.01. Spitalul reglementează modalitatea de acces al mass-mediei în instituţie şi la pacienţi.|Vizita presei se face cu personal însoțitor din administrație și respectarea orelor.
I|03.02.04.02|03.02.04.02. Spitalul protejează pacientul de intruziunile externe.|Pacientul refuză publicitatea: Paza și medicii resping jurnaliștii prezenți nejustificat la camera de gardă.
C|03.02.05|03.02.05. Spitalul reglementează înregistrarea audio/foto/video a pacienţilor în scop medical, didactic şi cercetare.
I|03.02.05.01|03.02.05.01. Spitalul asigură procedurile pentru înregistrarea audio/foto/video a pacientului pentru evitarea culpei.|Filmări ale interacțiunilor conflictuale (doar în zone permise, cu aviz juridic) cu notificare video la triaj.
I|03.02.05.02|03.02.05.02. Spitalul asigură procedurile de înregistrare audio/foto/video în scop medical, didactic și de cercetare.|Consimțământ specific pentru folosirea pozei de la operație în conferințe / cursuri universitare.
S|03.03|03.03. Spitalul promovează principiile binefacerii şi nonvătămării.
C|03.03.01|03.03.01. Spitalul impune limitarea practicii la sfera de competenţă deţinută în cadrul specialității.
I|03.03.01.01|03.03.01.01. Spitalul asigură pentru fiecare secție personalul medical cu competența specifică.|Atestate de competență (Ex: endoscopie pentru interne/gastro, ecografie pt chirurgi).
I|03.03.01.02|03.03.01.02. Spitalul asigură instruirea personalului medical pentru prevenirea depaşirii competențelor deținute.|Monitorizarea deciziilor dincolo de curicula de specialitate de către medicul șef.
C|03.03.02|03.03.02. Depăşirea limitelor competenţei este permisă în interesul pacientului.
I|03.03.02.01|03.03.02.01. Spitalul reglementează condițiile în care depăşirea competenţelor medicale este permisă în interesul pacientului.|Intervenții tip "Life-saving" (salvatoare de viață) imediate, din lipsa specialistului curent (ex: în urgențe).
I|03.03.02.02|03.03.02.02. Spitalul asigură instruirea personalului medical pentru respectarea drepturilor în situațiile de depășire a competențelor.|Medicul este responsabil doar pentru manevrele elementare de resuscitare generală dacă se produce urgența în fața lui.
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
            <p>Pentru moment puteți încărca direct documentul realizat de dumneavoastră pentru acest punct sau să solicitați SMC redactarea unuia conform cerinței specifice din Manualul ANMCS.</p>
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
