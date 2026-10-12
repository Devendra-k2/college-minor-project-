# 📧 English-to-Japanese Email Translator

> A college minor project that combines AI-powered email generation with neural machine translation — write a topic, get a polished professional email in Japanese, and send it instantly.

---

## 📖 Description

**English-to-Japanese Email Translator** is an end-to-end pipeline that:

1. **Generates** a professional English email from a short topic prompt using an NVIDIA-hosted large language model (Google DiffusionGemma 26B).
2. **Translates** the generated email from English to Japanese using a locally-run HuggingFace `facebook/nllb-200`-style seq2seq model.
3. **Sends** the final bilingual email (Japanese body + English reference) via SMTP with both plain-text and styled HTML formatting.

The entire pipeline is built with **LangChain**, making each stage composable and easy to extend.

---

## ✨ Features

- 🤖 **AI Email Generation** — Produces well-structured, professional emails from a single topic string using the NVIDIA AI API.
- 🌏 **Local Neural Translation** — Runs `facebook/nllb-200`-style translation entirely on-device (no third-party translation API needed).
- 📨 **SMTP Email Delivery** — Sends bilingual emails (Japanese primary + English reference) with both plain-text and styled HTML variants.
- 🔗 **LangChain Pipeline** — Each stage is a composable LangChain chain (`ChatPromptTemplate`, `ChatNVIDIA`, `RunnableLambda`).
- 🔒 **Secure Configuration** — API keys and SMTP credentials are loaded from a `.env` file and never hard-coded.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| LLM Backend | NVIDIA AI API · Google DiffusionGemma 26B |
| LLM Framework | LangChain (`langchain`, `langchain-nvidia-ai-endpoints`) |
| Translation Model | HuggingFace `facebook/nllb-200` architecture (local) |
| ML Runtime | PyTorch · `transformers` (`AutoModelForSeq2SeqLM`, `AutoTokenizer`) |
| Email Delivery | Python `smtplib` + `email.mime` |
| Configuration | `python-dotenv` |
| Language | Python 3.10+ |

---

## 📁 Project Structure

```
email translator/
├── email_trans/
│   ├── write_email.py      # Stage 1 — AI email generation (NVIDIA API + LangChain)
│   ├── translate.py        # Stage 2 — English → Japanese translation (local HuggingFace model)
│   └── email_sender.py     # Stage 3 — SMTP delivery (plain-text + HTML)
├── .env                    # 🔑 Secrets (not committed to version control)
├── .env.example            # Template for environment variables
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## 🚀 Usage

### 1 · Clone the Repository

```bash
git clone <your-repo-url>
cd "email translator"
```

### 2 · Install Dependencies

```bash
pip install -r requirements.txt
```

### 3 · Configure Environment Variables

Copy the example file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` (see [Configuration](#%EF%B8%8F-configuration) below).

### 4 · Generate an Email

```bash
python email_trans/write_email.py
```

When prompted (or by editing the `topic` variable), provide a topic such as:

```
"Request for project deadline extension due to technical issues"
```

The script prints the generated professional English email.

### 5 · Translate to Japanese

```bash
python email_trans/translate.py
```

Pipe the English email text into the translation chain. The script outputs the Japanese (`jpn_Jpan`) translation.

### 6 · Send the Email

```bash
python email_sender.py
```

The script sends a bilingual email to the configured recipient:

- **Primary body** — Japanese translation  
- **Reference section** — Original English text  
- Supports both **plain-text** and **styled HTML** (divs with inline CSS).

Returns a dict: `{"success": True, "message": "Email sent successfully"}`.

---

## ⚙️ Configuration

All sensitive values live in `.env`. Create this file in the project root:

```dotenv
# .env

# ── NVIDIA AI API ──────────────────────────────────────────
NVIDIA_API_KEY=nvapi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ── SMTP / Email ────────────────────────────────────────────
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-gmail-address@gmail.com
SMTP_PASSWORD=your-app-password          # Use a Gmail App Password, not your account password
EMAIL_RECIPIENT=recipient@example.com
```

> [!IMPORTANT]
> **Gmail users:** Enable 2-Step Verification and generate an **App Password** at  
> `Google Account → Security → App Passwords`.  
> Never use your main Gmail password here.

> [!CAUTION]
> Add `.env` to `.gitignore` before making your first commit to avoid leaking secrets.

### Local HuggingFace Model Path

In `translate.py`, update `MODEL_PATH` to point to your locally downloaded `nllb-200` model:

```python
MODEL_PATH = r"C:\path\to\your\nllb-200-model"   # Windows example
# MODEL_PATH = "/home/user/models/nllb-200"       # Linux / macOS example
```

---

## 📋 Requirements

```
langchain
langchain-nvidia-ai-endpoints
transformers
torch
sentencepiece
python-dotenv
```

Install everything at once:

```bash
pip install -r requirements.txt
```

> [!TIP]
> If you have a CUDA-capable GPU, install the GPU build of PyTorch for significantly faster translation:
> ```bash
> pip install torch --index-url https://download.pytorch.org/whl/cu121
> ```

---

## 🗺️ Pipeline Overview

```
User Topic Prompt
      │
      ▼
┌─────────────────────────────┐
│   write_email.py            │  ChatPromptTemplate + ChatNVIDIA (DiffusionGemma 26B)
│   → Professional English    │
│     email generated         │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│   translate.py              │  RunnableLambda + NLLB-200 (local PyTorch)
│   → Japanese translation    │  Target: jpn_Jpan
│     (jpn_Jpan)              │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│   email_sender.py           │  smtplib SMTP (gmail:587, STARTTLS)
│   → Bilingual email sent    │  Plain-text + HTML (styled divs)
└─────────────────────────────┘
```

---

## 📄 License

This project was developed as a **college minor project** for educational purposes.  
Feel free to study, adapt, and extend it.

```
MIT License — see LICENSE file for details (if included).
```

---

<p align="center">Made with ❤️ as a college minor project</p>
