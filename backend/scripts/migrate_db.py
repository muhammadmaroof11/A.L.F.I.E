import asyncio
import os
import sys

# Add the parent directory to sys.path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from migrations import main


if __name__ == "__main__":
    asyncio.run(main())

