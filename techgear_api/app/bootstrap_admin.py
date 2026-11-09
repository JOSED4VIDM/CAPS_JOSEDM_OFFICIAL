import asyncio
from getpass import getpass
from uuid import uuid4

from app.config import ADMIN_EMAIL, ADMIN_PASSWORD, DEBUG
from app.database import close_database, get_collection, initialize_database
from app.main import USER_STORE, persist_local_store
from app.security import hash_password


async def bootstrap_admin() -> None:
    if not ADMIN_EMAIL:
        raise RuntimeError("Configura ADMIN_EMAIL en techgear_api/.env antes de crear el administrador.")

    await initialize_database()
    try:
        users_collection = get_collection("users")
        existing_user = None
        if users_collection is not None:
            existing_user = await users_collection.find_one({"email": ADMIN_EMAIL})
        else:
            existing_user = next((user for user in USER_STORE if user.get("email", "").lower() == ADMIN_EMAIL.lower()), None)

        password = ADMIN_PASSWORD or getpass("Contraseña del administrador (mínimo 12 caracteres): ")
        if len(password) < 12:
            raise ValueError("La contraseña debe tener al menos 12 caracteres.")
        if not ADMIN_PASSWORD and password != getpass("Confirma la contraseña: "):
            raise ValueError("Las contraseñas no coinciden.")

        password_hash = hash_password(password)
        if existing_user:
            existing_user["is_admin"] = True
            existing_user["password_hash"] = password_hash
            if users_collection is not None:
                await users_collection.update_one(
                    {"email": ADMIN_EMAIL},
                    {"$set": {"is_admin": True, "password_hash": password_hash}},
                )
            else:
                persist_local_store()
            print("La cuenta existente quedó configurada como administrador.")
        else:
            full_name = input("Nombre del administrador: ").strip()
            if not full_name:
                raise ValueError("El nombre es obligatorio.")

            new_user = {
                "id": f"u-{uuid4().hex[:12]}",
                "full_name": full_name,
                "email": ADMIN_EMAIL,
                "password_hash": password_hash,
                "is_admin": True,
            }
            if users_collection is not None:
                await users_collection.insert_one(new_user)
            else:
                if DEBUG:
                    USER_STORE.append(new_user)
                    persist_local_store()
                else:
                    raise RuntimeError("La configuración de MongoDB es necesaria para crear el administrador.")
            print("La cuenta de administrador se creó correctamente.")
    finally:
        await close_database()


if __name__ == "__main__":
    asyncio.run(bootstrap_admin())
import asyncio
from getpass import getpass
from uuid import uuid4

from app.config import ADMIN_EMAIL, DEBUG
from app.database import close_database, get_collection, initialize_database
from app.main import USER_STORE, persist_local_store
from app.security import hash_password


async def bootstrap_admin() -> None:
    if not ADMIN_EMAIL:
        raise RuntimeError("Configura ADMIN_EMAIL en backend/.env antes de crear el administrador.")

    await initialize_database()
    try:
        users_collection = get_collection("users")
        existing_user = None
        if users_collection is not None:
            existing_user = await users_collection.find_one({"email": ADMIN_EMAIL})
        else:
            existing_user = next((user for user in USER_STORE if user.get("email", "").lower() == ADMIN_EMAIL.lower()), None)

        password = getpass("Contraseña del administrador (mínimo 12 caracteres): ")
        if len(password) < 12:
            raise ValueError("La contraseña debe tener al menos 12 caracteres.")
        if password != getpass("Confirma la contraseña: "):
            raise ValueError("Las contraseñas no coinciden.")

        password_hash = hash_password(password)
        if existing_user:
            existing_user["is_admin"] = True
            existing_user["password_hash"] = password_hash
            if users_collection is not None:
                await users_collection.update_one(
                    {"email": ADMIN_EMAIL},
                    {"$set": {"is_admin": True, "password_hash": password_hash}},
                )
            else:
                persist_local_store()
            print("La cuenta existente quedó configurada como administrador.")
        else:
            full_name = input("Nombre del administrador: ").strip()
            if not full_name:
                raise ValueError("El nombre es obligatorio.")

            new_user = {
                "id": f"u-{uuid4().hex[:12]}",
                "full_name": full_name,
                "email": ADMIN_EMAIL,
                "password_hash": password_hash,
                "is_admin": True,
            }
            if users_collection is not None:
                await users_collection.insert_one(new_user)
            else:
                if DEBUG:
                    USER_STORE.append(new_user)
                    persist_local_store()
                else:
                    raise RuntimeError("La configuración de MongoDB es necesaria para crear el administrador.")
            print("La cuenta de administrador se creó correctamente.")
    finally:
        await close_database()


if __name__ == "__main__":
    asyncio.run(bootstrap_admin())
