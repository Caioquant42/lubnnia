#!/usr/bin/env python3
"""
Simple script to identify and explore data in combine_all_may.db
"""

import sqlite3
import sys
from pathlib import Path
from io import StringIO
from datetime import datetime


class TeeOutput:
    """Write to both stdout and a buffer."""
    def __init__(self, stdout, buffer):
        self.stdout = stdout
        self.buffer = buffer
    
    def write(self, text):
        self.stdout.write(text)
        self.buffer.write(text)
    
    def flush(self):
        self.stdout.flush()
        self.buffer.flush()


def inspect_database(db_path, output_file=None):
    """Inspect the database and print information about its structure and data.
    
    Args:
        db_path: Path to the database file
        output_file: Optional path to save output to a text file
    """
    
    # Capture output if output_file is specified
    output_buffer = None
    original_stdout = None
    if output_file:
        output_buffer = StringIO()
        original_stdout = sys.stdout
        sys.stdout = TeeOutput(original_stdout, output_buffer)
    
    try:
        if not Path(db_path).exists():
            print(f"Error: Database file '{db_path}' not found!")
            if output_file and original_stdout:
                sys.stdout = original_stdout
            return
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=" * 80)
        print(f"Database: {db_path}")
        print("=" * 80)
        print()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("No tables found in the database.")
            return
        
        print(f"Found {len(tables)} table(s):")
        print("-" * 80)
        
        for table_tuple in tables:
            table_name = table_tuple[0]
            print(f"\n📊 Table: {table_name}")
            print("-" * 80)
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            row_count = cursor.fetchone()[0]
            print(f"  Row count: {row_count:,}")
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            print(f"\n  Columns ({len(columns)}):")
            print("  " + "-" * 76)
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                pk_str = " [PRIMARY KEY]" if pk else ""
                null_str = " NOT NULL" if not_null else ""
                default_str = f" DEFAULT {default_val}" if default_val else ""
                print(f"    • {col_name:30} {col_type:15}{pk_str}{null_str}{default_str}")
            
            # Show sample data (first 5 rows)
            if row_count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
                sample_rows = cursor.fetchall()
                
                print(f"\n  Sample data (first {min(5, len(sample_rows))} rows):")
                print("  " + "-" * 76)
                
                # Get column names for header
                column_names = [col[1] for col in columns]
                
                # Print header
                header = " | ".join([f"{name:15}" for name in column_names[:5]])  # Show first 5 columns
                if len(column_names) > 5:
                    header += f" ... ({len(column_names) - 5} more columns)"
                print(f"    {header}")
                print("  " + "-" * 76)
                
                # Print sample rows
                for row in sample_rows:
                    row_str = " | ".join([f"{str(val):15}"[:15] for val in row[:5]])
                    if len(row) > 5:
                        row_str += f" ... ({len(row) - 5} more values)"
                    print(f"    {row_str}")
            
            # Show samples grouped by categorical columns
            if row_count > 0:
                column_names = [col[1] for col in columns]
                column_types = {col[1]: col[2] for col in columns}
                
                # Identify categorical columns (TEXT columns that might have distinct values)
                categorical_columns = []
                for col_name, col_type in column_types.items():
                    if col_type.upper() in ['TEXT', 'VARCHAR', 'CHAR']:
                        # Check how many distinct values this column has
                        try:
                            cursor.execute(f"""
                                SELECT COUNT(DISTINCT {col_name}) 
                                FROM {table_name} 
                                WHERE {col_name} IS NOT NULL;
                            """)
                            distinct_count = cursor.fetchone()[0]
                            # Consider it categorical if it has between 2 and 50 distinct values
                            if 2 <= distinct_count <= 50:
                                categorical_columns.append((col_name, distinct_count))
                        except sqlite3.Error:
                            pass  # Skip if column name causes issues
                
                if categorical_columns:
                    print(f"\n  📋 Sample data grouped by categorical columns:")
                    print("  " + "-" * 76)
                    
                    for col_name, distinct_count in categorical_columns[:5]:  # Limit to first 5 categorical columns
                        print(f"\n    🔹 {col_name} ({distinct_count} distinct values):")
                        print("    " + "-" * 74)
                        
                        # Get distinct values
                        cursor.execute(f"""
                            SELECT DISTINCT {col_name} 
                            FROM {table_name} 
                            WHERE {col_name} IS NOT NULL 
                            ORDER BY {col_name} 
                            LIMIT 20;
                        """)
                        distinct_values = [row[0] for row in cursor.fetchall()]
                        
                        # Show sample for each distinct value (limit to first 10 values)
                        for i, value in enumerate(distinct_values[:10], 1):
                            # Get count for this value
                            cursor.execute(f"""
                                SELECT COUNT(*) 
                                FROM {table_name} 
                                WHERE {col_name} = ?;
                            """, (value,))
                            count = cursor.fetchone()[0]
                            
                            print(f"\n      {i}. {col_name} = '{value}' ({count:,} rows)")
                            
                            # Get sample rows for this value
                            cursor.execute(f"""
                                SELECT * 
                                FROM {table_name} 
                                WHERE {col_name} = ? 
                                LIMIT 3;
                            """, (value,))
                            sample_rows = cursor.fetchall()
                            
                            if sample_rows:
                                # Show first few columns of sample
                                for row in sample_rows:
                                    row_str = " | ".join([f"{str(val):20}"[:20] for val in row[:4]])
                                    if len(row) > 4:
                                        row_str += f" ... ({len(row) - 4} more columns)"
                                    print(f"         {row_str}")
                        
                        if len(distinct_values) > 10:
                            print(f"\n      ... and {len(distinct_values) - 10} more distinct values")
            
            print()
        
        # Additional analysis for options_data table
        options_table = None
        for table_tuple in tables:
            if 'options' in table_tuple[0].lower() or 'data' in table_tuple[0].lower():
                options_table = table_tuple[0]
                break
        
        if options_table:
            print("=" * 80)
            print("📈 OPTIONS DATA ANALYSIS")
            print("=" * 80)
            print()
            
            # Check if columns exist
            cursor.execute(f"PRAGMA table_info({options_table});")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            # Analyze Tipo column
            if 'Tipo' in column_names:
                print("🔍 Tipo Analysis:")
                print("-" * 80)
                cursor.execute(f"""
                    SELECT Tipo, COUNT(*) as count 
                    FROM {options_table} 
                    WHERE Tipo IS NOT NULL 
                    GROUP BY Tipo 
                    ORDER BY count DESC;
                """)
                tipo_results = cursor.fetchall()
                
                if tipo_results:
                    total_tipo = sum(row[1] for row in tipo_results)
                    for tipo, count in tipo_results:
                        percentage = (count / total_tipo) * 100
                        print(f"  • {tipo:30} {count:>12,} rows ({percentage:5.2f}%)")
                    print(f"\n  Total distinct Tipo values: {len(tipo_results)}")
                    
                    # Show sample data for each Tipo
                    print("\n  📊 Sample data for each Tipo:")
                    print("  " + "-" * 76)
                    
                    # Get column names for display
                    display_columns = ['Ativo', 'Data', 'Tipo', 'K', 'Vencimento', 'Dias4Vencimento', 'Bid', 'Ask']
                    available_columns = [col for col in display_columns if col in column_names]
                    
                    for tipo, count in tipo_results:
                        print(f"\n    🔸 Tipo: '{tipo}' ({count:,} rows)")
                        print("    " + "-" * 74)
                        
                        # Get sample rows for this Tipo
                        cursor.execute(f"""
                            SELECT * 
                            FROM {options_table} 
                            WHERE Tipo = ? 
                            LIMIT 5;
                        """, (tipo,))
                        sample_rows = cursor.fetchall()
                        
                        if sample_rows:
                            # Create header with available columns
                            col_indices = [column_names.index(col) for col in available_columns if col in column_names]
                            header = " | ".join([f"{col:15}" for col in available_columns[:6]])
                            if len(available_columns) > 6:
                                header += f" ... ({len(available_columns) - 6} more)"
                            print(f"      {header}")
                            print("    " + "-" * 74)
                            
                            # Print sample rows
                            for row in sample_rows:
                                row_values = [str(row[column_names.index(col)]) if col in column_names else '' 
                                            for col in available_columns[:6]]
                                row_str = " | ".join([f"{val:15}"[:15] for val in row_values])
                                if len(available_columns) > 6:
                                    row_str += f" ... ({len(available_columns) - 6} more)"
                                print(f"      {row_str}")
                else:
                    print("  No Tipo data found")
                print()
            
            # Analyze Ativo column (show samples)
            if 'Ativo' in column_names:
                print("🔍 Ativo Analysis:")
                print("-" * 80)
                cursor.execute(f"""
                    SELECT Ativo, COUNT(*) as count 
                    FROM {options_table} 
                    WHERE Ativo IS NOT NULL 
                    GROUP BY Ativo 
                    ORDER BY count DESC
                    LIMIT 20;
                """)
                ativo_results = cursor.fetchall()
                
                if ativo_results:
                    total_ativo = sum(row[1] for row in ativo_results)
                    print(f"  Top {len(ativo_results)} Ativo values (showing first 20):")
                    for ativo, count in ativo_results:
                        percentage = (count / total_ativo) * 100 if total_ativo > 0 else 0
                        print(f"  • {ativo:30} {count:>12,} rows ({percentage:5.2f}%)")
                    
                    # Show sample data for top 5 Ativo values
                    print("\n  📊 Sample data for top 5 Ativo values:")
                    print("  " + "-" * 76)
                    
                    display_columns = ['Ativo', 'Data', 'Tipo', 'K', 'Vencimento', 'Dias4Vencimento']
                    available_columns = [col for col in display_columns if col in column_names]
                    
                    for ativo, count in ativo_results[:5]:
                        print(f"\n    🔸 Ativo: '{ativo}' ({count:,} rows)")
                        print("    " + "-" * 74)
                        
                        # Get sample rows for this Ativo
                        cursor.execute(f"""
                            SELECT * 
                            FROM {options_table} 
                            WHERE Ativo = ? 
                            LIMIT 3;
                        """, (ativo,))
                        sample_rows = cursor.fetchall()
                        
                        if sample_rows:
                            header = " | ".join([f"{col:15}" for col in available_columns[:5]])
                            if len(available_columns) > 5:
                                header += f" ... ({len(available_columns) - 5} more)"
                            print(f"      {header}")
                            print("    " + "-" * 74)
                            
                            for row in sample_rows:
                                row_values = [str(row[column_names.index(col)]) if col in column_names else '' 
                                            for col in available_columns[:5]]
                                row_str = " | ".join([f"{val:15}"[:15] for val in row_values])
                                if len(available_columns) > 5:
                                    row_str += f" ... ({len(available_columns) - 5} more)"
                                print(f"      {row_str}")
                print()
            
            # Analyze Dias4Vencimento column
            if 'Dias4Vencimento' in column_names:
                print("📅 Dias4Vencimento (Days to Expiration) Analysis:")
                print("-" * 80)
                
                # Basic statistics
                cursor.execute(f"""
                    SELECT 
                        MIN(Dias4Vencimento) as min_days,
                        MAX(Dias4Vencimento) as max_days,
                        AVG(Dias4Vencimento) as avg_days,
                        COUNT(DISTINCT Dias4Vencimento) as distinct_values,
                        COUNT(*) as total_rows
                    FROM {options_table}
                    WHERE Dias4Vencimento IS NOT NULL;
                """)
                stats = cursor.fetchone()
                
                if stats and stats[4] > 0:
                    min_days, max_days, avg_days, distinct_values, total_rows = stats
                    print(f"  Min days to expiration:    {int(min_days) if min_days else 'N/A':>10}")
                    print(f"  Max days to expiration:    {int(max_days) if max_days else 'N/A':>10}")
                    print(f"  Average days to expiration: {avg_days:>10.2f}")
                    print(f"  Distinct expiration days:   {distinct_values:>10}")
                    print(f"  Total rows with data:       {total_rows:>10,}")
                    print()
                    
                    # Distribution by ranges
                    print("  Distribution by day ranges:")
                    print("  " + "-" * 76)
                    ranges = [
                        (0, 7, "0-7 days (Weekly)"),
                        (8, 14, "8-14 days"),
                        (15, 30, "15-30 days"),
                        (31, 60, "31-60 days"),
                        (61, 90, "61-90 days"),
                        (91, 180, "91-180 days"),
                        (181, 365, "181-365 days"),
                        (366, None, "366+ days")
                    ]
                    
                    for min_range, max_range, label in ranges:
                        if max_range is None:
                            query = f"""
                                SELECT COUNT(*) 
                                FROM {options_table} 
                                WHERE Dias4Vencimento >= {min_range};
                            """
                        else:
                            query = f"""
                                SELECT COUNT(*) 
                                FROM {options_table} 
                                WHERE Dias4Vencimento >= {min_range} AND Dias4Vencimento <= {max_range};
                            """
                        cursor.execute(query)
                        count = cursor.fetchone()[0]
                        percentage = (count / total_rows) * 100 if total_rows > 0 else 0
                        print(f"    {label:25} {count:>12,} rows ({percentage:5.2f}%)")
                    print()
                    
                    # Get all distinct Dias4Vencimento values (sorted)
                    cursor.execute(f"""
                        SELECT DISTINCT Dias4Vencimento 
                        FROM {options_table} 
                        WHERE Dias4Vencimento IS NOT NULL 
                        ORDER BY Dias4Vencimento;
                    """)
                    distinct_days = [row[0] for row in cursor.fetchall()]
                    
                    # Analyze for weekly options pattern
                    print("  🔍 Weekly Options Detection:")
                    print("  " + "-" * 76)
                    
                    if len(distinct_days) > 0:
                        # Calculate gaps between consecutive expiration days
                        gaps = []
                        for i in range(len(distinct_days) - 1):
                            gap = distinct_days[i + 1] - distinct_days[i]
                            gaps.append(gap)
                        
                        if gaps:
                            avg_gap = sum(gaps) / len(gaps)
                            min_gap = min(gaps)
                            max_gap = max(gaps)
                            
                            # Count gaps that are around 7 days (weekly pattern)
                            weekly_gaps = [g for g in gaps if 5 <= g <= 9]  # Allow some flexibility
                            
                            print(f"    Average gap between expirations: {avg_gap:.2f} days")
                            print(f"    Min gap: {min_gap:.2f} days")
                            print(f"    Max gap: {max_gap:.2f} days")
                            print(f"    Gaps in 5-9 day range (weekly): {len(weekly_gaps)}/{len(gaps)} ({len(weekly_gaps)/len(gaps)*100:.1f}%)")
                            
                            # Show first 20 distinct expiration days
                            print(f"\n    First 20 distinct expiration days:")
                            for i, days in enumerate(distinct_days[:20], 1):
                                print(f"      {i:2}. {int(days):>4} days", end="")
                                if i < len(distinct_days) and i < 20:
                                    gap = distinct_days[i] - distinct_days[i-1]
                                    print(f" (gap: {gap:.1f} days)")
                                else:
                                    print()
                            
                            if len(distinct_days) > 20:
                                print(f"      ... and {len(distinct_days) - 20} more")
                            
                            # Weekly options conclusion
                            print()
                            if len(weekly_gaps) / len(gaps) > 0.3:  # More than 30% of gaps are weekly
                                print("    ✅ WEEKLY OPTIONS DETECTED: Significant portion of expirations")
                                print("       follow a weekly pattern (5-9 day gaps)")
                            elif min_gap <= 7 and avg_gap <= 10:
                                print("    ⚠️  POSSIBLE WEEKLY OPTIONS: Some weekly patterns detected")
                            else:
                                print("    ❌ NO CLEAR WEEKLY PATTERN: Expirations are more spread out")
                    else:
                        print("    No distinct expiration days found")
                else:
                    print("  No Dias4Vencimento data found")
                print()
        
        # Summary
        print("=" * 80)
        print("Summary:")
        print("-" * 80)
        total_rows = sum(
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]};").fetchone()[0]
            for table in tables
        )
        print(f"Total tables: {len(tables)}")
        print(f"Total rows across all tables: {total_rows:,}")
        print("=" * 80)
        
        conn.close()
        
        # Write output to file if specified
        if output_file:
            sys.stdout.flush()
            output_text = output_buffer.getvalue()
            output_path = Path(output_file)
            output_path.write_text(output_text, encoding='utf-8')
            print(f"\n✅ Output saved to: {output_path.absolute()}")
            sys.stdout = original_stdout
        
    except sqlite3.Error as e:
        error_msg = f"Database error: {e}"
        print(error_msg)
        if output_file and original_stdout:
            # Write error to file before restoring
            if output_buffer:
                output_buffer.write(error_msg + "\n")
                output_text = output_buffer.getvalue()
                output_path = Path(output_file)
                output_path.write_text(output_text, encoding='utf-8')
            sys.stdout = original_stdout
        sys.exit(1)
    except Exception as e:
        error_msg = f"Error: {e}"
        print(error_msg)
        if output_file and original_stdout:
            # Write error to file before restoring
            if output_buffer:
                output_buffer.write(error_msg + "\n")
                output_text = output_buffer.getvalue()
                output_path = Path(output_file)
                output_path.write_text(output_text, encoding='utf-8')
            sys.stdout = original_stdout
        sys.exit(1)
    finally:
        # Restore stdout if it was redirected
        if output_file and original_stdout:
            sys.stdout = original_stdout


if __name__ == "__main__":
    # Default database path
    db_path = Path(__file__).parent / "BOVA.db"
    output_file = None
    
    # Parse command-line arguments
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    else:
        # Generate default output filename based on database name
        db_name = Path(db_path).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = Path(__file__).parent / f"{db_name}_inspection_{timestamp}.txt"
    
    inspect_database(db_path, output_file)

