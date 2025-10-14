# v2.0 Operational Management Platform

A modern, mobile-first operational management platform with comprehensive role-based access control, workflow management, and real-time collaboration features.

## 🎯 Overview

The v2.0 Operational Management Platform is designed as a secure, flexible system for operational workflows. It features a beautiful, token-driven design system with glassmorphism effects, dark mode support, and mobile-optimized components.

## ✨ Features

### Core Functionality
- **Role & User Management**: 10 system roles with granular permissions
- **Task Management**: Complete task lifecycle with priorities, assignments, and tracking
- **Inspections**: Template-based inspections with photo uploads and scoring
- **Checklists**: Dynamic checklist templates and execution tracking
- **Workflow Engine**: Approval workflows with delegation and audit trails
- **Organization Structure**: 5-level hierarchical organization management
- **Reports & Analytics**: Comprehensive analytics dashboard with trends and insights

### Modern UI/UX
- **Design System**: Token-driven components with Style Dictionary
- **Glassmorphism**: Modern glass effects throughout the interface
- **Dark Mode First**: Seamless theme switching with system preference detection
- **Mobile-Optimized**: 
  - Bottom Sheets for mobile modals
  - FAB (Floating Action Button) for quick actions
  - Adaptive navigation (Bottom Nav → Nav Rail → Sidebar)
  - Gesture support with swipe interactions
- **Responsive Design**: Works perfectly on mobile, tablet, and desktop

### Security & Integration
- **Multi-Factor Authentication (MFA)**: Enhanced security with 2FA
- **API Rate Limiting**: Protection against abuse
- **SendGrid Integration**: Email notifications and invitations
- **Twilio Integration**: SMS/WhatsApp notifications
- **Webhook Support**: Real-time event notifications
- **GDPR Compliance**: Data privacy features

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and Yarn
- Python 3.9+
- MongoDB 5.0+

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd operational-management-platform

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
yarn install

# Build design tokens
yarn tokens:build
```

### Running the Application

```bash
# Start backend (from /backend)
uvicorn server:app --reload --host 0.0.0.0 --port 8001

# Start frontend (from /frontend)
yarn start

# Start Storybook (from /frontend)
yarn storybook
```

The application will be available at:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8001`
- Storybook: `http://localhost:6006`

## 📚 Documentation

- **[Design System Guide](./DESIGN_SYSTEM_GUIDE.md)** - Complete design system documentation
- **[Component API Reference](./COMPONENT_API.md)** - API docs for all components
- **[Mobile UX Guide](./MOBILE_UX_GUIDE.md)** - Mobile UX patterns and best practices
- **[TypeScript Migration Guide](./TYPESCRIPT_MIGRATION_GUIDE.md)** - TypeScript adoption guide
- **[Testing Guide](./TESTING_GUIDE.md)** - Visual regression and testing strategies

## 🎨 Design System

### Components

The platform includes a comprehensive set of modern components:

- **Button**: Multiple variants (primary, secondary, ghost, danger)
- **Card & GlassCard**: Regular and glassmorphism cards
- **Input**: Form inputs with icons and validation
- **BottomSheet**: Mobile-optimized modals with gesture support
- **FAB**: Floating action button with speed dial
- **ModernTable**: Responsive data tables
- **Toast**: Notification system
- **Spinner**: Loading indicators
- **Navigation**: Adaptive navigation components

### Design Tokens

All styling is based on design tokens:

```css
--color-primary
--color-secondary
--spacing-md
--font-size-base
--radius-lg
```

Modify tokens in `/frontend/src/design-system/tokens/tokens.json` and rebuild.

## 📱 Mobile Features

### Bottom Sheets

Mobile-optimized modals that slide from the bottom:

```jsx
import { BottomSheet, useBottomSheet } from '@/design-system/components';

const { isOpen, open, close } = useBottomSheet();

<BottomSheet isOpen={isOpen} onClose={close} title="Details" snapPoint="half">
  <Content />
</BottomSheet>
```

**Snap Points**: peek (25%), half (50%), full (90%)

### FAB (Floating Action Button)

```jsx
import { FAB, FABIcons } from '@/design-system/components';

// Simple FAB
<FAB icon={<FABIcons.Plus />} onClick={create} />

// Speed Dial
<FAB
  variant="speedDial"
  actions={[
    { icon: <FABIcons.Task />, label: 'New Task', onClick: createTask },
    { icon: <FABIcons.Inspection />, label: 'New Inspection', onClick: createInspection },
  ]}
/>
```

### Gesture Support

All mobile components support touch gestures:
- Swipe down to close bottom sheets
- Swipe up to expand
- Pull to refresh (where applicable)
- Tap outside to dismiss

## 🧪 Testing

### Visual Regression Testing

```bash
cd frontend
yarn test:visual              # Run visual tests
yarn test:visual:update       # Update baselines
yarn test:visual:report       # View report
```

### Backend Testing

```bash
cd backend
pytest tests/
```

## 🏗️ Tech Stack

### Frontend
- **React 19**: Latest React with concurrent features
- **Style Dictionary**: Token-driven design system
- **Framer Motion**: Smooth animations
- **react-swipeable**: Gesture support
- **Storybook**: Component development and documentation
- **Playwright**: Visual regression testing
- **TypeScript**: (In progress) Type-safe codebase

### Backend
- **FastAPI**: Modern Python web framework
- **MongoDB**: NoSQL database
- **Motor**: Async MongoDB driver
- **JWT**: Authentication tokens
- **Pydantic**: Data validation

## 📦 Project Structure

```
├── backend/
│   ├── server.py              # Main FastAPI application
│   ├── models.py              # Database models
│   ├── auth_routes.py         # Authentication routes
│   ├── task_routes.py         # Task management
│   ├── workflow_engine.py     # Workflow system
│   └── ...
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── design-system/     # Design system components
│   │   │   ├── components/    # Reusable components
│   │   │   ├── tokens/        # Design tokens
│   │   │   └── hooks/         # Custom hooks
│   │   ├── contexts/          # React contexts
│   │   └── routing/           # Route configuration
│   ├── public/                # Static assets
│   └── .storybook/            # Storybook configuration
└── tests/                     # Test files
```

## 🔐 Environment Variables

### Backend (.env)
```
MONGO_URL=mongodb://localhost:27017/operational_mgmt
JWT_SECRET=your-secret-key
SENDGRID_API_KEY=your-sendgrid-key
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
```

### Frontend (.env)
```
REACT_APP_BACKEND_URL=http://localhost:8001
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and test thoroughly
4. Update documentation if needed
5. Commit with clear messages: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Development Guidelines

- Use design tokens instead of hardcoded values
- Write Storybook stories for new components
- Add JSDoc comments
- Ensure mobile responsiveness
- Test on real devices
- Follow accessibility best practices

## 📄 License

Copyright © 2025. All rights reserved.

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Check the documentation
- Visit Storybook for component examples

## 🎉 Recent Updates

### v2.0 (Latest)
- ✅ Complete UI/UX overhaul with modern design system
- ✅ Bottom Sheets component with gesture support
- ✅ FAB (Floating Action Button) component
- ✅ Storybook setup with 20+ stories
- ✅ Comprehensive documentation
- ✅ Mobile-optimized navigation
- ✅ Visual regression testing setup
- 🔄 TypeScript migration (in progress)

### Key Features
- **Glassmorphism Effects**: Modern glass UI throughout
- **Dark Mode First**: Automatic theme detection and switching
- **Gesture Support**: Swipe interactions on mobile
- **Token-Driven Design**: Consistent design language
- **Adaptive Navigation**: Responsive nav for all screen sizes

---

**Made with ❤️ using React, FastAPI, and MongoDB**
