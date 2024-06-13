# import os
#
# from dotenv import load_dotenv
# import psycopg2
#
#
# class DatabaseManager:
#     def __init__(self):
#         self.connect()
#
#     def connect(self):
#         try:
#             load_dotenv()
#             db_host = os.environ.get("DB_HOST")
#             db_name = os.environ.get("DB_NAME")
#             db_user = os.environ.get("DB_USER")
#             db_password = os.environ.get("DB_PASS")
#             db_port = os.environ.get("DB_PORT")
#             self.connection = psycopg2.connect(
#                 dbname=db_name,
#                 user=db_user,
#                 password=db_password,
#                 host=db_host,
#                 port=db_port
#             )
#         except psycopg2.Error as error:
#             print("Error while connecting to PostgreSQL:", error)
#
#     def disconnect(self):
#         if self.connection:
#             self.connection.close()
#             print("Disconnected from the database.")
#         else:
#             print("No active connection.")
#
#     def execute_query(self, query, params=None):
#         try:
#             cursor = self.connection.cursor()
#             if params:
#                 cursor.execute(query, params)
#             else:
#                 cursor.execute(query)
#             if query.strip().lower().startswith(("insert", "update", "delete")):
#                 self.connection.commit()
#                 return None
#             else:
#                 result = cursor.fetchall()
#                 cursor.close()
#                 return result
#         except psycopg2.Error as e:
#             print("Error executing query:", e)
