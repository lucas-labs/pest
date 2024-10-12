from examples.api.app.modules.auth.db.session import Session, User


class AuthService:
    db: Session  # 💉 automatically injected (scoped to request, using async generator)

    async def login(self, username: str, password: str) -> User | None:
        user = await self.db.select_user_where_username_eq(username)
        if not user:
            return None
        if user.password == password:
            return user
        return None
