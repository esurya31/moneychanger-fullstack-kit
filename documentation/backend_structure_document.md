# Backend Structure Document for moneychanger-fullstack-kit

This document outlines the backend setup for the moneychanger-fullstack-kit. It covers the overall architecture, database choices, API design, hosting, security, and more. You don’t need a deep technical background to follow along—it’s written in everyday language.

## 1. Backend Architecture

**Overview**
- We use Next.js API Routes to handle all server-side logic. That means our backend lives alongside our frontend in one codebase.  
- Authentication is powered by Better Auth, which plugs smoothly into Next.js.  
- Drizzle ORM connects our API routes to a PostgreSQL database in a type-safe way.

**Key design patterns and frameworks**
- **Serverless functions:** Each API route in Next.js acts like a small serverless function.  
- **ORM (Object-Relational Mapping):** Drizzle ORM maps JavaScript/TypeScript code to SQL statements, reducing manual SQL and preventing type mismatches.  
- **Modular folder structure:**  
  • `/app/api` for API code  
  • `/db/schema` for database definitions  
  • `/lib` for helper utilities  
  • `/components` for shared UI building blocks

**Scalability, maintainability, performance**
- **Scalability:** Next.js functions can scale horizontally: if traffic increases, the hosting platform (e.g., Vercel or AWS Lambda) spins up more instances.  
- **Maintainability:** Clear separation of concerns—database schemas, utility functions, and API logic live in dedicated folders.  
- **Performance:** Serverless functions start quickly on demand. Database queries run via Drizzle’s optimized queries.

## 2. Database Management

**Database technology**
- Type: Relational (SQL)  
- System: PostgreSQL

**How data is structured, stored, and accessed**
- Tables for currencies, customers, transactions, inventory denominations, audit logs, and users.  
- Drizzle ORM defines these schemas in TypeScript and translates them to SQL automatically.  
- Querying: API routes call Drizzle’s query methods (`db.insert`, `db.select`, etc.) to read or write data.

**Data management practices**
- **Migrations:** Any changes to schema are tracked and applied via migration scripts.  
- **Transactions:** Critical operations (like recording a transaction and updating inventory) run inside database transactions to keep data consistent.  
- **Backups:** Regular backups of the PostgreSQL database ensure you can restore data in case of a failure.

## 3. Database Schema

Below is a human-readable description of each table, followed by SQL definitions.

Currencies:
- code: unique currency code (e.g., USD)
- name: full name of the currency (e.g., US Dollar)
- rate_beli: buy rate (how much IDR to pay when buying foreign currency)
- rate_jual: sell rate (how much IDR to charge when selling foreign currency)

Customers:
- id: unique customer identifier
- name: customer’s full name
- identity_number: ID or passport number
- country: customer’s country of origin

Transactions:
- id: unique transaction number
- date: timestamp of the transaction
- type: “buy” or “sell”
- foreign_amount: amount in foreign currency
- exchange_rate: rate applied
- value_idr: computed value in IDR
- user_id: who performed the transaction

Inventory Denominations:
- id: record identifier
- currency_code: links to Currencies.code
- denomination: bill or coin value (e.g., 100)
- quantity: how many pieces available

Audit Logs:
- id: record identifier
- user_id: who took the action
- action: description of what happened
- timestamp: when it happened

Users:
- id: unique user identifier
- email: login email
- password_hash: secured password value
- role: Admin, Kasir, or Auditor

**SQL Schema (PostgreSQL)**
```sql
-- Currencies
CREATE TABLE currencies (
  code         VARCHAR(3)   PRIMARY KEY,
  name         TEXT         NOT NULL,
  rate_beli    NUMERIC(12,4) NOT NULL,
  rate_jual    NUMERIC(12,4) NOT NULL
);

-- Customers
CREATE TABLE customers (
  id                 SERIAL       PRIMARY KEY,
  name               TEXT         NOT NULL,
  identity_number    TEXT         NOT NULL UNIQUE,
  country            TEXT         NOT NULL
);

-- Users
CREATE TABLE users (
  id               SERIAL       PRIMARY KEY,
  email            TEXT         NOT NULL UNIQUE,
  password_hash    TEXT         NOT NULL,
  role             TEXT         NOT NULL  -- e.g., 'Admin', 'Kasir', 'Auditor'
);

-- Transactions
CREATE TABLE transactions (
  id               SERIAL       PRIMARY KEY,
  date             TIMESTAMP    NOT NULL DEFAULT now(),
  type             TEXT         NOT NULL,
  foreign_amount   NUMERIC(14,4) NOT NULL,
  exchange_rate    NUMERIC(12,4) NOT NULL,
  value_idr        NUMERIC(16,2) NOT NULL,
  user_id          INTEGER      NOT NULL REFERENCES users(id)
);

-- Inventory Denominations
CREATE TABLE inventory_denominations (
  id               SERIAL       PRIMARY KEY,
  currency_code    VARCHAR(3)   NOT NULL REFERENCES currencies(code),
  denomination     INTEGER      NOT NULL,
  quantity         INTEGER      NOT NULL
);

-- Audit Logs
CREATE TABLE audit_logs (
  id               SERIAL       PRIMARY KEY,
  user_id          INTEGER      NOT NULL REFERENCES users(id),
  action           TEXT         NOT NULL,
  timestamp        TIMESTAMP    NOT NULL DEFAULT now()
);
```  

## 4. API Design and Endpoints

**Approach**
- We follow a RESTful style using Next.js API Routes under `/app/api`.  
- Each endpoint maps to a specific resource (e.g., `/api/transactions`).

**Key endpoints**
- **Authentication**  
  • POST `/api/auth/sign-in`: log in and receive a session token  
  • POST `/api/auth/sign-out`: end the session
- **Users**  
  • GET `/api/users/me`: get current user’s info (including role)  
  • GET `/api/users` (Admin only): list all users
- **Currencies**  
  • GET `/api/currencies`: list all currencies and rates  
  • POST `/api/currencies`: add a new currency (Admin)  
  • PUT `/api/currencies/[code]`: update rates (Admin)
- **Customers**  
  • GET `/api/customers`: list customers  
  • POST `/api/customers`: add a new customer
- **Transactions**  
  • GET `/api/transactions`: list past transactions (filter by date, type)  
  • POST `/api/transactions`: record a new transaction  
  • GET `/api/transactions/[id]`: get details of a specific transaction
- **Inventory**  
  • GET `/api/inventory`: show all denominations and quantities  
  • PUT `/api/inventory/[id]`: adjust stock (Admin)
- **Audit Logs**  
  • GET `/api/audit-logs`: list recent actions (Admin/Auditor)

Each route includes validation, role checks, and error handling to keep data accurate and secure.

## 5. Hosting Solutions

We recommend a cloud-based, serverless-friendly setup:

**Application Hosting**
- **Vercel** (ideal for Next.js):  
  • Automatic deployment on push  
  • Built-in serverless functions for API routes  
  • Global CDN for static assets and edge caching

**Database Hosting**
- **Supabase** or **Amazon RDS (PostgreSQL)**:  
  • Managed backups, scaling, and high availability  
  • Secure connections (SSL)

**Benefits**
- **Reliability:** Managed services reduce downtime risk.  
- **Scalability:** Both Vercel and RDS/Supabase auto-scale to handle traffic spikes.  
- **Cost-effectiveness:** Pay-as-you-go pricing helps control costs.

## 6. Infrastructure Components

**Load Balancer / Edge Network**
- Vercel’s global edge network automatically routes users to the closest serverless location.  

**Caching Mechanisms**
- **Static assets:** Served from Vercel’s CDN for instant load times.  
- **API responses:** We can configure HTTP caching headers (e.g., `Cache-Control`) on GET routes like `/api/currencies`.

**Content Delivery Network (CDN)**
- Vercel’s CDN caches pages and static files worldwide, reducing latency for users everywhere.

**Containerization (Development)**
- Docker and Docker Compose create a reproducible local environment with Node.js and PostgreSQL.

## 7. Security Measures

**Authentication & Authorization**
- **Better Auth** handles secure login, session cookies, and token management.  
- **Role-Based Access Control (RBAC):** Middleware checks user roles (Admin, Kasir, Auditor) before allowing access to protected routes.

**Data Encryption**
- **In transit:** All traffic uses HTTPS/TLS.  
- **At rest:** Managed databases typically encrypt stored data automatically.

**Environment Variables**
- Store secrets (DB URLs, API keys) in environment files (`.env`) or hosting platform secret stores.

**Input Validation & Sanitization**
- Every API route validates the incoming data shape and value ranges to prevent bad data and SQL injection.

## 8. Monitoring and Maintenance

**Monitoring Tools**
- **Vercel Analytics:** Tracks serverless function performance and latency.  
- **Database monitoring (Supabase or AWS CloudWatch):** Monitors query times, connection counts, and errors.

**Logging**
- API routes log errors and important events. Logs can be forwarded to services like Sentry or Datadog.

**Maintenance Strategies**
- **Scheduled backups:** Automated daily backups of the database.  
- **Dependency updates:** Regularly update Next.js, Drizzle, and other libraries to get security patches.  
- **Health checks:** Use automated scripts or services to ping a health-check endpoint (`/api/health`) and alert if downtime occurs.

## 9. Conclusion and Overall Backend Summary

The backend for the moneychanger-fullstack-kit is built on a modern, integrated stack:

- **Next.js API Routes** for serverless, scalable functions  
- **Better Auth** for secure, role-based user management  
- **PostgreSQL + Drizzle ORM** for reliable, type-safe data handling  
- **Vercel + Managed DB** for effortless deployment and scaling  
- **Clear separation of folders** to keep code maintainable

This setup aligns perfectly with the needs of a Money Changer system: secure transaction processing, flexible role control, real-time data access, and easy growth as your user base or transaction volume increases. With these components in place, your team can focus on implementing business-specific logic—like exchange rate feeds, PDF receipts, and comprehensive reporting—without worrying about boilerplate infrastructure.