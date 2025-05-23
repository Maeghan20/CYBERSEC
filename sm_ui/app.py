from flask import Flask, render_template, redirect, request, url_for
from sqlalchemy import create_engine, text
import psycopg2


app = Flask(__name__)

# --- Supabase Postgres Connection ---
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
    # Include image_url in the SELECT query
    cursor.execute('SELECT id, content, is_approved, posted, image_url FROM summaries')
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
            'image_url': row[4]  # Add image_url to the post data
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
    cursor.execute('SELECT COUNT(*) FROM summaries')
    total_posts = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return render_template('analytics.html', total_posts=total_posts)

if __name__ == "__main__":
    app.run(debug=True)
