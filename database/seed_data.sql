-- Sample data for testing the FAQ system
-- Run this after creating the schema

-- Insert FAQ Categories
INSERT INTO faq_categories (name, description, display_order) VALUES
('Account Issues', 'Problems related to your account', 1),
('Payment & Billing', 'Issues with payments, refunds, and billing', 2),
('Technical Support', 'Technical issues and troubleshooting', 3),
('Product Information', 'Questions about products and services', 4);

-- Insert FAQ Subcategories for Account Issues
INSERT INTO faq_subcategories (category_id, name, description, display_order) VALUES
(1, 'Login Problems', 'Issues with logging into your account', 1),
(1, 'Password Reset', 'Help with resetting your password', 2),
(1, 'Account Verification', 'Issues with verifying your account', 3),
(1, 'Update Profile Information', 'Help with updating your profile', 4);

-- Insert FAQ Subcategories for Payment & Billing
INSERT INTO faq_subcategories (category_id, name, description, display_order) VALUES
(2, 'Payment Failed', 'Issues with failed payments', 1),
(2, 'Refund Request', 'How to request refunds', 2),
(2, 'Invoice Issues', 'Problems with invoices', 3),
(2, 'Subscription Management', 'Managing your subscription', 4);

-- Insert FAQ Subcategories for Technical Support
INSERT INTO faq_subcategories (category_id, name, description, display_order) VALUES
(3, 'Website Not Loading', 'Issues with website access', 1),
(3, 'Mobile App Issues', 'Problems with the mobile app', 2),
(3, 'Slow Performance', 'Performance-related issues', 3),
(3, 'Feature Not Working', 'Specific features not functioning', 4);

-- Insert FAQ Subcategories for Product Information
INSERT INTO faq_subcategories (category_id, name, description, display_order) VALUES
(4, 'Product Features', 'Information about product features', 1),
(4, 'Pricing Plans', 'Details about pricing and plans', 2),
(4, 'System Requirements', 'Technical requirements', 3),
(4, 'Integration Options', 'Available integrations', 4);

-- Insert FAQ Items for Account Issues
INSERT INTO faq_items (category_id, subcategory_id, question, answer, tags) VALUES
(1, 1, 'I cannot log into my account', 'To resolve login issues:

1. Make sure you''re using the correct email address
2. Check if your password is correct (remember it''s case-sensitive)
3. Clear your browser cache and cookies
4. Try using incognito/private browsing mode
5. If you forgot your password, use the ''Forgot Password'' link

If none of these work, the issue might be on our end. Please try again in a few minutes.', ARRAY['login', 'password', 'access']),

(1, 2, 'How do I reset my password?', 'To reset your password:

1. Go to the login page
2. Click on ''Forgot Password'' link
3. Enter your registered email address
4. Check your email for reset instructions (also check spam folder)
5. Follow the link in the email to create a new password
6. Make sure your new password is at least 8 characters long

The reset link expires in 24 hours. If you don''t receive the email within 10 minutes, please contact us.', ARRAY['password', 'reset', 'email']),

(1, 3, 'How do I verify my account?', 'To verify your account:

1. Check your email for a verification message from us
2. Click the verification link in the email
3. If the link has expired, you can request a new one from your account settings
4. Make sure to check your spam/junk folder
5. Add our email domain to your safe senders list

Verification is required within 48 hours of account creation.', ARRAY['verification', 'email', 'activate']),

(1, 4, 'How do I update my profile information?', 'To update your profile:

1. Log into your account
2. Go to ''Account Settings'' or ''Profile''
3. Click ''Edit Profile'' or the pencil icon
4. Update the information you want to change
5. Click ''Save Changes''
6. You may need to verify new email addresses

Some changes might require additional verification for security purposes.', ARRAY['profile', 'update', 'settings']);

-- Insert FAQ Items for Payment & Billing
INSERT INTO faq_items (category_id, subcategory_id, question, answer, tags) VALUES
(2, 1, 'My payment failed, what should I do?', 'If your payment failed:

1. Check that your card details are correct
2. Ensure your card has sufficient funds
3. Verify that your card is not expired
4. Check if your bank has blocked international transactions
5. Try using a different payment method
6. Clear your browser cache and try again

Some banks require you to authorize online payments. Contact your bank if the issue persists.', ARRAY['payment', 'failed', 'card', 'billing']),

(2, 2, 'How do I request a refund?', 'To request a refund:

1. Log into your account
2. Go to ''Order History'' or ''My Purchases''
3. Find the item you want to refund
4. Click ''Request Refund''
5. Select the reason for refund
6. Provide additional details if required
7. Submit the request

Refunds are processed within 5-7 business days. You''ll receive an email confirmation once processed.', ARRAY['refund', 'return', 'money back']),

(2, 3, 'I have issues with my invoice', 'For invoice-related problems:

1. Check your email for the invoice (including spam folder)
2. Log into your account and go to ''Billing'' section
3. Download invoices from your account dashboard
4. If you need a corrected invoice, contact our billing team
5. For tax-related invoice modifications, provide your tax information

Invoices are generated automatically after successful payments.', ARRAY['invoice', 'billing', 'receipt']),

(2, 4, 'How do I manage my subscription?', 'To manage your subscription:

1. Log into your account
2. Go to ''Subscription'' or ''Billing'' section
3. Here you can:
   - View current plan details
   - Upgrade or downgrade your plan
   - Cancel your subscription
   - Update payment method
   - View billing history

Changes take effect at the next billing cycle unless specified otherwise.', ARRAY['subscription', 'plan', 'billing', 'cancel']);

-- Insert FAQ Items for Technical Support
INSERT INTO faq_items (category_id, subcategory_id, question, answer, tags) VALUES
(3, 1, 'The website is not loading', 'If the website isn''t loading:

1. Check your internet connection
2. Try refreshing the page (Ctrl+F5 or Cmd+Shift+R)
3. Clear your browser cache and cookies
4. Try a different browser (Chrome, Firefox, Safari)
5. Disable browser extensions temporarily
6. Try incognito/private browsing mode
7. Check if the issue occurs on different devices

If the problem persists, there might be server maintenance ongoing.', ARRAY['website', 'loading', 'browser', 'connection']),

(3, 2, 'I''m having issues with the mobile app', 'For mobile app problems:

1. Force close and restart the app
2. Check if you have the latest app version
3. Update the app from App Store/Google Play
4. Restart your device
5. Check your internet connection
6. Clear app cache (Android) or reinstall (iOS)
7. Make sure your device OS is supported

Minimum requirements: iOS 12+ or Android 8+.', ARRAY['mobile', 'app', 'ios', 'android']),

(3, 3, 'The system is running slowly', 'To improve performance:

1. Close unnecessary browser tabs
2. Clear browser cache and cookies
3. Disable unnecessary browser extensions
4. Check your internet speed
5. Try using a wired connection instead of WiFi
6. Close other applications using internet
7. Try using a different browser

Optimal experience requires a stable internet connection of at least 5 Mbps.', ARRAY['performance', 'slow', 'speed', 'optimization']),

(3, 4, 'A feature is not working properly', 'If a feature isn''t working:

1. Try refreshing the page
2. Clear your browser cache
3. Check if JavaScript is enabled
4. Disable ad blockers temporarily
5. Try a different browser
6. Check if you have the required permissions
7. Ensure your browser is up to date

Some features require specific browser versions or settings to function properly.', ARRAY['feature', 'bug', 'functionality', 'browser']);

-- Insert FAQ Items for Product Information
INSERT INTO faq_items (category_id, subcategory_id, question, answer, tags) VALUES
(4, 1, 'What are the main product features?', 'Our main product features include:

• Advanced AI-powered chatbot system
• 24/7 customer support
• Multi-language support
• Integration with popular platforms
• Customizable responses and workflows
• Analytics and reporting dashboard
• Mobile-responsive design
• Enterprise-grade security

For detailed feature comparisons between plans, visit our pricing page.', ARRAY['features', 'capabilities', 'ai', 'chatbot']),

(4, 2, 'What are your pricing plans?', 'Our pricing plans:

**Basic Plan - $9/month:**
• Up to 1,000 conversations/month
• Email support
• Basic analytics

**Pro Plan - $29/month:**
• Up to 10,000 conversations/month
• Priority support
• Advanced analytics
• Custom branding

**Enterprise Plan - Custom:**
• Unlimited conversations
• Dedicated support
• Custom integrations
• SLA guarantee

All plans include a 14-day free trial.', ARRAY['pricing', 'plans', 'cost', 'subscription']),

(4, 3, 'What are the system requirements?', 'System requirements:

**Web Browser:**
• Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
• JavaScript enabled
• Cookies enabled

**Mobile App:**
• iOS 12.0+ (iPhone 6s or newer)
• Android 8.0+ (API level 26+)
• 2GB RAM minimum
• 100MB storage space

**Internet:**
• Stable connection (5 Mbps recommended)
• Ports 80 and 443 open for HTTPS traffic', ARRAY['requirements', 'browser', 'mobile', 'system']),

(4, 4, 'What integration options are available?', 'Available integrations:

**Communication Platforms:**
• WhatsApp Business API
• Facebook Messenger
• Telegram
• Slack
• Microsoft Teams

**CRM Systems:**
• Salesforce
• HubSpot
• Zoho CRM
• Pipedrive

**E-commerce:**
• Shopify
• WooCommerce
• Magento

**Other:**
• REST API for custom integrations
• Webhooks support
• Zapier compatibility', ARRAY['integration', 'api', 'whatsapp', 'crm', 'ecommerce']);

-- Sample WhatsApp transcript (for testing purposes)
INSERT INTO whatsapp_transcripts (wa_conversation_id, customer_phone, customer_name, agent_name, category, subcategory, resolved, resolution_summary, satisfaction_rating, messages, started_at, resolved_at) VALUES
('wa_conv_001', '+62812345678', 'John Doe', 'Agent Sarah', 'Account Issues', 'Login Problems', true, 'Customer was unable to login due to forgotten password. Agent helped reset password and customer successfully logged in.', 5, 
'[
  {
    "timestamp": "2024-01-15T10:00:00Z",
    "sender": "customer",
    "message": "Hi, I cannot login to my account"
  },
  {
    "timestamp": "2024-01-15T10:01:00Z",
    "sender": "agent",
    "message": "Hello! I''d be happy to help you with your login issue. Can you please provide your registered email address?"
  },
  {
    "timestamp": "2024-01-15T10:02:00Z",
    "sender": "customer",  
    "message": "Sure, it''s john.doe@email.com"
  },
  {
    "timestamp": "2024-01-15T10:03:00Z",
    "sender": "agent",
    "message": "Thank you. I see your account. Are you getting any specific error message when trying to login?"
  },
  {
    "timestamp": "2024-01-15T10:04:00Z",
    "sender": "customer",
    "message": "It just says invalid password, but I''m sure I''m using the right one"
  },
  {
    "timestamp": "2024-01-15T10:05:00Z",
    "sender": "agent",
    "message": "I understand. Let me send you a password reset link to your email. Please check your inbox and spam folder in a few minutes."
  },
  {
    "timestamp": "2024-01-15T10:10:00Z",
    "sender": "customer",
    "message": "Got it! I reset my password and I can login now. Thank you so much!"
  },
  {
    "timestamp": "2024-01-15T10:11:00Z",
    "sender": "agent",
    "message": "You''re welcome! I''m glad we could resolve this quickly. Is there anything else I can help you with today?"
  },
  {
    "timestamp": "2024-01-15T10:12:00Z",
    "sender": "customer",
    "message": "No, that''s all. Thanks again!"
  }
]'::jsonb, 
'2024-01-15T10:00:00Z', '2024-01-15T10:12:00Z');