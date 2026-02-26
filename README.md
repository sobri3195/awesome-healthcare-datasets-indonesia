# Awesome Healthcare Datasets Indonesia

Daftar dan pipeline pengumpulan dataset kesehatan untuk AI di Indonesia, dengan fokus pada sumber GitHub yang **open access**.

> Status saat ini: lingkungan eksekusi ini tidak dapat mengakses `github.com` (HTTP 403 dari proxy), sehingga saya menyiapkan analisis metodologis mendalam + skrip otomatis agar pengumpulan **1000+ repositori** bisa dijalankan langsung saat akses jaringan tersedia.

## Tujuan

1. Mengumpulkan minimal **1000 entri** repositori GitHub yang relevan.
2. Memetakan entri ke kategori utama:
   - SIMRS
   - Obat
   - Kardiovaskular
   - General Healthcare Dataset
3. Menyediakan output terstruktur agar mudah dipakai untuk riset, validasi, dan kurasi manual.

## Struktur proyek

- `scripts/fetch_github_healthcare_repos.py` → crawler GitHub API + klasifikasi + ringkasan.
- `data/github_healthcare_repositories.csv` → output utama (akan berisi 1000+ entri jika eksekusi berhasil).
- `data/github_healthcare_summary.md` → ringkasan statistik hasil crawling.

## Analisis mendalam: pendekatan pengumpulan data

### 1) Strategi discovery multi-query

Kueri dirancang untuk menutup spektrum luas healthcare data:

- `"healthcare dataset" in:name,description,readme`
- `"medical dataset" in:name,description,readme`
- `"hospital dataset" in:name,description,readme`
- `"simrs" in:name,description,readme`
- `"obat" "dataset" indonesia in:name,description,readme`
- `"kardiovaskular" dataset in:name,description,readme`
- `"indonesia health" dataset in:name,description,readme`
- `"rekam medis" dataset in:name,description,readme`

Dengan kombinasi ini, repositori lintas bahasa dan lintas domain bisa tercakup; deduplikasi dilakukan menggunakan `full_name` repo (`owner/repo`).

### 2) Klasifikasi domain

Klasifikasi rule-based berbasis kata kunci:

- **SIMRS**: `simrs`, `hospital information system`, `his`, `rekam medis`
- **Obat**: `obat`, `drug`, `pharmaceutical`, `farmasi`, `medicine`
- **Kardiovaskular**: `kardi`, `cardio`, `heart`, `ecg`, `ekg`
- **General**: selain kata kunci spesifik di atas

Satu repositori bisa memiliki beberapa sinyal, namun kategori dipilih berdasar prioritas domain untuk konsistensi output.

### 3) Kualitas data dan risiko

- **False positive**: repo menyebut keyword tetapi bukan dataset.
- **False negative**: repo relevan tapi deskripsi minim.
- **Mitigasi**:
  - normalisasi teks (`name + description + topics`),
  - simpan metadata (stars, forks, timestamps) untuk scoring,
  - sisipkan tahap kurasi manual untuk kandidat prioritas tinggi.

### 4) Metrik yang dihasilkan

- Jumlah total entri unik.
- Distribusi per kategori.
- Distribusi bahasa pemrograman.
- Top 20 repo berdasarkan stars.

## Cara menjalankan (target 1000+)

```bash
python scripts/fetch_github_healthcare_repos.py --target 1200 --per-page 100 --max-pages 10 --sleep 2
```

Jika berhasil, skrip akan menghasilkan:

- `data/github_healthcare_repositories.csv`
- `data/github_healthcare_summary.md`

## Catatan penting lingkungan

Pada eksekusi saat ini, request ke GitHub gagal karena pembatasan jaringan/proxy (`CONNECT tunnel failed: 403`). Pipeline sudah siap, sehingga Anda cukup menjalankannya di environment dengan akses internet ke GitHub API.

- - -

Todo:
* Tambahkan tahap validasi otomatis bahwa repo benar-benar berisi berkas dataset (`.csv`, `.parquet`, `.json`, `.xlsx`).
* Tambahkan scoring relevansi berbasis deskripsi + topic.
* Tambahkan sinkronisasi periodik (mis. weekly cron).

Inspiration From:
* [Awesome Python](https://github.com/vinta/awesome-python)
* [Awesome Public Datasets](https://github.com/caesar0301/awesome-public-datasets)
* [Meta Awesome](https://github.com/sindresorhus/awesome)
* [Awesome Healthcare Dataset non Indonesia](https://github.com/nickls/awesome-healthcare-datasets)
