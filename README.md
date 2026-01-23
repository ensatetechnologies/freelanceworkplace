# Freelance Marketplace

A full-featured freelance marketplace web application built with Django 5.0 and MySQL.

## Features

- **User Authentication**: Email-based registration, login, and profile management
- **Dual User Roles**: Freelancers and Clients with role-specific features
- **Project Management**: Create, browse, and manage projects with advanced filtering
- **Proposal System**: Freelancers can submit proposals, clients can review and accept
- **Contract Management**: Milestone-based contracts with deliverable tracking
- **Messaging System**: Real-time-like chat between users (polling-based)
- **Payment System**: Simulated escrow-based payment gateway
- **Review System**: Two-way review system after contract completion
- **Notifications**: In-app notification system
- **Admin Dashboard**: Comprehensive admin panel for platform management

## Tech Stack

- **Backend**: Python 3.11+, Django 5.0
- **Database**: MySQL 8.0
- **Frontend**: Bootstrap 5, JavaScript
- **Authentication**: Django Allauth

## Quick Start

### Prerequisites

- Python 3.11 or higher
- MySQL 8.0
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   cd FreelanceMarketPlace
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy the example env file
   copy env.example .env  # Windows
   cp env.example .env    # macOS/Linux
   
   # Edit .env with your settings
   ```

5. **Create MySQL Database**
   ```sql
   CREATE DATABASE freelance_marketplace CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

6. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Load initial data**
   ```bash
   python manage.py loaddata fixtures/initial_data.json
   ```

8. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

9. **Run the development server**
   ```bash
   python manage.py runserver
   ```

10. **Access the application**
    - Main site: http://localhost:8000
    - Admin panel: http://localhost:8000/admin
    - Admin Dashboard: http://localhost:8000/dashboard

## Using SQLite (Alternative)

If you prefer SQLite for easier setup, edit `config/settings/development.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

## Project Structure

```
freelance_marketplace/
├── apps/                    # Django applications
│   ├── accounts/           # User management
│   ├── projects/           # Project management
│   ├── proposals/          # Bidding system
│   ├── contracts/          # Contract management
│   ├── messaging/          # Chat system
│   ├── payments/           # Payment processing (simulated)
│   ├── reviews/            # Review system
│   ├── notifications/      # Notification system
│   ├── admin_dashboard/    # Admin panel
│   └── core/               # Shared utilities
├── config/                  # Project configuration
│   ├── settings/           # Settings files
│   └── urls.py             # URL configuration
├── templates/               # HTML templates
├── static/                  # Static files (CSS, JS)
├── fixtures/                # Initial data
└── media/                   # User uploads
```

## User Roles

### Freelancer
- Browse and apply to projects
- Submit proposals with cover letters
- Manage contracts and milestones
- Upload deliverables
- Receive payments (simulated)
- View earnings and wallet

### Client
- Post projects with requirements
- Review freelancer proposals
- Accept/reject proposals
- Manage contracts
- Fund escrow and release payments (simulated)
- Leave reviews

### Admin
- Access admin dashboard
- Manage users, projects, and contracts
- Process withdrawal requests
- View platform analytics

## Payment System (Simulated)

The payment system is fully simulated for local development:

- **Escrow Funding**: Clients can fund project escrow accounts
- **Milestone Payments**: Release payments upon milestone approval
- **Platform Fee**: 10% fee on all transactions
- **Withdrawals**: Freelancers can request withdrawals from their wallet

No real money is transferred - all transactions are simulated.

## API Endpoints

The application includes REST API endpoints under `/api/v1/`:

- `/api/v1/auth/` - Authentication endpoints
- `/api/v1/projects/` - Project management
- `/api/v1/proposals/` - Proposal management
- `/api/v1/contracts/` - Contract management
- `/api/v1/messages/` - Messaging
- `/api/v1/payments/` - Payment operations
- `/api/v1/reviews/` - Reviews
- `/api/v1/notifications/` - Notifications

## Development

### Running Tests
```bash
python manage.py test
```

### Code Style
The project follows PEP 8 guidelines. Use the following tools:
```bash
# Format code
black .

# Sort imports
isort .

# Check style
flake8 .
```

## Configuration

Key settings in `.env`:

```env
DEBUG=1
SECRET_KEY=your-secret-key
DB_NAME=freelance_marketplace
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is for educational purposes.

## Support

For issues and feature requests, please create an issue in the repository.
