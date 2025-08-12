# Simple Charity MVP - Misjonarze Parafia Świętej Rodziny

A simplified single-organization charity donation platform with QR code support and Fiserv/Polcard payment integration.

## Features

- Single organization (Misjonarze Parafia Świętej Rodziny - Tarnów)
- 3 charity goals with progress tracking
- QR code generation for each goal
- Fiserv/Polcard payment gateway integration
- Responsive design with Tarnów branding
- Polish language interface

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React + Vite + Tailwind CSS
- **Payment**: Fiserv/Polcard API
- **Storage**: JSON files (simplified MVP)

## Setup

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables in `.env`:
```
FISERV_API_KEY=your_api_key_here
FISERV_API_SECRET=your_api_secret_here
FISERV_BASE_URL=https://prod.emea.api.fiservapps.com/sandbox/exp/v1
FISERV_STORE_ID=your_store_id_here
WEBHOOK_BASE_URL=http://localhost:8000
FRONTEND_BASE_URL=http://localhost:5173
```

4. Run the backend:
```bash
python main.py
```

The backend will run on http://localhost:8000

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will run on http://localhost:5173

## Project Structure

```
simple-charity-mvp/
├── backend/
│   ├── app/
│   │   ├── data/           # JSON data storage
│   │   ├── routes/         # API endpoints
│   │   └── utils/          # Fiserv client
│   └── static/             # Static assets
└── frontend/
    ├── src/
    │   ├── pages/          # React pages
    │   ├── components/     # Reusable components
    │   └── assets/         # Tarnów design assets
    └── public/
```

## API Endpoints

- `GET /api/organization` - Get organization details
- `GET /api/organization/goal/{goal_id}` - Get specific goal
- `GET /api/organization/stats` - Get donation statistics
- `GET /api/organization/qr/{goal_id}` - Generate QR code
- `POST /api/payments/initiate` - Initialize payment
- `GET /api/payments/{payment_id}/status` - Check payment status
- `POST /api/webhooks/fiserv` - Fiserv webhook handler

## Charity Goals

1. **Ofiara na kościół** - Church donations
2. **Ofiara na ubogich** - Poor donations
3. **Ofiara za świeczki intencyjne** - Candle intentions

## Production Deployment

1. Update `.env` with production Fiserv credentials
2. Configure webhook URL in Fiserv dashboard
3. Update `FRONTEND_BASE_URL` and `WEBHOOK_BASE_URL`
4. Build frontend: `npm run build`
5. Deploy with proper SSL certificates

## License

Private - All rights reserved