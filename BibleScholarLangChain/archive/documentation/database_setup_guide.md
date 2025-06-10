# Database Setup and Troubleshooting Guide

## Current Issue: PostgreSQL Service Not Running ❌

The BibleScholarLangChain project requires PostgreSQL with the `bible_db` database and `pgvector` extension. Currently, the PostgreSQL service is not running, which blocks all database-dependent features.

## Quick Diagnosis

Run the database diagnostic tool:
```bash
python test_db_connection.py
```

Expected output when working:
```
✅ Connection successful!
✅ Database version: PostgreSQL 14.x
✅ Connected to database: bible_db
✅ Bible schema exists
✅ Found X tables in bible schema
```

Current output (broken):
```
❌ Database connection failed: connection timeout expired
❌ PostgreSQL service needs to be started
```

## Solution Steps

### 1. Check PostgreSQL Service Status

**Windows Command:**
```cmd
sc query postgresql-x64-14
```

**Expected Output (Working):**
```
SERVICE_NAME: postgresql-x64-14
STATE: 4 RUNNING
```

**Current Output (Broken):**
```
SERVICE_NAME: postgresql-x64-14
STATE: 1 STOPPED
```

### 2. Start PostgreSQL Service

**Option A: Command Line (Run as Administrator)**
```cmd
net start postgresql-x64-14
```

**Option B: Services Manager**
1. Press `Win + R`, type `services.msc`
2. Find "PostgreSQL Database Server 14"
3. Right-click → Start

**Option C: Alternative Service Names**
If `postgresql-x64-14` doesn't work, try:
```cmd
sc query | findstr postgresql
net start postgresql-x64-13
net start postgresql-x64-15
net start PostgreSQL
```

### 3. Verify Database Setup

Once PostgreSQL is running, verify the database setup:

```bash
# Test basic connection
python test_db_connection.py

# If connection works but database doesn't exist, create it:
psql -U postgres -c "CREATE DATABASE bible_db;"

# Verify pgvector extension
psql -U postgres -d bible_db -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Check if bible schema exists
psql -U postgres -d bible_db -c "CREATE SCHEMA IF NOT EXISTS bible;"
```

### 4. Verify Required Tables

The project expects these tables in the `bible` schema:
- `bible.verses` - Bible verse text data
- `bible.verse_embeddings` - Vector embeddings for semantic search
- `bible.hebrew_ot_words` - Hebrew Old Testament lexicon
- `bible.greek_nt_words` - Greek New Testament lexicon

Check if tables exist:
```sql
psql -U postgres -d bible_db -c "
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'bible' 
ORDER BY table_name;
"
```

## Configuration Details

### Database Connection String
```
postgresql://postgres:postgres@localhost:5432/bible_db
```

### Required Components
- **PostgreSQL**: Version 14+ recommended
- **pgvector extension**: For vector similarity search
- **Database**: `bible_db`
- **Schema**: `bible`
- **User**: `postgres` with password `postgres`

## Troubleshooting Common Issues

### Issue 1: Service Won't Start
**Error**: "The service did not respond to the start or control request in a timely fashion"

**Solutions**:
1. Check if another PostgreSQL instance is running on port 5432
2. Check PostgreSQL logs in `C:\Program Files\PostgreSQL\14\data\log\`
3. Restart as Administrator
4. Check disk space (PostgreSQL needs space for logs)

### Issue 2: Authentication Failed
**Error**: "authentication failed for user postgres"

**Solutions**:
1. Reset postgres password:
   ```cmd
   psql -U postgres -c "ALTER USER postgres PASSWORD 'postgres';"
   ```
2. Check `pg_hba.conf` file for authentication settings
3. Ensure connection method is set to `md5` or `trust` for localhost

### Issue 3: Database Doesn't Exist
**Error**: "database \"bible_db\" does not exist"

**Solution**:
```sql
psql -U postgres -c "CREATE DATABASE bible_db;"
psql -U postgres -d bible_db -c "CREATE EXTENSION IF NOT EXISTS vector;"
psql -U postgres -d bible_db -c "CREATE SCHEMA IF NOT EXISTS bible;"
```

### Issue 4: Port Already in Use
**Error**: "could not bind IPv4 address \"0.0.0.0\": Address already in use"

**Solutions**:
1. Find what's using port 5432:
   ```cmd
   netstat -ano | findstr :5432
   ```
2. Kill the process or change PostgreSQL port
3. Check for multiple PostgreSQL installations

## Data Population

If the database exists but is empty, you'll need to populate it with Bible data. This typically involves:

1. **Bible Verses**: Loading Bible text from various translations
2. **Vector Embeddings**: Generating embeddings for semantic search
3. **Lexicon Data**: Hebrew and Greek word definitions and morphology

Check the ETL pipeline documentation for data loading procedures.

## Integration with BibleScholarLangChain

Once PostgreSQL is running and `bible_db` is set up:

1. **Test Connection**: `python test_db_connection.py` should show all green checkmarks
2. **Start Servers**: `.\start_servers.bat` will start both API and Web UI servers
3. **Test Features**: Web UI at `http://localhost:5002` should show database connectivity
4. **Semantic Search**: Vector search features should be available

## Monitoring and Maintenance

### Health Checks
- **Database**: `python test_db_connection.py`
- **Servers**: `python test_server_status.py`
- **Full System**: Web UI dashboard at `http://localhost:5002`

### Log Locations
- **PostgreSQL**: `C:\Program Files\PostgreSQL\14\data\log\`
- **Web UI**: `logs/web_app.log`
- **Database Connections**: `database_connection.log`

### Performance Monitoring
```sql
-- Check database size
SELECT pg_size_pretty(pg_database_size('bible_db'));

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'bible'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check vector embedding count
SELECT COUNT(*) FROM bible.verse_embeddings;
```

## Next Steps After Database Fix

Once PostgreSQL is running and `bible_db` is accessible:

1. ✅ **Verify Connection**: All database tests pass
2. 🔄 **Test Vector Search**: Semantic search capabilities
3. 🔄 **Validate ETL Pipeline**: Data loading and processing
4. 🔄 **End-to-End Testing**: Full Bible study workflows
5. 🔄 **Performance Optimization**: Query optimization and indexing

## Emergency Contacts and Resources

- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **pgvector Extension**: https://github.com/pgvector/pgvector
- **Project Issues**: Check `logs/` directory for detailed error messages
- **Database Schema**: See `docs/reference/DATABASE_SCHEMA.md` for complete schema documentation 