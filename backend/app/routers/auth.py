"""
认证路由 - 用户注册、登录、信息管理

提供完整的用户认证功能：
- 用户注册和登录
- JWT Token生成和验证
- 用户信息管理
- 密码加密存储
"""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import Field

from app.services.database import get_db
from app.models.user import User, UserCreate, UserLogin, UserResponse, Token, UserUpdate
from app.services.auth_service import (
    verify_password,
    get_password_hash,
    create_access_token,
)
from app.dependencies.auth import get_current_user

router = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
    responses={
        400: {"description": "请求参数错误"},
        401: {"description": "认证失败 - 用户名或密码错误"},
        404: {"description": "资源不存在"},
        500: {"description": "服务器内部错误"},
    },
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
    description="""
创建新用户账号。

**要求**:
- 用户名：3-20个字符，只能包含字母、数字、下划线
- 密码：至少8个字符，建议包含大小写字母、数字和特殊字符
- 邮箱：可选，如果提供必须是有效格式

**注意**: 
- 用户名和邮箱必须唯一
- 密码会自动加密存储，不会明文保存
""",
    response_description="成功创建的用户信息（不包含密码）",
)
async def register(
    user_data: UserCreate = Body(..., description="用户注册信息"),
    db: AsyncSession = Depends(get_db)
):
    """
    用户注册
    
    Args:
        user_data: 用户注册信息
        db: 数据库会话
    
    Returns:
        新创建的用户信息（不含密码）
    
    Raises:
        HTTPException: 用户名已存在
    """
    # 检查用户名是否已存在
    result = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已被注册"
        )
    
    # 检查邮箱是否已存在（如果提供了邮箱）
    if user_data.email:
        result = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
    
    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        nickname=user_data.nickname,
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return UserResponse.from_orm(new_user)


@router.post(
    "/login",
    response_model=Token,
    summary="用户登录",
    description="""
使用用户名/邮箱和密码登录，获取JWT访问令牌。

**返回内容**:
- `access_token`: JWT访问令牌
- `token_type`: Token类型（Bearer）
- `expires_in`: 过期时间（秒）
- `user`: 用户基本信息

**使用方式**:
在后续请求的Header中添加: `Authorization: Bearer {access_token}`
""",
    response_description="包含访问令牌和用户信息的响应",
)
async def login(
    login_data: UserLogin = Body(..., description="登录凭证"),
    db: AsyncSession = Depends(get_db)
):
    """
    用户登录
    
    Args:
        login_data: 登录凭证
        db: 数据库会话
    
    Returns:
        JWT token 和用户信息
    
    Raises:
        HTTPException: 用户名或密码错误
    """
    # 查找用户
    result = await db.execute(
        select(User).where(User.username == login_data.username)
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    # 更新最后登录时间
    user.last_login = datetime.utcnow()
    await db.commit()
    
    # 创建 access token
    access_token_expires = timedelta(minutes=60 * 24 * 7)  # 7天
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return UserResponse.from_orm(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新当前用户信息
    
    Args:
        user_update: 更新数据
        current_user: 当前用户
        db: 数据库会话
    
    Returns:
        更新后的用户信息
    """
    # 更新邮箱
    if user_update.email is not None:
        # 检查邮箱是否被其他用户使用
        result = await db.execute(
            select(User).where(User.email == user_update.email, User.id != current_user.id)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = user_update.email
    
    # 更新昵称
    if user_update.nickname is not None:
        current_user.nickname = user_update.nickname
    
    # 更新头像
    if user_update.avatar_url is not None:
        current_user.avatar_url = user_update.avatar_url
    
    # 更新密码
    if user_update.password is not None:
        current_user.hashed_password = get_password_hash(user_update.password)
    
    await db.commit()
    await db.refresh(current_user)
    
    return UserResponse.from_orm(current_user)


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    用户登出
    
    Note: JWT 是无状态的，客户端需要删除 token
    """
    return {"message": "Successfully logged out"}
