"""
Database Optimization Service
Handles query optimization, indexing, and performance monitoring.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from sqlalchemy import text, inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from core.config import settings
from db.session import get_db


class DatabaseOptimizer:
    """Database optimization and monitoring service."""
    
    def __init__(self):
        self.query_stats: Dict[str, Any] = {}
        self.slow_queries: List[Dict[str, Any]] = []
        self.index_recommendations: List[str] = []
    
    async def analyze_query_performance(self, db: AsyncSession) -> Dict[str, Any]:
        """Analyze database query performance."""
        try:
            # Get database statistics
            stats = await self._get_database_stats(db)
            
            # Analyze slow queries
            slow_queries = await self._analyze_slow_queries(db)
            
            # Generate index recommendations
            index_recommendations = await self._generate_index_recommendations(db)
            
            return {
                "database_stats": stats,
                "slow_queries": slow_queries,
                "index_recommendations": index_recommendations,
                "optimization_score": self._calculate_optimization_score(stats, slow_queries)
            }
        except Exception as e:
            print(f"Error analyzing query performance: {e}")
            return {"error": str(e)}
    
    async def _get_database_stats(self, db: AsyncSession) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            # Get table sizes
            table_sizes = await self._get_table_sizes(db)
            
            # Get index usage
            index_usage = await self._get_index_usage(db)
            
            # Get connection pool stats
            pool_stats = await self._get_pool_stats(db)
            
            return {
                "table_sizes": table_sizes,
                "index_usage": index_usage,
                "pool_stats": pool_stats,
                "timestamp": time.time()
            }
        except Exception as e:
            print(f"Error getting database stats: {e}")
            return {}
    
    async def _get_table_sizes(self, db: AsyncSession) -> Dict[str, int]:
        """Get table sizes in bytes."""
        try:
            result = await db.execute(text("""
                SELECT 
                    schemaname,
                    tablename,
                    pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY size_bytes DESC
            """))
            
            tables = {}
            for row in result.fetchall():
                tables[f"{row.schemaname}.{row.tablename}"] = row.size_bytes
            
            return tables
        except Exception as e:
            print(f"Error getting table sizes: {e}")
            return {}
    
    async def _get_index_usage(self, db: AsyncSession) -> Dict[str, Any]:
        """Get index usage statistics."""
        try:
            result = await db.execute(text("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan,
                    idx_tup_read,
                    idx_tup_fetch
                FROM pg_stat_user_indexes
                ORDER BY idx_scan DESC
            """))
            
            indexes = []
            for row in result.fetchall():
                indexes.append({
                    "schema": row.schemaname,
                    "table": row.tablename,
                    "index": row.indexname,
                    "scans": row.idx_scan,
                    "tuples_read": row.idx_tup_read,
                    "tuples_fetched": row.idx_tup_fetch
                })
            
            return {"indexes": indexes}
        except Exception as e:
            print(f"Error getting index usage: {e}")
            return {"indexes": []}
    
    async def _get_pool_stats(self, db: AsyncSession) -> Dict[str, Any]:
        """Get connection pool statistics."""
        try:
            # This would depend on your specific database connection setup
            # For now, return basic stats
            return {
                "pool_size": settings.DB_POOL_SIZE,
                "max_overflow": settings.DB_MAX_OVERFLOW,
                "pool_timeout": settings.DB_POOL_TIMEOUT,
                "pool_recycle": settings.DB_POOL_RECYCLE
            }
        except Exception as e:
            print(f"Error getting pool stats: {e}")
            return {}
    
    async def _analyze_slow_queries(self, db: AsyncSession) -> List[Dict[str, Any]]:
        """Analyze slow queries from pg_stat_statements."""
        try:
            result = await db.execute(text("""
                SELECT 
                    query,
                    calls,
                    total_time,
                    mean_time,
                    rows
                FROM pg_stat_statements
                WHERE mean_time > 100  -- Queries taking more than 100ms
                ORDER BY mean_time DESC
                LIMIT 10
            """))
            
            slow_queries = []
            for row in result.fetchall():
                slow_queries.append({
                    "query": row.query[:200] + "..." if len(row.query) > 200 else row.query,
                    "calls": row.calls,
                    "total_time": row.total_time,
                    "mean_time": row.mean_time,
                    "rows": row.rows
                })
            
            return slow_queries
        except Exception as e:
            print(f"Error analyzing slow queries: {e}")
            return []
    
    async def _generate_index_recommendations(self, db: AsyncSession) -> List[str]:
        """Generate index recommendations based on query patterns."""
        try:
            recommendations = []
            
            # Check for missing indexes on foreign keys
            fk_result = await db.execute(text("""
                SELECT 
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
            """))
            
            for row in fk_result.fetchall():
                # Check if index exists on foreign key
                index_result = await db.execute(text(f"""
                    SELECT indexname 
                    FROM pg_indexes 
                    WHERE tablename = '{row.table_name}' 
                    AND indexdef LIKE '%{row.column_name}%'
                """))
                
                if not index_result.fetchone():
                    recommendations.append(
                        f"Add index on {row.table_name}.{row.column_name} (foreign key)"
                    )
            
            # Check for missing indexes on frequently queried columns
            query_result = await db.execute(text("""
                SELECT 
                    schemaname,
                    tablename,
                    attname,
                    n_distinct,
                    correlation
                FROM pg_stats 
                WHERE schemaname = 'public'
                AND n_distinct > 100  -- High cardinality columns
                ORDER BY n_distinct DESC
            """))
            
            for row in query_result.fetchall():
                # Check if index exists
                index_result = await db.execute(text(f"""
                    SELECT indexname 
                    FROM pg_indexes 
                    WHERE tablename = '{row.tablename}' 
                    AND indexdef LIKE '%{row.attname}%'
                """))
                
                if not index_result.fetchone():
                    recommendations.append(
                        f"Consider index on {row.tablename}.{row.attname} (high cardinality)"
                    )
            
            return recommendations
        except Exception as e:
            print(f"Error generating index recommendations: {e}")
            return []
    
    def _calculate_optimization_score(self, stats: Dict[str, Any], slow_queries: List[Dict[str, Any]]) -> float:
        """Calculate database optimization score (0-100)."""
        try:
            score = 100.0
            
            # Deduct points for slow queries
            slow_query_count = len(slow_queries)
            score -= min(slow_query_count * 5, 30)  # Max 30 points deduction
            
            # Deduct points for large tables without proper indexing
            table_sizes = stats.get("table_sizes", {})
            large_tables = sum(1 for size in table_sizes.values() if size > 10 * 1024 * 1024)  # 10MB
            score -= min(large_tables * 2, 20)  # Max 20 points deduction
            
            # Deduct points for poor index usage
            index_usage = stats.get("index_usage", {}).get("indexes", [])
            unused_indexes = sum(1 for idx in index_usage if idx.get("scans", 0) == 0)
            score -= min(unused_indexes * 1, 10)  # Max 10 points deduction
            
            return max(score, 0.0)
        except Exception as e:
            print(f"Error calculating optimization score: {e}")
            return 50.0
    
    async def optimize_queries(self, db: AsyncSession) -> Dict[str, Any]:
        """Optimize database queries and indexes."""
        try:
            optimizations = []
            
            # Analyze current performance
            analysis = await self.analyze_query_performance(db)
            
            # Generate optimization recommendations
            if analysis.get("slow_queries"):
                optimizations.append("Consider query optimization for slow queries")
            
            if analysis.get("index_recommendations"):
                optimizations.extend(analysis["index_recommendations"])
            
            # Check for connection pool optimization
            pool_stats = analysis.get("database_stats", {}).get("pool_stats", {})
            if pool_stats.get("pool_size", 0) < 10:
                optimizations.append("Consider increasing connection pool size")
            
            return {
                "optimizations": optimizations,
                "current_score": analysis.get("optimization_score", 0),
                "estimated_improvement": min(len(optimizations) * 5, 30)  # 5 points per optimization
            }
        except Exception as e:
            print(f"Error optimizing queries: {e}")
            return {"error": str(e)}
    
    async def create_recommended_indexes(self, db: AsyncSession) -> List[str]:
        """Create recommended indexes."""
        try:
            analysis = await self.analyze_query_performance(db)
            recommendations = analysis.get("index_recommendations", [])
            
            created_indexes = []
            for recommendation in recommendations[:5]:  # Limit to 5 indexes
                try:
                    # Extract table and column from recommendation
                    if "Add index on" in recommendation:
                        parts = recommendation.split("Add index on ")[1].split(".")
                        table = parts[0]
                        column = parts[1].split(" ")[0]
                        
                        # Create index
                        index_name = f"idx_{table}_{column}"
                        await db.execute(text(f"""
                            CREATE INDEX IF NOT EXISTS {index_name} 
                            ON {table} ({column})
                        """))
                        
                        created_indexes.append(f"{table}.{column}")
                        
                except Exception as e:
                    print(f"Error creating index for {recommendation}: {e}")
            
            return created_indexes
        except Exception as e:
            print(f"Error creating recommended indexes: {e}")
            return []
    
    def track_query_performance(self, query: str, execution_time: float, rows_returned: int):
        """Track query performance for analysis."""
        query_hash = hash(query)
        
        if query_hash not in self.query_stats:
            self.query_stats[query_hash] = {
                "query": query,
                "execution_count": 0,
                "total_time": 0,
                "avg_time": 0,
                "max_time": 0,
                "total_rows": 0
            }
        
        stats = self.query_stats[query_hash]
        stats["execution_count"] += 1
        stats["total_time"] += execution_time
        stats["avg_time"] = stats["total_time"] / stats["execution_count"]
        stats["max_time"] = max(stats["max_time"], execution_time)
        stats["total_rows"] += rows_returned
        
        # Track slow queries
        if execution_time > 1.0:  # 1 second threshold
            self.slow_queries.append({
                "query": query,
                "execution_time": execution_time,
                "rows_returned": rows_returned,
                "timestamp": time.time()
            })
            
            # Keep only last 100 slow queries
            if len(self.slow_queries) > 100:
                self.slow_queries = self.slow_queries[-100:]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        total_queries = sum(stats["execution_count"] for stats in self.query_stats.values())
        avg_execution_time = sum(stats["total_time"] for stats in self.query_stats.values()) / total_queries if total_queries > 0 else 0
        
        return {
            "total_queries": total_queries,
            "unique_queries": len(self.query_stats),
            "avg_execution_time": avg_execution_time,
            "slow_queries_count": len(self.slow_queries),
            "query_stats": self.query_stats,
            "slow_queries": self.slow_queries[-10:]  # Last 10 slow queries
        }


# Create singleton instance
database_optimizer = DatabaseOptimizer() 