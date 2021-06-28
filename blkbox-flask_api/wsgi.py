"""Web Server Gateway Interface"""

##################
# FOR PRODUCTION
####################
from application import application

if __name__ == "__main__":
    ####################
    # FOR DEVELOPMENT
    ####################
    application.run(host='0.0.0.0', debug=True)