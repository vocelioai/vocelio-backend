#!/usr/bin/env python3
import asyncio, os, socket, sys, time

TARGETS = [
    (os.getenv('POSTGRES_HOST', 'postgres'), int(os.getenv('POSTGRES_PORT', '5432'))),
    (os.getenv('REDIS_HOST', 'redis'), int(os.getenv('REDIS_PORT', '6379')))
]

TIMEOUT = int(os.getenv('WAIT_TIMEOUT', '60'))

async def check_host(host, port):
    try:
        fut = asyncio.open_connection(host, port)
        reader, writer = await asyncio.wait_for(fut, timeout=2)
        writer.close()
        await writer.wait_closed()
        return True
    except Exception:
        return False

async def wait_all():
    start = time.time()
    remaining = set(TARGETS)
    while remaining and time.time() - start < TIMEOUT:
        done = set()
        for host, port in list(remaining):
            if await check_host(host, port):
                print(f"✅ {host}:{port} is up")
                done.add((host, port))
        remaining -= done
        if remaining:
            await asyncio.sleep(2)
    if remaining:
        print(f"❌ Timeout waiting for: {', '.join(f'{h}:{p}' for h,p in remaining)}")
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(wait_all())
