:: 新开窗口启动后端
start cmd /k "cd backend && py app.py"

:: 新开窗口启动前端
start cmd /k "cd frontend && py app.py"

:: 打开浏览器
start http://localhost:5000/