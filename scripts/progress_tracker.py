import os
import sqlite3
import datetime
import logging
import json

# Path to the SQLite database file
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'progress.db'))

# Setup logging
logger = logging.getLogger('progress_tracker')
logger.setLevel(logging.INFO)
log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, 'progress_tracker.log')
if not logger.handlers:
    handler = logging.FileHandler(log_path)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

def ensure_tables():
    """Create tables if they do not already exist."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        # Users table
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL
            )
        ''')
        # Skills table
        c.execute('''
            CREATE TABLE IF NOT EXISTS skills (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        # Points log table
        c.execute('''
            CREATE TABLE IF NOT EXISTS points_log (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                skill_id INTEGER NOT NULL,
                points INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(skill_id) REFERENCES skills(id)
            )
        ''')
        # Snapshots table
        c.execute('''
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                period TEXT CHECK(period IN ('day','week','month','year')),
                taken_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                data_json TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        # Add index for performance
        c.execute('CREATE INDEX IF NOT EXISTS idx_points_log_user_skill ON points_log(user_id, skill_id)')
        conn.commit()
        conn.close()
        logger.info('Tables ensured and index created.')
    except Exception as e:
        logger.error(f'Error ensuring tables: {e}')


def seed_data():
    """Insert initial users and skills."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Seed users
    for username in ['Orchestrator', 'Logan']:
        c.execute('INSERT OR IGNORE INTO users(username) VALUES(?)', (username,))
    # Seed skills
    skills = [
        'Python Programming',
        'Terminal/Command Line',
        'AI Orchestration',
        'Agentic AI',
        'Human Orchestration',
        'API Usage',
        'ETL/Data Engineering',
        'Testing/Debugging',
        'Documentation/Communication',
        'Version Control',
        'DevOps/Config',
        'Database/SQL',
        'ML/Model Usage',
        'Prompt Engineering',
        'Code Review/Best Practices'
    ]
    for skill in skills:
        c.execute('INSERT OR IGNORE INTO skills(name) VALUES(?)', (skill,))
    conn.commit()
    conn.close()


def initialize():
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    ensure_tables()
    seed_data()

# Initialize on import
def initialize_on_import():
    initialize()

initialize_on_import()

# Progress tracking API functions
def add_user(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users(username) VALUES(?)', (username,))
    conn.commit()
    conn.close()

def add_skill(name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO skills(name) VALUES(?)', (name,))
    conn.commit()
    conn.close()

def award_points(username, skill_name, points):
    """Award points to a user for a given skill."""
    try:
        add_user(username)
        add_skill(skill_name)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT id FROM users WHERE username=?', (username,))
        user_row = c.fetchone()
        c.execute('SELECT id FROM skills WHERE name=?', (skill_name,))
        skill_row = c.fetchone()
        if not user_row or not skill_row:
            logger.error(f"User or skill not found: {username}, {skill_name}")
            raise ValueError(f"User or skill not found: {username}, {skill_name}")
        user_id = user_row[0]
        skill_id = skill_row[0]
        c.execute('INSERT INTO points_log(user_id, skill_id, points) VALUES(?,?,?)',
                  (user_id, skill_id, points))
        conn.commit()
        conn.close()
        logger.info(f"Awarded {points} points to {username} for {skill_name}")
    except Exception as e:
        logger.error(f"Error awarding points: {e}")
        raise

def get_current_points(username):
    """Get total points per skill for the given user."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT id FROM users WHERE username=?', (username,))
        row = c.fetchone()
        if not row:
            logger.error(f"User not found: {username}")
            raise ValueError(f"User not found: {username}")
        user_id = row[0]
        c.execute('''
            SELECT s.name, COALESCE(SUM(pl.points),0)
            FROM skills s
            LEFT JOIN points_log pl
              ON pl.skill_id = s.id AND pl.user_id = ?
            GROUP BY s.id
        ''', (user_id,))
        result = {name: total for name, total in c.fetchall()}
        conn.close()
        logger.info(f"Fetched current points for {username}: {result}")
        return result
    except Exception as e:
        logger.error(f"Error getting current points: {e}")
        raise

def get_points_for_period(username, start, end):
    """Get total points per skill for user between start and end datetimes."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT id FROM users WHERE username=?', (username,))
        row = c.fetchone()
        if not row:
            logger.error(f"User not found: {username}")
            raise ValueError(f"User not found: {username}")
        user_id = row[0]
        c.execute('''
            SELECT s.name, COALESCE(SUM(pl.points),0)
            FROM skills s
            LEFT JOIN points_log pl
              ON pl.skill_id = s.id
                 AND pl.user_id = ?
                 AND pl.timestamp >= ?
                 AND pl.timestamp <= ?
            GROUP BY s.id
        ''', (user_id, start, end))
        result = {name: total for name, total in c.fetchall()}
        conn.close()
        logger.info(f"Fetched points for {username} from {start} to {end}: {result}")
        return result
    except Exception as e:
        logger.error(f"Error getting points for period: {e}")
        raise

def get_report(username, period):
    """Generate a progress report for the given period (day, week, month, year)."""
    try:
        now = datetime.datetime.now()
        if period == 'day':
            delta = datetime.timedelta(days=1)
        elif period == 'week':
            delta = datetime.timedelta(weeks=1)
        elif period == 'month':
            delta = datetime.timedelta(days=30)
        elif period == 'year':
            delta = datetime.timedelta(days=365)
        else:
            logger.error(f"Invalid period: {period}")
            raise ValueError(f"Invalid period: {period}")
        end_current = now
        start_current = now - delta
        end_previous = start_current
        start_previous = start_current - delta
        current = get_points_for_period(username, start_current.strftime('%Y-%m-%d %H:%M:%S'), end_current.strftime('%Y-%m-%d %H:%M:%S'))
        previous = get_points_for_period(username, start_previous.strftime('%Y-%m-%d %H:%M:%S'), end_previous.strftime('%Y-%m-%d %H:%M:%S'))
        diff = {skill: current.get(skill,0) - previous.get(skill,0) for skill in current}
        logger.info(f"Report for {username} period {period}: current={current}, previous={previous}, diff={diff}")
        return {'period': period, 'current': current, 'previous': previous, 'diff': diff}
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise

def take_snapshot(username, period):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT id FROM users WHERE username=?', (username,))
        row = c.fetchone()
        if not row:
            logger.error(f"User not found: {username}")
            raise ValueError(f"User not found: {username}")
        user_id = row[0]
        points = get_current_points(username)
        data_json = json.dumps(points)
        c.execute('INSERT INTO snapshots(user_id, period, data_json) VALUES(?,?,?)',
                  (user_id, period, data_json))
        conn.commit()
        conn.close()
        logger.info(f"Snapshot taken for {username} period {period}")
    except Exception as e:
        logger.error(f"Error taking snapshot: {e}")
        raise

def get_snapshot(username, period):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT id FROM users WHERE username=?', (username,))
        row = c.fetchone()
        if not row:
            logger.error(f"User not found: {username}")
            raise ValueError(f"User not found: {username}")
        user_id = row[0]
        c.execute('SELECT data_json, taken_at FROM snapshots WHERE user_id=? AND period=? ORDER BY taken_at DESC LIMIT 1',
                  (user_id, period))
        row = c.fetchone()
        conn.close()
        if row:
            logger.info(f"Fetched snapshot for {username} period {period}")
            return {"data": json.loads(row[0]), "taken_at": row[1]}
        logger.info(f"No snapshot found for {username} period {period}")
        return None
    except Exception as e:
        logger.error(f"Error getting snapshot: {e}")
        raise 