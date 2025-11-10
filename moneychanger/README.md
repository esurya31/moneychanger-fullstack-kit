# 🏦 Money Changer Application

A comprehensive foreign exchange management system built with Streamlit, featuring multi-role access control, real-time inventory tracking, transaction processing, and complete audit trails.

## ✨ Features

### 💱 Core Features
- **Multi-Currency Support**: Manage 10+ major foreign currencies with real-time rate updates
- **Transaction Processing**: Complete buy/sell transaction workflow with denomination tracking
- **Real-time Inventory**: Automated stock management with low stock alerts
- **Customer Management**: Comprehensive customer database with search capabilities
- **Exchange Rate Management**: Dynamic rate updates with historical tracking

### 👥 Multi-Role Access Control
- **Admin**: Full system access including user management and settings
- **Kasir (Cashier)**: Transaction processing and basic reporting
- **Auditor**: Read-only access for compliance and auditing

### 📊 Business Intelligence
- **Executive Dashboard**: Real-time metrics and KPIs
- **Financial Reports**: Profit & Loss, transaction analytics, customer insights
- **Custom Reports**: Flexible report builder with export capabilities
- **Audit Trail**: Complete activity logging with compliance reporting

### 🔐 Security & Compliance
- **Session Management**: Secure authentication with configurable timeouts
- **Audit Logs**: Comprehensive activity tracking for all user actions
- **Role-Based Permissions**: Granular access control by user role
- **Data Integrity**: Transaction-based database operations

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd moneychanger
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
streamlit run app.py
```

4. **Access the application**
Open your web browser and navigate to `http://localhost:8501`

### Default Login Credentials
For demonstration purposes, the application comes with pre-configured users:

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Kasir | cashier1 | cashier123 |
| Auditor | auditor1 | auditor123 |

## 📁 Project Structure

```
moneychanger/
├── app.py                          # Main application entry point
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── database/                       # Database layer
│   ├── schema.py                   # Database schema definition
│   ├── models.py                   # Database models and operations
│   └── seed_data.py                # Sample data generation
├── modules/                        # Feature modules
│   ├── currencies.py               # Currency management
│   ├── customers.py                # Customer management
│   ├── users.py                    # User management
│   ├── transactions.py             # Transaction processing
│   ├── inventory.py                # Inventory management
│   ├── reports.py                  # Reporting system
│   └── audit_logs.py               # Audit trail
├── utils/                          # Utility functions
│   ├── auth.py                     # Authentication & authorization
│   └── helpers.py                  # Helper functions
├── pages/                          # Streamlit pages
│   ├── 1_💱_Currencies.py
│   ├── 2_👥_Customers.py
│   ├── 3_👤_Users.py
│   ├── 4_💸_Transactions.py
│   ├── 5_📜_Transaction_History.py
│   ├── 6_📊_Stock_Inventory.py
│   ├── 7_📊_Reports.py
│   └── 8_🔍_Audit_Logs.py
└── data/                           # Database files (auto-created)
    └── moneychanger.db             # SQLite database
```

## 🏗️ Architecture

### Database Schema
The application uses SQLite with the following main entities:

- **Users**: Multi-role user management
- **Currencies**: Foreign currency definitions with exchange rates
- **Customers**: Customer information and records
- **Transactions**: Buy/sell transactions with full audit trail
- **Denomination Inventory**: Stock management by currency and denomination
- **Audit Logs**: Comprehensive activity tracking

### Authentication System
- **Session-based**: Secure session management with configurable timeouts
- **Role-based**: Granular permissions by user role
- **Password Security**: Salted hash password storage
- **Audit Logging**: Automatic logging of all authentication events

### Transaction Flow
1. **Customer Selection**: Search or select existing customer
2. **Currency & Amount**: Choose currency and enter amount
3. **Rate Calculation**: Automatic calculation based on buy/sell rates
4. **Denomination Breakdown**: Specify bill denominations for inventory tracking
5. **Confirmation**: Review and confirm transaction
6. **Processing**: Atomic database update with inventory adjustment
7. **Receipt Generation**: Digital receipt with full transaction details

## 📱 User Interface

### Dashboard
- Real-time transaction metrics
- Inventory status and alerts
- Recent activity overview
- Quick action buttons

### Module Navigation
- **Master Data**: Currencies, Customers, Users
- **Operations**: Transactions, Inventory
- **Reports**: Business Analytics, Audit Logs
- **Settings**: User preferences (Admin only)

### Responsive Design
- Mobile-friendly interface
- Adaptive layouts for different screen sizes
- Consistent design language across modules

## 🛠️ Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
DEBUG=false
LOG_LEVEL=INFO
SESSION_TIMEOUT_HOURS=8
DATABASE_PATH=./data/moneychanger.db
```

### Customization
Edit `config.py` to modify:
- Supported currencies
- Business rules and thresholds
- User roles and permissions
- UI/UX settings
- Security configurations

## 📊 Features in Detail

### Currency Management
- **Rate Updates**: Real-time buy/sell rate management
- **Historical Tracking**: Complete rate change history
- **Spread Analysis**: Automated spread calculation and analysis
- **Multi-currency Support**: 10+ major currencies pre-configured

### Transaction Processing
- **Buy Operations**: Purchase foreign currency from customers
- **Sell Operations**: Sell foreign currency to customers
- **Denomination Tracking**: Detailed bill denomination management
- **Automatic Calculations**: Real-time IDR amount calculation
- **Receipt Generation**: Digital receipts with QR codes (future feature)

### Inventory Management
- **Real-time Tracking**: Live inventory status by denomination
- **Low Stock Alerts**: Automated alerts for inventory thresholds
- **Stock Adjustments**: Manual stock adjustment with audit trail
- **Valuation Reporting**: Inventory value in IDR and foreign currencies

### Reporting System
- **Executive Dashboard**: High-level business metrics
- **Financial Reports**: P&L, revenue analysis, transaction trends
- **Customer Analytics**: Customer behavior and transaction patterns
- **Custom Reports**: Flexible report builder with filters
- **Export Capabilities**: CSV, Excel, PDF export options

### Audit Trail
- **Complete Logging**: All user actions and data changes
- **Compliance Reports**: Security and compliance reporting
- **Search & Filter**: Advanced log search capabilities
- **Activity Analysis**: User activity patterns and trends

## 🔒 Security Features

### Authentication
- **Secure Login**: Password-based authentication with session management
- **Role-Based Access**: Granular permissions by user role
- **Session Security**: Configurable session timeouts and automatic logout
- **Password Policies**: Minimum password length and complexity requirements

### Data Protection
- **Input Validation**: Comprehensive input validation and sanitization
- **SQL Injection Prevention**: Parameterized queries for database operations
- **Audit Logging**: Complete audit trail for all data modifications
- **Error Handling**: Secure error handling without information disclosure

## 🔧 Development

### Adding New Features
1. **Database**: Update schema in `database/schema.py`
2. **Models**: Add data access methods in `database/models.py`
3. **Business Logic**: Implement in appropriate `modules/` file
4. **UI**: Create new page in `pages/` or update existing module
5. **Permissions**: Add to role definitions in `config.py`

### Testing
```bash
# Run unit tests (when implemented)
python -m pytest tests/

# Run with specific configuration
DEBUG=true streamlit run app.py
```

### Deployment
The application can be deployed on:
- **Streamlit Cloud**: Direct deployment from GitHub
- **Docker**: Containerized deployment
- **VPS/Cloud**: Traditional server deployment with reverse proxy

## 📈 Performance Optimization

### Database Optimization
- **Indexing**: Optimized indexes for frequent queries
- **Connection Pooling**: Efficient database connection management
- **Query Optimization**: Optimized SQL queries for performance

### Caching
- **Session Caching**: Streamlit session state for performance
- **Data Caching**: Cached data for frequently accessed information
- **UI Caching**: Cached UI components for faster rendering

## 🐛 Troubleshooting

### Common Issues

**Database Connection Errors**
- Ensure write permissions to the `data/` directory
- Check if SQLite is properly installed
- Verify database file exists and is accessible

**Login Issues**
- Verify default credentials are correct
- Check database initialization completed successfully
- Ensure user accounts are active in the database

**Performance Issues**
- Check database size and consider optimization
- Verify sufficient system resources
- Review logs for performance bottlenecks

### Logging
Application logs are written to the console. Check the terminal output for detailed error information.

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make changes with appropriate testing
4. Submit a pull request with detailed description

### Code Standards
- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add appropriate comments and docstrings
- Ensure all database operations are transactional

## 📞 Support

For issues and questions:
1. Check this README for common solutions
2. Review the issue tracker on GitHub
3. Create a new issue with detailed information
4. Include error messages and system information

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

## 🗺️ Roadmap

### Version 2.0 Features (Planned)
- **API Integration**: External exchange rate APIs
- **QRIS Payments**: Indonesian QR code payment integration
- **Multi-Branch**: Multi-location support
- **Mobile App**: React Native mobile application
- **Advanced Analytics**: AI-powered business insights
- **Email Notifications**: Automated email reports and alerts

### Version 1.1 Features (In Progress)
- **Backup & Restore**: Automated database backup
- **Import/Export**: Bulk data import and export
- **Advanced Search**: Enhanced search capabilities
- **Dashboard Widgets**: Customizable dashboard components

---

**Money Changer Application** - Complete Foreign Exchange Management System

Built with ❤️ using Streamlit