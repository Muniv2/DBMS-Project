import pyodbc

# SQL Server details
server = 'ALI-MAHMOODI'
database = 'spotify_project'  # Our database name
use_windows_authentication = True
username = ''
password = ''

# Create the connection string
if use_windows_authentication:
    connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
else:
    connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

class Database:
    def __init__(self):
        self.connection = None
        self.connect()
        if self.connection:
            self.create_tables()
    
    def connect(self):
        """Connect to SQL Server"""
        try:
            self.connection = pyodbc.connect(connection_string)
            print("Connected to the database successfully.")
            return True
            
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False
    
    def create_tables(self):
        """Create all tables using simple, direct SQL"""
        try:
            cursor = self.connection.cursor() #cursor is used to execute SQL commands

            # Create tables one by one
            tables = [
                # Listener table
                """
                CREATE TABLE Listener (
                    HUID INT PRIMARY KEY,
                    name NVARCHAR(255) NOT NULL,
                    password NVARCHAR(255) NOT NULL,
                    profilePic VARBINARY(MAX)
                )
                """,
                
                # Uploader table
                """
                CREATE TABLE Uploader (
                    HUID INT PRIMARY KEY,
                    name NVARCHAR(255) NOT NULL,
                    password NVARCHAR(255) NOT NULL,
                    profilePic VARBINARY(MAX),
                    totalViewCount INT DEFAULT 0,
                    totalLikeCount INT DEFAULT 0
                )
                """,
                
                # Song table
                """
                CREATE TABLE Song (
                    songID INT IDENTITY(1,1) PRIMARY KEY,
                    songName NVARCHAR(255) NOT NULL,
                    genre NVARCHAR(100),
                    paid BIT DEFAULT 0,
                    price DECIMAL(10,2) DEFAULT 0.00,
                    songFile NVARCHAR(255),
                    songViewCount INT DEFAULT 0,
                    songLikeCount INT DEFAULT 0
                )
                """,
                
                # Upload relationship table
                """
                CREATE TABLE Upload (
                    HUID INT,
                    songID INT,
                    FOREIGN KEY (HUID) REFERENCES Uploader(HUID),
                    FOREIGN KEY (songID) REFERENCES Song(songID),
                    PRIMARY KEY (HUID, songID)
                )
                """,
                
                # Purchase table
                """
                CREATE TABLE Purchase (
                    purchaseID INT IDENTITY(1,1) PRIMARY KEY,
                    songID INT,
                    HUID INT,
                    creditCardNum NVARCHAR(255),
                    expiryDate DATE,
                    FOREIGN KEY (songID) REFERENCES Song(songID),
                    FOREIGN KEY (HUID) REFERENCES Listener(HUID)
                )
                """
            ]
            
            # Execute each table creation
            for i, table_sql in enumerate(tables):
                try:
                    cursor.execute(table_sql)
                    print(f"Table {i+1} created successfully.")
                except Exception as e:
                    if "There is already an object named" in str(e):
                        print(f"Table {i+1} already exists")
                    else:
                        print(f"Error creating table {i+1}: {e}")
            
            self.connection.commit()
            
        except Exception as e:
            print(f"Table creation failed: {e}")
    
    def execute_query(self, query, params=None):
        """Execute SQL queries"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # For SELECT queries, return results
            if query.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            else:
                # For INSERT/UPDATE/DELETE, commit changes
                self.connection.commit()
                return True
                
        except Exception as e:
            print(f"Query failed: {e}")
            return None