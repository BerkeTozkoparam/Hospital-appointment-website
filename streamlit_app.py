import os
import random
import sqlite3
from datetime import date

import streamlit as st

# ─────────────────────────────────────────────
# SAYFA AYARLARI
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Hastane Randevu Sistemi",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# VERİTABANI
# ─────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hastane.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    con = get_db()
    con.executescript("""
        CREATE TABLE IF NOT EXISTS hastalar (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            ad      TEXT NOT NULL,
            soyad   TEXT NOT NULL,
            yas     INTEGER,
            telefon TEXT,
            tcno    TEXT
        );
        CREATE TABLE IF NOT EXISTS doktorlar (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            ad       TEXT NOT NULL,
            soyad    TEXT NOT NULL,
            uzmanlik TEXT,
            telefon  TEXT
        );
        CREATE TABLE IF NOT EXISTS randevular (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            hasta_id  INTEGER,
            doktor_id INTEGER,
            tarih     TEXT,
            saat      TEXT,
            durum     TEXT DEFAULT 'Aktif',
            FOREIGN KEY (hasta_id)  REFERENCES hastalar(id),
            FOREIGN KEY (doktor_id) REFERENCES doktorlar(id)
        );
    """)
    con.commit()
    con.close()


init_db()

# ─────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────
st.html("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
/* ── Temel ── */
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.block-container { padding-top: 1.5rem !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0c1f5e 0%, #1a3a8f 100%) !important;
    border-right: none;
}
[data-testid="stSidebar"] * { color: #c7d2fe !important; }
[data-testid="stSidebar"] .stRadio label { font-size: .95rem; }
[data-testid="stSidebar"] hr { border-color: #2d4fb0 !important; }
[data-testid="stSidebar"] .stRadio [data-baseweb="radio"] {
    margin-bottom: .3rem;
}

/* ── Sayfa başlığı şeridi ── */
.page-header {
    background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
    color: white;
    border-radius: 14px;
    padding: 1.4rem 2rem;
    margin-bottom: 1.6rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}
.page-header h2 { margin: 0; font-size: 1.5rem; font-weight: 700; }
.page-header p  { margin: .2rem 0 0; opacity: .8; font-size: .9rem; }

/* ── İstatistik kartları ── */
.stat-card {
    background: white;
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    box-shadow: 0 4px 16px rgba(0,0,0,.08);
    border: 1px solid #e5e7eb;
    border-left: 5px solid var(--accent);
    height: 100%;
}
.stat-top    { display:flex; align-items:center; gap:.8rem; }
.stat-emoji  { font-size: 2rem; line-height:1; }
.stat-num    { font-size: 2.4rem; font-weight: 800; color: var(--accent); line-height:1.1; }
.stat-lbl    { color: #6b7280; font-size: .82rem; font-weight: 500; margin-top:.15rem; letter-spacing:.3px; }
.stat-bar    { height: 4px; border-radius: 4px; background: var(--accent); opacity:.15; margin-top: 1rem; }

/* ── Tablo başlığı ── */
.tbl-header {
    background: #f8fafc;
    border-radius: 10px 10px 0 0;
    padding: .6rem 1rem;
    border: 1px solid #e5e7eb;
    border-bottom: 2px solid #e5e7eb;
    display: flex;
    font-size: .8rem;
    font-weight: 600;
    color: #6b7280;
    letter-spacing: .5px;
    text-transform: uppercase;
}

/* ── Satır kartı ── */
.row-item {
    background: white;
    border: 1px solid #e5e7eb;
    border-top: none;
    padding: .75rem 1rem;
    transition: background .15s;
}
.row-item:hover { background: #f0f7ff; }
.row-item:last-child { border-radius: 0 0 10px 10px; }

/* ── Doktor / Hasta kartı ── */
.doc-card {
    background: white;
    border-radius: 14px;
    padding: 1.4rem;
    box-shadow: 0 2px 12px rgba(0,0,0,.07);
    border: 1px solid #e5e7eb;
    transition: transform .2s, box-shadow .2s;
    height: 100%;
}
.doc-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,.11); }
.doc-avatar {
    width: 52px; height: 52px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.4rem; font-weight: 700; color: white;
    margin-bottom: .8rem;
}
.doc-name   { font-size: 1rem; font-weight: 700; color: #1e293b; margin-bottom: .2rem; }
.doc-spec   {
    display: inline-block;
    background: #eff6ff; color: #2563eb;
    padding: 2px 10px; border-radius: 20px;
    font-size: .75rem; font-weight: 600;
    margin-bottom: .7rem;
}
.doc-info   { font-size: .82rem; color: #6b7280; }
.doc-info span { display: block; margin-top: .2rem; }

/* ── Hasta avatar ── */
.hasta-avatar {
    width: 38px; height: 38px; border-radius: 50%;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: .9rem; font-weight: 700; color: white;
    flex-shrink: 0;
}

/* ── Badge'ler ── */
.badge-aktif {
    background: #dcfce7; color: #16a34a;
    padding: 3px 12px; border-radius: 20px; font-size: .78rem; font-weight: 700;
}
.badge-iptal {
    background: #fee2e2; color: #dc2626;
    padding: 3px 12px; border-radius: 20px; font-size: .78rem; font-weight: 700;
}

/* ── Form ── */
[data-testid="stForm"] {
    background: #f8fafc;
    border-radius: 12px;
    padding: 1.2rem 1.4rem !important;
    border: 1px solid #e2e8f0;
}

/* ── Butonlar ── */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all .15s !important;
}
.stButton > button:hover { transform: translateY(-1px); }

/* ── Expander ── */
[data-testid="stExpander"] {
    border-radius: 12px !important;
    border: 1px solid #e2e8f0 !important;
    overflow: hidden;
}

/* ── Chat balonları ── */
.chat-user {
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    color: white; border-radius: 18px 18px 4px 18px;
    padding: .8rem 1.2rem; margin: .4rem 0; display:inline-block;
    max-width: 80%; font-size: .93rem;
}
.chat-bot {
    background: white; color: #1e293b;
    border-radius: 18px 18px 18px 4px;
    padding: .8rem 1.2rem; margin: .4rem 0; display:inline-block;
    max-width: 85%; font-size: .93rem;
    box-shadow: 0 2px 10px rgba(0,0,0,.07);
    border: 1px solid #e5e7eb;
}

/* ── Hızlı soru butonları ── */
.quick-btn button {
    background: #eff6ff !important;
    color: #1d4ed8 !important;
    border: 1px solid #bfdbfe !important;
    border-radius: 20px !important;
    font-size: .82rem !important;
    padding: .3rem .9rem !important;
    font-weight: 600 !important;
}
.quick-btn button:hover {
    background: #dbeafe !important;
    transform: translateY(-1px);
}

/* ── Divider ince ── */
hr { margin: .6rem 0 !important; }

/* ── st.info / success / warning güzelleştir ── */
[data-testid="stAlert"] { border-radius: 10px !important; }
</style>
""")


# ─────────────────────────────────────────────
# RENK PALETİ
# ─────────────────────────────────────────────
AVATAR_COLORS = [
    "#6366f1", "#0ea5e9", "#10b981", "#f59e0b",
    "#ef4444", "#8b5cf6", "#14b8a6", "#f97316",
]


def avatar_color(name: str) -> str:
    return AVATAR_COLORS[sum(ord(c) for c in name) % len(AVATAR_COLORS)]


def initials(ad: str, soyad: str) -> str:
    return (ad[:1] + soyad[:1]).upper()


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:.5rem 0 1rem;">
        <div style="font-size:3rem;">🏥</div>
        <div style="font-size:1.1rem; font-weight:700; color:#e0e7ff;">Hastane Sistemi</div>
        <div style="font-size:.75rem; color:#93a3c8; margin-top:.2rem;">Randevu Yönetimi</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    page = st.radio(
        "Menü",
        ["🏠 Ana Sayfa", "👥 Hastalar", "👨‍⚕️ Doktorlar", "📅 Randevular", "🤖 Yapay Zeka Asistan"],
        label_visibility="collapsed",
    )

    st.markdown("---")

    # Özet istatistik
    con = get_db()
    _h = con.execute("SELECT COUNT(*) FROM hastalar").fetchone()[0]
    _d = con.execute("SELECT COUNT(*) FROM doktorlar").fetchone()[0]
    _r = con.execute("SELECT COUNT(*) FROM randevular WHERE durum='Aktif'").fetchone()[0]
    con.close()
    st.markdown(f"""
    <div style="font-size:.78rem; color:#93a3c8; text-align:center; line-height:2;">
        👥 {_h} Hasta &nbsp;|&nbsp; 👨‍⚕️ {_d} Doktor<br>
        📅 {_r} Aktif Randevu
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("v2.0 · Streamlit · Kendi Chatbot")


# ══════════════════════════════════════════════════════════════
# SAYFA: ANA SAYFA
# ══════════════════════════════════════════════════════════════
if page == "🏠 Ana Sayfa":
    st.markdown("""
    <div class="page-header">
        <div>
            <h2>🏥 Hastane Randevu Sistemi</h2>
            <p>Hasta, doktor ve randevu yönetimini buradan kolayca yapabilirsiniz.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    con = get_db()
    hasta_n   = con.execute("SELECT COUNT(*) FROM hastalar").fetchone()[0]
    doktor_n  = con.execute("SELECT COUNT(*) FROM doktorlar").fetchone()[0]
    aktif_n   = con.execute("SELECT COUNT(*) FROM randevular WHERE durum='Aktif'").fetchone()[0]
    iptal_n   = con.execute("SELECT COUNT(*) FROM randevular WHERE durum='İptal'").fetchone()[0]
    son_randevular = con.execute("""
        SELECT r.tarih, r.saat, r.durum,
               h.ad||' '||h.soyad AS hasta_adi,
               d.ad||' '||d.soyad AS doktor_adi,
               d.uzmanlik
        FROM randevular r
        JOIN hastalar h  ON r.hasta_id  = h.id
        JOIN doktorlar d ON r.doktor_id = d.id
        ORDER BY r.tarih DESC, r.saat DESC LIMIT 6
    """).fetchall()
    con.close()

    # ── 4 istatistik kartı ──
    c1, c2, c3, c4 = st.columns(4)
    cards = [
        (c1, "👥",  hasta_n,  "Kayıtlı Hasta",   "#2563eb"),
        (c2, "👨‍⚕️",  doktor_n, "Kayıtlı Doktor",  "#10b981"),
        (c3, "✅",  aktif_n,  "Aktif Randevu",    "#f59e0b"),
        (c4, "❌",  iptal_n,  "İptal Randevu",    "#ef4444"),
    ]
    for col, icon, num, lbl, color in cards:
        col.markdown(f"""
        <div class="stat-card" style="--accent:{color};">
            <div class="stat-top">
                <div class="stat-emoji">{icon}</div>
                <div>
                    <div class="stat-num">{num}</div>
                    <div class="stat-lbl">{lbl}</div>
                </div>
            </div>
            <div class="stat-bar"></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Hızlı erişim ──
    st.markdown("##### Hızlı Erişim")
    b1, b2, b3 = st.columns(3)
    if b1.button("➕ Yeni Hasta Ekle", use_container_width=True):
        st.session_state["_goto"] = "👥 Hastalar"
    if b2.button("➕ Yeni Doktor Ekle", use_container_width=True):
        st.session_state["_goto"] = "👨‍⚕️ Doktorlar"
    if b3.button("📅 Randevu Al", use_container_width=True):
        st.session_state["_goto"] = "📅 Randevular"
    if "_goto" in st.session_state:
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Son randevular tablosu ──
    st.markdown("##### Son Randevular")
    if son_randevular:
        st.markdown("""
        <div class="tbl-header">
            <span style="flex:2.5">Hasta</span>
            <span style="flex:2.5">Doktor</span>
            <span style="flex:1.5">Uzmanlık</span>
            <span style="flex:1.2">Tarih</span>
            <span style="flex:.8">Saat</span>
            <span style="flex:1">Durum</span>
        </div>
        """, unsafe_allow_html=True)
        for r in son_randevular:
            badge = "badge-aktif" if r["durum"] == "Aktif" else "badge-iptal"
            ic    = avatar_color(r["hasta_adi"])
            ini   = r["hasta_adi"][:2].upper()
            st.markdown(f"""
            <div class="row-item" style="display:flex; align-items:center; gap:.5rem;">
                <span style="flex:2.5; display:flex; align-items:center; gap:.6rem;">
                    <span style="width:30px;height:30px;border-radius:50%;background:{ic};
                        display:inline-flex;align-items:center;justify-content:center;
                        font-size:.7rem;font-weight:700;color:white;flex-shrink:0;">{ini}</span>
                    {r["hasta_adi"]}
                </span>
                <span style="flex:2.5">Dr. {r["doktor_adi"]}</span>
                <span style="flex:1.5; color:#6b7280; font-size:.85rem;">{r["uzmanlik"] or "—"}</span>
                <span style="flex:1.2">{r["tarih"]}</span>
                <span style="flex:.8">{r["saat"]}</span>
                <span style="flex:1"><span class="{badge}">{r["durum"]}</span></span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Henüz randevu kaydı bulunmuyor.")


# ══════════════════════════════════════════════════════════════
# SAYFA: HASTALAR
# ══════════════════════════════════════════════════════════════
elif page == "👥 Hastalar":
    # Yönlendirme temizle
    st.session_state.pop("_goto", None)

    st.markdown("""
    <div class="page-header">
        <div><h2>👥 Hasta Yönetimi</h2><p>Hasta kayıtlarını görüntüleyin, ekleyin veya silin.</p></div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("➕ Yeni Hasta Ekle", expanded=False):
        with st.form("hasta_ekle_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            ad      = c1.text_input("Ad *")
            soyad   = c2.text_input("Soyad *")
            yas     = c1.number_input("Yaş", min_value=0, max_value=150, value=0)
            telefon = c2.text_input("Telefon")
            tcno    = c1.text_input("TC No")
            if st.form_submit_button("💾 Kaydet", type="primary"):
                if ad.strip() and soyad.strip():
                    con = get_db()
                    con.execute(
                        "INSERT INTO hastalar (ad, soyad, yas, telefon, tcno) VALUES (?,?,?,?,?)",
                        (ad.strip(), soyad.strip(), yas or None, telefon, tcno),
                    )
                    con.commit(); con.close()
                    st.success("✅ Hasta kaydedildi!")
                    st.rerun()
                else:
                    st.error("Ad ve soyad zorunludur.")

    q = st.text_input("🔍 Hasta Ara", placeholder="Ad, soyad veya TC no ile arayın…")
    con = get_db()
    rows = con.execute(
        "SELECT * FROM hastalar WHERE ad LIKE ? OR soyad LIKE ? OR tcno LIKE ? ORDER BY ad",
        (f"%{q}%",) * 3,
    ).fetchall() if q.strip() else con.execute("SELECT * FROM hastalar ORDER BY ad").fetchall()
    con.close()

    st.markdown(f"<p style='color:#6b7280; font-size:.85rem;'>{len(rows)} kayıt</p>",
                unsafe_allow_html=True)

    if rows:
        st.markdown("""
        <div class="tbl-header">
            <span style="flex:.4">&nbsp;</span>
            <span style="flex:3">Ad Soyad</span>
            <span style="flex:2">TC No</span>
            <span style="flex:1">Yaş</span>
            <span style="flex:2">Telefon</span>
            <span style="flex:.5"></span>
        </div>
        """, unsafe_allow_html=True)
        for r in rows:
            ic  = avatar_color(r["ad"] + r["soyad"])
            ini = initials(r["ad"], r["soyad"])
            cols = st.columns([0.4, 3, 2, 1, 2, 0.5])
            cols[0].markdown(f"""
            <div class="hasta-avatar" style="background:{ic};">{ini}</div>
            """, unsafe_allow_html=True)
            cols[1].markdown(f"**{r['ad']} {r['soyad']}**")
            cols[2].write(r["tcno"] or "—")
            cols[3].write(str(r["yas"]) if r["yas"] else "—")
            cols[4].write(r["telefon"] or "—")
            if cols[5].button("🗑️", key=f"dh{r['id']}", help="Sil"):
                con = get_db()
                con.execute("DELETE FROM hastalar WHERE id=?", (r["id"],))
                con.commit(); con.close()
                st.rerun()
            st.markdown('<div style="height:1px;background:#f1f5f9;margin:0;"></div>',
                        unsafe_allow_html=True)
    else:
        st.info("Kayıt bulunamadı.")


# ══════════════════════════════════════════════════════════════
# SAYFA: DOKTORLAR
# ══════════════════════════════════════════════════════════════
elif page == "👨‍⚕️ Doktorlar":
    st.session_state.pop("_goto", None)

    st.markdown("""
    <div class="page-header" style="background:linear-gradient(135deg,#065f46,#10b981);">
        <div><h2>👨‍⚕️ Doktor Yönetimi</h2><p>Doktor profillerini görüntüleyin ve yönetin.</p></div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("➕ Yeni Doktor Ekle", expanded=False):
        with st.form("doktor_ekle_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            ad       = c1.text_input("Ad *")
            soyad    = c2.text_input("Soyad *")
            uzmanlik = c1.text_input("Uzmanlık Alanı")
            telefon  = c2.text_input("Telefon")
            if st.form_submit_button("💾 Kaydet", type="primary"):
                if ad.strip() and soyad.strip():
                    con = get_db()
                    con.execute(
                        "INSERT INTO doktorlar (ad, soyad, uzmanlik, telefon) VALUES (?,?,?,?)",
                        (ad.strip(), soyad.strip(), uzmanlik, telefon),
                    )
                    con.commit(); con.close()
                    st.success("✅ Doktor kaydedildi!")
                    st.rerun()
                else:
                    st.error("Ad ve soyad zorunludur.")

    con = get_db()
    rows = con.execute("SELECT * FROM doktorlar ORDER BY ad").fetchall()
    con.close()

    st.markdown(f"<p style='color:#6b7280; font-size:.85rem;'>{len(rows)} doktor kayıtlı</p>",
                unsafe_allow_html=True)

    if rows:
        # Kart grid — 3 sütun
        for i in range(0, len(rows), 3):
            cols = st.columns(3)
            for j, r in enumerate(rows[i:i+3]):
                ic  = avatar_color(r["ad"] + r["soyad"])
                ini = initials(r["ad"], r["soyad"])
                with cols[j]:
                    st.markdown(f"""
                    <div class="doc-card">
                        <div class="doc-avatar" style="background:{ic};">{ini}</div>
                        <div class="doc-name">Dr. {r['ad']} {r['soyad']}</div>
                        <div class="doc-spec">{r['uzmanlik'] or 'Genel'}</div>
                        <div class="doc-info">
                            <span>📞 {r['telefon'] or '—'}</span>
                            <span style="color:#c7d2fe;">ID #{r['id']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("🗑️ Sil", key=f"dd{r['id']}", use_container_width=True):
                        con = get_db()
                        con.execute("DELETE FROM doktorlar WHERE id=?", (r["id"],))
                        con.commit(); con.close()
                        st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("Kayıtlı doktor bulunamadı.")


# ══════════════════════════════════════════════════════════════
# SAYFA: RANDEVULAR
# ══════════════════════════════════════════════════════════════
elif page == "📅 Randevular":
    st.session_state.pop("_goto", None)

    st.markdown("""
    <div class="page-header" style="background:linear-gradient(135deg,#78350f,#f59e0b);">
        <div><h2>📅 Randevu Yönetimi</h2><p>Randevuları görüntüleyin, ekleyin veya iptal edin.</p></div>
    </div>
    """, unsafe_allow_html=True)

    con = get_db()
    hastalar_list  = con.execute("SELECT * FROM hastalar ORDER BY ad").fetchall()
    doktorlar_list = con.execute("SELECT * FROM doktorlar ORDER BY ad").fetchall()
    con.close()

    with st.expander("➕ Yeni Randevu Al", expanded=False):
        if not hastalar_list:
            st.warning("⚠️ Önce hasta ekleyin.")
        elif not doktorlar_list:
            st.warning("⚠️ Önce doktor ekleyin.")
        else:
            with st.form("randevu_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                hasta_map  = {f"{h['ad']} {h['soyad']}  (#{h['id']})": h["id"] for h in hastalar_list}
                doktor_map = {f"Dr. {d['ad']} {d['soyad']} – {d['uzmanlik'] or 'Genel'}  (#{d['id']})": d["id"] for d in doktorlar_list}
                hasta_sec  = c1.selectbox("Hasta *", list(hasta_map.keys()))
                doktor_sec = c2.selectbox("Doktor *", list(doktor_map.keys()))
                tarih      = c1.date_input("Tarih *", min_value=date.today())
                saat_list  = [f"{h:02d}:{m:02d}" for h in range(8, 18) for m in (0, 30)]
                saat       = c2.selectbox("Saat *", saat_list)
                if st.form_submit_button("📅 Randevu Al", type="primary"):
                    con = get_db()
                    con.execute(
                        "INSERT INTO randevular (hasta_id, doktor_id, tarih, saat, durum) VALUES (?,?,?,?,?)",
                        (hasta_map[hasta_sec], doktor_map[doktor_sec], str(tarih), saat, "Aktif"),
                    )
                    con.commit(); con.close()
                    st.success("✅ Randevu alındı!")
                    st.rerun()

    # ── Filtreler ──
    fc1, fc2 = st.columns(2)
    hasta_opts   = {"— Tüm Hastalar —": ""} | {f"{h['ad']} {h['soyad']}": str(h["id"]) for h in hastalar_list}
    hasta_filter = fc1.selectbox("👤 Hastaya Göre", list(hasta_opts.keys()))
    durum_filter = fc2.selectbox("🔖 Duruma Göre", ["Tümü", "Aktif", "İptal"])

    query = """
        SELECT r.id, r.tarih, r.saat, r.durum,
               h.ad||' '||h.soyad AS hasta_adi,
               d.ad||' '||d.soyad AS doktor_adi,
               d.uzmanlik
        FROM randevular r
        JOIN hastalar h  ON r.hasta_id  = h.id
        JOIN doktorlar d ON r.doktor_id = d.id
        WHERE 1=1
    """
    params = []
    if hasta_opts[hasta_filter]:
        query += " AND r.hasta_id = ?";  params.append(hasta_opts[hasta_filter])
    if durum_filter != "Tümü":
        query += " AND r.durum = ?";     params.append(durum_filter)
    query += " ORDER BY r.tarih DESC, r.saat DESC"

    con  = get_db()
    rows = con.execute(query, params).fetchall()
    con.close()

    st.markdown(f"<p style='color:#6b7280; font-size:.85rem;'>{len(rows)} randevu</p>",
                unsafe_allow_html=True)

    if rows:
        st.markdown("""
        <div class="tbl-header">
            <span style="flex:2.5">Hasta</span>
            <span style="flex:2.5">Doktor</span>
            <span style="flex:1.8">Uzmanlık</span>
            <span style="flex:1.3">Tarih</span>
            <span style="flex:.8">Saat</span>
            <span style="flex:1">Durum</span>
            <span style="flex:1.5"></span>
        </div>
        """, unsafe_allow_html=True)

        for r in rows:
            badge = "badge-aktif" if r["durum"] == "Aktif" else "badge-iptal"
            ic    = avatar_color(r["hasta_adi"])
            ini   = r["hasta_adi"][:2].upper()
            c = st.columns([2.5, 2.5, 1.8, 1.3, 0.8, 1, 0.8, 0.7])
            c[0].markdown(f"""
            <div style="display:flex;align-items:center;gap:.5rem;">
                <span style="width:28px;height:28px;border-radius:50%;background:{ic};
                    display:inline-flex;align-items:center;justify-content:center;
                    font-size:.65rem;font-weight:700;color:white;flex-shrink:0;">{ini}</span>
                <span style="font-size:.9rem;">{r["hasta_adi"]}</span>
            </div>
            """, unsafe_allow_html=True)
            c[1].write(f"Dr. {r['doktor_adi']}")
            c[2].markdown(f"<span style='color:#6b7280;font-size:.85rem;'>{r['uzmanlik'] or '—'}</span>",
                          unsafe_allow_html=True)
            c[3].write(r["tarih"])
            c[4].write(r["saat"])
            c[5].markdown(f'<span class="{badge}">{r["durum"]}</span>', unsafe_allow_html=True)
            if r["durum"] == "Aktif":
                if c[6].button("İptal", key=f"ip{r['id']}", help="İptal et"):
                    con = get_db()
                    con.execute("UPDATE randevular SET durum='İptal' WHERE id=?", (r["id"],))
                    con.commit(); con.close()
                    st.rerun()
            if c[7].button("🗑️", key=f"dr{r['id']}", help="Sil"):
                con = get_db()
                con.execute("DELETE FROM randevular WHERE id=?", (r["id"],))
                con.commit(); con.close()
                st.rerun()
            st.markdown('<div style="height:1px;background:#f1f5f9;margin:0;"></div>',
                        unsafe_allow_html=True)
    else:
        st.info("Randevu bulunamadı.")


# ══════════════════════════════════════════════════════════════
# SAYFA: YAPAY ZEKA ASİSTAN
# ══════════════════════════════════════════════════════════════
elif page == "🤖 Yapay Zeka Asistan":
    st.session_state.pop("_goto", None)

    st.markdown("""
    <div class="page-header" style="background:linear-gradient(135deg,#4c1d95,#7c3aed);">
        <div>
            <h2>🤖 Yapay Zeka Asistan</h2>
            <p>Doktorlar, randevular ve hastane hakkında Türkçe sorularınızı sorun.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Chatbot Motoru ────────────────────────────────────────
    UZMANLIKLAR = [
        "kardiyoloji", "kardiyolog", "kalp",
        "ortopedi", "ortopedist", "kemik", "eklem",
        "dahiliye", "dahiliyeci", "iç hastalık",
        "nöroloji", "nörolog", "sinir",
        "pediatri", "çocuk", "pediatrist",
        "göz", "oftalmoloji", "oftalmolog",
        "kulak burun boğaz", "kbb",
        "dermatoloji", "deri", "dermatolog",
        "psikiyatri", "psikiyatrist", "ruh",
        "genel cerrahi", "cerrahi", "cerrah",
        "jinekoloji", "jinekolog", "kadın doğum", "kadın hastalık",
        "üroloji", "ürolog",
        "onkoloji", "onkolog", "kanser",
        "endokrinoloji", "endokrinolog", "şeker", "tiroid",
        "fizik tedavi", "fizik", "rehabilitasyon",
        "radyoloji", "radyolog",
        "anestezi", "anestezist",
        "acil", "aile hekimliği", "aile hekimi",
    ]

    def normalize(text: str) -> str:
        text = text.lower()
        for k, v in {"ı":"i","ğ":"g","ü":"u","ş":"s","ö":"o","ç":"c",
                     "İ":"i","Ğ":"g","Ü":"u","Ş":"s","Ö":"o","Ç":"c"}.items():
            text = text.replace(k, v)
        return text

    def detect_intent(text: str) -> str:
        t = normalize(text)
        if any(k in t for k in ["merhaba","selam","gunaydin","iyi gunler","iyi aksamlar","hosgeldin","hey"]):
            return "selamlama"
        if any(k in t for k in ["112","ambulans","imdat","yardim et acil","oluyorum"]):
            return "acil"
        if any(k in t for k in ["tesekkur","sagol","eyvallah","bravo","harika"]):
            return "tesekkur"
        if any(k in t for k in ["goruse","hosca kal","bye","cikiyorum","kapatiyorum"]):
            return "veda"
        if any(k in t for k in ["istatistik","kac hasta","kac doktor","kac randevu","toplam","sayi","rakam"]):
            return "istatistik"
        if any(k in t for k in ["randevu listesi","randevularim","aktif randevu","randevulari listele",
                                  "randevulari goster","iptal randevu","randevu goster"]):
            return "randevu_listesi"
        if any(k in t for k in ["randevu nasil","nasil randevu","randevu almak","randevu al",
                                  "randevu icin","nasil kayit","basvuru"]):
            return "randevu_nasil"
        if any(k in t for k in ["doktor listesi","hangi doktor","doktorlar","doktor var mi",
                                  "hekim","doktor goster","doktor bul"]):
            return "doktor_listesi"
        for uzm in UZMANLIKLAR:
            if normalize(uzm) in t:
                return "uzmanlik_sorgu"
        if any(k in t for k in ["hasta kayit","hasta ekle","yeni hasta","kayit ol"]):
            return "hasta_kayit_bilgi"
        if any(k in t for k in ["calisma saati","saat","kacta","adres","nerede","hakkinda"]):
            return "hastane_bilgi"
        if any(k in t for k in ["yardim","ne yapabilir","ne sorabilirim","neler sorabilir","menu"]):
            return "yardim"
        return "bilinmiyor"

    def detect_specialty(text: str) -> str:
        t = normalize(text)
        for uzm in sorted(UZMANLIKLAR, key=len, reverse=True):
            if normalize(uzm) in t:
                return uzm
        return ""

    def db_doctors(uzmanlik_filter: str = "") -> list:
        con = get_db()
        rows = con.execute(
            "SELECT * FROM doktorlar WHERE uzmanlik LIKE ? ORDER BY ad" if uzmanlik_filter
            else "SELECT * FROM doktorlar ORDER BY ad",
            (f"%{uzmanlik_filter}%",) if uzmanlik_filter else ()
        ).fetchall()
        con.close()
        return [dict(r) for r in rows]

    def db_appointments(durum: str = "") -> list:
        con = get_db()
        q = """
            SELECT r.tarih, r.saat, r.durum,
                   h.ad||' '||h.soyad AS hasta_adi,
                   d.ad||' '||d.soyad AS doktor_adi,
                   d.uzmanlik
            FROM randevular r
            JOIN hastalar h  ON r.hasta_id = h.id
            JOIN doktorlar d ON r.doktor_id = d.id
        """
        params: list = []
        if durum:
            q += " WHERE r.durum = ?"
            params.append(durum)
        q += " ORDER BY r.tarih DESC, r.saat DESC LIMIT 15"
        rows = con.execute(q, params).fetchall()
        con.close()
        return [dict(r) for r in rows]

    def db_stats() -> dict:
        con = get_db()
        s = {
            "hasta":         con.execute("SELECT COUNT(*) FROM hastalar").fetchone()[0],
            "doktor":        con.execute("SELECT COUNT(*) FROM doktorlar").fetchone()[0],
            "aktif_randevu": con.execute("SELECT COUNT(*) FROM randevular WHERE durum='Aktif'").fetchone()[0],
            "iptal_randevu": con.execute("SELECT COUNT(*) FROM randevular WHERE durum='İptal'").fetchone()[0],
        }
        con.close()
        return s

    def generate_response(user_text: str, history: list) -> str:
        intent  = detect_intent(user_text)
        t_lower = normalize(user_text)

        if intent == "selamlama":
            return random.choice([
                "Merhaba! 👋 Hastane asistanınız olarak size yardımcı olmaktan memnuniyet duyarım.\n\n"
                "Şunlar hakkında sorabilirsiniz:\n"
                "- 👨‍⚕️ Doktorlarımız ve uzmanlık alanları\n"
                "- 📅 Randevu alma süreci\n"
                "- 📊 Hastane istatistikleri",

                "Hoş geldiniz! 😊 Size nasıl yardımcı olabilirim?\n\n"
                "Doktor bilgisi, randevu süreci veya hastane hakkında her şeyi sorabilirsiniz.",
            ])

        if intent == "acil":
            return (
                "🚨 **ACİL DURUM!**\n\n"
                "Lütfen hemen **112**'yi arayın!\n\n"
                "- **Ambulans**: 112\n"
                "- **İtfaiye**: 110\n"
                "- **Polis**: 155\n\n"
                "Güvende olmanızı diliyoruz. Acil servisimiz 7/24 hizmetinizdedir."
            )

        if intent == "tesekkur":
            return random.choice([
                "Rica ederim! 😊 Başka bir sorunuz varsa buradayım.",
                "Ne demek! Sağlıklı günler dilerim. 🌟",
                "Yardımcı olabildiğime sevindim. Başka bir şey sormak ister misiniz?",
            ])

        if intent == "veda":
            return random.choice([
                "Hoşça kalın! 👋 Sağlıklı günler dilerim.",
                "Güle güle! Herhangi bir sorunuzda yine bekleriz. 😊",
            ])

        if intent == "istatistik":
            s = db_stats()
            return (
                f"📊 **Hastane İstatistikleri**\n\n"
                f"| Alan | Sayı |\n|------|------|\n"
                f"| 👥 Kayıtlı Hasta | **{s['hasta']}** |\n"
                f"| 👨‍⚕️ Kayıtlı Doktor | **{s['doktor']}** |\n"
                f"| ✅ Aktif Randevu | **{s['aktif_randevu']}** |\n"
                f"| ❌ İptal Randevu | **{s['iptal_randevu']}** |"
            )

        if intent == "randevu_listesi":
            durum = "Aktif" if "aktif" in t_lower else ("İptal" if "iptal" in t_lower else "")
            rows = db_appointments(durum)
            if not rows:
                return "📅 Şu an kayıtlı randevu bulunmuyor."
            baslik = f"📅 **{'Aktif ' if durum=='Aktif' else 'İptal ' if durum=='İptal' else ''}Randevular** (son 15)\n\n"
            return baslik + "\n".join(
                f"- **{r['tarih']} {r['saat']}** | {r['hasta_adi']} → Dr. {r['doktor_adi']}"
                f" ({r['uzmanlik'] or 'Genel'}) `{r['durum']}`"
                for r in rows
            )

        if intent == "randevu_nasil":
            return (
                "📅 **Randevu Alma Adımları**\n\n"
                "1. Sol menüden **📅 Randevular** sayfasına gidin.\n"
                "2. **'Yeni Randevu Al'** butonuna tıklayın.\n"
                "3. Listeden **hastanızı** seçin.\n"
                "4. **Doktor** ve **uzmanlık alanı** seçin.\n"
                "5. **Tarih** ve **saat** belirleyin.\n"
                "6. **'Randevu Al'** butonuna basın. ✅\n\n"
                "> 💡 Sistemde kayıtlı hasta yoksa önce **👥 Hastalar** sayfasından hasta ekleyin."
            )

        if intent == "doktor_listesi":
            rows = db_doctors()
            if not rows:
                return "Henüz sisteme kayıtlı doktor bulunmuyor.\n\n👨‍⚕️ Doktorlar sayfasından ekleyebilirsiniz."
            return (
                f"👨‍⚕️ **Kayıtlı Doktorlarımız** ({len(rows)} doktor)\n\n"
                + "\n".join(
                    f"- **Dr. {r['ad']} {r['soyad']}** — {r['uzmanlik'] or 'Genel'}"
                    + (f" _(Tel: {r['telefon']})_" if r.get("telefon") else "")
                    for r in rows
                )
            )

        if intent == "uzmanlik_sorgu":
            uzm  = detect_specialty(user_text)
            rows = db_doctors(uzm)
            if not rows:
                return (
                    f"Üzgünüm, **{uzm}** alanında şu an kayıtlı doktorumuz bulunmuyor. 😔\n\n"
                    "Tüm doktorlarımızı görmek için 'doktorları listele' yazabilirsiniz."
                )
            return (
                f"👨‍⚕️ **{uzm.title()} Alanındaki Doktorlarımız**\n\n"
                + "\n".join(
                    f"- **Dr. {r['ad']} {r['soyad']}** — {r['uzmanlik'] or uzm}"
                    + (f" _(Tel: {r['telefon']})_" if r.get("telefon") else "")
                    for r in rows
                )
            )

        if intent == "hasta_kayit_bilgi":
            return (
                "👥 **Yeni Hasta Kaydı**\n\n"
                "1. Sol menüden **👥 Hastalar** sayfasına gidin.\n"
                "2. **'Yeni Hasta Ekle'** bölümünü açın.\n"
                "3. Ad, soyad, yaş, telefon ve TC no bilgilerini doldurun.\n"
                "4. **'Kaydet'** butonuna basın. ✅"
            )

        if intent == "hastane_bilgi":
            s = db_stats()
            return (
                "🏥 **Hastanemiz Hakkında**\n\n"
                f"- {s['doktor']} uzman doktorumuz hizmetinizdedir.\n"
                f"- {s['hasta']} kayıtlı hastamız bulunmaktadır.\n"
                "- Çalışma saatlerimiz: **Hafta içi 08:00 – 17:00**, Cumartesi **08:00 – 13:00**\n"
                "- Acil servisimiz **7/24** hizmet vermektedir.\n\n"
                "> Randevu için 📅 Randevular sayfasını kullanabilirsiniz."
            )

        if intent == "yardim":
            return (
                "🤖 **Size şu konularda yardımcı olabilirim:**\n\n"
                "| Konu | Örnek Soru |\n|------|------------|\n"
                "| 👨‍⚕️ Doktor Listesi | _\"Hangi doktorlar var?\"_ |\n"
                "| 🔍 Uzmanlık Arama | _\"Kardiyolog var mı?\"_ |\n"
                "| 📅 Randevu Alma | _\"Randevu nasıl alırım?\"_ |\n"
                "| 📋 Randevu Listesi | _\"Aktif randevuları göster\"_ |\n"
                "| 📊 İstatistikler | _\"Kaç hasta var?\"_ |\n"
                "| 🚨 Acil | _\"Acil yardım\"_ |"
            )

        last_intents = [m.get("intent", "") for m in history[-3:] if m.get("role") == "assistant"]
        hint = "\n\nDoktor bilgisi hakkında başka bir şey sormak ister misiniz?" \
               if "doktor_listesi" in last_intents or "uzmanlik_sorgu" in last_intents else ""
        return (
            "Anlayamadım, özür dilerim. 🙏\n\n"
            "Şu konularda yardımcı olabilirim:\n"
            "- **'Hangi doktorlar var?'**\n"
            "- **'Kardiyolog var mı?'**\n"
            "- **'Randevu nasıl alırım?'**\n"
            "- **'Aktif randevuları göster'**\n"
            "- **'Kaç hasta var?'**\n"
            "- **'Yardım'** yazarak tam listeyi görebilirsiniz." + hint
        )

    # ── Chat geçmişi başlat ───────────────────────────────────
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [{
            "role": "assistant",
            "content": (
                "Merhaba! 👋 Ben **Hastane Asistanı**'yım.\n\n"
                "Doktorlarımız, randevu süreci ve hastane hakkında Türkçe sorularınızı yanıtlayabilirim.\n\n"
                "Başlamak için yazın ya da aşağıdaki hızlı sorulardan birini seçin. 😊"
            ),
            "intent": "selamlama",
        }]

    # ── Hızlı sorular ─────────────────────────────────────────
    qcols = st.columns(4)
    quick = ["Hangi doktorlar var?", "Randevu nasıl alırım?",
             "İstatistikleri göster", "Aktif randevuları göster"]
    for col, q in zip(qcols, quick):
        with col:
            st.markdown('<div class="quick-btn">', unsafe_allow_html=True)
            if st.button(q, key=f"qk_{q}", use_container_width=True):
                st.session_state["_quick_input"] = q
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Mesaj listesi ─────────────────────────────────────────
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # ── Temizle ───────────────────────────────────────────────
    if len(st.session_state.chat_history) > 1:
        if st.button("🗑️ Sohbeti Temizle", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()

    # ── Giriş ─────────────────────────────────────────────────
    pending    = st.session_state.pop("_quick_input", None)
    user_input = pending or st.chat_input("Sorunuzu yazın…")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        reply  = generate_response(user_input, st.session_state.chat_history)
        intent = detect_intent(user_input)
        st.session_state.chat_history.append({
            "role": "assistant", "content": reply, "intent": intent,
        })
        with st.chat_message("assistant"):
            st.markdown(reply)
