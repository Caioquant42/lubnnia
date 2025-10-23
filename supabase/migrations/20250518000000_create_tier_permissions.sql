-- Create tier_permissions table to store tier-based application access
CREATE TABLE IF NOT EXISTS tier_permissions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tier_name TEXT NOT NULL UNIQUE,
  applications TEXT[] NOT NULL DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add trigger to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_tier_permissions_modtime
BEFORE UPDATE ON tier_permissions
FOR EACH ROW
EXECUTE FUNCTION update_modified_column();

-- Insert default tier permissions based on the STRIPE_PRODUCTS configuration
INSERT INTO tier_permissions (tier_name, applications)
VALUES 
  ('FREE', ARRAY['market_overview', 'basic_charts']),
  ('ZOMMA_PRO', ARRAY['market_overview', 'basic_charts', 'advanced_charts', 'portfolio_tracker', 'basic_alerts', 'advanced_alerts', 'custom_strategies', 'historical_data', 'api_access', 'priority_support', 'pairs_trading', 'volatility_analysis', 'options_strategies', 'retirement_calculator', 'flow_analysis'])
ON CONFLICT (tier_name) DO UPDATE 
SET applications = EXCLUDED.applications;

-- Update auth.users to include a default plan/auth_role if not present
ALTER TABLE auth.users ADD COLUMN IF NOT EXISTS raw_user_meta_data JSONB;
