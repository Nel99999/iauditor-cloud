# OpsPlatform - Operational Management System

## 🚀 Project Overview
A comprehensive operational management platform for inspections, tasks, checklists, and team collaboration. Built with FastAPI (Backend) and React (Frontend).

## 📂 Project Structure

```
project-root/
├── backend/                 # FastAPI backend application
├── frontend/                # React frontend application
├── docs/                    # Documentation
│   ├── api/                 # API guides & security
│   ├── architecture/        # System architecture docs
│   ├── design/              # Design system & component API
│   └── guides/              # User & developer guides
├── scripts/
│   └── tests/               # Core test suite
├── CURRENT_STATUS.md        # Latest project status
└── PHASE2_IMPLEMENTATION_GUIDE.md # PWA setup guide
```

## 🛠️ Quick Start

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python server.py
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## 🧪 Testing

Run the core backend test suite:
```bash
python scripts/tests/backend_test.py
```

## 📱 PWA Features
See [PHASE2_IMPLEMENTATION_GUIDE.md](PHASE2_IMPLEMENTATION_GUIDE.md) for PWA setup and offline capabilities.

## 📚 Documentation
- [API Keys & Security](docs/api/API_KEYS_SECURITY.md)
- [Architecture Overview](docs/architecture/OPERATIONAL_PLATFORM_ARCHITECTURE.md)
- [Testing Guide](docs/guides/TESTING_GUIDE.md)
