# Verityn AI Frontend

Next.js frontend for the Verityn AI application with audit-focused design and API integration.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation
```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── app/                 # Next.js App Router pages
│   ├── components/          # Reusable React components
│   ├── hooks/              # Custom React hooks
│   ├── lib/                # API client and utilities
│   ├── types/              # TypeScript type definitions
│   └── utils/              # Helper functions
├── public/                 # Static assets
├── package.json           # Dependencies and scripts
├── next.config.ts         # Next.js configuration
├── tailwind.config.js     # Tailwind CSS configuration
└── tsconfig.json          # TypeScript configuration
```

## 🔧 Development

### Available Scripts
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

### API Integration
The frontend communicates with the FastAPI backend through:
- **API Client**: `src/lib/api.ts` - Axios-based HTTP client
- **React Hooks**: `src/hooks/useApi.ts` - Custom hooks for API calls
- **TypeScript Types**: `src/types/api.ts` - Type definitions for API responses

### Key Features
- **Document Upload**: Drag-and-drop file upload with progress tracking
- **Chat Interface**: Real-time chat with document analysis
- **Compliance Dashboard**: Risk metrics and compliance insights
- **Question Suggestions**: AI-powered question recommendations
- **Responsive Design**: Mobile-friendly audit-focused interface

## 🎨 Design System

### Color Palette
- **Primary**: Blue tones for trust and professionalism
- **Success**: Green for compliance and positive metrics
- **Warning**: Orange for medium-risk items
- **Danger**: Red for high-risk findings

### Components
- Audit-focused UI components
- Professional enterprise design
- Accessibility compliant
- Mobile responsive

## 🔌 API Endpoints

The frontend integrates with these FastAPI endpoints:
- `POST /documents/upload` - Document upload and processing
- `POST /chat/message` - Send chat messages
- `POST /chat/suggestions` - Get question suggestions
- `GET /health` - Health check
- `GET /documents` - List documents
- `DELETE /documents/{id}` - Delete document

## 🚀 Deployment

### Vercel (Recommended)
```bash
# Deploy to Vercel
vercel --prod
```

### Environment Variables
Set these environment variables for production:
- `NEXT_PUBLIC_API_URL` - Backend API URL

## 📱 Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🔒 Security
- API keys stored securely
- CORS configured for backend communication
- Input validation and sanitization
- HTTPS enforcement in production 