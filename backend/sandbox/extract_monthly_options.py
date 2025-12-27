#!/usr/bin/env python3
"""
Extract monthly options from BOVA.db to a new database.

Monthly options are those that don't have 'W' in their ticker name.
Weekly options have W1, W2, W3, etc. in the ticker.
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime


def extract_monthly_options(source_db, output_db):
    """
    Extract monthly options from source database to output database.
    
    Args:
        source_db: Path to source database (BOVA.db)
        output_db: Path to output database
    """
    source_path = Path(source_db)
    output_path = Path(output_db)
    
    if not source_path.exists():
        print(f"Error: Source database '{source_path}' not found!")
        return False
    
    print("=" * 80)
    print("EXTRACTING MONTHLY OPTIONS FROM BOVA.DB")
    print("=" * 80)
    print(f"Source: {source_path}")
    print(f"Output: {output_path}")
    print("=" * 80)
    
    # Connect to source database
    source_conn = sqlite3.connect(source_path)
    source_cursor = source_conn.cursor()
    
    # Connect to output database (will be created if doesn't exist)
    output_conn = sqlite3.connect(output_path)
    output_cursor = output_conn.cursor()
    
    try:
        # Get table schema from source
        print("\n1. Getting table schema...")
        source_cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='options_data'")
        schema_result = source_cursor.fetchone()
        
        if not schema_result:
            print("Error: 'options_data' table not found in source database!")
            return False
        
        create_table_sql = schema_result[0]
        
        # Create table in output database
        print("2. Creating table in output database...")
        output_cursor.execute("DROP TABLE IF EXISTS options_data")
        output_cursor.execute(create_table_sql)
        
        # sqlite_sequence will be created automatically by SQLite if needed
        
        # Count total records
        source_cursor.execute("SELECT COUNT(*) FROM options_data")
        total_records = source_cursor.fetchone()[0]
        print(f"   Total records in source: {total_records:,}")
        
        # Extract monthly options (those without 'W' in ticker) and all underlying assets
        print("\n3. Extracting monthly options...")
        print("   (Monthly = ticker doesn't contain 'W', Weekly = ticker contains 'W1', 'W2', etc.)")
        
        # Get counts
        source_cursor.execute("""
            SELECT 
                Tipo,
                COUNT(*) as count,
                COUNT(CASE WHEN Ativo LIKE '%W%' THEN 1 END) as weekly_count,
                COUNT(CASE WHEN Ativo NOT LIKE '%W%' OR Ativo IS NULL THEN 1 END) as monthly_count
            FROM options_data
            GROUP BY Tipo
        """)
        
        print("\n   Breakdown by type:")
        for row in source_cursor.fetchall():
            tipo, total, weekly, monthly = row
            print(f"     {tipo:20} | Total: {total:>10,} | Weekly: {weekly:>10,} | Monthly: {monthly:>10,}")
        
        # Extract monthly options and all underlying assets
        print("\n4. Copying data...")
        
        # Get column names for proper insertion
        source_cursor.execute("PRAGMA table_info(options_data)")
        columns = [row[1] for row in source_cursor.fetchall()]
        column_list = ','.join(columns)
        placeholders = ','.join(['?' for _ in columns])
        insert_sql = f"INSERT INTO options_data ({column_list}) VALUES ({placeholders})"
        
        # First, copy all underlying assets (AtivoSubjacente)
        source_cursor.execute("""
            SELECT COUNT(*) FROM options_data WHERE Tipo = 'AtivoSubjacente'
        """)
        underlying_count = source_cursor.fetchone()[0]
        print(f"   Copying {underlying_count:,} underlying asset records...")
        
        source_cursor.execute("""
            SELECT * FROM options_data WHERE Tipo = 'AtivoSubjacente'
        """)
        underlying_batch = source_cursor.fetchall()
        
        if underlying_batch:
            output_cursor.executemany(insert_sql, underlying_batch)
            print(f"     ✓ Copied {len(underlying_batch):,} underlying asset records")
        
        # Copy monthly options (CALL and PUT without 'W' in ticker)
        source_cursor.execute("""
            SELECT COUNT(*) FROM options_data 
            WHERE Tipo IN ('CALL', 'PUT') 
            AND (Ativo NOT LIKE '%W%' OR Ativo IS NULL)
        """)
        monthly_options_count = source_cursor.fetchone()[0]
        print(f"   Copying {monthly_options_count:,} monthly option records...")
        
        # Use a more efficient approach: copy in batches
        batch_size = 100000
        offset = 0
        total_copied = 0
        
        while True:
            source_cursor.execute(f"""
                SELECT {column_list} FROM options_data 
                WHERE Tipo IN ('CALL', 'PUT') 
                AND (Ativo NOT LIKE '%W%' OR Ativo IS NULL)
                LIMIT ? OFFSET ?
            """, (batch_size, offset))
            
            batch = source_cursor.fetchall()
            if not batch:
                break
            
            output_cursor.executemany(insert_sql, batch)
            total_copied += len(batch)
            offset += batch_size
            
            if len(batch) < batch_size:
                break
            
            if total_copied % 100000 == 0:
                print(f"     Copied {total_copied:,} records...")
        
        print(f"     ✓ Copied {total_copied:,} monthly option records")
        
        # Commit changes
        output_conn.commit()
        
        # Verify output
        output_cursor.execute("SELECT COUNT(*) FROM options_data")
        output_count = output_cursor.fetchone()[0]
        
        output_cursor.execute("""
            SELECT Tipo, COUNT(*) 
            FROM options_data 
            GROUP BY Tipo
        """)
        
        print("\n5. Verification:")
        print(f"   Total records in output: {output_count:,}")
        print("\n   Breakdown by type in output database:")
        for row in output_cursor.fetchall():
            print(f"     {row[0]:20} | {row[1]:>10,} records")
        
        # Check for any weekly options that might have slipped through
        output_cursor.execute("""
            SELECT COUNT(*) FROM options_data 
            WHERE Tipo IN ('CALL', 'PUT') 
            AND Ativo LIKE '%W%'
        """)
        weekly_in_output = output_cursor.fetchone()[0]
        
        if weekly_in_output > 0:
            print(f"\n   WARNING: Found {weekly_in_output} weekly options in output!")
        else:
            print("\n   ✓ No weekly options found in output (good!)")
        
        print("\n" + "=" * 80)
        print("EXTRACTION COMPLETE!")
        print("=" * 80)
        print(f"Output database: {output_path.absolute()}")
        print(f"Total records: {output_count:,}")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        output_conn.rollback()
        return False
        
    finally:
        source_conn.close()
        output_conn.close()


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract monthly options from BOVA.db')
    parser.add_argument('--source', type=str, default='BOVA.db', help='Source database path')
    parser.add_argument('--output', type=str, default='BOVA_monthly.db', help='Output database path')
    
    args = parser.parse_args()
    
    source_db = Path(__file__).parent / args.source
    output_db = Path(__file__).parent / args.output
    
    success = extract_monthly_options(source_db, output_db)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()

