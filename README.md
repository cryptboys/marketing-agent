
<p align="center">
  <h1 align="center">🤖 Marketing Agent CLI</h1>
  <p align="center"><em>Enterprise-grade AI marketing automation — CLI-powered, LLM-native, extensible by design.</em></p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/status-MVP-green?style=flat-square" alt="Status" />
  <img src="https://img.shields.io/badge/python-3.8%2B-blue?style=flat-square" alt="Python" />
  <img src="https://img.shields.io/badge/LLM-9Router%20%7C%20DeepSeek%20%7C%20Gemini-orange?style=flat-square" alt="LLM" />
  <img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="License" />
</p>

---

## 📋 Overview

**Marketing Agent CLI** adalah alat bantu marketing berbasis AI yang berjalan di terminal. Didukung oleh LLM lokal via [9Router](http://localhost:20128) untuk menghasilkan konten, menganalisis data, mengelola kampanye, dan memperluas kemampuan melalui sistem skill yang fleksibel.

Dibangun dengan arsitektur modular — lapisan governance, audit trace, CRM, dan dashboard — siap untuk produksi ringan maupun eksperimen cepat.

---

## ✨ Features

### Content Generation
| Command | Deskripsi |
|---------|-----------|
| `generate-social-post` | Buat draft postingan sosial media (LinkedIn, Twitter, dll) via LLM |
| `generate-email` | Tulis email marketing dengan subject dan body context |
| *(akan datang)* `generate-ad-copy` | Iklan copy untuk Google, Meta, TikTok Ads |

### Data Analysis
| Command | Deskripsi |
|---------|-----------|
| `analyze-keywords` | Analisis volume pencarian + tingkat kompetisi keyword |

### Campaign Management
| Command | Deskripsi |
|---------|-----------|
| `plan-campaign` | Rencanakan kampanye dengan budget tracking |
| `execute-campaign` | Eksekusi kampanye (state persist via JSON) |

### CRM
| Command | Deskripsi |
|---------|-----------|
| `add-lead` | Tambah lead baru dengan scoring otomatis |

### Dashboard & Governance
| Command | Deskripsi |
|---------|-----------|
| `dashboard-view` | Tampilkan ringkasan kampanye, budget, audit log |
| *(built-in)* | Audit trace, budget cap, egress allowlist |

### Skill System
| Command | Deskripsi |
|---------|-----------|
| `run-skill` | Jalankan method dari skill eksternal di folder `skills/` |

Skill dapat ditambahkan tanpa mengubah kode utama — cukup buat file `.py` di folder `skills/` dan jalankan via CLI.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- [9Router](http://localhost:20128) lokal dengan API key (model `easy` atau lainnya)

### Installation

```bash
# Clone repositori
git clone https://github.com/cryptboys/marketing-agent.git
cd marketing-agent

# (Opsional) Buat virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -e .
```

### Konfigurasi

Buat file `.env` di root proyek:

```env
NINE_ROUTER_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
NINE_ROUTER_URL=http://localhost:20128/v1
```

### Usage

```bash
# Generate konten
python main.py generate-social-post --topic "AI Marketing" --platform LinkedIn

# Analisis keyword
python main.py analyze-keywords AI marketing automation SEO

# Manajemen kampanye
python main.py plan-campaign "Q4 Launch" --objective "Sales" --audience "Enterprise" --budget 5000
python main.py execute-campaign "Q4 Launch"

# CRM
python main.py add-lead "Budi Santoso" budi@company.com Referral

# Dashboard
python main.py dashboard-view

# Skill eksternal
python main.py run-skill social-media-skill generate_post "Product Launch" "Instagram"
```

---

## 🏗️ Architecture

```
marketing-agent/
├── main.py                      # Entry point CLI
├── pyproject.toml               # Project metadata
├── .gitignore
├── .env                         # Environment variables (API keys)
├── src/
│   └── marketing_agent/
│       ├── cli.py               # CLI commands (Click-based)
│       ├── config_manager.py    # Config loader (.env, yaml)
│       ├── campaign_manager.py  # Campaign CRUD (JSON persist)
│       ├── content_generator.py # Content generation (LLM + mock fallback)
│       ├── data_analyzer.py     # Keyword analysis (LLM + mock fallback)
│       ├── crm_manager.py       # CRM / lead management
│       ├── governance.py        # Budget cap, egress validator, audit tracer
│       ├── skill_manager.py     # Dynamic skill loader
│       ├── dashboard.py         # Dashboard overview
│       └── llm_client.py        # 9Router LLM client
├── skills/                      # Extensible skill directory
│   ├── social_media_skill.py
│   ├── ad_copy_skill.py
│   ├── keyword_analysis_skill.py
│   └── campaign_planning_skill.py
├── campaign_data.json           # Persistent campaign state (auto-generated)
└── README.md
```

### Layer Architecture

```
┌─────────────────────────────┐
│       CLI (Click)           │  ← main.py → src/marketing_agent/cli.py
├─────────────────────────────┤
│     Governance Layer        │  ← budget, egress, trace
├─────────────────────────────┤
│    Core Business Logic      │  ← content, analysis, campaign, CRM
├─────────────────────────────┤
│     LLM Client (9Router)    │  ← llm_client.py → DeepSeek/Gemini/Claude
├─────────────────────────────┤
│    Skill System (Dynamic)   │  ← skills/*.py
├─────────────────────────────┤
│     Persistence (JSON)      │  ← campaign_data.json
└─────────────────────────────┘
```

---

## 🧠 LLM Integration

Agent ini menggunakan **[9Router](http://localhost:20128)** sebagai LLM Gateway lokal. Model default adalah `easy` (DeepSeek V4 Flash), yang otomatis routing ke model gratis terbaik.

**Model yang tersedia:**
- `easy` — combo, cepat untuk generate konten & analisis ringan
- `think` — reasoning (streaming, untuk analisis mendalam)
- `gemini/gemini-3.1-pro-preview` — kualitas tinggi

LLM client mendukung fallback ke mode mock jika API key tidak tersedia, sehingga agent tetap berfungsi untuk pengembangan.

---

## 🧪 Testing

Semua command telah diuji dalam sesi pengembangan:

```bash
# Test seluruh command
python main.py generate-social-post --topic "AI Marketing" --platform LinkedIn
python main.py analyze-keywords SEO content AI
python main.py plan-campaign "Test" --objective "Branding" --audience "General" --budget 1000
python main.py execute-campaign "Test"
python main.py add-lead "Test User" test@example.com Web
python main.py dashboard-view
python main.py run-skill social-media-skill generate_post "Topic" "Platform"
```

---

## 🛣️ Roadmap

### v0.1 (Current) ✅
- [x] CLI dasar (Click-based)
- [x] Content generation (social post, email)
- [x] Keyword analysis
- [x] Campaign management (plan + execute)
- [x] CRM (add lead)
- [x] Governance (budget cap, audit trace)
- [x] Dashboard
- [x] Skill system (dynamic loader)
- [x] 9Router LLM integration

### v0.2 (Planned)
- [ ] Ad copy generation (Google, Meta, TikTok)
- [ ] Campaign launch via platform API
- [ ] Lead scoring & segmentation
- [ ] Report generation (PDF, HTML)
- [ ] Skill wrapper — auto-select model per task
- [ ] Persistent database (SQLite)

### v0.3 (Future)
- [ ] Browser extension interface
- [ ] Multi-agent orchestration (ref: `agentkits-marketing`)
- [ ] Platform-specific audit (ref: `claude-ads`)
- [ ] MCP server integration (ref: `ads-mcp`)
- [ ] Web dashboard (React/Next.js)

---

## 🤝 Contributing

Silakan buka issue atau pull request. Untuk perubahan besar, buka issue terlebih dahulu.

---

## 📄 License

MIT License — see [LICENSE](LICENSE).

---

<p align="center">
  <sub>Built with ❤️ using <a href="https://hermes-agent.nousresearch.com" target="_blank">Hermes Agent</a></sub>
</p>
