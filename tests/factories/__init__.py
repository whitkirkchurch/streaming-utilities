from services import Service


def serviceFactory(fields, id: str = "a1b2c3d4") -> Service:
    return Service({"id": id, "fields": fields})
