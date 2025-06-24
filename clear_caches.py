import os
import shutil

CACHE_DIRS = [
    '__pycache__',
    '.pytest_cache',
    '.cache',
    'logs',
    'build',
    'dist',
    'downloads',
    'env',
    '.ipynb_checkpoints',
    '.mypy_cache',
    '.nox',
    '.tox',
]


def clear_cache_dirs(base_dir='.'):
    removed = []
    for root, dirs, files in os.walk(base_dir):
        for d in dirs:
            if d in CACHE_DIRS:
                dir_path = os.path.join(root, d)
                try:
                    shutil.rmtree(dir_path)
                    removed.append(dir_path)
                except Exception as e:
                    print(f'Could not remove {dir_path}: {e}')
    return removed

if __name__ == '__main__':
    removed = clear_cache_dirs('.')
    if removed:
        print('Removed:')
        for path in removed:
            print(f'  {path}')
    else:
        print('No cache directories found.')
