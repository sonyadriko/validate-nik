# Validasi NIK API

FastAPI-based Indonesian NIK (Nomor Induk Kependudukan) parser.

## Features

- Parse 16-digit NIK into biodata
- Extract: gender, birth date, location (province/regency/district)
- Additional: age, zodiac, Javanese pasaran
- Optional birth date verification
- 7071 districts from complete region database
- Serverless-ready (Vercel/AWS Lambda)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize region database (required)
python3 scripts/init_db.py

# Run locally
uvicorn main:app --reload
```

## API Usage

```bash
# Parse NIK (without verification)
curl "http://localhost:8000/api/v1/parse?nik=3173086804790005"

# Parse NIK with birth date verification
curl "http://localhost:8000/api/v1/parse?nik=3173086804790005&tanggal_lahir=1979-04-28"
```

With API key:
```bash
curl "http://localhost:8000/api/v1/parse?nik=3173086804790005" \
  -H "X-API-Key: your-api-key"
```

## Response

```json
{
  "nik": "3173086804790005",
  "kelamin": "PEREMPUAN",
  "lahir": "28/04/79",
  "lahir_lengkap": "28 April 1979",
  "provinsi": {"kode": "31", "nama": "DKI JAKARTA"},
  "kotakab": {"kode": "3173", "nama": "KOTA JAKARTA PUSAT", "jenis": "Kota"},
  "kecamatan": {"kode": "317308", "nama": "GAMBIR"},
  "kode_wilayah": "31.73.08",
  "nomor_urut": "0005",
  "tambahan": {
    "pasaran": "Sabtu Pon, 28 April 1979",
    "usia": "47 Tahun 0 Bulan 9 Hari",
    "kategori_usia": "Paruh Baya",
    "ultah": "0 Bulan 3 Hari Lagi",
    "zodiak": "Taurus"
  },
  "validasi": {
    "status": "valid",
    "reason": "dob_verified"
  }
}
```

### Validation Status

| `status` | `reason` | Description |
|----------|----------|-------------|
| `valid` | `nik_only` | NIK parsing without verification |
| `valid` | `dob_verified` | Birth date provided and matches NIK |
| `mismatch` | `dob_mismatch` | Birth date provided but differs from NIK |
| `error` | `invalid_birthdate` | Invalid date (e.g., Feb 30) |

## Architecture

- **Domain**: Business entities and value objects
- **Application**: NIK parser service
- **Infrastructure**: SQLite region repository (7071 districts)
- **API**: FastAPI routes, middleware, DTOs

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_KEYS` | Comma-separated API keys | (no auth required) |
| `DB_PATH` | Path to regions.db | `data/regions.db` |

## Deployment

### Docker
```bash
docker-compose up
```

### Vercel (Serverless)
- Runtime: `python-3.11`
- Handler: `api/serverless.py`
- Environment: Set `API_KEYS` for authentication

## License

MIT
