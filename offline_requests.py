from kivy.storage.jsonstore import JsonStore


class OfflineRequest:
    def __init__(self, func_string, data):
        self.func_string = func_string
        self.func_names = ['authenticate', 'confirmForgotPassword', 'confirmSignUp', 'delete', 'forgotPassword',
                           'getCredentials', 'populate', 'refresh', 'signUp', 'sqlCreate', 'sqlUpdate', 'sqlDelete', 'upload']
        self.funcs = self.populate_func_list()
        self.func = self.request_handler()
        self.data = data
        self.error_message = {'message': "Incorrect input data", 'success': False}
        self.register = JsonStore('database/register.json')
        self.iteration = int(self.register['iteration'])
        self.credentials = {'aws_access_key_id': 'AKIASIQAEAFGMW6PUMM4',
                            'aws_secret_access_key': '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',
                            'bucket': 'seagrave'}

    def populate_func_list(self):
        return [self.authenticate, self.confirm_forgot_password, self.confirm_signup, self.delete, self.forgot_password,
                self.get_credentials, self.populate, self.refresh, self.signup, self.sql_create, self.sql_update, self.sql_delete,
                self.upload]

    def request_handler(self):
        return self.funcs[self.func_names.index(self.func_string)]

    def data_verification(self, input_data):
        return all(x in self.data for x in input_data)

    def authenticate(self):
        if not self.data_verification(['email', 'password']):
            return self.error_message
        if self.data['email'] == 'Tyson' and self.data['password'] == 'Tyson,123':
            return {'AuthenticationResult': {
                'AccessToken': 'string',
                'ExpiresIn': 123,
                'TokenType': 'string',
                'RefreshToken': 'string',
                'IdToken': 'string',
                'NewDeviceMetadata': {
                    'DeviceKey': 'string',
                    'DeviceGroupKey': 'string'
                }
            }
            }
        else:
            return {'message': "The username or password is incorrect",
                    'success': False}

    def confirm_forgot_password(self):
        return {"error": False, "success": True, "message": "Password has been changed successfully", "data": None}\
            if self.data_verification(['code', 'email', 'password']) else self.error_message

    def confirm_signup(self):
        return {"success": True, "message": "User is already confirmed"}\
            if self.data_verification(['code', 'email']) else self.error_message

    def delete(self):
        return {'result': 'success', 'iteration': self.iteration + 1}\
            if self.data_verification(['AccessToken', 'SiteId', 'action']) else self.error_message

    def forgot_password(self):
        return {"error": False, "success": True, "message": "Please check your Registered email id for validation code", "data": None} \
            if self.data_verification(['email']) else self.error_message

    def get_credentials(self):
        return self.credentials if self.data_verification(['AccessToken']) else self.error_message

    def populate(self):
        return {'status': 'none', 'user': 'Tyson'} \
            if self.data_verification(['blueprints', 'pictures', 'AccessToken', 'iteration']) else self.error_message

    def refresh(self):
        pass

    def signup(self):
        return {'UserConfirmed': False,
                'CodeDeliveryDetails': {'Destination': 'string', 'DeliveryMedium': 'EMAIL', 'AttributeName': 'string'},
                'UserSub': 'string'} \
            if self.data_verification(['email', 'password']) else self.error_message

    def sql_create(self):
        if not self.data_verification(['database']):
            return self.error_message
        db_name = self.data['database']
        if db_name in ['blueprints', 'pictures']:
            db_name = f"{db_name}/{db_name}"
        elif 'forms' in db_name:
            db_name = f"forms/{db_name}"
        db = JsonStore(f"database/{db_name}.json")
        new_id = max(int(x) for x in db) + 1 if db else 1
        return {'statusCode': 200,
                'body': new_id,
                'iteration': self.iteration + 1}

    def sql_update(self):
        return {'statusCode': 200, 'iteration': self.iteration + 1}\
            if self.data_verification([]) else self.error_message

    def sql_delete(self):
        return {'statusCode': 200, 'iteration': self.iteration + 1, 'body': 'success'}\
            if self.data_verification(['id']) else self.error_message

    def upload(self):
        return {'statusCode': 200, 'body': 's3_response', 'iteration': self.iteration + 1}\
            if self.data_verification(['file', 'name']) else self.error_message
