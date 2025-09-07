#!/usr/bin/python3
from itertools import islice
import importlib.util
import sys
import os

# Dynamically import 0-stream_users.py as a module
module_name = 'stream_users_mod'
stream_users_path = os.path.join(os.path.dirname(__file__), '0-stream_users.py')
spec = importlib.util.spec_from_file_location(module_name, stream_users_path)
stream_users_module = importlib.util.module_from_spec(spec)
sys.modules[module_name] = stream_users_module
spec.loader.exec_module(stream_users_module)

for user in islice(stream_users_module.stream_users(), 6):
    print(user)

