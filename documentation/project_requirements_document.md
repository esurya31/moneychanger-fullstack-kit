# Project Requirements Document for moneychanger-fullstack-kit

## 1. Project Overview

moneychanger-fullstack-kit is a ready-made starter template designed to jump-start the development of a Money Changer web application. It provides secure user authentication, a protected dashboard, modern UI components, and a type-safe PostgreSQL integration using Drizzle ORM. With this foundation in place, developers can focus on implementing the unique business logic—like exchange rate calculations, cash inventory management, and report generation—without rewriting common boilerplate.

The goal is to build a reliable, maintainable, and secure Money Changer system that supports multiple user roles (Admin, Kasir, Auditor), daily transaction processing, master data management, and detailed financial reporting with audit trails. Success will be measured by rapid feature delivery, clear code structure, type safety to reduce runtime errors, and an intuitive user interface that performs under real-world load conditions.

## 2. In-Scope vs. Out-of-Scope

**In-Scope (Version 1.0):**
- User authentication with role-based access control (Admin, Kasir, Auditor).
- Protected dashboard layout with sidebar navigation.
- Daily transaction module (foreign currency buy/sell) with real-time IDR calculation.
- Master data management for currencies and customers.
- Inventory tracking for currency denominations.
- Reporting pages: daily summaries, profit/loss, audit trail.
- PDF receipt generation for completed transactions.
- Integration with a third-party exchange rate API for automatic updates.
- Containerized development environment using Docker and Docker Compose.

**Out-of-Scope (Future Phases):**
- Mobile-specific app or responsive PWA optimizations beyond default responsive UI.
- Integration with payment gateways beyond QRIS (e.g., credit card, e-wallet).
- Advanced analytics dashboards or machine-learning-driven rate predictions.
- Multi-branch or multi-currency inventory transfer workflows.
- Offline mode or local data caching.
- User notifications via SMS or email.

## 3. User Flow

When a new user (Kasir or Admin) arrives, they navigate to the `/sign-in` page. After entering valid credentials, they land on the main dashboard, which features a left sidebar for navigation and a content area that shows key widgets—like today’s transaction count and low-stock alerts. The sidebar includes links for Transactions, Master Data, Reports, and Settings (for Admins).

For daily operations, a Kasir clicks **Transactions**, selects **New Transaction**, and chooses a currency (e.g., USD). The form fetches the current buy/sell rates, calculates the IDR equivalent as the Kasir types the foreign amount, and allows entry of customer details. On submission, the system records the transaction, updates inventory denominations, generates a PDF receipt, and redirects to a confirmation page showing transaction details. Admins follow a similar path for **Master Data** and **Reports**, where they can add currencies/customers or generate and export audit trail logs.

## 4. Core Features

- **Authentication & Authorization**: Sign-up, login, logout; JWT or session-based; role checks (Admin, Kasir, Auditor).
- **Dashboard**: Protected area with sidebar navigation and configurable widgets.
- **Transaction Module**: Buy/sell form, rate lookup, real-time IDR calculation, inventory update, PDF receipt.
- **Master Data Management**: CRUD screens for currencies (`kode`, `nama`, `rate_beli`, `rate_jual`) and customers (`nama`, `no_identitas`, `negara_asal`).
- **Inventory Management**: Track denominations per currency code, adjust quantities on each transaction.
- **Reporting & Audit Trail**: Daily summaries, profit/loss by currency, detailed action logs.
- **External Rate Integration**: Scheduled or on-demand fetch from a public exchange rate API.
- **PDF Generation**: Server-side receipt creation via `pdf-lib` or `react-pdf`.
- **Containerization**: Dockerfiles for app and database, Docker Compose setup.

## 5. Tech Stack & Tools

- **Frontend**: Next.js (App Router), React 19, TypeScript, Tailwind CSS, shadcn/ui components.
- **Backend**: Next.js API Routes, Node.js/TypeScript, Better Auth for authentication.
- **Database**: PostgreSQL with Drizzle ORM for type-safe schema and queries.
- **Infrastructure**: Docker, Docker Compose for consistent environments; environment variables via `.env`.
- **PDF Library**: `pdf-lib` or `react-pdf` for server-side PDF generation.
- **Testing**: Vitest or Jest for unit tests; Playwright or Cypress for end-to-end tests.

## 6. Non-Functional Requirements

- **Performance**: API endpoints should respond within 200ms under typical loads; dashboard load time under 1s.
- **Security**: HTTPS enforced; input validation on both client and server; role-based access control; secure storage of secrets in environment variables.
- **Reliability**: Database migrations and seed scripts; Docker-based dev/prod parity; backup strategies for PostgreSQL.
- **Usability**: Responsive design; dark mode support; real-time form validation and error feedback.
- **Compliance**: Follow best practices for handling personal data; consider local regulations for financial transactions and record-keeping.

## 7. Constraints & Assumptions

- **Docker Installed**: Developers must have Docker and Docker Compose available locally.
- **Third-Party API Availability**: Exchange rate API endpoints must support CORS or server-side fetching.
- **Role Definitions**: Assumes three roles only (Admin, Kasir, Auditor) with no custom roles in V1.
- **Precision**: Currency amounts handled as decimal types; assume 2-4 decimal places is sufficient.
- **Server Environment**: Node.js v18+ and PostgreSQL v13+.

## 8. Known Issues & Potential Pitfalls

- **API Rate Limits**: External rate API may throttle calls. Mitigation: cache rates for a configurable interval; use background job for updates.
- **Race Conditions**: Simultaneous transactions could lead to inaccurate inventory counts. Mitigation: wrap transaction/​inventory updates in a DB transaction.
- **Decimal Precision Errors**: JavaScript number precision can cause rounding issues. Mitigation: use a decimal library (e.g., `decimal.js`) on the client or server.
- **PDF Generation Performance**: Generating large receipts could be slow. Mitigation: offload to a background queue if needed.
- **Migration Drift**: Schema changes across environments can get out of sync. Mitigation: enforce migration scripts and version control for `.sql` or Drizzle migration files.

---
This document provides a clear and comprehensive foundation for building the Money Changer application on top of moneychanger-fullstack-kit. Use it as the authoritative guide for all subsequent technical design, implementation, and testing activities.