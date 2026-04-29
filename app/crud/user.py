# from sqlalchemy.orm import Session
# from app.models.user import  LandLord
# from app.schemas.user import UserCreate
# from app.core.security import get_password_hash
#
# def get_user_by_email(db:Session, email: str):
#     return db.query(LandLord).filter(LandLord.email == email).first()
#
# def create_user(db: Session, user_data: UserCreate):
#     hashed_password = get_password_hash(user_data.password)
#     db_user = LandLord(
#         email=user_data.email.lower(),
#         hashed_password= hashed_password
#     )
#
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user
#
# def get_user_by_id(db: Session, user_id):
#     return db.query(LandLord).filter(LandLord.id == user_id).first()
#
#



