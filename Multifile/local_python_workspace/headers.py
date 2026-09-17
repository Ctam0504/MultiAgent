# headers.py

class Headers:
    @staticmethod
    def get_default_headers():
        return {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {token}'
        }

    @staticmethod
    def get_auth_headers(token):
        return {
            'Authorization': f'Bearer {token}'
        }