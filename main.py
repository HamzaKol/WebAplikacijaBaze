import configparser
from flask import Flask, request, render_template
import mysql.connector

config = configparser.ConfigParser()
config.read("config.ini")
dbconfig = config["database"]

app = Flask(__name__)

cnxpool = mysql.connector.pooling.MySQLConnectionPool(
    host = dbconfig["host"],
    user = dbconfig["user"],
    password = dbconfig["password"],
    database = dbconfig["database"],
    port = int(dbconfig["port"]),
    pool_name = "pool",
    pool_size = int(dbconfig["pool_size"])
)

@app.route("/")
def get_pocetna():
    return render_template("index.html")
@app.route("/radni_nalozi.html")
def get_radni_nalozi_html():
    lista_radnih_naloga = []
    with cnxpool.get_connection() as cnx:
        with cnx.cursor() as rn_cur:
            rn_cur.execute(
                "select " +
                "   rn.broj_radnog_naloga, " +
                "   rn.datum_radnog_naloga, " +
                "   k.ime_kupca, " +
                "   k.prezime_kupca, " +
                "   mv.naziv_vozila, " +
                "   mv.marka_vozila, " +
                "   mv.tip_vozila, " +
                "   rn.zapazanja " +
                "from Radni_Nalog as rn inner join " +
                "Vozilo as v on v.sifra_vozila = rn.sifra_vozila " +
                "inner join Model_Vozila as mv on v.sifra_modela_vozila = mv.sifra_modela_vozila "+
                "inner join Kupac as k on k.sifra_kupca = rn.sifra_kupca")

            lista_radnih_naloga = rn_cur.fetchall()

    return render_template("RadniNalozi.html", lista=lista_radnih_naloga)

@app.route('/UnesiPeriod.html')
def set_operacije():
    return render_template("UnesiPeriod.html")


@app.route('/IzvrseneOperacijeUPeriodu.html')
def get_operacije():
    lista = []
    popust = float(request.args.get('popust'))
    pocetni_datum = str(request.args.get('pocetni_datum'))
    krajnji_datum = str(request.args.get('krajnji_datum'))
    with cnxpool.get_connection() as cnx:
        with cnx.cursor() as rn_cur:
            rn_cur.callproc('Izvrsene_Operacije_U_Periodu',[pocetni_datum, krajnji_datum, popust])

            for t in rn_cur.stored_results():
                lista = t.fetchall()
    return render_template("IzvrseneOperacijeUPeriodu.html", lista=lista)

@app.route('/Vozilo.html')
def set_vozilo():
    lista = []
    with cnxpool.get_connection() as cnx:
        with cnx.cursor() as v_cur:
            v_cur.execute(
                "select " +
                "   naziv_vozila " +
                "from Model_Vozila "+
                "group by naziv_vozila")

            lista = v_cur.fetchall()
    return render_template("Vozilo.html", lista = lista)

@app.route('/IspisiVozilo.html/Prikazi', methods = ['POST', 'GET'])
def prikazi_vozilo():
    sifra_vozila = str(request.args.get('sifra_vozila'))
    posljednji_registarski_broj_vozila = str(request.args.get('posljednji_registarski_broj_vozila'))
    sifra_modela_vozila = str(request.args.get('sifra_modela_vozila'))
    naziv_vozila = str(request.args.get('naziv_vozila'))
    pomocni = ""
    duzina = 0
    if(len(sifra_vozila)):
        pomocni += "sifra_vozila = " + sifra_vozila + " and "
        duzina = 1
    if (len(posljednji_registarski_broj_vozila)):
        pomocni += "posljednji_registarski_broj_vozila = " + '"' + posljednji_registarski_broj_vozila + '"' + " and "
        duzina = 1
    if (len(sifra_modela_vozila)):
        pomocni += "mv.sifra_modela_vozila = " + '"' + sifra_modela_vozila + '"' + " and "
        duzina = 1
    if (len(naziv_vozila)):
        pomocni += "naziv_vozila = " + '"' + naziv_vozila + '"' + " and "
        duzina = 1
    lista = []

    with cnxpool.get_connection() as cnx:
        with cnx.cursor() as v_cur:
            if (duzina == 0):
                v_cur.execute(
                    "select " +
                    "sifra_vozila, " +
                    "posljednji_registarski_broj_vozila, " +
                    "naziv_vozila, " +
                    "marka_vozila, " +
                    "tip_vozila "
                    "from Vozilo as v inner join Model_Vozila as mv " +
                    "on v.sifra_modela_vozila = mv.sifra_modela_vozila " +
                    "order by sifra_vozila")
            else:
                pomocni = pomocni[:-4]
                v_cur.execute(
                    "select " +
                    "sifra_vozila, " +
                    "posljednji_registarski_broj_vozila, " +
                    "naziv_vozila, " +
                    "marka_vozila, " +
                    "tip_vozila "
                    "from Vozilo as v inner join Model_Vozila as mv " +
                    "on v.sifra_modela_vozila = mv.sifra_modela_vozila " +
                    "where " + pomocni +
                    " order by sifra_vozila")


            lista = v_cur.fetchall()


    return render_template("IspisiVozilo.html", lista = lista)

@app.route('/IspisiVozilo.html/Dodaj', methods = ['POST', 'GET'])
def dodaj_vozilo():
    sifra_vozila = str(request.form['sifra_vozila'])
    posljednji_registarski_broj_vozila = str(request.form['posljednji_registarski_broj_vozila'])
    sifra_modela_vozila = str(request.form['sifra_modela_vozila'])
    naziv_vozila = str(request.form['naziv_vozila'])
    pomocni1 = ""
    pomocni2 = ""
    duzina = 0
    if (len(posljednji_registarski_broj_vozila) and posljednji_registarski_broj_vozila != None and posljednji_registarski_broj_vozila != "None"):
        pomocni1 += "posljednji_registarski_broj_vozila, "
        pomocni2 += '"' + posljednji_registarski_broj_vozila + '"' + ", "
        duzina = 1

    if (len(naziv_vozila) and naziv_vozila != None and naziv_vozila != "None"):
        with cnxpool.get_connection() as cnx:
            with cnx.cursor() as v_cur:
                v_cur.execute("select * from Model_Vozila where naziv_vozila =" +
                              '"' + naziv_vozila + '"' + "limit 1")
                sifra_modela_vozila = str(v_cur.fetchone()[0])
                duzina = 1
    if (len(sifra_modela_vozila) and sifra_modela_vozila != None and sifra_modela_vozila != "None"):
        pomocni1 += "sifra_modela_vozila, "
        pomocni2 += '"' + sifra_modela_vozila + '"' + ", "
        duzina = 1


    lista = []
    with cnxpool.get_connection() as cnx:
        with cnx.cursor() as v_cur:
            if (duzina == 0):
                v_cur.execute(
                    "select " +
                    "sifra_vozila, " +
                    "posljednji_registarski_broj_vozila, " +
                    "naziv_vozila, " +
                    "marka_vozila, " +
                    "tip_vozila "
                    "from Vozilo as v inner join Model_Vozila as mv " +
                    "on v.sifra_modela_vozila = mv.sifra_modela_vozila " +
                    "order by sifra_vozila")
            else:
                pomocni1 = pomocni1[:-2]
                pomocni2 = pomocni2[:-2]
                v_cur.execute(
                    "insert into Vozilo(" +
                    pomocni1 + ") values(" +
                    pomocni2 + ")")
                cnx.commit()
                v_cur.execute("select " +
                    "sifra_vozila, " +
                    "posljednji_registarski_broj_vozila, " +
                    "naziv_vozila, " +
                    "marka_vozila, " +
                    "tip_vozila "
                    "from Vozilo as v inner join Model_Vozila as mv " +
                    "on v.sifra_modela_vozila = mv.sifra_modela_vozila " +
                    "order by 1")

            lista = v_cur.fetchall()

    return render_template("IspisiVozilo.html", lista = lista)

@app.route('/IspisiVozilo.html/Obrisi', methods = ['POST', 'GET'])
def brisi_vozilo():
    sifra_vozila = str(request.args.get('sifra_vozila'))
    duzina = 0
    if (len(sifra_vozila)):
        duzina = 1
    lista = []

    with cnxpool.get_connection() as cnx:
        with cnx.cursor() as v_cur:
            if (duzina == 0):
                v_cur.execute(
                    "select " +
                    "sifra_vozila, " +
                    "posljednji_registarski_broj_vozila, " +
                    "naziv_vozila, " +
                    "marka_vozila, " +
                    "tip_vozila "
                    "from Vozilo as v inner join Model_Vozila as mv " +
                    "on v.sifra_modela_vozila = mv.sifra_modela_vozila " +
                    "order by sifra_vozila")
            else:
                v_cur.execute(
                    "delete from Vozilo " +
                    "where sifra_vozila = " +
                    '"' + sifra_vozila + '"')
                cnx.commit()
                v_cur.execute(
                    "select " +
                    "sifra_vozila, " +
                    "posljednji_registarski_broj_vozila, " +
                    "naziv_vozila, " +
                    "marka_vozila, " +
                    "tip_vozila "
                    "from Vozilo as v inner join Model_Vozila as mv " +
                    "on v.sifra_modela_vozila = mv.sifra_modela_vozila " +
                    "order by sifra_vozila")

            lista = v_cur.fetchall()

    return render_template("IspisiVozilo.html", lista = lista)

@app.route("/Radovi.html")
def set_radovi():
    with cnxpool.get_connection() as cnx:
        with cnx.cursor() as v_cur:
            v_cur.execute("select broj_radnog_naloga from Radni_Nalog order by 1")
            lista = v_cur.fetchall()

    return render_template("Radovi.html", lista = lista)

@app.route('/IzvjestajRadovi.html')
def get_radovi():
    lista = []
    broj_radnog_naloga = str(request.args.get('broj_radnog_naloga'))
    with cnxpool.get_connection() as cnx:
        with cnx.cursor() as r_cur:
            r_cur.execute("select * from Radovi where broj_radnog_naloga = " +
                          '"' + broj_radnog_naloga + '"')
            lista_radovi = r_cur.fetchall()

            r_cur.execute("select * from Oprema where broj_radnog_naloga = " +
                          '"' + broj_radnog_naloga + '"')
            lista_oprema = r_cur.fetchall()
            r_cur.execute("select * from Radni_Nalog where broj_radnog_naloga = " +
                          '"' + broj_radnog_naloga + '"')
            lista_radni_nalog = r_cur.fetchall()
    print("select * from Radni_Nalog where broj_radnog_naloga = " +
                          '"' + broj_radnog_naloga + '"')
    print(lista_radni_nalog)
    lista = []
    lista.append(lista_radni_nalog[0][0])
    lista.append(str(lista_radni_nalog[0][1]))
    lista.append(str(lista_radni_nalog[0][4]))
    oprema_str = ""
    for opreme in lista_oprema:
        print(opreme)
        for i in range(11):
            if(i == 1 and opreme[i] == 1):
                oprema_str += "Rezervna Guma, "
            if (i == 2 and opreme[i] == 1):
                oprema_str += "Aparat Protiv Pozara, "
            if (i == 3 and opreme[i] == 1):
                oprema_str += "Sigurnosni Trougao, "
            if (i == 4 and opreme[i] == 1):
                oprema_str += "Prva Pomoć, "
            if (i == 5 and opreme[i] == 1):
                oprema_str += "Rezervne Sijalice i Osigurači, "
            if (i == 6 and opreme[i] == 1):
                oprema_str += "Fluorescentni Prsluk, "
            if (i == 7 and opreme[i] == 1):
                oprema_str += "Uže, "
            if (i == 8 and opreme[i] == 1):
                oprema_str += "Sajla, "
            if (i == 9 and opreme[i] == 1):
                oprema_str += "Kruta Veza, "
            if (i == 10 and opreme[i] == 1):
                oprema_str += "Lanci za Snijeg, "

    radovi_str = ""
    for rad in lista_radovi:
        for i in range(8):
            if(i == 1):
                radovi_str += "Šifra operacije: " + str(rad[i])
            if (i == 2):
                radovi_str += ", broj odrađenih operacija: " + str(rad[i])
            if (i == 3):
                radovi_str += ", šifra zaposlenika: " + str(rad[i])
            if (i == 4):
                radovi_str += ", broj sati: " + str(rad[i])
            if (i == 5):
                radovi_str += ", cijena po operaciji: " + str(rad[i])
            if (i == 6):
                radovi_str += ", iznos za sve operacije: " + str(rad[i])
            if (i == 7):
                radovi_str += ", redni broj operacije: " + str(rad[i])


    oprema_str = oprema_str[:-2]
    lista.append(oprema_str)
    lista.append(radovi_str)
    print(lista)

    return render_template("IzvjestajRadovi.html", lista=lista)


if __name__ == '__main__':
    app.run()