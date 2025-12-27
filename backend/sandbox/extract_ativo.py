#!/usr/bin/env python3
"""
Extract a list of all distinct Ativo values from BOVA.db
"""

import sqlite3
import sys
from pathlib import Path


def extract_ativo_list(db_path, output_file=None):
    """Extract all distinct Ativo values from the database."""
    
    if not Path(db_path).exists():
        print(f"Error: Database file '{db_path}' not found!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Find the options table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        options_table = None
        for table_tuple in tables:
            table_name = table_tuple[0]
            # Check if table has Ativo column
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            if 'Ativo' in column_names:
                options_table = table_name
                break
        
        if not options_table:
            print("Error: No table with 'Ativo' column found in the database.")
            conn.close()
            return
        
        # Extract distinct Ativo values
        cursor.execute(f"""
            SELECT DISTINCT Ativo 
            FROM {options_table} 
            WHERE Ativo IS NOT NULL 
            ORDER BY Ativo;
        """)
        
        ativo_list = [row[0] for row in cursor.fetchall()]
        
        # Also get counts for each Ativo
        cursor.execute(f"""
            SELECT Ativo, COUNT(*) as count 
            FROM {options_table} 
            WHERE Ativo IS NOT NULL 
            GROUP BY Ativo 
            ORDER BY count DESC;
        """)
        
        ativo_counts = cursor.fetchall()
        
        conn.close()
        
        # Print results
        print("=" * 80)
        print(f"Ativo values from {db_path}")
        print("=" * 80)
        print(f"\nFound {len(ativo_list)} distinct Ativo value(s):\n")
        
        # Print with counts
        print("Ativo (sorted by count):")
        print("-" * 80)
        for ativo, count in ativo_counts:
            print(f"  • {ativo:40} {count:>12,} rows")
        
        print("\n" + "=" * 80)
        print("Ativo (alphabetically sorted):")
        print("-" * 80)
        for ativo in ativo_list:
            print(f"  • {ativo}")
        
        # Save to file if requested
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("# List of all Ativo values\n")
                f.write(f"# Extracted from: {db_path}\n")
                f.write(f"# Total distinct values: {len(ativo_list)}\n\n")
                for ativo in ativo_list:
                    f.write(f"{ativo}\n")
            print(f"\n✅ Ativo list saved to: {output_file}")
        
        # Also print as Python list format
        print("\n" + "=" * 80)
        print("Python list format:")
        print("-" * 80)
        print("ativo_list = [")
        for ativo in ativo_list:
            print(f"    '{ativo}',")
        print("]")
        
        return ativo_list
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Default database path
    db_path = Path(__file__).parent / "BOVA.db"
    
    # Allow command-line arguments
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    
    output_file = None
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    extract_ativo_list(db_path, output_file)

