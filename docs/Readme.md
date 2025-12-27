本项目在python 3.13上开展

要运行本项目
后端
# 1、更改backend\config.py中Wu20050612!为你自己的数据库密码
# 2. 进入后端目录
cd backend
# 3. 安装依赖
pip install -r requirements.txt
# 4. 初始化数据库（MySQL）
mysql -u root -p < database.sql
# 前四步仅在初次构建时进行
# 5. 启动Flask应用
python app.py

前端
# 1. 进入前端目录
cd frontend
# 2. 安装依赖
npm install 
# 前两步仅在初次构建时需要进行
# 3. 开发模式启动
npm run dev
# 4. 生产构建
npm run build
# 5. 预览生产构建
npm run preview

若是数据库创建错误
mysql -u root -p

DROP DATABASE IF EXISTS library_system;

EXIT;
然后再次创建

默认管理员
账号： admin
密码： admin123

# 暂时没解决图像显示问题