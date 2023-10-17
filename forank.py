import streamlit as st
from PIL import Image
import math
import numpy as np
from io import BytesIO
import xlsxwriter

st.set_page_config(page_title='Forankringslengde i berg', layout="wide")




with st.container():

    kol1, kol2, kol3, kol4 = st.columns(4)
    with kol1:
        st.header('Forankringslengde i berg')
        st.write('Denne siden er laget basert på et innlegg av Arild Neby, Tunnel- og betongeksjonen Vegdirektoratet, 2015.')
        st.markdown(
                f'''
                Noen tips:
                * Forankringskraften er typisk 1.1-1.25 ganger den dimensjonerende kraften.
                * Flere parametre kan hentes i tabbellene under.
                * Feltene som allerede er utfylt bør las stå dersom en ikke har annen kjennskap.
                * Partialfaktoren for berg bør vurderes om trengs å være så høy som 3.
    
                ''')
    with kol4:
        av_logo = Image.open(r'av-logo.png')
        st.image(av_logo, caption=None, width=500)



with st.container():
    st.subheader('Parametre')

    left_column, right_column = column = st.columns(2)
    with left_column:

        kraft = st.number_input('Forankringskraft (prøvekraft) [kN]: ')
        d_bolt = st.number_input('Diameter bolt [m]: ')
        d_borehull = st.number_input('Diameter borehull [m]: ')
        pf_m = st.number_input('Partialfaktor mørtel: ', min_value=None, max_value=None, value=1.25)
        pf_b = st.number_input('Partialfaktor berg: ', min_value=None, max_value=None, value=3)

        st.markdown('Etter å ha trykket på "Kalkuler", scroll ned for å se resultatet. :point_down:')

        trykk = Image.open('pics\trykk.jpg')
        st.image(trykk, caption='Heftfasthet og bruddvinkel basert på en bergarts trykkfasthet.')

    with right_column:
        bv = st.number_input('Bergmassen bruddvinkel [grader]: ')
        bp = st.number_input('Karakteristisk heftasthet bruddplan [kPa]: ')
        h_bm = st.number_input('Karakteristisk heftfasthet mellom bolt og mørtel [MPa]: ', min_value=None, max_value=None,value=2.4)
        h_mb = st.number_input('Karakteristisk heftfasthet mellom mørtel og berg [MPa]: ')

        form = st.form(key='my_form')
        submit = form.form_submit_button(label='Kalkuler')

        ba = Image.open('pics\ba.jpg')
        st.image(ba, caption='Tyngedetetthet, trykkfasthet og heftfasthet for vanlige bergarter.')




if submit:

    try:
        with st.container():
            st.subheader('Brudd mellom bolt og mørtel')

            td = (h_bm / pf_m) * 1000
            l_tb = kraft / (td * d_bolt * np.pi)

            st.markdown(
                f'''
                * Dimmensjonerende heftfasthet melllom stål-mørtel: **{round(td,3)} kPa**
                * Dimmensjonerende forankringslengde for bolt-mørtel: **{round(l_tb,3)} m**
    
                ''')

            ltb = Image.open('pics\ltb.jpg')
            st.image(ltb, caption='Formel')

        with st.container():
            st.subheader('Brudd mellom mørtel og berg')

            td2 = (h_mb / pf_m) * 1000
            l_tb2 = kraft / (td2 * d_borehull * np.pi)

            st.markdown(
                f'''
                * Dimmensjonerende heftfasthet mellom mørtel-berg: **{round(td2,3)} kPa**
                * Dimmensjonerende forankringslengde for mørtel-berg: **{round(l_tb2,3)} m**
    
                ''')

            ltb2 = Image.open('pics\ltb2.jpg')
            st.image(ltb2)

        with st.container():
            st.subheader('Brudd i berg')

            lam = math.sqrt((pf_b * kraft) / (bp * np.pi * math.tan(math.radians(bv))))

            st.markdown(
                f'''
                * Dimmensjonerende forankringslengde for brudd i berg: **{round(lam,3)} m**
    
                ''')

            left_col, right_col = st.columns(2)
            with left_col:
                lampic = Image.open('pics\lampic.jpg')
                st.image(lampic)
            with right_col:
                lampic2 = Image.open('pics\lampic2.jpg')
                st.image(lampic2)

            forank = max(l_tb, l_tb2, lam)

            string = f'Dimensjonerende forankringslengde: {round(forank,3)} m'

            st.markdown(f'<h1 style="color:red;font-size:27px;">{string}</h1>', unsafe_allow_html=True)


            #Nedlastbar excelfil med resultat
            output = BytesIO()

            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            worksheet = workbook.add_worksheet()

            dict_1 = {'Parametre': ['Forankringskraft [kN]', 'Diameter bolt [m]', 'Diameter borehull [m]', 'Partialfaktor mørtel', 'Partialfaktor berg', 'Bergmassens bruddvinkel [grader]', 'Karakteristisk heftfasthet bruddplan [kPa]', 'Karakteristisk heftasthet mellom bolt og mørtel [MPa]','Karakteristisk heftasthet mellom mørtel og berg [MPa]'],
                    'Verdier': [kraft, d_bolt, d_borehull, pf_m, pf_b, bv, bp, h_bm, h_mb]}

            col_num = 0
            for key, value in dict_1.items():
                worksheet.write(0, col_num, key)
                worksheet.write_column(1, col_num, value)
                col_num += 1

            worksheet.write(12,0,'Resultat')
            worksheet.write(13,0,'Dimensjonerende heftfasthet stål-mørtel [kPa]')
            worksheet.write(13,1,td)
            worksheet.write(14,0,'Dimensjonerende forankringslengde stål-mørtel [m]')
            worksheet.write(14,1,l_tb)

            worksheet.write(16,0,'Dimensjonerende heftfasthet mørtel-berg [kPa]')
            worksheet.write(16,1,td2)
            worksheet.write(17,0,'Dimensjonerende forankringslengde mørtel-berg [m]')
            worksheet.write(17,1,l_tb2)

            worksheet.write(19,0,'Dimensjonerende forankringslengde brudd i berg [m]')
            worksheet.write(19,1,lam)

            worksheet.write(21,0,'Dimensjonerende forankringslengde [m]')
            worksheet.write(21,1,forank)

            workbook.close()

            st.download_button(
                label="Last ned resultatet som Excel-fil",
                data=output.getvalue(),
                file_name="forankringslengde_i_berg.xlsx",
                mime="application/vnd.ms-excel"
            )
    except :
        st.markdown(f'<h1 style="color:red;font-size:27px;">Feil: Ingen parametre kan være satt lik 0.</h1>', unsafe_allow_html=True)
