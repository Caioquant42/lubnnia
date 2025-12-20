# Zomma Quant Documentation

Welcome to the Zomma Quant documentation! This folder contains all project documentation organized by area.

## Documentation Structure

```
docs/
├── frontend/              # Frontend-specific documentation
│   ├── ARCHITECTURE.md   # Frontend architecture overview
│   ├── CONTRIBUTING.md   # Contributing guide for frontend
│   ├── DEPLOYMENT.md     # Deployment instructions
│   ├── access-control.md # Access control implementation
│   └── ...
└── README.md             # This file
```

## Quick Links

### For New Team Members
1. Start with [Frontend Architecture](frontend/ARCHITECTURE.md) to understand the codebase structure
2. Read [Contributing Guide](frontend/CONTRIBUTING.md) for code standards and conventions
3. Review [Deployment Guide](frontend/DEPLOYMENT.md) for deployment procedures

### Common Topics

#### Frontend Development
- **Architecture Overview**: [frontend/ARCHITECTURE.md](frontend/ARCHITECTURE.md)
- **Contributing Guidelines**: [frontend/CONTRIBUTING.md](frontend/CONTRIBUTING.md)
- **Deployment**: [frontend/DEPLOYMENT.md](frontend/DEPLOYMENT.md)

#### Features & Components
- **Collar Strategy**: [frontend/COLLAR_APP_IMPROVEMENTS.md](frontend/COLLAR_APP_IMPROVEMENTS.md)
- **Dividend Calendar**: [frontend/DIVIDEND_CALENDAR_IMPROVEMENTS.md](frontend/DIVIDEND_CALENDAR_IMPROVEMENTS.md)
- **Dashboard Enhancements**: [frontend/Dashboard_Enhancement_Suggestions.md](frontend/Dashboard_Enhancement_Suggestions.md)

#### Authentication & Access
- **Username Authentication**: [frontend/username-authentication.md](frontend/username-authentication.md)
- **Access Control**: [frontend/access-control.md](frontend/access-control.md)

#### Integration
- **Stripe & Supabase**: [frontend/STRIPE_SUPABASE_INTEGRATION_DETAILED.md](frontend/STRIPE_SUPABASE_INTEGRATION_DETAILED.md)
- **Email Customization**: [frontend/SUPABASE_EMAIL_CUSTOMIZATION_GUIDE.md](frontend/SUPABASE_EMAIL_CUSTOMIZATION_GUIDE.md)

#### Implementation Guides
- **Phase 1 Guide**: [frontend/PHASE1_IMPLEMENTATION_GUIDE.md](frontend/PHASE1_IMPLEMENTATION_GUIDE.md)

#### Troubleshooting
- **Cookie/Caching Issues**: [frontend/COOKIE_CACHING_ISSUE_ANALYSIS.md](frontend/COOKIE_CACHING_ISSUE_ANALYSIS.md)
- **Browser Errors**: [frontend/webbrosererror.md](frontend/webbrosererror.md)

## Key Architectural Decisions

### Why Radix UI / shadcn/ui?
- Industry-standard component library
- Accessibility-first approach
- Full customization control
- Used by professional teams worldwide

### Why Next.js App Router?
- Modern React framework with SSR
- File-based routing with conventions
- Built-in optimization
- Seamless deployment

### Why Tailwind CSS?
- Utility-first CSS framework
- Consistent design system
- Optimized build output
- Developer productivity

## Project Structure

```
project-root/
├── backend/           # Python/Flask backend
├── frontend/          # Next.js frontend
├── supabase/          # Supabase functions and migrations
├── docs/             # Documentation (you are here)
└── README.md         # Project README
```

## Contributing

Before contributing to the project, please read:
1. [Frontend Contributing Guide](frontend/CONTRIBUTING.md)
2. [Frontend Architecture](frontend/ARCHITECTURE.md)

## Recent Refactoring (October 2024)

The frontend underwent a major refactoring to improve code quality and maintainability:

✅ **Completed:**
- Removed duplicate images and unused assets (~50+ files)
- Consolidated folder structure (docs and supabase at root)
- Added JSDoc comments to API services and hooks
- Created comprehensive architecture and contributing guides
- Updated config files with explanatory comments
- Standardized import paths using @ aliases

📊 **Results:**
- Cleaner codebase
- Better documentation
- Easier onboarding for new developers
- Improved maintainability

## Getting Help

- **Questions?** Ask the team
- **Found a bug?** Create an issue
- **Want to contribute?** Read the contributing guide

## Maintenance

This documentation should be updated as the project evolves. When making significant changes:

1. Update relevant documentation files
2. Keep the architecture guide current
3. Add new patterns to the contributing guide
4. Document breaking changes

---

**Last Updated**: October 2024  
**Maintained by**: Zomma Quant Team

