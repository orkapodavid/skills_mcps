#!/usr/bin/env python3
"""
Analyze SQLAlchemy query performance.

Captures and analyzes SQL queries to identify:
- N+1 query problems
- Missing eager loading
- Slow queries
- Query patterns

Usage:
    Enable echo logging in your application and pipe output to this script
    or use SQLAlchemy event listeners to capture queries
"""

import re
from collections import defaultdict, Counter
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class QueryInfo:
    """Information about a query execution."""
    sql: str
    duration_ms: float
    table: str
    operation: str  # SELECT, INSERT, UPDATE, DELETE

class QueryAnalyzer:
    """Analyze query patterns for performance issues."""
    
    def __init__(self):
        self.queries: List[QueryInfo] = []
        self.n_plus_one_threshold = 5  # Flag if same query runs 5+ times
    
    def add_query(self, sql: str, duration_ms: float):
        """Add a query for analysis."""
        # Parse query type and table
        operation = self._extract_operation(sql)
        table = self._extract_table(sql)
        
        query = QueryInfo(
            sql=sql,
            duration_ms=duration_ms,
            table=table,
            operation=operation
        )
        self.queries.append(query)
    
    def _extract_operation(self, sql: str) -> str:
        """Extract SQL operation (SELECT, INSERT, etc.)."""
        match = re.match(r'^\s*(\w+)', sql, re.IGNORECASE)
        return match.group(1).upper() if match else "UNKNOWN"
    
    def _extract_table(self, sql: str) -> str:
        """Extract primary table from query."""
        # Simple extraction - can be improved
        if 'FROM' in sql.upper():
            match = re.search(r'FROM\s+(\w+)', sql, re.IGNORECASE)
            return match.group(1) if match else "unknown"
        elif 'INSERT INTO' in sql.upper():
            match = re.search(r'INSERT INTO\s+(\w+)', sql, re.IGNORECASE)
            return match.group(1) if match else "unknown"
        elif 'UPDATE' in sql.upper():
            match = re.search(r'UPDATE\s+(\w+)', sql, re.IGNORECASE)
            return match.group(1) if match else "unknown"
        return "unknown"
    
    def detect_n_plus_one(self) -> List[Dict]:
        """Detect potential N+1 query problems."""
        # Normalize queries (remove specific values)
        normalized_queries = []
        for q in self.queries:
            # Replace numbers and strings with placeholders
            normalized = re.sub(r'\d+', '?', q.sql)
            normalized = re.sub(r"'[^']*'", '?', normalized)
            normalized_queries.append((normalized, q))
        
        # Count occurrences
        query_counts = Counter(norm for norm, _ in normalized_queries)
        
        # Find queries that ran many times
        issues = []
        for query_pattern, count in query_counts.items():
            if count >= self.n_plus_one_threshold:
                sample_query = next(q for norm, q in normalized_queries if norm == query_pattern)
                issues.append({
                    "pattern": query_pattern[:100] + "...",
                    "count": count,
                    "table": sample_query.table,
                    "operation": sample_query.operation,
                    "suggestion": "Consider using eager loading (joinedload/selectinload)"
                })
        
        return issues
    
    def find_slow_queries(self, threshold_ms: float = 100) -> List[QueryInfo]:
        """Find queries slower than threshold."""
        return [q for q in self.queries if q.duration_ms > threshold_ms]
    
    def get_statistics(self) -> Dict:
        """Get query statistics."""
        if not self.queries:
            return {"error": "No queries analyzed"}
        
        total_duration = sum(q.duration_ms for q in self.queries)
        
        # Count by operation
        operation_counts = Counter(q.operation for q in self.queries)
        
        # Count by table
        table_counts = Counter(q.table for q in self.queries)
        
        return {
            "total_queries": len(self.queries),
            "total_duration_ms": total_duration,
            "avg_duration_ms": total_duration / len(self.queries),
            "by_operation": dict(operation_counts),
            "by_table": dict(table_counts),
            "slowest_query": max(self.queries, key=lambda q: q.duration_ms)
        }
    
    def generate_report(self) -> str:
        """Generate analysis report."""
        report = ["Query Performance Analysis", "=" * 50, ""]
        
        # Statistics
        stats = self.get_statistics()
        if "error" in stats:
            return "No queries to analyze"
        
        report.append(f"Total queries: {stats['total_queries']}")
        report.append(f"Total duration: {stats['total_duration_ms']:.2f}ms")
        report.append(f"Average duration: {stats['avg_duration_ms']:.2f}ms")
        report.append("")
        
        # By operation
        report.append("Queries by operation:")
        for op, count in sorted(stats['by_operation'].items()):
            report.append(f"  {op}: {count}")
        report.append("")
        
        # N+1 detection
        n_plus_one = self.detect_n_plus_one()
        if n_plus_one:
            report.append("⚠️  Potential N+1 Query Problems:")
            for issue in n_plus_one:
                report.append(f"  - {issue['operation']} on {issue['table']}: ran {issue['count']} times")
                report.append(f"    {issue['suggestion']}")
        else:
            report.append("✅ No N+1 query problems detected")
        report.append("")
        
        # Slow queries
        slow_queries = self.find_slow_queries()
        if slow_queries:
            report.append(f"⚠️  Slow Queries (>{100}ms):")
            for q in slow_queries[:5]:  # Show top 5
                report.append(f"  - {q.duration_ms:.2f}ms: {q.operation} on {q.table}")
        else:
            report.append("✅ No slow queries detected")
        
        return "\n".join(report)

if __name__ == "__main__":
    print("Query Analyzer")
    print("=" * 50)
    print("\nTo use this analyzer:")
    print("1. Enable SQLAlchemy query logging (echo=True)")
    print("2. Capture queries with timing information")
    print("3. Add queries to analyzer:")
    print("   analyzer = QueryAnalyzer()")
    print("   analyzer.add_query(sql, duration_ms)")
    print("4. Generate report:")
    print("   print(analyzer.generate_report())")
    print("\nExample integration with SQLAlchemy events:")
    print("""
from sqlalchemy import event
from time import time

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time()

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    duration = time() - context._query_start_time
    analyzer.add_query(statement, duration * 1000)  # Convert to ms
""")
