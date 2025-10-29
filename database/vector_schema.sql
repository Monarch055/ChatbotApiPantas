-- Enhanced schema with vector search capabilities
-- Run this in your Supabase SQL Editor

-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Add embedding column to faq_items
ALTER TABLE faq_items 
ADD COLUMN IF NOT EXISTS content_embedding vector(1536);

-- Create index for vector similarity search
CREATE INDEX IF NOT EXISTS idx_faq_items_embedding 
ON faq_items USING ivfflat (content_embedding vector_cosine_ops) 
WITH (lists = 100);

-- Add full-text search capability
ALTER TABLE faq_items 
ADD COLUMN IF NOT EXISTS search_content tsvector 
GENERATED ALWAYS AS (
  to_tsvector('indonesian', coalesce(question, '') || ' ' || coalesce(answer, ''))
) STORED;

-- Create index for full-text search
CREATE INDEX IF NOT EXISTS idx_faq_items_search_content 
ON faq_items USING gin(search_content);

-- Create documents table for additional knowledge base
CREATE TABLE IF NOT EXISTS documents (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    document_type TEXT DEFAULT 'sop' CHECK (document_type IN ('sop', 'guide', 'manual', 'faq')),
    tags TEXT[],
    content_embedding vector(1536),
    search_content tsvector GENERATED ALWAYS AS (
        to_tsvector('indonesian', title || ' ' || content)
    ) STORED,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for documents
CREATE INDEX IF NOT EXISTS idx_documents_embedding 
ON documents USING ivfflat (content_embedding vector_cosine_ops) 
WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_documents_search_content 
ON documents USING gin(search_content);

CREATE INDEX IF NOT EXISTS idx_documents_type_active 
ON documents(document_type, is_active);

-- Function to search similar content
CREATE OR REPLACE FUNCTION search_similar_content(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id bigint,
    title text,
    content text,
    document_type text,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.id,
        d.title,
        d.content,
        d.document_type,
        1 - (d.content_embedding <=> query_embedding) as similarity
    FROM documents d
    WHERE d.is_active = true
    AND 1 - (d.content_embedding <=> query_embedding) > match_threshold
    ORDER BY d.content_embedding <=> query_embedding
    LIMIT match_count;
END;
$$;