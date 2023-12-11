import subprocess

# Function to run Django management commands
def run_django_command(command):
    try:
        subprocess.run(command.split(), check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        # Handle the error as needed

# Run 'migrate' command
run_django_command('python3 manage.py migrate')

# Run 'loaddata' for each data file
files_to_load = ['db_data/users_data.json', 'db_data/inventory_data.json', 'db_data/pos_data.json']

for file in files_to_load:
    run_django_command(f'python3 manage.py loaddata {file}')
