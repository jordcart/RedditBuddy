import psycopg2

def add_to_database(connection, cur, user_id, subreddit, keyword, unix_time):
    #checking if entry already exists
    sql = "SELECT * FROM Searches WHERE discord_id=%s AND subreddit=%s AND keyword=%s;"
    val = (str(user_id), subreddit, keyword)
    cur.execute(sql, val)
    entries = cur.fetchall()

    #if listing doesnt exist add to database
    if entries == []:
        val = (user_id, subreddit, keyword, unix_time, 0)
        sql = """INSERT INTO Searches (discord_id, subreddit, keyword, last_check, listings_found) VALUES (%s, %s, %s, %s, %s)"""
        try:
            cur.execute(sql, val)
            connection.commit()
        except:
            return False

        print("Entry inserted successfully into table")
        return True 
    else:
        return False 

def remove_from_database(connection, cur, user_id, keyword, subreddit):
    sql = "SELECT * FROM Searches WHERE discord_id=%s AND subreddit=%s AND keyword=%s;"
    val = (str(user_id), keyword, subreddit, )
    try:
        cur.execute(sql, val)
        entries = cur.fetchall()
    except:
        return False

    if entries == []:
        return False 
    else: 
        sql = "DELETE FROM Searches WHERE discord_id=%s AND subreddit=%s AND keyword=%s;"
        val = (str(user_id), keyword, subreddit, )
        cur.execute(sql, val)
        connection.commit()
        return True 

# updates the time for when a listing is found as well as incremements a variable containg number of listings found
def update_entry(connection, cur, user_id, subreddit, keyword, new_time):
    sql = "UPDATE Searches SET last_check=%s, listings_found=listings_found+1 WHERE discord_id=%s AND subreddit=%s AND keyword=%s"
    val = (str(new_time), str(user_id), subreddit, keyword, )
    try:
        cur.execute(sql, val)
        connection.commit()
    except:
        print(error)

def get_user_entries(connection, cur, user_id):
    sql = "SELECT subreddit, keyword, listings_found FROM Searches WHERE discord_id=%s;"
    val = (str(user_id), )
    try:
        cur.execute(sql, val)
        entries = cur.fetchall()
    except:
        print(error)
        return None
    return entries

def get_all_entries(connection, cur):
    sql = "SELECT * FROM Searches;"
    try:
        cur.execute(sql)
        entries = cur.fetchall()
    except:
        print(error)
        return None
    return entries

def add_new_user(connection, cur):
    sql = "UPDATE Stats SET all_users=all_users+1 WHERE name='main';"
    try:
        cur.execute(sql)
        connection.commit()
    except:
        print(error)
        return False
    return True

def add_listing(connection, cur):
    sql = "UPDATE Stats SET all_listings=all_listings+1 WHERE name='main';"
    try:
        cur.execute(sql)
        connection.commit()
    except:
        print(error)
        return False
    return True

def connect_to_database(user, database, password, host, port):
    myConnection = psycopg2.connect(
            user=user,
            database=database,
            password=password,
            host=host,
            port=port)
    return myConnection

