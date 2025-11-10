# Frontend Guideline Document

This document lays out the key aspects of the frontend setup for the Money Changer application. It explains the architecture, design principles, styling, component structure, state handling, routing, performance tricks, and testing practices in clear, everyday language.

## 1. Frontend Architecture

**Framework and Language**  
- We use **Next.js** (App Router) as our core framework. It gives us server-rendered pages, file-based routing, and built-in API support.  
- **React 19** handles the UI.  
- **TypeScript** adds type safety, helping us catch bugs early—crucial for financial calculations.

**Libraries and Tools**  
- **shadcn/ui**: A set of ready-made components (forms, tables, modals) we can drop in and customize.  
- **Tailwind CSS**: A utility-first CSS framework that speeds up styling without writing custom CSS files.

**Why this setup?**  
- **Scalability**: File-based routing and reusable components let us add new pages or features without rewriting existing code.  
- **Maintainability**: Clear folder structure—UI components in `/components`, pages in `/app`, utilities in `/lib`—keeps code organized.  
- **Performance**: Server-side rendering for fast first loads, combined with client-side navigation for snappy transitions.

## 2. Design Principles

1. **Usability**  
   - Keep forms and tables simple and clear. Labels, placeholders, and error messages guide the user.  
   - Provide real-time feedback (e.g., show converted IDR as soon as the user types a foreign amount).

2. **Accessibility**  
   - Follow WCAG basics: color contrast, keyboard navigation, and proper ARIA labels on interactive elements.  
   - Ensure all buttons and inputs are reachable and usable without a mouse.

3. **Responsiveness**  
   - Design mobile-first. Each page adapts from phone to large desktop.  
   - Use Tailwind’s responsive utilities (`sm:`, `md:`, `lg:`) to adjust layouts seamlessly.

4. **Consistency**  
   - Keep spacing, colors, and typography uniform across the app.  
   - Use shared components (buttons, inputs) from `shadcn/ui` so every screen feels part of the same family.

## 3. Styling and Theming

### Styling Approach  
- **Utility-First CSS**: We rely on **Tailwind CSS**. Instead of writing long class names or BEM structures, we apply small, reusable utility classes directly in JSX.  
- **No separate SASS** or CSS Modules—Tailwind handles everything, and unused styles are purged in production.

### Theming  
- **Light and Dark Mode**: Built into Tailwind using CSS variables. Users can toggle, and the app remembers their preference.  
- Colors, backgrounds, and shadows all switch based on a `data-theme` attribute.

### Visual Style  
- **Flat Design**: Clean, minimal, with bold shapes and clear typography.  
- **Subtle Glassmorphism**: On dialogs and cards, we use a slight semi-transparent background with blur to give depth without clutter.

### Color Palette  
- Primary: Indigo 600 (`#4F46E5`)  
- Secondary: Emerald 500 (`#10B981`)  
- Accent: Amber 400 (`#FBBF24`)  
- Neutral Light: Gray 100 (`#F3F4F6`)  
- Neutral Dark: Gray 800 (`#1F2937`)  
- Warning/Error: Red 500 (`#EF4444`)

### Typography  
- **Font Family**: `Inter`, fallbacks `sans-serif`.  
- **Base Size**: 16px, scaling up for headings.  
- Line heights and letter spacing set in Tailwind’s theme for readability, especially in tables and forms.

## 4. Component Structure

- **Atomic Components**: Stored in `/components/ui`. These are basic building blocks—Button, Input, Modal. They come from `shadcn/ui` but can be extended.  
- **Feature Components**: In `/components`, folders like `Transactions`, `Dashboard`, `Reports` hold related pieces (e.g., `TransactionForm.tsx`, `DailyReport.tsx`).  
- **Why this helps**: Breaking down UI into small pieces means we can reuse and test each piece separately. If the design changes, we update one Button component and see it everywhere.

## 5. State Management

- **Local State**: For simple, component-level data (form fields, toggles), we use React’s `useState` and `useReducer`.  
- **Context API**: For auth status, user info, and theme settings, a React context provides data to any component that needs it.  
- **Optional Global Store**: If certain data (like a large list of currencies or user settings) grows complex, we can introduce **Zustand**—a lightweight, hook-based state library—as an alternative to Redux.

## 6. Routing and Navigation

- **File-Based Routing**: Next.js App Router reads folders under `/app` and turns them into routes automatically.  
- **Nested Layouts**: Shared layout (header, sidebar) lives in `/app/(dashboard)/layout.tsx`. Inside, child pages render in the same frame.  
- **Dynamic Routes**: For editing a transaction, we might have `/app/dashboard/transactions/[id]/page.tsx`.  
- **Link Component**: We use Next’s `<Link>` to prefetch pages and enable instant client-side navigation.

## 7. Performance Optimization

1. **Code Splitting & Lazy Loading**  
   - Components that aren’t needed immediately (charts, PDF previews) are imported with `next/dynamic`, loading only when they come into view.

2. **Image Optimization**  
   - Next.js’s `<Image>` component auto-resizes and serves modern formats (WebP) for logos or charts.

3. **Tailwind Purge**  
   - In production, Tailwind removes unused CSS, resulting in a small stylesheet.

4. **Prefetching**  
   - Next.js prefetches linked pages when links appear in the viewport, speeding up navigation.

5. **Caching API Calls**  
   - We can use SWR or React Query (optional) to cache data, avoid repeat calls, and keep the UI responsive.

## 8. Testing and Quality Assurance

- **Unit Tests**  
  - Use **Vitest** (or Jest) with React Testing Library to cover core logic: currency calculations, form validation, button clicks.

- **Integration Tests**  
  - Combine multiple components and simulate user flows—like filling out a transaction form—using Testing Library.

- **End-to-End Tests**  
  - Use **Playwright** or **Cypress** to drive a headless browser through sign-in, creating transactions, and viewing reports. This catches issues across the full stack.

- **Linting & Formatting**  
  - **ESLint** enforces code style and catches potential errors early.  
  - **Prettier** keeps formatting consistent across teams.

- **Continuous Integration**  
  - Tests run on every pull request to ensure we don’t break core features.

## 9. Conclusion and Overall Frontend Summary

This frontend setup combines **Next.js**, **TypeScript**, **shadcn/ui**, and **Tailwind CSS** to deliver a modern, secure, and fast application shell for your Money Changer system. It emphasizes:  

- Clear **architecture** that grows with your business logic.  
- Strong **design principles** around usability, accessibility, and responsiveness.  
- A **styling system** that maintains consistency and supports light/dark themes.  
- A **component-driven structure** that makes building new features fast and safe.  
- Flexible **state management** with room to scale.  
- Built-in **performance tricks** and **comprehensive testing** to keep the user experience smooth and error-free.

With these guidelines in hand, any developer—even without deep knowledge of the codebase—can understand, extend, and maintain the frontend with confidence.