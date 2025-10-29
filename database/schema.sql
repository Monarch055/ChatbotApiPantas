-- Supabase database schema for Chatbot API
-- Run these SQL commands in your Supabase SQL editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- FAQ Categories table
CREATE TABLE IF NOT EXISTS faq_categories (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- FAQ Subcategories table
CREATE TABLE IF NOT EXISTS faq_subcategories (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category_id BIGINT REFERENCES faq_categories(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- FAQ Items table
CREATE TABLE IF NOT EXISTS faq_items (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category_id BIGINT REFERENCES faq_categories(id) ON DELETE CASCADE,
    subcategory_id BIGINT REFERENCES faq_subcategories(id) ON DELETE CASCADE,
    question TEXT,
    answer TEXT NOT NULL,
    tags TEXT[],
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chat Sessions table
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id TEXT,
    stage TEXT DEFAULT 'active' CHECK (stage IN ('active', 'completed', 'escalated')),
    current_category_id BIGINT REFERENCES faq_categories(id),
    menu_map JSONB,
    helpful BOOLEAN,
    escalated BOOLEAN DEFAULT FALSE,
    escalated_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chat Messages table
CREATE TABLE IF NOT EXISTS chat_messages (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    tokens_used INTEGER,
    model_used TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- WhatsApp Transcripts table (for storing resolved human conversations)
CREATE TABLE IF NOT EXISTS whatsapp_transcripts (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    wa_conversation_id TEXT UNIQUE,
    customer_phone TEXT,
    customer_name TEXT,
    agent_name TEXT,
    category TEXT,
    subcategory TEXT,
    resolved BOOLEAN DEFAULT TRUE,
    resolution_summary TEXT,
    satisfaction_rating INTEGER CHECK (satisfaction_rating BETWEEN 1 AND 5),
    messages JSONB NOT NULL, -- Array of message objects
    started_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_faq_categories_active ON faq_categories(is_active, display_order);
CREATE INDEX IF NOT EXISTS idx_faq_subcategories_category ON faq_subcategories(category_id, is_active, display_order);
CREATE INDEX IF NOT EXISTS idx_faq_items_category_subcategory ON faq_items(category_id, subcategory_id, is_active);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user ON chat_sessions(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON chat_messages(session_id, created_at);
CREATE INDEX IF NOT EXISTS idx_whatsapp_transcripts_phone ON whatsapp_transcripts(customer_phone, created_at);

-- Full-text search index for FAQ answers (PostgreSQL specific)
CREATE INDEX IF NOT EXISTS idx_faq_items_answer_fts ON faq_items USING gin(to_tsvector('english', answer));

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers to automatically update updated_at
CREATE TRIGGER update_faq_categories_updated_at BEFORE UPDATE ON faq_categories 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_faq_subcategories_updated_at BEFORE UPDATE ON faq_subcategories 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_faq_items_updated_at BEFORE UPDATE ON faq_items 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chat_sessions_updated_at BEFORE UPDATE ON chat_sessions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_whatsapp_transcripts_updated_at BEFORE UPDATE ON whatsapp_transcripts 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) policies
-- Note: Adjust these based on your security requirements

-- Enable RLS
ALTER TABLE faq_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE faq_subcategories ENABLE ROW LEVEL SECURITY;
ALTER TABLE faq_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE whatsapp_transcripts ENABLE ROW LEVEL SECURITY;

-- Policies for FAQ tables (public read, authenticated write)
CREATE POLICY "FAQ categories are viewable by everyone" ON faq_categories FOR SELECT USING (is_active = true);
CREATE POLICY "FAQ subcategories are viewable by everyone" ON faq_subcategories FOR SELECT USING (is_active = true);
CREATE POLICY "FAQ items are viewable by everyone" ON faq_items FOR SELECT USING (is_active = true);

-- Policies for chat sessions (users can only access their own sessions)
-- Note: This assumes you'll implement user authentication
CREATE POLICY "Users can view own chat sessions" ON chat_sessions FOR SELECT USING (true); -- Adjust based on auth
CREATE POLICY "Users can create chat sessions" ON chat_sessions FOR INSERT WITH CHECK (true); -- Adjust based on auth
CREATE POLICY "Users can update own chat sessions" ON chat_sessions FOR UPDATE USING (true); -- Adjust based on auth

-- Policies for chat messages
CREATE POLICY "Users can view messages from accessible sessions" ON chat_messages FOR SELECT USING (true); -- Adjust based on auth
CREATE POLICY "Users can create messages" ON chat_messages FOR INSERT WITH CHECK (true); -- Adjust based on auth

-- Policies for WhatsApp transcripts (admin only)
CREATE POLICY "Admins can manage WhatsApp transcripts" ON whatsapp_transcripts FOR ALL USING (true); -- Adjust based on role