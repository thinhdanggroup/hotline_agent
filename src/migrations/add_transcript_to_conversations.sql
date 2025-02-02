-- Add transcript column to conversations table
alter table conversations 
add transcript jsonb;
