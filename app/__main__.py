import sys
import asyncio

from . import rb_worker, redis_worker


if __name__ == '__main__':
    argv = sys.argv
    cmd = argv[1]
    
    if cmd == 'redis_worker':
        asyncio.run(redis_worker.main())
    elif cmd == 'rb_worker':
        asyncio.run(rb_worker.main())

