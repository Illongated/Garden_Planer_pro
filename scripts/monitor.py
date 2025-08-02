import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.session import engine, AsyncSessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_query(db: AsyncSession, title: str, query: str):
    """Helper to run a SQL query and print the results."""
    logger.info(f"--- {title} ---")
    try:
        result = await db.execute(text(query))
        rows = result.fetchall()
        if not rows:
            logger.info("No results found.")
        else:
            # Print header
            logger.info(" | ".join(map(str, result.keys())))
            # Print rows
            for row in rows:
                logger.info(" | ".join(map(str, row)))
    except Exception as e:
        logger.error(f"Error executing query for '{title}': {e}")
    finally:
        logger.info("-" * (len(title) + 6))
        logger.info("") # Newline for spacing


async def monitor_database(db: AsyncSession):
    """
    Connects to the database and runs several monitoring queries.
    """
    logger.info("Starting database monitoring checks...")

    # Check active connections
    active_connections_query = """
    SELECT
        pid,
        usename,
        client_addr,
        state,
        wait_event,
        query
    FROM pg_stat_activity
    WHERE datname = current_database() AND state = 'active';
    """
    await run_query(db, "Active Connections", active_connections_query)

    # Check for long-running queries
    long_running_queries_query = """
    SELECT
        pid,
        age(clock_timestamp(), query_start) AS duration,
        usename,
        query
    FROM pg_stat_activity
    WHERE state = 'active'
      AND query_start < clock_timestamp() - interval '1 minutes'
    ORDER BY duration DESC;
    """
    await run_query(db, "Long Running Queries (older than 1 minute)", long_running_queries_query)

    # Check cache hit rate
    cache_hit_rate_query = """
    SELECT
      'Cache Hit Rate' AS metric,
      (sum(heap_blks_hit) - sum(heap_blks_read)) / sum(heap_blks_hit) * 100 AS percentage
    FROM pg_statio_user_tables;
    """
    await run_query(db, "Cache Hit Rate", cache_hit_rate_query)

    # Check index usage
    index_usage_query = """
    SELECT
        relname AS table_name,
        indexrelname AS index_name,
        idx_scan AS index_scans,
        idx_tup_read AS index_tuples_read,
        idx_tup_fetch AS index_tuples_fetched
    FROM pg_stat_user_indexes
    ORDER BY idx_scan ASC, relname;
    """
    await run_query(db, "Index Usage (low scan count first)", index_usage_query)


async def main():
    logger.info("Connecting to the database for monitoring...")
    try:
        async with AsyncSessionLocal() as session:
            await monitor_database(session)
    except Exception as e:
        logger.error(f"Failed to connect or run monitoring script: {e}")
    finally:
        await engine.dispose()
        logger.info("Monitoring script finished.")

if __name__ == "__main__":
    asyncio.run(main())
