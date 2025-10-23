# Stripe & Supabase Integration - Complete Guide

## Overview

This document provides a comprehensive explanation of how the Stripe payment system is integrated with Supabase for the Zomma Quant platform. The integration handles user subscriptions, payment processing, and automatic monthly billing through Stripe's subscription system.

## Architecture Overview

```
Frontend (Next.js) → Supabase Edge Functions → Stripe API → Supabase Database
```

### Components:
- **Frontend**: React components for checkout and subscription management
- **Supabase Edge Functions**: Serverless functions handling Stripe operations
- **Stripe**: Payment processing and subscription management
- **Supabase Database**: User data, subscription status, and payment records

## 1. User Registration & Plan Selection

### Frontend Flow (`frontend/app/auth/register/page.tsx`)

When a user registers, they select a plan:

```typescript
const [selectedPlan, setSelectedPlan] = useState<"FREE" | "ZOMMA_PRO">("FREE");
```

**Available Plans:**
- **FREE**: Basic access (R$ 0/month)
- **ZOMMA_PRO**: Premium access (R$ 79.90/month)

### Plan Configuration (`frontend/stripe-config.ts`)

```typescript
export const STRIPE_PRODUCTS = {
  ZOMMA_PRO: {
    name: 'Zomma Pro',
    description: 'Full access to all premium features and priority support',
    priceId: 'price_1RJftABcLZsh0tZTuFtDix8E', // Stripe Price ID
    mode: 'subscription' as const, // Monthly recurring
    price: 79.90,
    currency: 'BRL',
    // ... features list
  }
}
```

## 2. Checkout Process

### Frontend Checkout (`frontend/app/checkout/page.tsx`)

1. **User redirected** to `/checkout?plan=ZOMMA_PRO`
2. **Checkout page** automatically calls `createCheckoutSession()`
3. **User redirected** to Stripe Checkout page

### Stripe Integration (`frontend/lib/stripe.ts`)

```typescript
export async function createCheckoutSession(priceId: string, mode: 'subscription' | 'payment'): Promise<string> {
  // 1. Verify user authentication via Supabase
  const { data: { session } } = await supabase.auth.getSession();
  
  // 2. Call Supabase Edge Function
  const { data, error } = await supabase.functions.invoke('stripe-checkout', {
    body: {
      price_id: priceId,
      mode,
      success_url: `${window.location.origin}/checkout/success`,
      cancel_url: `${window.location.origin}/checkout/cancel`,
    },
  });
  
  return data.url; // Stripe Checkout URL
}
```

## 3. Supabase Edge Functions

### Stripe Checkout Function (`supabase/functions/stripe-checkout/index.ts`)

This function handles the creation of Stripe checkout sessions:

#### Key Operations:

1. **User Authentication**
   ```typescript
   const { data: { user } } = await supabase.auth.getUser(token);
   ```

2. **Customer Management**
   ```typescript
   // Check if user already has a Stripe customer record
   const { data: customer } = await supabase
     .from('stripe_customers')
     .select('customer_id')
     .eq('user_id', user.id);
   
   // If no customer exists, create one in Stripe
   if (!customer) {
     const newCustomer = await stripe.customers.create({
       email: user.email,
       metadata: { userId: user.id }
     });
   }
   ```

3. **Subscription Record Creation**
   ```typescript
   if (mode === 'subscription') {
     await supabase.from('stripe_subscriptions').insert({
       customer_id: customerId,
       status: 'not_started'
     });
   }
   ```

4. **Checkout Session Creation**
   ```typescript
   const session = await stripe.checkout.sessions.create({
     customer: customerId,
     payment_method_types: ['card'],
     line_items: [{ price: price_id, quantity: 1 }],
     mode, // 'subscription' for monthly billing
     success_url,
     cancel_url,
   });
   ```

## 4. Monthly Payment System

### How Monthly Billing Works

**YES, payments are automatically collected monthly by Stripe's subscription system.**

#### Subscription Lifecycle:

1. **Initial Payment**: User completes checkout on Stripe
2. **Subscription Created**: Stripe creates a subscription with the specified price
3. **Automatic Billing**: Stripe automatically charges the user's card every month
4. **Webhook Notifications**: Stripe sends webhooks to update subscription status

#### Stripe Subscription Features:

- **Automatic Renewal**: No manual intervention required
- **Failed Payment Handling**: Stripe retries failed payments
- **Dunning Management**: Automatic retry logic for declined cards
- **Subscription Updates**: Can modify plans, quantities, or cancel

### Stripe Webhook Handler (`supabase/functions/stripe-webhook/index.ts`)

This function processes Stripe events and updates the database:

```typescript
// Handle subscription events
if (event.type === 'customer.subscription.created') {
  // New subscription created
  await updateSubscriptionStatus(event.data.object);
}

if (event.type === 'customer.subscription.updated') {
  // Subscription updated (renewal, plan change, etc.)
  await updateSubscriptionStatus(event.data.object);
}

if (event.type === 'invoice.payment_succeeded') {
  // Monthly payment successful
  await recordSuccessfulPayment(event.data.object);
}

if (event.type === 'invoice.payment_failed') {
  // Payment failed - Stripe will retry automatically
  await updateSubscriptionStatus(event.data.object);
}
```

## 5. Database Schema

### Core Tables

#### `stripe_customers`
```sql
CREATE TABLE stripe_customers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id),
  customer_id TEXT NOT NULL UNIQUE, -- Stripe customer ID
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  deleted_at TIMESTAMP WITH TIME ZONE
);
```

#### `stripe_subscriptions`
```sql
CREATE TABLE stripe_subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id TEXT NOT NULL, -- Stripe customer ID
  subscription_id TEXT UNIQUE, -- Stripe subscription ID
  status TEXT NOT NULL, -- 'active', 'past_due', 'canceled', etc.
  current_period_start TIMESTAMP WITH TIME ZONE,
  current_period_end TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### `stripe_orders`
```sql
CREATE TABLE stripe_orders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id TEXT NOT NULL,
  order_id TEXT UNIQUE, -- Stripe order ID
  amount INTEGER NOT NULL, -- Amount in cents
  currency TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Secure Views

#### `stripe_user_subscriptions`
```sql
CREATE VIEW stripe_user_subscriptions AS
SELECT s.*, c.user_id
FROM stripe_subscriptions s
JOIN stripe_customers c ON s.customer_id = c.customer_id
WHERE c.user_id = auth.uid(); -- Row Level Security
```

## 6. Payment Flow Details

### Monthly Billing Cycle:

1. **Day 1**: Stripe creates invoice for next month
2. **Day 1**: Stripe attempts to charge the customer's card
3. **Success**: Subscription continues, access granted
4. **Failure**: Stripe retries payment (3 attempts over 7 days)
5. **Final Failure**: Subscription marked as 'past_due' or 'canceled'

### Failed Payment Handling:

- **Automatic Retries**: Stripe retries failed payments automatically
- **Retry Schedule**: 1 day, 3 days, and 7 days after failure
- **Dunning Emails**: Stripe sends automatic emails about failed payments
- **Grace Period**: Users maintain access during retry period

## 7. Frontend Subscription Management

### Check Subscription Status (`frontend/lib/stripe.ts`)

```typescript
export async function hasActiveSubscription(): Promise<boolean> {
  try {
    const subscription = await getUserSubscription();
    return subscription?.status === 'active';
  } catch (error) {
    return false;
  }
}
```

### Subscription Data Access:

```typescript
export async function getUserSubscription() {
  const { data, error } = await supabase
    .from('stripe_user_subscriptions')
    .select('*')
    .single();
  
  return data;
}
```

## 8. Security Features

### Row Level Security (RLS)

All Stripe-related tables have RLS enabled:

```sql
ALTER TABLE stripe_customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE stripe_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE stripe_orders ENABLE ROW LEVEL SECURITY;

-- Users can only see their own data
CREATE POLICY "Users can view own subscription data" ON stripe_subscriptions
  FOR SELECT USING (customer_id IN (
    SELECT customer_id FROM stripe_customers WHERE user_id = auth.uid()
  ));
```

### Authentication Required

All payment operations require valid Supabase authentication:

```typescript
// Verify user is authenticated
const { data: { session } } = await supabase.auth.getSession();
if (!session) {
  throw new Error('User not authenticated');
}
```

## 9. Environment Variables

### Required Configuration:

```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# Stripe (in Supabase Edge Functions)
STRIPE_SECRET_KEY=sk_live_... or sk_test_...
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

## 10. Testing & Development

### Test Mode:

- Use Stripe test keys (`sk_test_...`)
- Test card numbers: `4242 4242 4242 4242`
- Test webhook endpoints for local development

### Production Deployment:

1. **Deploy Edge Functions**:
   ```bash
   supabase functions deploy stripe-checkout
   supabase functions deploy stripe-webhook
   ```

2. **Set Production Secrets**:
   ```bash
   supabase secrets set STRIPE_SECRET_KEY=sk_live_...
   ```

3. **Configure Webhook Endpoints** in Stripe Dashboard

## 11. Monitoring & Analytics

### Stripe Dashboard:

- **Subscription Metrics**: Active subscriptions, churn rate
- **Payment Analytics**: Success/failure rates, revenue
- **Customer Insights**: Payment methods, geographic data

### Supabase Monitoring:

- **Function Logs**: Edge function execution logs
- **Database Performance**: Query performance, connection usage
- **Error Tracking**: Failed requests, authentication issues

## 12. Common Scenarios

### New Subscription:
1. User selects ZOMMA_PRO plan
2. Completes checkout on Stripe
3. Stripe creates subscription
4. Webhook updates database
5. User gains premium access

### Monthly Renewal:
1. Stripe automatically charges card
2. Webhook confirms successful payment
3. Subscription remains active
4. User continues premium access

### Failed Payment:
1. Stripe attempts to charge card
2. Payment fails
3. Stripe retries automatically
4. User receives dunning emails
5. Subscription suspended if all retries fail

### Plan Cancellation:
1. User cancels in Stripe dashboard
2. Webhook updates subscription status
3. Access continues until period end
4. No further charges

## 13. Troubleshooting

### Common Issues:

1. **Edge Function Not Found**:
   - Check if functions are deployed
   - Verify function names in Supabase dashboard

2. **Authentication Errors**:
   - Verify Supabase auth is working
   - Check user session validity

3. **Payment Failures**:
   - Check Stripe dashboard for error details
   - Verify webhook configuration

4. **Database Errors**:
   - Check RLS policies
   - Verify table structure

## 14. Best Practices

### Security:
- Always validate user authentication
- Use RLS policies for data access
- Never expose Stripe secret keys in frontend

### Performance:
- Cache subscription status when possible
- Use efficient database queries
- Monitor Edge Function execution time

### User Experience:
- Provide clear error messages
- Handle payment failures gracefully
- Offer multiple payment methods

## 15. Future Enhancements

### Potential Improvements:

1. **Multiple Payment Methods**: Support for PayPal, PIX, etc.
2. **Usage-Based Billing**: Pay-per-use pricing models
3. **Trial Periods**: Free trial before charging
4. **Promotional Codes**: Discount codes and coupons
5. **Proration**: Handle mid-cycle plan changes
6. **Multi-Currency**: Support for different currencies

## Conclusion

The Stripe and Supabase integration provides a robust, secure, and scalable payment system for the Zomma Quant platform. The monthly subscription model is fully automated through Stripe's subscription system, requiring no manual intervention for recurring payments.

Key benefits:
- **Automated Billing**: Monthly payments handled automatically
- **Secure**: RLS policies and authentication required
- **Scalable**: Edge Functions handle high traffic
- **Reliable**: Stripe's proven payment infrastructure
- **Transparent**: Full audit trail of all transactions

This system ensures that premium users are automatically billed each month while maintaining access to premium features, providing a seamless user experience and reliable revenue collection for the platform. 