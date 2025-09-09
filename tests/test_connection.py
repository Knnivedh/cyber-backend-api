#!/usr/bin/env python3
"""
Simple Supabase Connection Test
"""

from supabase import create_client

# Supabase credentials
url = "https://odczfcygmifymbfqpmra.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9kY3pmY3lnbWlmeW1iZnFwbXJhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NzA2OTE4NSwiZXhwIjoyMDcyNjQ1MTg1fQ.cY7wGRfVTxRyFPpf3Of27Q_xHFXqjQAzce2-b5pwlMs"

try:
    supabase = create_client(url, key)
    print("✅ Supabase client created successfully")

    # Test connection with a simple query
    result = supabase.table('expert_knowledge').select('id', count='exact').limit(1).execute()
    print(f"✅ Database connection successful - found {result.count} records")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
