# 📖 User Guide

Complete guide for using the Money Changer application for daily operations.

## 🚀 Getting Started

### Accessing the Application
1. Open your web browser
2. Navigate to the application URL (e.g., http://localhost:8501)
3. Enter your username and password
4. Click "Login" to access the system

### First Login
- Use the credentials provided by your administrator
- Change your password immediately after first login (if required)
- Familiarize yourself with the dashboard and navigation

### Dashboard Overview
The main dashboard displays:
- Today's transaction summary
- Current inventory status
- Quick action buttons
- Recent activities
- Low stock alerts

## 🔐 User Roles and Permissions

### Admin
- **Full Access**: Can access all modules and features
- **User Management**: Create, edit, and deactivate user accounts
- **System Settings**: Configure exchange rates and system parameters
- **Reports**: Access to all reports and audit logs

### Kasir (Cashier)
- **Transaction Processing**: Create buy/sell transactions
- **Customer Management**: Add and edit customer information
- **Basic Reports**: View transaction history and basic summaries
- **Inventory View**: Check current stock levels (read-only)

### Auditor
- **Read-Only Access**: View all data without modification rights
- **Reports**: Access all financial and operational reports
- **Audit Logs**: Review complete activity history
- **Compliance**: Generate compliance and security reports

## 💱 Currency Management

### Viewing Exchange Rates
1. Navigate to **Master Data → Currencies**
2. View current buy and sell rates for all currencies
3. Check rate history and trend analysis
4. Review spread percentages

### Updating Exchange Rates (Admin Only)
1. Go to **Currencies → Quick Update**
2. Select currency from dropdown
3. Enter new buy and sell rates
4. Review calculated spread
5. Click "Update Rates" to save changes

### Adding New Currency (Admin Only)
1. Navigate to **Currencies → Add Currency**
2. Fill in currency information:
   - Currency Code (3-letter code, e.g., USD)
   - Currency Name (e.g., United States Dollar)
   - Symbol (e.g., $)
   - Initial Buy and Sell Rates
3. Click "Save Currency"

## 👥 Customer Management

### Adding New Customer
1. Go to **Master Data → Customers → Add Customer**
2. Fill in customer information:
   - Customer Code (auto-generated or manual)
   - Full Name (required)
   - Identity Number (optional)
   - Country (optional)
   - Phone Number (optional)
   - Email Address (optional)
   - Address (optional)
3. Click "Save Customer"

### Searching Customers
1. Navigate to **Customers → Search**
2. Type customer name, code, or ID number
3. View search results
4. Click on customer to view details or process transaction

### Viewing Customer Details
1. From customer list, click "View Details"
2. Review customer information
3. View transaction history
4. Edit customer information if needed

## 💸 Transaction Processing

### Processing Buy Transaction (Customer sells foreign currency to us)
1. Go to **Operations → New Transaction**
2. Select transaction type: **BUY**
3. Search and select customer:
   - Type customer name or code in search box
   - Select from search results
4. Select currency
5. Enter foreign currency amount
6. Review automatically calculated IDR amount
7. **Important**: Enter denomination breakdown:
   - Specify how many bills of each denomination
   - System validates total matches transaction amount
8. Add notes (optional)
9. Click "Process BUY Transaction"

### Processing Sell Transaction (We sell foreign currency to customer)
1. Follow steps 1-6 from buy transaction
2. Select transaction type: **SELL**
3. The system will check inventory availability
4. Enter denomination breakdown
5. Click "Process SELL Transaction"

### Transaction Receipt
After successful transaction:
- Receipt is automatically displayed
- Includes all transaction details
- Shows denomination breakdown
- Displays customer information
- Option to print or save receipt

### Transaction History
1. Navigate to **Operations → Transaction History**
2. Apply filters as needed:
   - Date range
   - Customer
   - Currency
   - Transaction type
3. View transaction list
4. Click on transaction for detailed receipt
5. Export data if needed

## 📊 Inventory Management

### Viewing Inventory Status
1. Go to **Operations → Stock Inventory**
2. View dashboard with:
   - Total inventory value
   - Low stock alerts
   - Currency-wise breakdown
3. Select specific currency to view denominations

### Checking Stock by Currency
1. From inventory dashboard, select currency
2. View available denominations and quantities
3. Check total value in IDR and foreign currency
4. Review last update times

### Stock Adjustment (Admin Only)
1. Navigate to **Inventory → Stock Adjustment**
2. Select currency and denomination
3. Choose adjustment type:
   - Add Stock (increase inventory)
   - Remove Stock (decrease inventory)
4. Enter quantity and reason
5. Confirm adjustment
6. System logs all adjustments for audit trail

### Low Stock Alerts
- Dashboard shows items with quantity ≤ 10
- Critical alerts for items ≤ 5
- Automatic notifications can be configured

## 📈 Reports and Analytics

### Executive Dashboard
1. Navigate to **Reports → Executive Dashboard**
2. View key performance indicators:
   - Total transactions and revenue
   - Currency performance
   - Customer analytics
   - Daily trends

### Financial Reports
1. Go to **Reports → Financial Reports**
2. Select report type:
   - **Profit & Loss**: Analyze profit by currency
   - **Transaction Analytics**: Detailed transaction analysis
   - **Customer Analytics**: Customer behavior insights
3. Set date range and filters
4. View interactive charts and tables
5. Export reports in CSV or Excel format

### Generating Custom Reports
1. Navigate to **Reports → Custom Reports**
2. Configure report parameters:
   - Report type
   - Date range
   - Filters and options
3. Click "Generate Custom Report"
4. Review generated report
5. Export or save as needed

## 🔍 Audit and Compliance

### Viewing Audit Logs
1. Go to **Reports → Audit Logs**
2. Apply filters:
   - Date range
   - User
   - Action type
   - Table/Entity
3. Review activity logs
4. Search for specific events
5. Export audit data

### Compliance Reports
1. Navigate to **Audit Logs → Compliance Reports**
2. Select report period
3. Generate reports for:
   - Authentication activities
   - Data modifications
   - Security incidents
   - User activities

## ⚙️ System Settings (Admin Only)

### User Management
1. Go to **Master Data → Users**
2. View all user accounts
3. Add new user:
   - Enter username and password
   - Assign role (Admin, Kasir, Auditor)
   - Set user details
4. Edit existing users:
   - Update user information
   - Change roles
   - Reset passwords
   - Activate/deactivate accounts

### System Configuration
- Session timeout settings
- Password policies
- Currency configurations
- Business rules and thresholds

## 🔧 Troubleshooting

### Common Issues

#### Login Problems
- **Forgot Password**: Contact administrator to reset
- **Account Locked**: Wait for timeout or contact admin
- **Wrong Credentials**: Check username and spelling

#### Transaction Issues
- **Insufficient Inventory**: Check stock levels before sell transactions
- **Invalid Amount**: Ensure positive numbers only
- **Customer Not Found**: Use search functionality or add new customer

#### Inventory Issues
- **Stock Mismatch**: Use stock adjustment with proper reason
- **Denomination Errors**: Ensure breakdown matches total amount
- **Negative Stock**: System prevents negative inventory

#### Performance Issues
- **Slow Loading**: Check internet connection
- **Data Not Loading**: Refresh page or check browser console
- **Report Generation**: Use smaller date ranges for large datasets

### Error Messages
- **"Authentication Required"**: Please login to access this feature
- **"Permission Denied"**: Your role doesn't have access to this feature
- **"Insufficient Inventory"**: Not enough stock for this transaction
- **"Invalid Data"**: Check entered values and try again

### Getting Help
1. **Check User Guide**: Review relevant sections
2. **Contact Administrator**: For system issues and account problems
3. **System Logs**: Administrators can check audit logs for detailed errors

## 📱 Best Practices

### Daily Operations
- **Start of Day**: Check inventory levels and exchange rates
- **During Day**: Process transactions efficiently with proper documentation
- **End of Day**: Review daily reports and reconcile transactions

### Customer Service
- **Professional Conduct**: Maintain professional behavior with all customers
- **Accuracy**: Double-check all amounts and calculations
- **Documentation**: Ensure all transactions are properly recorded

### Data Management
- **Regular Backups**: Administrators should perform regular database backups
- **Log Reviews**: Periodically review audit logs for unusual activities
- **Rate Updates**: Keep exchange rates updated regularly

### Security
- **Password Security**: Use strong passwords and change regularly
- **Session Management**: Logout when finished, especially on shared computers
- **Access Control**: Only access features relevant to your role

## 🎓 Training Tips

### New Cashiers
1. **Practice Transactions**: Use test mode or small amounts initially
2. **Currency Recognition**: Learn to identify different denominations
3. **Customer Interaction**: Practice professional customer service
4. **Error Handling**: Learn common error resolution steps

### New Administrators
1. **System Configuration**: Understand all system settings
2. **User Management**: Learn role-based access control
3. **Backup Procedures**: Master backup and restore processes
4. **Reporting**: Familiarize with all report types and features

## 📞 Support and Contacts

### For Technical Support
- **System Administrator**: [Contact Information]
- **IT Help Desk**: [Contact Information]
- **Software Provider**: [Contact Information]

### For Business Questions
- **Operations Manager**: [Contact Information]
- **Finance Department**: [Contact Information]
- **Compliance Officer**: [Contact Information]

### Training Resources
- **Online Training**: Available in the system help section
- **Video Tutorials**: Link to tutorial videos
- **User Manual**: This guide and additional documentation

---

*This guide covers all essential features of the Money Changer application. For specific questions or advanced features, consult your system administrator or refer to the technical documentation.*