import streamlit as st

KENDARAAN = {
    4: 5,
    5: 7,
    6: 10,
    7: 12,
    8: 16,
    9: 24
}

class LantaiKapal:
    def __init__(self, panjang, lebar):
        self.panjang = panjang
        self.lebar = lebar
        self.slot_count = lebar // 3
        self.slot_panjang_tersisa = [panjang] * self.slot_count
        self.grid = [['.' for _ in range(self.slot_count)] for _ in range(self.panjang)]

    def tambah_kendaraan(self, gol):
        panjang_kendaraan = KENDARAAN.get(gol)
        label = f"G{gol}"
        for i in range(self.slot_count):
            if self.slot_panjang_tersisa[i] >= panjang_kendaraan:
                start_pos = self.panjang - self.slot_panjang_tersisa[i]
                for j in range(start_pos, start_pos + panjang_kendaraan):
                    self.grid[j][i] = label
                self.slot_panjang_tersisa[i] -= panjang_kendaraan
                return True, f"Gol {gol} dimuat di slot {i+1}"
        return False, f"Tidak cukup ruang untuk Gol {gol}"

    def get_kemungkinan_sisa(self):
        sisa = {}
        for gol, panjang in KENDARAAN.items():
            total = sum(slot // panjang for slot in self.slot_panjang_tersisa)
            sisa[gol] = total
        return sisa

class Kapal:
    def __init__(self, lantai_defs):
        self.lantai_list = [LantaiKapal(p, l) for p, l in lantai_defs]

    def tambah_kendaraan(self, gol):
        if gol in [4, 5]:
            for idx in range(1, len(self.lantai_list)):
                ok, msg = self.lantai_list[idx].tambah_kendaraan(gol)
                if ok:
                    return f"(Lantai {idx+1}) {msg}"
            ok, msg = self.lantai_list[0].tambah_kendaraan(gol)
            return f"(Lantai 1) {msg}"
        else:
            ok, msg = self.lantai_list[0].tambah_kendaraan(gol)
            return f"(Lantai 1) {msg}"

    def visualisasi(self):
        cols = st.columns(len(self.lantai_list))
        for idx, lantai in enumerate(self.lantai_list):
            with cols[idx]:
                st.markdown(f"### Lantai {idx+1}")
                grid = lantai.grid
                display = ""
                for row in grid:
                    display += " | ".join(row) + "\n"
                st.code(display, language="text")

# Streamlit App
st.set_page_config(layout="wide")
st.title("🚢 Sistem Pemuatan Kendaraan Kapal Bertingkat (Web Version)")

if "kapal" not in st.session_state:
    st.session_state.kapal = None

if "input_lantai" not in st.session_state:
    st.session_state.input_lantai = []

st.sidebar.header("📐 Pengaturan Kapal")

if st.session_state.kapal is None:
    jumlah = st.sidebar.number_input("Jumlah lantai kapal", min_value=1, max_value=5, value=2)
    if len(st.session_state.input_lantai) != jumlah:
        st.session_state.input_lantai = [{"panjang": 30, "lebar": 9} for _ in range(jumlah)]

    for i in range(jumlah):
        st.sidebar.markdown(f"**Lantai {i+1}**")
        st.session_state.input_lantai[i]["panjang"] = st.sidebar.number_input(
            f"Panjang Lantai {i+1} (m)", min_value=1, max_value=100, value=st.session_state.input_lantai[i]["panjang"], key=f"p_{i}")
        st.session_state.input_lantai[i]["lebar"] = st.sidebar.number_input(
            f"Lebar Lantai {i+1} (m)", min_value=3, max_value=30, value=st.session_state.input_lantai[i]["lebar"], key=f"l_{i}")

    if st.sidebar.button("Mulai Kapal"):
        data = [(d["panjang"], d["lebar"]) for d in st.session_state.input_lantai]
        st.session_state.kapal = Kapal(data)
        st.rerun()
else:
    st.sidebar.success("Kapal sudah dibuat ✅")
    if st.sidebar.button("🔁 Reset"):
        st.session_state.kapal = None
        st.rerun()

    st.sidebar.markdown("### 🚗 Tambah Kendaraan")
    gol = st.sidebar.selectbox("Golongan Kendaraan", options=list(KENDARAAN.keys()))
    if st.sidebar.button("Tambah"):
        hasil = st.session_state.kapal.tambah_kendaraan(gol)
        st.success(hasil)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ Info Sisa Muat")
    for i, lantai in enumerate(st.session_state.kapal.lantai_list):
        st.sidebar.markdown(f"**Lantai {i+1}**")
        sisa = lantai.get_kemungkinan_sisa()
        for g in sorted(sisa.keys()):
            if g >= 6 and i > 0:
                continue
            st.sidebar.write(f"Gol {g}: {sisa[g]} unit")

    # Tampilkan visualisasi
    st.subheader("📊 Visualisasi Lantai Kapal")
    st.session_state.kapal.visualisasi()
