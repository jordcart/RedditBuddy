import psycopg2

def add_to_database(connection, cur, user_id, subreddit, keyword, unix_time):
    #checking if listing already exists
    sql = "SELECT * FROM Searches WHERE discord_id=%s AND subreddit=%s AND keyword=%s;"
    val = (str(user_id), subreddit, keyword)
    cur.execute(sql, val)
    entries = cur.fetchall()

    #if listing doesnt exist add to database
    if entries == []:
        val = (user_id, subreddit, keyword, unix_time, 0)
        sql = """INSERT INTO Searches (discord_id, subreddit, keyword, last_check, listings_found) VALUES (%s, %s, %s, %s, %s)"""
        cur.execute(sql, val)
        connection.commit()
        count = cur.rowcount
        print(count, "Record inserted successfully into mobile table")
        return True 
    else:
        return False 

def remove_from_database(connection, cur, user_id, keyword, subreddit):
    sql = "SELECT * FROM Searches WHERE discord_id='{}' AND subreddit='{}' AND keyword='{}';".format(user_id, keyword,
            subreddit)
    cur.execute(sql)
    entries = cur.fetchall()

    if entries == []:
        return False 
    else: 
        sql = "DELETE FROM Searches WHERE discord_id='{}' AND subreddit='{}' AND keyword='{}';".format(user_id, keyword,
                subreddit)
        cur.execute(sql)
        connection.commit()
        return True 

# updates the time for when a listing is found as well as incremements a variable containg number of listings found
def update_entry(connection, cur, user_id, subreddit, keyword, new_time):
    sql = """UPDATE Searches SET last_check='{}', listings_found=listings_found+1
             WHERE discord_id='{}' AND subreddit='{}' AND keyword='{}'""".format(new_time, user_id, subreddit, keyword)
    cur.execute(sql)
    connection.commit()

def get_user_entries(connection, cur, user_id):
    sql = "SELECT subreddit, keyword, listings_found FROM Searches WHERE discord_id='{}';".format(user_id)
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

