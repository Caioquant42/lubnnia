# Stripe & Supabase Integration Guide

This document explains how Stripe payments and subscriptions are integrated with Supabase authentication in your project. It covers the frontend, backend (Edge Functions), and database schema, and describes the flow for user authentication, checkout, and subscription management.

---

## 1. Overview

- **Supabase** handles user authentication (sign up, login, session management).
- **Stripe** manages payments and subscriptions.
- **Integration**: Each Supabase user is mapped to a Stripe customer. Payments and subscriptions are linked to the authenticated user, and all relevant data is stored in Supabase tables for secure, user-specific access.

---

## 2. Stripe Product Configuration

Defined in [`frontend/stripe-config.ts`]:

- All available plans (e.g., `FREE`, `ZOMMA_PRO`) are listed with their Stripe `priceId`, features, and metadata.
- These plans are referenced throughout the app for pricing, checkout, and feature gating.

---

## 3. Supabase Client Setup

Defined in [`frontend/lib/supabase.ts`]:

- The Supabase client is initialized using environment variables (`NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`).
- Handles authentication, session persistence, and user management.

---

## 4. Stripe Checkout Flow

### Frontend Logic (`frontend/lib/stripe.ts`):

- **Creating a Checkout Session:**
  1. The user must be authenticated via Supabase.
  2. The frontend calls `createCheckoutSession(priceId, mode)`:
      - Gets the current Supabase session/access token.
      - Sends a POST request to the Supabase Edge Function `/functions/v1/stripe-checkout` with the price, mode, and redirect URLs.
      - The access token is sent in the `Authorization` header.
      - On success, the user is redirected to the Stripe Checkout page.

- **Fetching Subscription Status:**
  - The frontend queries the `stripe_user_subscriptions` view to get the current user's subscription info.

---

## 5. Supabase Edge Functions

### `stripe-checkout` (`frontend/supabase/functions/stripe-checkout/index.ts`):

- **Purpose:** Creates a Stripe Checkout session for the authenticated user.
- **Flow:**
  1. Validates the request and authenticates the user using the Supabase access token.
  2. Checks if the user already has a Stripe customer record in the `stripe_customers` table.
      - If not, creates a new Stripe customer and links it to the Supabase user.
      - Also creates a placeholder subscription record if the mode is `subscription`.
  3. Creates a Stripe Checkout session for the customer.
  4. Returns the session URL to the frontend.

### `stripe-webhook` (`frontend/supabase/functions/stripe-webhook/index.ts`):

- **Purpose:** Handles Stripe webhook events (e.g., payment completed, subscription updated).
- **Flow:**
  1. Verifies the webhook signature.
  2. For subscription events, synchronizes the latest subscription state from Stripe to the `stripe_subscriptions` table.
  3. For one-time payments, records the order in the `stripe_orders` table.

---

## 6. Supabase Database Schema

Defined in [`frontend/supabase/migrations/20250430190506_pink_ember.sql`]:

- **Tables:**
  - `stripe_customers`: Maps Supabase users to Stripe customers.
  - `stripe_subscriptions`: Stores subscription details (status, period, payment info).
  - `stripe_orders`: Stores one-time payment/order details.

- **Views:**
  - `stripe_user_subscriptions`: Secure view for the authenticated user's subscription.
  - `stripe_user_orders`: Secure view for the authenticated user's order history.

- **Security:**
  - Row Level Security (RLS) is enabled on all tables.
  - Policies ensure users can only view their own data.

---

## 7. User Signup & Plan Selection

- On signup, users can select a plan (e.g., Free, Pro).
- If a paid plan is selected, after signup the user is redirected to the checkout flow.
- The user's plan is stored in their Supabase profile metadata.

---

## 8. How Authentication & Payment Are Linked

- **Authentication:** All payment and subscription actions require the user to be authenticated with Supabase.
- **Linking:** The user's Supabase `user_id` is mapped to a Stripe `customer_id` in the `stripe_customers` table.
- **Security:** All queries for subscription/order data are filtered by the authenticated user's ID, ensuring privacy and security.

---

## 9. Example Flow

1. **User logs in or signs up** via Supabase.
2. **User selects a plan** and initiates checkout.
3. **Frontend** calls `createCheckoutSession`, passing the user's access token.
4. **Edge Function** creates or finds the Stripe customer, creates a checkout session, and returns the URL.
5. **User completes payment** on Stripe.
6. **Stripe sends a webhook** to the Edge Function, which updates the subscription/order state in Supabase.
7. **Frontend** can now query the user's subscription/order status securely via Supabase.

---

## 10. Key Files

- `frontend/stripe-config.ts` — Stripe product definitions.
- `frontend/lib/stripe.ts` — Frontend logic for checkout and subscription queries.
- `frontend/lib/supabase.ts` — Supabase client setup.
- `frontend/supabase/functions/stripe-checkout/index.ts` — Edge Function for creating checkout sessions.
- `frontend/supabase/functions/stripe-webhook/index.ts` — Edge Function for handling Stripe webhooks.
- `frontend/supabase/migrations/20250430190506_pink_ember.sql` — Database schema for Stripe integration.

---

## 11. Environment Variables

- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`

---

## 12. Summary

- **Supabase** handles authentication and user management.
- **Stripe** handles payments and subscriptions.
- **Integration** is achieved by mapping Supabase users to Stripe customers, and synchronizing payment/subscription state via Edge Functions and webhooks.
- **Security** is enforced via Row Level Security and authenticated API calls.

---

If you need to extend or debug the integration, start by checking the Edge Functions, the Supabase tables/views, and the environment variables. All payment and subscription logic is tightly coupled to the authenticated user, ensuring a secure and seamless experience.

---

Let me know if you want a more detailed breakdown of any specific part! 