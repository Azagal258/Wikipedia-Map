import state
import psycopg2
from psycopg2.extras import execute_values
import os
import dotenv
dotenv.load_dotenv()

def get_conn():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

def create_tables():
    with get_conn() as conn:
        cur = conn.cursor()
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS page(
            "id" BIGINT PRIMARY KEY,
            "title" TEXT NOT NULL,
            "redirect_to" BIGINT REFERENCES page(id)
        );""")

        cur.execute("""
            CREATE TABLE IF NOT EXISTS wikilinks(
            "from_id" BIGINT REFERENCES page(id),
            "from_title" TEXT,
            "to_id" BIGINT REFERENCES page(id),
            "to_title" TEXT,
            "reference_count" BIGINT NOT NULL,
            PRIMARY KEY (from_id, to_id)
        );""")

        conn.commit()

def insert_data_page():
    row_list = []

    query = """
        INSERT INTO page (id, title, redirect_to)
        VALUES %s
        ON CONFLICT (id) DO NOTHING;
        """

    with get_conn() as conn:
        cur = conn.cursor()
        pdo = state.parser_data_out
       
        for i, entry in enumerate(pdo):
            row = (pdo[entry]["id"], entry, None)
            row_list.append(row)

            if i%50000 == 0:
                execute_values(cur, query, row_list)
                print(f"{i} articles inserted")
                row_list.clear()
                

        execute_values(cur, query, row_list)

def insert_data_links():
    row_list = []

    query = """
        INSERT INTO wikilinks (from_id, from_title, to_id, to_title, reference_count)
        VALUES %s
        ON CONFLICT DO NOTHING;
        """

    with get_conn() as conn:
        cur = conn.cursor()
        pdo = state.parser_data_out
        cnt = 0
       
        for article_entry in pdo:
            for link_entry in pdo[article_entry]["link_to"]:
                row = (
                    pdo[article_entry]["id"], 
                    article_entry, 
                    pdo[link_entry["title"]]["id"], 
                    link_entry["title"], 
                    link_entry["count"]
                    )
                row_list.append(row)

                if len(row_list)%50000 == 0:
                    execute_values(cur, query, row_list)
                    cnt += 1
                    print(f"{cnt*50000} wikilinks inserted")
                    row_list.clear()

        execute_values(cur, query, row_list)

def main():
    print("Starting data inserts")
    create_tables()
    get_conn().cursor().execute("""TRUNCATE page CASCADE""")
    insert_data_page()
    insert_data_links()
    print("Data insertion finished")

if __name__ == "__main__":
    is_test = True

    if is_test:
        state.load_test_data()
    main()
