import motor.motor_asyncio

CLIENT = None


async def connect(connection_uri: str) -> None:
    """Connect to the database

    Parameters:
    connection_uri (str): MongoDB connection uri

    """

    global CLIENT
    CLIENT = motor.motor_asyncio.AsyncIOMotorClient(connection_uri)


def client():
    """Returns current client"""

    return CLIENT


class Ignore:
    """Use this class for when you need to ignore a key"""

    pass


class Model:
    """Pythongo MongoDB Model"""

    def __init__(self) -> None:
        self.old_data = self.to_dict()

    def to_dict(self) -> dict:
        """Convert variables into the dictionary

        Returns:
        dict: key-value dictionary variables
        """

        return {k: v for k, v in vars(self).items() if k not in ("database", "collection", "old_data") and not v == Ignore}

    async def save(self):
        """Save the model to the collection"""

        result = await CLIENT[self.database][self.collection].update_one(self.old_data, {"$set": self.to_dict()}, upsert=True)
        self.old_data = self.to_dict()

        return result

    async def find_one(self):
        """Find the first data that matches"""

        return await CLIENT[self.database][self.collection].find_one(self.to_dict())

    async def find(self):
        """Returns all of the datas that matches with model"""

        async for doc in CLIENT[self.database][self.collection].find(self.to_dict()):
            yield doc

    async def delete(self):
        """Deletes all matching documents from collection"""

        return await CLIENT[self.database][self.collection].delete_many(self.to_dict())

    async def count(self):
        """Determine the number of document in a collection"""

        return await CLIENT[self.database][self.collection].count_documents(self.to_dict())
