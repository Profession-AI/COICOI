from os import environ
import sys
import os

_KEY_EXT = "_API_KEY"

class _KeyManager:

    _instance = None
    _keys = None
    _key_file_path = os.path.dirname(os.path.abspath(sys.argv[0]))+"\providers.keys"
    _is_enabled = True

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(_KeyManager, cls).__new__(cls)
        return cls._instance

    def set_key_file(self, key_file_path: str):
        self._key_file_path = key_file_path

    def enabled(self, enable: bool):
        self._is_enabled = enable

    def load_key(self, provider: str):
        print(self._key_file_path)
        if not self._is_enabled:
            return

        key_name = provider.upper() + _KEY_EXT

        if self._keys is None:
            self._load_keys_from_file()            
            
        key = self._keys.get(key_name)
        if key is None:
            raise ValueError(f"Key for {provider} not found")
        
        environ[key_name] = key


    def _load_keys_from_file(self):

        try:
            with open(self._key_file_path, 'r') as f:
                self._keys = {}
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    if '=' in line:
                        provider, key = line.split('=', 1)
                        provider, key = provider.strip().upper(), key.strip().strip('"')
                        
                        if not provider.endswith(_KEY_EXT):
                            provider += _KEY_EXT
                            
                        self._keys[provider] = key
                    else:
                        print(f"Warning: Invalid line format in providers.keys: {line}")
        except FileNotFoundError:
            raise FileNotFoundError("providers.keys file not found. Please create it with your API keys.")



def load_key(provider: str):

    key_name = provider + _KEY_EXT

    if key_name in environ:
        return
    
    if 'google.colab' in sys.modules:
        _load_keys_from_colab(key_name)
    else:
        _KeyManager().load_key(provider)


def _load_keys_from_colab(key_name: str):
    from google.colab import userdata
    environ[key_name] = userdata.get(key_name)



if __name__ == "__main__":
    load_key("openai")
    print(environ["OPENAI_API_KEY"])
    load_key("deepseek")
    print(environ["DEEPSEEK_API_KEY"])

