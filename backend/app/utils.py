"""
工具函数模块

注意：此文件中的 hash_password 是临时占位实现，将在 Task 3 中替换为真实的加密实现
"""

def hash_password(password: str) -> str:
    """
    密码加密函数（临时占位实现）

    Args:
        password: 明文密码

    Returns:
        str: 加密后的密码
    """
    # 临时实现：简单返回密码 + "_hashed" 前缀
    # 这将在 Task 3 中替换为 bcrypt 实现
    return f"hashed_{password}"
