# Tech Stack Document for Moneychanger Fullstack Kit

This document explains, in everyday language, the technology choices behind the `moneychanger-fullstack-kit`. It’s designed to help you understand why each tool was chosen, how it works together, and what benefits it brings to building a modern, secure money exchanger application.

## Frontend Technologies

We chose these tools to create a fast, responsive, and user-friendly interface:

- **Next.js (App Router)**
  - Provides both client-side and server-side rendering. Pages load quickly, and we can securely handle data (like exchange rates) on the server.
  - Built-in routing makes it easy to organize sections like `Sign In`, `Dashboard`, and sub-pages for transactions or reports.

- **TypeScript**
  - Adds “types” to JavaScript so we catch mistakes early (e.g., mixing up a currency code with a customer name).
  - Especially important in finance, where a small typo in a calculation can lead to big errors.

- **React 19**
  - The core library for building interactive UIs. We create components for forms, tables, buttons, and more.

- **shadcn/ui**
  - A set of pre-built React components styled with Tailwind. Speeds up development of forms (transaction entry), tables (customer lists), and charts (dashboard analytics).

- **Tailwind CSS**
  - A utility-first styling framework. We write short class names to style elements, making the design process fast and consistent.
  - Includes built-in support for dark mode, so cashiers can work comfortably in low-light environments.

- **Recharts (optional for charts)**
  - A friendly charting library that lets you visualize data like daily transaction volumes or profit/loss by currency.

## Backend Technologies

These choices power the core logic, data storage, and secure actions behind the scenes:

- **Next.js API Routes**
  - Lets us create server-side endpoints inside the same codebase (e.g., `/api/transactions`, `/api/rates`).
  - All validation, database updates, and PDF generation happen here, keeping sensitive logic off the client.

- **Better Auth**
  - Handles user registration, login, session management, and role-based access (Admin, Kasir, Auditor).
  - Extensible so you can enforce who can view reports, who can perform transactions, etc.

- **PostgreSQL**
  - A reliable, open-source relational database. Stores all core data: currencies, customers, transactions, inventory, and audit logs.

- **Drizzle ORM**
  - A type-safe way to define your database schema and run queries in TypeScript.
  - Reduces common SQL mistakes and ensures your queries match your data structures.

- **PDF Generation (e.g., `pdf-lib` or `react-pdf`)**
  - Used in server code to create printable transaction receipts (nota transaksi) on demand.

## Infrastructure and Deployment

Our infrastructure choices make the app reliable, scalable, and easy to work on:

- **Docker & Docker Compose**
  - Package the application and database into containers so everyone on the team runs the same environment.
  - Simplifies moving from development to staging to production—no “it works on my machine” surprises.

- **Environment Variables (.env files)**
  - Store sensitive data (database URLs, API keys) outside of code. Each environment (dev, test, prod) can have its own settings.

- **Version Control: Git & GitHub**
  - Keeps track of every change, making collaboration and rollback easy.

- **CI/CD with GitHub Actions**
  - Automates testing, builds, and deployments. Every push to `main` can trigger a fresh Docker build and deploy to your production server.

- **Hosting Options**
  - You can deploy Docker containers to services like AWS ECS, DigitalOcean App Platform, or even use Vercel (next-on-vercel) for the frontend and serverless functions.

## Third-Party Integrations

These services add extra power and connectivity to the application:

- **Exchange Rate API (e.g., Bank Indonesia API)**
  - Automatically fetch current buy/sell rates so your cashiers always have up-to-date information.

- **QRIS Payment Gateway**
  - Integrate local digital payments so customers can pay via national QR codes.

- **Analytics (e.g., Google Analytics)**
  - Track usage patterns on your dashboard to see which features are most popular or where users get stuck.

- **Cron Jobs / Background Tasks**
  - Use Vercel Cron Jobs or a lightweight scheduler to pull rates periodically, keeping your data fresh without slowing down user requests.

## Security and Performance Considerations

We built in these measures to protect user data and keep the app running smoothly:

- **Role-Based Access Control (RBAC)**
  - Leverage Better Auth to restrict routes and API endpoints based on user roles (only Admins see audit logs, only Kasirs perform day-to-day transactions).

- **Secure Session Handling**
  - Sessions or JWTs stored in HttpOnly cookies to prevent cross-site scripting attacks.

- **Database Transactions**
  - Wrap related operations (record transaction + update inventory) in a single database transaction using Drizzle, ensuring data integrity.

- **Type Safety**
  - TypeScript + Drizzle ORM catches errors at compile time, reducing runtime bugs.

- **Centralized Error Handling**
  - A unified strategy for catching and reporting server errors, so users see friendly messages and issues can be logged for investigation.

- **Performance Optimizations**
  - Server-side rendering for pages that need fresh data (e.g., transaction history).
  - Caching strategies (in-memory or CDN) for static assets and infrequently changing data.
  - Lazy loading of components and charts to speed up initial page loads.

- **Testing**
  - **Unit Tests** with Vitest or Jest for core logic (calculations, role checks).
  - **End-to-End Tests** with Playwright or Cypress for user flows like logging in and making a transaction.

## Conclusion and Overall Tech Stack Summary

At its core, the `moneychanger-fullstack-kit` brings together a proven set of technologies to help you build a secure, maintainable, and high-performing money exchanger system:

- A **modern frontend** powered by Next.js, React 19, TypeScript, shadcn/ui, and Tailwind CSS for a sleek, responsive UI.
- A **robust backend** based on Next.js API Routes, Better Auth, PostgreSQL, and Drizzle ORM, ensuring data integrity and secure operations.
- **Containerized infrastructure** with Docker, environment variable management, and automated CI/CD to streamline development and deployment.
- **Third-party integrations** for real-time exchange rates, digital payments, and analytics—so your app remains connected and up-to-date.
- **Built-in security** and **performance optimizations** to protect user data, enforce proper access, and deliver a fast user experience.

Together, these choices form a solid foundation. You can now focus on the unique business logic of your Money Changer—like custom reporting, advanced auditing, and tailored customer workflows—while relying on this kit for all the common plumbing and best practices.