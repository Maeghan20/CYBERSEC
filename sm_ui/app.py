from flask import Flask, render_template, redirect, request, url_for
from sqlalchemy import create_engine, text
import psycopg2
from datetime import datetime, timedelta

app = Flask(__name__)

# --- Database Connection ---
DATABASE_URL = "postgresql://postgres.oxtygtquuepqrtwsbnsr:maeghansdb123@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"
engine = create_engine(DATABASE_URL)

def get_db_connection():
    conn = psycopg2.connect(
        host="aws-0-ap-south-1.pooler.supabase.com",
        port="6543",
        dbname="postgres",
        user="postgres.oxtygtquuepqrtwsbnsr",
        password="maeghansdb123"  
    )
    return conn

@app.route('/')
def home():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Get non-archived posts sorted by created_at (newest first)
    cursor.execute('''
        SELECT id, content, is_approved, posted, image_url, archived, created_at 
        FROM summaries 
        WHERE archived = FALSE 
        ORDER BY created_at DESC
    ''')
    result = cursor.fetchall()
    cursor.close()
    conn.close()

    posts = []
    for row in result:
        posts.append({
            'id': row[0],
            'content': row[1],
            'is_approved': row[2],
            'posted': row[3],
            'image_url': row[4],
            'archived': row[5],
            'created_at': row[6]  # Added created_at
        })

    return render_template('home.html', posts=posts)

@app.route('/unapprove/<post_id>')
def unapprove(post_id):
    with engine.connect() as conn:
        conn.execute(
            text("UPDATE summaries SET is_approved = FALSE WHERE id = :id"),
            {"id": post_id}
        )
        conn.commit()
    return redirect(url_for('home'))

@app.route('/approve/<post_id>')
def approve(post_id):
    with engine.connect() as conn:
        conn.execute(
            text("UPDATE summaries SET is_approved = TRUE WHERE id = :id"),
            {"id": post_id}
        )
        conn.commit()
    return redirect(url_for('home'))

@app.route('/edit/<post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    if request.method == 'POST':
        new_content = request.form['content']
        with engine.connect() as conn:
            conn.execute(
                text("UPDATE summaries SET content = :content WHERE id = :id"),
                {"content": new_content, "id": post_id}
            )
            conn.commit()
        return redirect(url_for('home'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM summaries WHERE id = %s', (post_id,))
    post = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return render_template('edit_post.html', post=post)

@app.route('/analytics')
def analytics():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM summaries WHERE archived = FALSE')
    total_posts = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return render_template('analytics.html', total_posts=total_posts)

@app.route('/archive_post/<post_id>', methods=['POST'])
def archive_post(post_id):
    with engine.connect() as conn:
        conn.execute(
            text("UPDATE summaries SET archived = TRUE WHERE id = :id"),
            {"id": post_id}
        )
        conn.commit()
    return redirect(url_for('home'))

@app.route('/archive_all', methods=['POST'])
def archive_all():
    ten_days_ago = datetime.now() - timedelta(days=10)
    with engine.connect() as conn:
        conn.execute(
            text("UPDATE summaries SET archived = TRUE WHERE created_at < :date AND archived = FALSE"),
            {"date": ten_days_ago}
        )
        conn.commit()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
