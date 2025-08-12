# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains two charity donation platforms:
1. **Main Project** (root): Simple single-organization platform for Misjonarze Parafia Świętej Rodziny in Tarnów
2. **Advanced Project** (`bramka-platnicza-mvp-qr/`): Multi-organization platform with admin panel and authentication

## Essential Commands

### Main Project
```bash
# Backend (FastAPI on port 8000)
cd backend
pip install -r requirements.txt
python main.py

# Frontend (React/Vite on port 5173)
cd frontend
npm install
npm run dev
npm run build
npm run preview
```

### Advanced Project (bramka-platnicza-mvp-qr)
```bash
# Docker (Recommended)
docker-compose up --build

# Manual Backend (port 8000)
cd bramka-platnicza-mvp-qr/backend
pip install -r requirements.txt
python main.py

# Manual Frontend (port 5174)
cd bramka-platnicza-mvp-qr/frontend
npm install
npm run dev
npm run lint
npm run build
```

## Architecture & Key Patterns

### Payment Gateway Integration (Fiserv/Polcard)
- **Store ID**: 760995999 (test environment)
- **Shared Secret**: `j}2W3P)Lwv` (from working test implementation)
- **Hash Algorithm**: HMACSHA256
- **Timezone**: Europe/Warsaw (critical for hash validation)
- **Gateway URL**: `https://test.ipg-online.com/connect/gateway/processing`

### Working Payment Hash Generation
The correct hash generation follows this exact pattern (verified in payment-tester/test.html):
1. Sort all parameters alphabetically by key
2. Join values with pipe separator (|)
3. Generate HMAC-SHA256 with shared secret
4. Encode as Base64

### API Structure
- **Organization Endpoints**: `/api/organization/*` - charity details, goals, stats
- **Payment Endpoints**: `/api/payments/*` - initiate, status check
- **Webhook Handler**: `/api/webhooks/fiserv` - payment confirmations
- **QR Generation**: `/api/organization/qr/{goal_id}` - dynamic QR codes

### Frontend Architecture
- React 18/19 with functional components and hooks
- Vite for development and building
- Tailwind CSS for styling (v3 main, v4 advanced)
- Context API for state management (Auth, Language)
- Mobile-first responsive design

### Data Storage
- File-based JSON storage in `app/data/`:
  - `organization.json` - charity configuration
  - `payments.json` - transaction records
  - `users.json` (advanced project only)

### CORS Configuration
Allows: `http://localhost:5173`, `http://localhost:5174`, `http://localhost:8000`, wildcard for development

## Critical Implementation Details

### Payment Flow
1. User selects donation goal (QR or direct)
2. Frontend calls `/api/payments/initiate`
3. Backend generates payment hash and form data
4. User redirected to Fiserv gateway
5. Fiserv processes payment and sends webhook
6. Backend updates payment status
7. User redirected to success/failure page

### Charity Goals (Main Project)
- `goal_1`: Ofiara na kościół (Church donations)
- `goal_2`: Ofiara na ubogich (Poor donations)
- `goal_3`: Ofiara za świeczki intencyjne (Candle intentions)

### Required Environment Variables
```bash
FISERV_API_KEY=your_api_key
FISERV_API_SECRET=your_api_secret
FISERV_STORE_ID=760995999
WEBHOOK_BASE_URL=http://localhost:8000
FRONTEND_BASE_URL=http://localhost:5173
```

### Testing Resources
- Extensive test files in `backend/test_*.py` and `backend/test_*.html`
- Working reference implementation: `/Users/wojciechwiesner/ai/payment-tester/test.html`
- Test cards documented in `backend/FISERV_TEST_CARDS.md`

## Development Guidelines

### When Working with Payments
- Always use Europe/Warsaw timezone for datetime generation
- Verify hash generation matches the working pattern from test.html
- Test with both card and BLIK payment methods
- Check webhook handling for payment confirmation

### Frontend Development
- Maintain mobile-first approach
- Use existing Tarnów branding assets in `static/` directories
- Follow React functional component patterns
- Leverage existing Tailwind utility classes

### Backend Development
- Follow FastAPI async patterns
- Update JSON files atomically to prevent corruption
- Log all payment transactions for debugging
- Handle Fiserv webhook responses correctly

### Multi-Organization Features (Advanced Project)
- JWT authentication required for protected endpoints
- Role-based access: admin, organization, user
- Organization approval workflow through admin panel
- Logo upload functionality in `static/uploads/logos/`