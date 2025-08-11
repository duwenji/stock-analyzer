import os
import shutil

def create_env_file():
    env_path = os.path.join('backend', '.env')
    example_path = os.path.join('backend', '.env.example')
    
    if not os.path.exists(env_path):
        shutil.copyfile(example_path, env_path)
        print(f"Created {env_path} from {example_path}")
    else:
        print(f"{env_path} already exists")

if __name__ == "__main__":
    create_env_file()
