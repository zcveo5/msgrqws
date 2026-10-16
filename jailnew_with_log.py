import asyncio
import asyncio.subprocess as sub
import sys


async def main():
    while True:
        proc = await sub.create_subprocess_exec(sys.executable, 'jailnew.py', '--no-restart-log', stdout=sub.PIPE, stderr=sub.PIPE)
        fl = open('./data/msgr1.log', 'wb')

        async def read_stream(stream: asyncio.StreamReader, color=''):
            while True:
                line = await stream.readline()
                if not line:
                    return

                sys.stdout.write(f'{color}{line.decode('utf-8')}\x1b[0m')
                sys.stdout.flush()
                fl.write(line)

        await asyncio.gather(read_stream(proc.stdout), read_stream(proc.stderr, '\x1b[31m'))

        code = await proc.wait()
        if code == 1:
            print('An error occurred!')
            print('See logs')
            break
        if code != 2:
            print(f'Restart not needed ({code})')
            break

asyncio.run(main())

print('Log saved in ./data/msgr1.log')