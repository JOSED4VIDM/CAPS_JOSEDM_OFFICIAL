import asyncio
from getpass import getpass
from uuid import uuid4

from app.config import ADMIN_EMAIL
from app.database import close_database, get_collection, initialize_database
from app.security import hash_password


async def bootstrap_admin() -> None:
    if not ADMIN_EMAIL:
        raise RuntimeError("Configura ADMIN_EMAIL en backend/.env antes de crear el administrador.")

    await initialize_database()
    try:
        users_collection = get_collection("users")
        if users_collection is None:
            raise RuntimeError("La configuración de MongoDB es necesaria para crear el administrador.")

        existing_user = await users_collection.find_one({"email": ADMIN_EMAIL})
        password = getpass("Contraseña del administrador (mínimo 12 caracteres): ")
        if len(password) < 12:
            raise ValueError("La contraseña debe tener al menos 12 caracteres.")
        if password != getpass("Confirma la contraseña: "):
            raise ValueError("Las contraseñas no coinciden.")

        password_hash = hash_password(password)
        if existing_user:
            await users_collection.update_one(
                {"email": ADMIN_EMAIL},
                {"$set": {"is_admin": True, "password_hash": password_hash}},
            )
            print("La cuenta existente quedó configurada como administrador.")
        else:
            full_name = input("Nombre del administrador: ").strip()
            if not full_name:
                raise ValueError("El nombre es obligatorio.")

            await users_collection.insert_one({
                "id": f"u-{uuid4().hex[:12]}",
                "full_name": full_name,
                "email": ADMIN_EMAIL,
                "password_hash": password_hash,
                "is_admin": True,
            })
            print("La cuenta de administrador se creó correctamente.")
    finally:
        await close_database()


if __name__ == "__main__":
    asyncio.run(bootstrap_admin())
