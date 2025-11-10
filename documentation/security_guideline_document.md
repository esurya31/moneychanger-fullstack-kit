# Security Guidelines for `moneychanger-fullstack-kit`

This document outlines the essential security principles and best practices tailored to the `moneychanger-fullstack-kit` starter repository. Adhering to these guidelines will help you build a robust, resilient, and secure Money Changer application.

---

## 1. Security by Design

- Embed security from the earliest design phases.  
- Perform threat modeling for core flows (authentication, transaction processing, reporting).  
- Enforce peer reviews for all security-related code changes.

## 2. Authentication & Access Control

### 2.1 Robust Authentication with Better Auth

- Use strong password policies: minimum 12 characters, mixed case, digits, and symbols.  
- Hash passwords with a modern algorithm (Argon2 or bcrypt) and unique per-user salts.  
- Enforce account lockout and exponential back-off after repeated failed logins.

### 2.2 Session Management

- Store sessions in a secure, server-side store (e.g., Redis) with unpredictable session IDs.  
- Set cookies with `Secure`, `HttpOnly`, and `SameSite=Strict`.  
- Implement idle and absolute session timeouts.

### 2.3 Role-Based Access Control (RBAC)

- Define explicit roles: **Admin**, **Kasir**, **Auditor**.  
- Store user roles in the database and include them in JWTs or session objects.  
- Implement server-side middleware in Next.js API routes to enforce role checks on every request.

### 2.4 Multi-Factor Authentication (MFA)

- Offer MFA (TOTP or SMS) for administrative accounts and high-risk transactions.  
- Integrate established libraries/services (e.g., Authy, Google Authenticator).

## 3. Input Handling & Processing

### 3.1 Prevent Injection Attacks

- Use Drizzle ORM with parameterized queries exclusively—never concatenate SQL strings.  
- Validate and sanitize all user input on the server, including form data and URL parameters.  
- Rigorously validate JSON payloads in Next.js API routes using a schema validator (e.g., Zod).

### 3.2 Mitigate Cross-Site Scripting (XSS)

- Perform context-aware output encoding in React components.  
- Sanitize any rich text or HTML fields using libraries like DOMPurify.  
- Enforce a strict [Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP) (CSP) at the application entry point.

### 3.3 Secure File Uploads (if applicable)

- Accept only whitelisted MIME types and extensions.  
- Scan files for malware and store them outside the webroot with randomized filenames.  
- Restrict maximum file size in the API route configuration.

## 4. Data Protection & Privacy

### 4.1 Encryption in Transit and at Rest

- Enforce HTTPS (TLS 1.2+) for all client–server communication.  
- Use strong cipher suites and disable weak protocols (SSLv3, TLS 1.0/1.1).  
- Encrypt sensitive fields (e.g., API keys, PII) in the database if required by regulation.

### 4.2 Secrets Management

- Do not hardcode secrets in source code or `.env`.  
- Use a dedicated secrets manager (AWS Secrets Manager, HashiCorp Vault) and inject at runtime.  
- Rotate secrets periodically and after personnel changes.

### 4.3 Logging & Monitoring

- Mask or omit sensitive data (passwords, credit card numbers) in logs.  
- Centralize logs and monitor for suspicious activity (e.g., failed logins, unusual transaction volumes).  
- Implement alerting for critical events (CSRF violations, repeated 4xx/5xx errors).

## 5. API & Service Security

### 5.1 Secure Next.js API Routes

- Require authentication for all protected endpoints; return HTTP 401/403 appropriately.  
- Enforce proper HTTP methods (GET, POST, PUT, DELETE) and reject unexpected verbs.  
- Implement rate limiting and throttling per IP or per user to mitigate brute-force attacks.

### 5.2 CORS Configuration

- Restrict `Access-Control-Allow-Origin` to trusted domains only.  
- Only enable credentials (`Access-Control-Allow-Credentials`) if necessary, and scope them tightly.

### 5.3 API Versioning

- Prefix routes with `/api/v1/…` to allow safe, backwards-compatible changes.

## 6. Web Application Security Hygiene

### 6.1 CSRF Protection

- Use anti-CSRF tokens (Synchronizer Token Pattern) for all state-changing forms and AJAX requests.  
- Integrate Next.js middleware or libraries (e.g., `next-csrf`) to enforce tokens.

### 6.2 Security Headers

- Strict-Transport-Security: `max-age=63072000; includeSubDomains; preload`  
- X-Content-Type-Options: `nosniff`  
- X-Frame-Options or CSP `frame-ancestors`: `deny` or allow only trusted frames  
- Referrer-Policy: `no-referrer-when-downgrade` or stricter

### 6.3 Subresource Integrity (SRI)

- Apply SRI hashes to all external scripts and stylesheets loaded via CDN.

## 7. Infrastructure & Configuration Management

### 7.1 Docker & Deployment

- Run containers with non-root users.  
- Limit exposed ports; only publish the necessary HTTP(s) port.  
- Use immutable tags for images and avoid `latest` in production.

### 7.2 Server Hardening

- Disable unused services and close unneeded ports on your host OS.  
- Apply security updates regularly to the OS, Docker Engine, and base images.

### 7.3 Environment & Configuration

- Validate `.env` values at startup to ensure required settings (DB URL, secret keys) are present.  
- Segregate environments (development, staging, production) with distinct credentials and resources.

## 8. Dependency Management

- Maintain a lockfile (`package-lock.json`) and audit dependencies with tools like `npm audit` or Snyk.  
- Keep frameworks (Next.js, Drizzle, React) and libraries up to date, prioritizing security patches.  
- Remove unused packages to minimize attack surface.

## 9. Testing & Continuous Security

- Implement automated unit, integration, and end-to-end tests (Vitest, Jest, Playwright) covering all critical flows.  
- Integrate static analysis (ESLint, TypeScript strict mode) and SCA tools into your CI pipeline.  
- Perform regular security reviews and penetration tests before major releases.

---

By following these guidelines, your `moneychanger-fullstack-kit`-based application will meet stringent security standards, ensuring trustworthiness and compliance in handling financial transactions and sensitive customer data.
