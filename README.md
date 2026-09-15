# HiveXchange

HiveXchange is a behavior-adaptive web honeypot designed as a realistic digital asset trading platform.

It combines deception, behavioral monitoring, synthetic user flows, and defender-side telemetry to study suspicious authentication and probing behavior in a controlled environment.

## Features

- behavior-based risk assessment
- adaptive deception
- synthetic normal and decoy user flows
- endpoint and probe monitoring
- visitor state tracking
- risk decay
- attacker activity logging
- separate defender console
- synthetic wallet and portfolio environment
- SQLite-based telemetry

## Tech Stack

**Backend**
- Python
- Flask
- SQLite
- Jinja2
- python-dotenv

**Frontend**
- HTML
- CSS
- Vanilla JavaScript
- Chart.js

## Project Structure

```text
HiveXchange/
├── app.py
├── monitor.py
├── config.py
├── services/
├── database/
├── templates/
├── static/
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

```bash
git clone <your-repository-url>
cd HiveXchange
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Create a local `.env` file using `.env.example`, then run:

```bash
python app.py
```

For the defender console:

```bash
python monitor.py
```

## Status

HiveXchange is an evolving personal cybersecurity project focused on adaptive deception, behavioral monitoring, and defender-side telemetry.

## Disclaimer

This project is intended for cybersecurity education, experimentation, and controlled environments only.