import asyncio
from prisma import Prisma
import os
from datetime import datetime
import json

async def execute_command(command: str, prisma: Prisma):
    if command.startswith('await '):
        command = command[6:]  # Remove 'await ' prefix
    
    # Execute the command
    result = await eval(command)
    
    # Convert result to dict for better formatting
    if hasattr(result, '__dict__'):
        result = result.__dict__
    elif isinstance(result, list):
        result = [item.__dict__ if hasattr(item, '__dict__') else item for item in result]
    
    return result

async def main():
    # Initialize Prisma client
    prisma = Prisma()
    await prisma.connect()

    # Example usage
    print("Prisma client initialized. You can use 'prisma' to interact with the database.")
    print("\nExample commands:")
    print("  await prisma.moneta_lagosubscription.create(data={'customer_id': 'test123', 'status': 'active'})")
    print("  await prisma.moneta_lagosubscription.find_many()")
    print("  await prisma.moneta_lagosubscription.find_unique(where={'id': 'some_id'})")
    print("\nType 'exit' to quit")

    while True:
        try:
            command = input("\n>>> ")
            if command.lower() == 'exit':
                break

            # Execute the command
            result = await execute_command(command, prisma)
            print(json.dumps(result, default=str, indent=2))

        except Exception as e:
            print(f"Error: {str(e)}")

    await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(main()) 