# 必须配置（从历史）
FLASK_APP = 'superset.app:create_app()'
SECRET_KEY = 'your_random_secret_key_here'  # 确保有随机密钥

# 数据库 URI：用绝对路径修复 Windows 反射问题
SQLALCHEMY_DATABASE_URI = r'sqlite:///F:\Python\agent_Project2\superset_home.db'

# 修复 NoSuchTableError：允许不安全连接（反射时绕过权限检查）
PREVENT_UNSAFE_DB_CONNECTIONS = False

# 汉化（保留）
BABEL_DEFAULT_LOCALE = "zh"
LANGUAGES = {
    "zh": {"name": "Chinese"},
    "en": {"name": "English"},
}
