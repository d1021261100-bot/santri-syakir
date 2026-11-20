"""
Tugas Besar - Aplikasi Perhitungan Biaya Laundry Kiloan
Dibuat dengan Python dan Streamlit.
Nama : Syakir Zidan Rafael
NIM  : 1021261110

Cara menjalankan:
    pip install streamlit
    streamlit run Tugasbesar_syakir_1021261110.py
"""

import re

import streamlit as st

# ---------------------------------------------------------------------------
# Konstanta
# ---------------------------------------------------------------------------
TARIF_DASAR = 5000          # Rp per kg
TARIF_PER_DIGIT = 500       # tambahan Rp per nilai digit terakhir NIM
DIGIT_GENAP = set("02468")  # angka 0 termasuk genap
PANJANG_NIM = 10
NAMA_WATERMARK = "Syakir Zidan Rafael"
WARNA_UTAMA = "rgb(0, 178, 251)"  # kode warna tema: 0, 178, 251


# ---------------------------------------------------------------------------
# Fungsi logika (dipisah dari tampilan agar mudah diuji)
# ---------------------------------------------------------------------------
def format_rupiah(nilai: int) -> str:
    """Contoh: 80750 -> 'Rp 80.750'."""
    return "Rp " + f"{int(nilai):,}".replace(",", ".")


def validasi_nim(nim: str):
    """Mengembalikan pesan kesalahan, atau None jika NIM valid."""
    # [0-9] dipakai (bukan str.isdigit) agar hanya angka 0-9 biasa yang diterima.
    if re.fullmatch(r"[0-9]{%d}" % PANJANG_NIM, nim) is None:
        return f"NIM tidak valid. NIM harus terdiri dari tepat {PANJANG_NIM} digit angka."
    return None


def validasi_berat(berat):
    """Mengembalikan pesan kesalahan, atau None jika berat valid."""
    if isinstance(berat, bool) or not isinstance(berat, int):
        return "Berat cucian harus berupa bilangan bulat."
    if berat <= 0:
        return "Berat cucian harus lebih dari 0."
    return None


def hitung_biaya(nim: str, berat: int) -> dict:
    """Menghitung seluruh komponen biaya laundry. Input diasumsikan sudah valid."""
    digit_terakhir = int(nim[-1])
    tarif_per_kg = TARIF_DASAR + digit_terakhir * TARIF_PER_DIGIT
    jumlah_genap = sum(1 for d in nim if d in DIGIT_GENAP)
    persen_diskon = jumlah_genap  # 1% per digit genap
    biaya_normal = berat * tarif_per_kg
    potongan = biaya_normal * persen_diskon // 100  # selalu bulat (kelipatan 5)
    total_bayar = biaya_normal - potongan
    return {
        "nim": nim,
        "berat": berat,
        "digit_terakhir": digit_terakhir,
        "tarif_per_kg": tarif_per_kg,
        "jumlah_genap": jumlah_genap,
        "persen_diskon": persen_diskon,
        "biaya_normal": biaya_normal,
        "potongan": potongan,
        "total_bayar": total_bayar,
    }


# ---------------------------------------------------------------------------
# Callback tombol
# ---------------------------------------------------------------------------
def aksi_hitung():
    nim = str(st.session_state.get("nim", "")).strip()
    berat = st.session_state.get("berat")

    # Antisipasi widget yang mengembalikan float bulat (mis. 4.0 -> 4)
    if isinstance(berat, float) and berat.is_integer():
        berat = int(berat)

    pesan = validasi_nim(nim)
    if pesan is None:
        pesan = validasi_berat(berat)

    if pesan is not None:
        st.session_state["error"] = pesan
        st.session_state["hasil"] = None
    else:
        st.session_state["error"] = None
        st.session_state["hasil"] = hitung_biaya(nim, berat)


def aksi_reset():
    st.session_state["nim"] = ""
    st.session_state["berat"] = 0
    st.session_state["hasil"] = None
    st.session_state["error"] = None


# ---------------------------------------------------------------------------
# Tampilan: gaya kartu hasil perhitungan
# ---------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;800&family=DM+Mono:wght@400;500&display=swap');
:root { --biru: rgb(0, 178, 251); --biru-tua: rgb(0, 140, 201); --biru-muda: #E6F7FF; --tinta: #062B3D; }
.stApp { background: #EAF8FF; font-family: 'Sora', 'Segoe UI', system-ui, sans-serif; }
#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; }
.block-container { max-width: 1000px; padding-top: 1.5rem; padding-bottom: 4rem; }
.kepala { background: var(--biru); color: var(--tinta); border-radius: 22px; padding: 24px 30px; margin-bottom: 30px; display: flex; align-items: center; gap: 20px; }
.kepala .ikon { font-size: 2.5rem; background: #ffffff; border-radius: 18px; width: 74px; height: 74px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.kepala .judul { font-size: 1.8rem; font-weight: 800; line-height: 1.2; color: var(--tinta); }
.kepala .sub { margin-top: 4px; font-size: 1rem; color: var(--tinta); }
.bagian { font-weight: 800; font-size: 1.05rem; color: var(--tinta); margin-bottom: 12px; }
[data-testid="stWidgetLabel"] p { color: var(--tinta) !important; font-weight: 600; }
[data-baseweb="input"], [data-baseweb="base-input"] { background: #ffffff !important; border-radius: 12px !important; }
[data-baseweb="input"] { border: 2px solid #BFE6F7 !important; }
[data-baseweb="input"]:focus-within { border-color: var(--biru) !important; box-shadow: 0 0 0 3px rgba(0, 178, 251, 0.30); }
[data-baseweb="input"] input { color: var(--tinta) !important; -webkit-text-fill-color: var(--tinta) !important; }
[data-testid="stNumberInput"] button { background: #ffffff !important; color: var(--tinta) !important; }
div.stButton { width: 100%; }
div.stButton > button { width: 100%; border-radius: 12px; font-weight: 700; padding: 0.65rem 1rem; }
div.stButton > button * { color: inherit !important; }
div.stButton > button[kind="primary"], div.stButton > button[data-testid="stBaseButton-primary"] { background: var(--biru); border: 2px solid var(--biru); color: var(--tinta); }
div.stButton > button[kind="primary"]:hover, div.stButton > button[data-testid="stBaseButton-primary"]:hover { background: var(--biru-tua); border-color: var(--biru-tua); color: #ffffff; }
div.stButton > button[kind="secondary"], div.stButton > button[data-testid="stBaseButton-secondary"] { background: #ffffff; border: 2px solid var(--tinta); color: var(--tinta); }
div.stButton > button[kind="secondary"]:hover, div.stButton > button[data-testid="stBaseButton-secondary"]:hover { background: var(--biru-muda); }
.hasil-perhitungan { background: #ffffff; color: var(--tinta); padding: 24px 26px 26px; border-radius: 14px 14px 0 0; position: relative; margin-bottom: 24px; box-shadow: 0 10px 24px rgba(0, 100, 150, 0.15); }
.hasil-perhitungan::after { content: ""; position: absolute; left: 0; right: 0; bottom: -10px; height: 10px; background: linear-gradient(135deg, #ffffff 5px, transparent 0) 0 0, linear-gradient(225deg, #ffffff 5px, transparent 0) 0 0; background-size: 10px 10px; }
.hasil-perhitungan .judul-hasil { font-weight: 800; font-size: 1.15rem; }
.hasil-perhitungan .meta { display: flex; justify-content: space-between; font-size: 0.9rem; margin-top: 6px; }
.hasil-perhitungan .meta:first-child { margin-top: 0; }
.hasil-perhitungan .garis { border-top: 2px dashed #BFE6F7; margin: 16px 0; }
.hasil-perhitungan .baris { display: flex; justify-content: space-between; align-items: center; padding: 7px 0; }
.hasil-perhitungan .nilai { font-family: 'DM Mono', ui-monospace, Consolas, monospace; font-weight: 500; }
.hasil-perhitungan .total { background: var(--biru); color: var(--tinta); border-radius: 12px; padding: 14px 18px; display: flex; justify-content: space-between; align-items: center; margin-top: 8px; }
.hasil-perhitungan .total .label { font-weight: 800; font-size: 1.05rem; }
.hasil-perhitungan .total .angka { font-family: 'DM Mono', ui-monospace, Consolas, monospace; font-weight: 500; font-size: 1.6rem; }
.kosong { border: 2px dashed rgb(0, 178, 251); border-radius: 14px; padding: 48px 24px; text-align: center; color: var(--tinta); background: rgba(255, 255, 255, 0.55); }
.galat { background: #FFE9E7; border-left: 6px solid #D93025; color: #5B1410; padding: 16px 18px; border-radius: 10px; font-weight: 600; }
</style>
"""


def html(teks: str):
    """Menampilkan HTML. Baris dirapatkan agar tidak dibaca sebagai blok kode markdown."""
    baris = [b.strip() for b in teks.strip().splitlines() if b.strip()]
    st.markdown("\n".join(baris), unsafe_allow_html=True)


def tampilkan_watermark(nama: str):
    """Satu watermark di bagian bawah halaman (tidak menghalangi klik)."""
    html(
        f"""
<style>
.watermark {{ position: fixed; left: 0; right: 0; bottom: 8px; z-index: 999; text-align: center;
font-size: 0.9rem; font-weight: 600; color: rgba(6, 43, 61, 0.6); pointer-events: none; user-select: none; }}
</style>
<div class="watermark">{nama}</div>
"""
    )


def tampilkan_kepala():
    html(
        """
<div class="kepala">
<div class="ikon">🧺</div>
<div>
<div class="judul">Laundry Kiloan</div>
<div class="sub">Hitung biaya laundry dari NIM dan berat cucian</div>
</div>
</div>
"""
    )


def hasil_html(h: dict) -> str:
    return f"""
<div class="hasil-perhitungan">
<div class="meta"><span>NIM</span><span class="nilai">{h['nim']}</span></div>
<div class="meta"><span>Berat cucian</span><span class="nilai">{h['berat']} kg</span></div>
<div class="garis"></div>
<div class="baris"><span>Tarif per kg</span><span class="nilai">{format_rupiah(h['tarif_per_kg'])}</span></div>
<div class="baris"><span>Persen diskon</span><span class="nilai">{h['persen_diskon']} %</span></div>
<div class="baris"><span>Biaya normal</span><span class="nilai">{format_rupiah(h['biaya_normal'])}</span></div>
<div class="baris"><span>Potongan</span><span class="nilai">{format_rupiah(h['potongan'])}</span></div>
<div class="garis"></div>
<div class="total"><span class="label">Total bayar</span><span class="angka">{format_rupiah(h['total_bayar'])}</span></div>
</div>
"""


def tampilkan_hasil():
    if st.session_state["error"]:
        html(f'<div class="galat">{st.session_state["error"]}</div>')
    elif st.session_state["hasil"]:
        html(hasil_html(st.session_state["hasil"]))
    else:
        html(
            """
<div class="kosong">
<div style="font-size:2rem">🧾</div>
<div>Hasil perhitungan akan muncul di sini setelah kamu menekan <b>Hitung</b>.</div>
</div>
"""
        )


def main():
    st.set_page_config(page_title="Laundry Kiloan", page_icon="🧺", layout="wide")
    html(CSS)
    tampilkan_watermark(NAMA_WATERMARK)

    # Inisialisasi state
    st.session_state.setdefault("nim", "")
    st.session_state.setdefault("berat", 0)
    st.session_state.setdefault("hasil", None)
    st.session_state.setdefault("error", None)

    tampilkan_kepala()

    kol_input, kol_hasil = st.columns([5, 6], gap="large")

    with kol_input:
        html('<div class="bagian">Data cucian</div>')
        st.text_input("NIM (10 digit)", key="nim", max_chars=PANJANG_NIM,
                      placeholder="Contoh: 1021261110")
        st.number_input("Berat cucian (kg)", step=1, format="%d", key="berat")

        tombol_hitung, tombol_reset = st.columns(2)
        tombol_hitung.button("🧮 Hitung", type="primary", on_click=aksi_hitung)
        tombol_reset.button("🔄 Reset", on_click=aksi_reset)

    with kol_hasil:
        html('<div class="bagian">Hasil perhitungan</div>')
        tampilkan_hasil()


if __name__ == "__main__":
    main()