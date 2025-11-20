import psycopg2
from config import config

def get_connection():
    return psycopg2.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        database=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD
    )

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    
    # Создаем enum типы
    cur.execute("""
        DO $$ BEGIN
            CREATE TYPE note_status AS ENUM ('active', 'completed');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        
        DO $$ BEGIN
            CREATE TYPE reminder_type AS ENUM ('once', 'daily', 'weekly', 'monthly');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Создаем таблицы
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id BIGINT PRIMARY KEY,
            username VARCHAR(32),
            first_name VARCHAR(64),
            created_at TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
            title VARCHAR(200) NOT NULL,
            content TEXT,
            status note_status DEFAULT 'active',
            is_pinned BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS tags (
            id SERIAL PRIMARY KEY,
            user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
            name VARCHAR(50) NOT NULL,
            UNIQUE(user_id, name)
        );

        CREATE TABLE IF NOT EXISTS note_tags (
            note_id INTEGER REFERENCES notes(id) ON DELETE CASCADE,
            tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
            PRIMARY KEY (note_id, tag_id)
        );

        CREATE TABLE IF NOT EXISTS reminders (
            id SERIAL PRIMARY KEY,
            note_id INTEGER REFERENCES notes(id) ON DELETE CASCADE,
            reminder_time TIMESTAMP NOT NULL,
            reminder_type reminder_type DEFAULT 'once',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)
    
    conn.commit()
    cur.close()
    conn.close()