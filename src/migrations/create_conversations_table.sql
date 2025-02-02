-- Create conversations table
create table if not exists conversations (
    id uuid primary key,
    room_url text not null,
    created_at timestamp with time zone not null default timezone('utc'::text, now()),
    updated_at timestamp with time zone,
    contact jsonb,
    status text not null default 'active'::text,
    constraint conversations_status_check check (status in ('active', 'ended'))
);

-- Create index on room_url for faster lookups
create index if not exists conversations_room_url_idx on conversations(room_url);

-- Add comment to table
comment on table conversations is 'Stores conversation records with contact information';

-- Add comments to columns
comment on column conversations.id is 'Unique identifier for the conversation';
comment on column conversations.room_url is 'Daily room URL associated with the conversation';
comment on column conversations.created_at is 'Timestamp when the conversation was created';
comment on column conversations.updated_at is 'Timestamp when the conversation was last updated';
comment on column conversations.contact is 'JSONB column storing contact information (email, phone)';
comment on column conversations.status is 'Current status of the conversation (active/ended)';
