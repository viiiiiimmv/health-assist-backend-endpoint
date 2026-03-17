# HealthAssist — Frontend

> Your personal AI health companion. Track symptoms, log moods, and get intelligent support.

[![React](https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat-square&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![Vercel](https://img.shields.io/badge/Vercel-000000?style=flat-square&logo=vercel&logoColor=white)](https://vercel.com/)

**Live Demo →** [health-assist-chatbot-viiiiiimmv.vercel.app](https://health-assist-chatbot-viiiiiimmv.vercel.app)  
**Backend Repo →** [health-assist-backend-endpoint](https://github.com/viiiiiimmv/health-assist-backend-endpoint)

---

## About

HealthAssist is an AI-powered health chatbot platform that helps users track symptoms, log daily moods, and interact with an NLP-driven assistant. This repository contains the frontend client — a responsive web application that communicates with the HealthAssist backend API.

---

## Features

- **AI Chat Interface** — Conversational UI for symptom queries and health guidance
- **Mood Journaling** — Log and visualise daily mood entries over time
- **Chat History** — Browse and revisit past conversations and health logs
- **Sentiment Feedback** — Visual indicators for daily mood classification results
- **Responsive Design** — Fully mobile-friendly layout
- **Session Management** — Persistent user sessions with secure API communication

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | React.js |
| Language | TypeScript |
| Build Tool | Vite |
| Styling | Tailwind CSS |
| HTTP Client | Axios |
| Deployment | Vercel |

---

## Project Structure

```
health-assist-frontend-service/
├── src/                  # Application source code
│   ├── components/       # Reusable UI components
│   ├── pages/            # Page-level components
│   ├── services/         # API call functions
│   └── hooks/            # Custom React hooks
├── public/               # Static assets
├── index.html            # HTML entry point
├── vite.config.ts        # Vite configuration
├── tailwind.config.js    # Tailwind CSS configuration
├── tsconfig.json         # TypeScript configuration
└── package.json
```

---

## Getting Started

### Prerequisites
- Node.js 16+
- HealthAssist backend running locally or deployed

### Installation

```bash
# Clone the repository
git clone https://github.com/viiiiiimmv/health-assist-frontend-service.git
cd health-assist-frontend-service

# Install dependencies
npm install
```

### Environment Variables

Create a `.env` file in the root:

```env
VITE_API_URL=http://localhost:5000
```

For production, replace with your Render backend URL.

### Run Locally

```bash
npm start
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

> Make sure the backend server is running before starting the frontend.

---

## Deployment

Frontend is deployed on **Vercel**. To deploy your own instance:

1. Fork this repository
2. Connect to [Vercel](https://vercel.com)
3. Set `REACT_APP_API_URL` to your Render backend URL in Vercel environment variables
4. Deploy

---

## Related

- **Backend API** → [health-assist-backend-endpoint](https://github.com/viiiiiimmv/health-assist-backend-endpoint)

---

## Author

**Shiv Chauhan**

[![Portfolio](https://img.shields.io/badge/Portfolio-000000?style=flat-square&logo=vercel&logoColor=white)](https://shivchauhan835.netlify.app)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://linkedin.com/in/shivchauhan)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/viiiiiimmv)

---

## License

This project is open source and available under the [MIT License](LICENSE).
