from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash

class Subscription:
    db = 'login_reg_schema'

    def __init__(self, data):
        self.user_id = data['user_id']
        self.newsletter_id = data['newsletter_id']

    @staticmethod
    def create(form_data, user_id):
        selected_newsletters = form_data.getlist('newsletters')
        for newsletter_id in selected_newsletters:
            print(newsletter_id)
            query = """
                INSERT INTO newsletter_subscriptions
                (user_id, newsletter_id)
                VALUES
                (%(user_id)s, %(newsletter_id)s);
        """
            data = {
                'user_id': user_id,
                'newsletter_id': newsletter_id
            }

            connectToMySQL('login_reg_schema').query_db(query, data)

            
        
