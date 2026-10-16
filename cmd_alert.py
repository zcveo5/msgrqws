import os

for root, folders, files in os.walk('./'):
    if 'teardown' in str(root).lower():
        for file in files:
            spl = str(root).replace('\\', '/').split('/')
            if len(spl) > 5:
                print(f'Founded path: {'/'.join(spl[0:3])}...{'/'.join(spl[-3::])}')
            else:
                print(f'Founded path: {'/'.join(spl)}')
input('Finish')