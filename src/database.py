import psycopg2

def add_to_database(connection, cur, user_id, subreddit, keyword, unix_time):
    #checking if listing already exists
    sql = "SELECT * FROM Searches WHERE discord_id=%s AND subreddit=%s AND keyword=%s;"
    val = (str(user_id), subreddit, keyword)
    cur.execute(sql, val)
    entries = cur.fetchall()

    #if listing doesnt exist add to database
    if entries == []:
        val = (user_id, subreddit, keyword, unix_time)
        sql = """INSERT INTO Searches (discord_id, subreddit, keyword, last_check) VALUES (%s, %s, %s, %s)"""
        cur.execute(sql, val)
        connection.commit()
        count = cur.rowcount
        print(count, "Record inserted successfully into mobile table")
        return 1;
    else:
        return 0;

def remove_from_database(connection, cur, user_id, keyword, subreddit):
    sql = "SELECT * FROM Searches WHERE discord_id='{}' AND subreddit='{}' AND keyword='{}';".format(user_id, keyword,
            subreddit)
    cur.execute(sql)
    entries = cur.fetchall()

    if entries == []:
        print("no entries")
        return 0
    else: 
        sql = "DELETE FROM Searches WHERE discord_id='{}' AND subreddit='{}' AND keyword='{}';".format(user_id, keyword,
                subreddit)
        cur.execute(sql)
        connection.commit()
        return 1


def get_user_entries(connection, cur, user_id):
    sql = "SELECT subreddit, keyword FROM Searches WHERE discord_id='{}';".format(user_id)
    cur.execute(sql)
    entries = cur.fetchall()
    return entries

def get_all_entries(connection, cur):
    sql = "SELECT * FROM Searches;"
    cur.execute(sql)
    entries = cur.fetchall()
    return entries

def connect_to_database(user, database, password, host, port):
    myConnection = psycopg2.connect(
            user=user,
            database=database,
            password=password,
            host=host,
            port=port)
    return myConnection

