import concurrent.futures
import subprocess
import sys

def run_script():
    try:
        # Replace 'your_script.py' with your actual Python script
        subprocess.check_call(['python3', 'generateBaseLine.py'])
    except subprocess.CalledProcessError:
        print('An instance crashed, starting a new one...')
        return run_script()

def main():
    # Number of parallel instances you want to run
    num_instances = 700

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_instances) as executor:
        futures = {executor.submit(run_script) for _ in range(num_instances)}

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f'An error occurred: {e}', file=sys.stderr)

if __name__ == '__main__':
    main()
