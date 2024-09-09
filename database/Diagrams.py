from diagrams import Diagram
from diagrams.programming.language import Python
from diagrams.onprem.database import Postgresql
from diagrams.onprem.client import User

with Diagram("System Architecture", show=False):
    user = User("User")
    
    web_app = Python("Web Application")
    
    db = Postgresql("SQLite Database")
    
    appliance_data_table = Postgresql("appliance_data Table")
    maintenance_data_table = Postgresql("maintenance_data Table")
    
    # User interacts with the web application
    user >> web_app

    # Web application ensures the database structure
    web_app >> db

    # The web application interacts with the appliance_data table
    web_app >> appliance_data_table
    
    # The web application interacts with the maintenance_data table
    web_app >> maintenance_data_table
    
    # Data retrieval from the database tables
    appliance_data_table >> web_app
    maintenance_data_table >> web_app
