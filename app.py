from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'hastane2024'
DB = 'hastane.db'


def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    con = db()
    con.executescript('''
        CREATE TABLE IF NOT EXISTS hastalar (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            ad       TEXT NOT NULL,
            soyad    TEXT NOT NULL,
            yas      INTEGER,
            telefon  TEXT,
            tcno     TEXT
        );
        CREATE TABLE IF NOT EXISTS doktorlar (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            ad        TEXT NOT NULL,
            soyad     TEXT NOT NULL,
            uzmanlik  TEXT,
            telefon   TEXT
        );
        CREATE TABLE IF NOT EXISTS randevular (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            hasta_id   INTEGER,
            doktor_id  INTEGER,
            tarih      TEXT,
            saat       TEXT,
            durum      TEXT DEFAULT "Aktif",
            FOREIGN KEY (hasta_id)  REFERENCES hastalar(id),
            FOREIGN KEY (doktor_id) REFERENCES doktorlar(id)
        );
    ''')
    con.close()


# =================== ANA SAYFA ===================

@app.route('/')
def index():
    con = db()
    hasta_n   = con.execute('SELECT COUNT(*) FROM hastalar').fetchone()[0]
    doktor_n  = con.execute('SELECT COUNT(*) FROM doktorlar').fetchone()[0]
    randevu_n = con.execute("SELECT COUNT(*) FROM randevular WHERE durum='Aktif'").fetchone()[0]
    son_randevular = con.execute('''
        SELECT r.*, h.ad||" "||h.soyad AS hasta_adi,
               d.ad||" "||d.soyad AS doktor_adi
        FROM randevular r
        JOIN hastalar h  ON r.hasta_id  = h.id
        JOIN doktorlar d ON r.doktor_id = d.id
        ORDER BY r.tarih DESC, r.saat DESC LIMIT 5
    ''').fetchall()
    con.close()
    return render_template('index.html',
                           hasta_n=hasta_n,
                           doktor_n=doktor_n,
                           randevu_n=randevu_n,
                           son_randevular=son_randevular)


# =================== HASTALAR ===================

@app.route('/hastalar')
def hastalar():
    q = request.args.get('q', '').strip()
    con = db()
    if q:
        rows = con.execute(
            "SELECT * FROM hastalar WHERE ad LIKE ? OR soyad LIKE ? OR tcno LIKE ? ORDER BY id",
            (f'%{q}%', f'%{q}%', f'%{q}%')
        ).fetchall()
    else:
        rows = con.execute('SELECT * FROM hastalar ORDER BY id').fetchall()
    con.close()
    return render_template('hastalar.html', hastalar=rows, q=q)


@app.route('/hasta/ekle', methods=['POST'])
def hasta_ekle():
    con = db()
    con.execute(
        'INSERT INTO hastalar (ad, soyad, yas, telefon, tcno) VALUES (?,?,?,?,?)',
        (request.form['ad'], request.form['soyad'], request.form.get('yas') or None,
         request.form['telefon'], request.form['tcno'])
    )
    con.commit()
    con.close()
    flash('Hasta başarıyla kaydedildi!', 'success')
    return redirect(url_for('hastalar'))


@app.route('/hasta/sil/<int:hid>')
def hasta_sil(hid):
    con = db()
    con.execute('DELETE FROM hastalar WHERE id=?', (hid,))
    con.commit()
    con.close()
    flash('Hasta silindi.', 'warning')
    return redirect(url_for('hastalar'))


# =================== DOKTORLAR ===================

@app.route('/doktorlar')
def doktorlar():
    con = db()
    rows = con.execute('SELECT * FROM doktorlar ORDER BY id').fetchall()
    con.close()
    return render_template('doktorlar.html', doktorlar=rows)


@app.route('/doktor/ekle', methods=['POST'])
def doktor_ekle():
    con = db()
    con.execute(
        'INSERT INTO doktorlar (ad, soyad, uzmanlik, telefon) VALUES (?,?,?,?)',
        (request.form['ad'], request.form['soyad'],
         request.form['uzmanlik'], request.form['telefon'])
    )
    con.commit()
    con.close()
    flash('Doktor başarıyla kaydedildi!', 'success')
    return redirect(url_for('doktorlar'))


@app.route('/doktor/sil/<int:did>')
def doktor_sil(did):
    con = db()
    con.execute('DELETE FROM doktorlar WHERE id=?', (did,))
    con.commit()
    con.close()
    flash('Doktor silindi.', 'warning')
    return redirect(url_for('doktorlar'))


# =================== RANDEVULAR ===================

@app.route('/randevular')
def randevular():
    hasta_id  = request.args.get('hasta_id', '')
    durum_f   = request.args.get('durum', '')
    con = db()
    hastalar_list  = con.execute('SELECT * FROM hastalar ORDER BY ad').fetchall()
    doktorlar_list = con.execute('SELECT * FROM doktorlar ORDER BY ad').fetchall()

    query  = '''
        SELECT r.*,
               h.ad||" "||h.soyad AS hasta_adi,
               d.ad||" "||d.soyad AS doktor_adi,
               d.uzmanlik
        FROM randevular r
        JOIN hastalar h  ON r.hasta_id  = h.id
        JOIN doktorlar d ON r.doktor_id = d.id
        WHERE 1=1
    '''
    params = []
    if hasta_id:
        query += ' AND r.hasta_id = ?'
        params.append(hasta_id)
    if durum_f:
        query += ' AND r.durum = ?'
        params.append(durum_f)
    query += ' ORDER BY r.tarih DESC, r.saat DESC'

    rows = con.execute(query, params).fetchall()
    con.close()
    return render_template('randevular.html',
                           randevular=rows,
                           hastalar=hastalar_list,
                           doktorlar=doktorlar_list,
                           hasta_id=hasta_id,
                           durum_f=durum_f)


@app.route('/randevu/al', methods=['POST'])
def randevu_al():
    con = db()
    con.execute(
        'INSERT INTO randevular (hasta_id, doktor_id, tarih, saat, durum) VALUES (?,?,?,?,?)',
        (request.form['hasta_id'], request.form['doktor_id'],
         request.form['tarih'], request.form['saat'], 'Aktif')
    )
    con.commit()
    con.close()
    flash('Randevu başarıyla alındı!', 'success')
    return redirect(url_for('randevular'))


@app.route('/randevu/iptal/<int:rid>')
def randevu_iptal(rid):
    con = db()
    con.execute("UPDATE randevular SET durum='İptal' WHERE id=?", (rid,))
    con.commit()
    con.close()
    flash('Randevu iptal edildi.', 'warning')
    return redirect(url_for('randevular'))


@app.route('/randevu/sil/<int:rid>')
def randevu_sil(rid):
    con = db()
    con.execute('DELETE FROM randevular WHERE id=?', (rid,))
    con.commit()
    con.close()
    flash('Randevu silindi.', 'danger')
    return redirect(url_for('randevular'))


if __name__ == '__main__':
    init_db()
    print('\n  ✓ Hastane Randevu Sistemi çalışıyor')
    print('  → http://localhost:5000\n')
    app.run(debug=True, port=5000)
