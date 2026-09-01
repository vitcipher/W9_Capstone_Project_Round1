-- Property Ledger — Supabase schema
-- Run this in the Supabase SQL Editor (Project → SQL Editor → New query) once,
-- on a fresh project. Safe to re-run: uses IF NOT EXISTS / CREATE OR REPLACE
-- where practical, but DROP + re-run is the simplest path if you're iterating.
--
-- Design principle: every table has an `owner_id` pointing at auth.users(id),
-- and Row Level Security enforces `owner_id = auth.uid()` at the database
-- layer — not just filtered in the Streamlit app. That's the actual privacy
-- guarantee the "tenants/documents private to themselves" requirement needs;
-- app-level filtering alone is one bug away from leaking another landlord's
-- data.

-- ============================================================
-- properties — replaces data/synthetic_landlord_portfolio.csv
-- ============================================================
create table if not exists properties (
    id uuid primary key default gen_random_uuid(),
    owner_id uuid not null references auth.users(id) on delete cascade,
    nickname text not null,
    city text,
    region text,
    living_space_sqm numeric,
    no_rooms integer,
    year_construction integer,
    purchase_year integer,
    purchase_price numeric,
    current_valuation_estimate numeric,
    loan_amount numeric,
    interest_rate_annual numeric,
    loan_term_years integer,
    monthly_emi numeric,
    monthly_base_rent numeric,
    monthly_nebenkosten_budget numeric,
    monthly_property_mgmt_fee numeric,
    monthly_maintenance_reserve numeric,
    monthly_insurance numeric,
    monthly_property_tax numeric,
    created_at timestamptz not null default now()
);

alter table properties enable row level security;

create policy "properties_select_own" on properties
    for select using (owner_id = auth.uid());
create policy "properties_insert_own" on properties
    for insert with check (owner_id = auth.uid());
create policy "properties_update_own" on properties
    for update using (owner_id = auth.uid());
create policy "properties_delete_own" on properties
    for delete using (owner_id = auth.uid());

-- ============================================================
-- tenants — new table (not in the CSV-based POC)
-- ============================================================
create table if not exists tenants (
    id uuid primary key default gen_random_uuid(),
    owner_id uuid not null references auth.users(id) on delete cascade,
    property_id uuid not null references properties(id) on delete cascade,
    tenant_name text not null,
    contact_email text,
    contact_phone text,
    lease_start_date date,
    lease_end_date date,
    monthly_rent_eur numeric,
    deposit_eur numeric,
    notice_period_months integer,
    created_at timestamptz not null default now()
);

alter table tenants enable row level security;

create policy "tenants_select_own" on tenants
    for select using (owner_id = auth.uid());
create policy "tenants_insert_own" on tenants
    for insert with check (owner_id = auth.uid());
create policy "tenants_update_own" on tenants
    for update using (owner_id = auth.uid());
create policy "tenants_delete_own" on tenants
    for delete using (owner_id = auth.uid());

-- ============================================================
-- monthly_transactions — replaces synthetic_monthly_transactions.csv
-- ============================================================
create table if not exists monthly_transactions (
    id uuid primary key default gen_random_uuid(),
    owner_id uuid not null references auth.users(id) on delete cascade,
    property_id uuid not null references properties(id) on delete cascade,
    month date not null,  -- store as the 1st of the month, e.g. 2026-09-01
    occupancy text not null check (occupancy in ('Occupied', 'Vacant')),
    rent_collected numeric not null default 0,
    nebenkosten_collected numeric not null default 0,
    nebenkosten_spent numeric not null default 0,
    maintenance_spike numeric not null default 0,
    mortgage_emi numeric not null default 0,
    total_income numeric not null default 0,
    total_expenses_ex_emi numeric not null default 0,
    net_cashflow numeric not null default 0,
    created_at timestamptz not null default now(),
    unique (property_id, month)
);

alter table monthly_transactions enable row level security;

create policy "transactions_select_own" on monthly_transactions
    for select using (owner_id = auth.uid());
create policy "transactions_insert_own" on monthly_transactions
    for insert with check (owner_id = auth.uid());
create policy "transactions_update_own" on monthly_transactions
    for update using (owner_id = auth.uid());
create policy "transactions_delete_own" on monthly_transactions
    for delete using (owner_id = auth.uid());

-- ============================================================
-- documents — replaces the in-memory "confirmed_records" list in
-- app/streamlit_app.py (the AI-extracted, human-confirmed drafts)
-- ============================================================
create table if not exists documents (
    id uuid primary key default gen_random_uuid(),
    owner_id uuid not null references auth.users(id) on delete cascade,
    property_id uuid not null references properties(id) on delete cascade,
    document_type text not null,  -- rental_contract | rent_receipt | emi_statement | nebenkosten_invoice
    extracted_fields jsonb not null default '{}'::jsonb,
    confidence numeric,
    needs_human_review boolean not null default false,
    confirmed_at timestamptz not null default now()
);

alter table documents enable row level security;

create policy "documents_select_own" on documents
    for select using (owner_id = auth.uid());
create policy "documents_insert_own" on documents
    for insert with check (owner_id = auth.uid());
create policy "documents_update_own" on documents
    for update using (owner_id = auth.uid());
create policy "documents_delete_own" on documents
    for delete using (owner_id = auth.uid());

-- ============================================================
-- maintenance_requests — replaces synthetic_maintenance_requests.csv
-- ============================================================
create table if not exists maintenance_requests (
    id uuid primary key default gen_random_uuid(),
    owner_id uuid not null references auth.users(id) on delete cascade,
    property_id uuid not null references properties(id) on delete cascade,
    description text not null,
    urgency text not null default 'Medium' check (urgency in ('Low', 'Medium', 'High')),
    status text not null default 'New' check (status in ('New', 'In Progress', 'Resolved')),
    created_date date not null default current_date
);

alter table maintenance_requests enable row level security;

create policy "maintenance_select_own" on maintenance_requests
    for select using (owner_id = auth.uid());
create policy "maintenance_insert_own" on maintenance_requests
    for insert with check (owner_id = auth.uid());
create policy "maintenance_update_own" on maintenance_requests
    for update using (owner_id = auth.uid());
create policy "maintenance_delete_own" on maintenance_requests
    for delete using (owner_id = auth.uid());

-- ============================================================
-- Helpful indexes (RLS already filters by owner_id on every query,
-- so it should always be part of the index for these lookups)
-- ============================================================
create index if not exists idx_properties_owner on properties(owner_id);
create index if not exists idx_tenants_owner on tenants(owner_id);
create index if not exists idx_tenants_property on tenants(property_id);
create index if not exists idx_transactions_owner on monthly_transactions(owner_id);
create index if not exists idx_transactions_property on monthly_transactions(property_id);
create index if not exists idx_documents_owner on documents(owner_id);
create index if not exists idx_documents_property on documents(property_id);
create index if not exists idx_maintenance_owner on maintenance_requests(owner_id);
create index if not exists idx_maintenance_property on maintenance_requests(property_id);
