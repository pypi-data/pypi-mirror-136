class StorageMount:
    def __init__(self, 
                 mount_point:str,
                 storage_config:dict, 
                 secrets_config:dict):
        '''This is a class to mount Azure Storage account'''

        self.mount_point = mount_point
        self.storage_config = storage_config
        self.secrets_config = secrets_config
        
    
    def __repr__(self):
        return f"Details fo Storage account are as below: \n{self.mount_point}\n{self.storage_config}"
    
    def keys(self):
        '''This is a method to mount Azure Storage account'''
        self.keys_and_secrets = False
        try:
            self.storage_name = self.storage_config['storageaccountname']
            self.container_name = self.storage_config['containername']
            self.secret_scope = self.secrets_config['secret_scope']
            self.secret_key_name = self.secrets_config['secret_key_name']
            print(self.storage_name, self.container_name, self.secret_scope, self.secret_key_name)
        except KeyError as e:
            print(f"KeyError: {e}")
            return False
        else:
            self.keys_and_secrets = True
            return self.keys_and_secrets
    
    def mount(self):
        keys_and_secrets = self.keys()

        if keys_and_secrets == False:
            return "Please provide the keys and secrets"
        else:
            try:
                dbutils.fs.mount(
                    source = f"wasbs://{self.container_name}@{self.storage_name}.blob.core.windows.net",
                    mount_point = f"/mnt/{self.mount_point}",
                    extra_configs = {
                        f"fs.azure.account.key.{self.storage_name}.blob.core.windows.net":dbutils.secrets.get(scope = self.secret_scope, key = self.secret_key_name)
                    })
            except Exception as e:
                print(f"Storage is already mounted at: {self.mount_point}")
                print(f"Exception: {e}")