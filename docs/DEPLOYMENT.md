# 部署指南

## 部署方式

本系统支持多种部署方式，适用于不同场景。

## 1. 本地开发部署

### 系统要求

**最低配置**：
- CPU: 4核心
- 内存: 8GB RAM
- 磁盘: 20GB 可用空间
- 操作系统: Linux/macOS/Windows

**推荐配置**：
- CPU: 8核心+
- 内存: 16GB+ RAM
- 磁盘: 50GB+ SSD
- GPU: 可选（NVIDIA GPU 加速）

### 快速部署

```bash
# 1. 克隆项目
git clone https://github.com/Irene-hua/graduation-design.git
cd graduation-design

# 2. 运行自动安装脚本
chmod +x setup.sh
./setup.sh

# 3. 启动系统
source venv/bin/activate
streamlit run src/web/app.py
```

### 手动部署

#### 步骤1: 安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

#### 步骤2: 启动 Qdrant

**使用 Docker**:
```bash
docker-compose up -d
```

**或手动启动**:
```bash
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant
```

验证 Qdrant 运行:
```bash
curl http://localhost:6333/health
```

#### 步骤3: 安装 Ollama

访问 https://ollama.ai 下载安装。

```bash
# 拉取模型
ollama pull llama3.2:3b

# 验证
ollama list
```

#### 步骤4: 初始化系统

```bash
# 生成加密密钥
python cli.py setup-key

# 测试系统
python examples/basic_usage.py
```

#### 步骤5: 启动服务

```bash
# Web界面
streamlit run src/web/app.py

# 或使用CLI
python cli.py query -q "你的问题"
```

## 2. Docker 部署

### 创建 Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 暴露端口
EXPOSE 8501

# 启动命令
CMD ["streamlit", "run", "src/web/app.py", "--server.address", "0.0.0.0"]
```

### 构建和运行

```bash
# 构建镜像
docker build -t privacy-rag:latest .

# 运行容器
docker run -p 8501:8501 \
    -v $(pwd)/data:/app/data \
    -v $(pwd)/config:/app/config \
    privacy-rag:latest
```

### Docker Compose 完整部署

```yaml
version: '3.8'

services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage
    
  rag-app:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./config:/app/config
    depends_on:
      - qdrant
    environment:
      - QDRANT_HOST=qdrant
      - QDRANT_PORT=6333

volumes:
  qdrant_data:
```

启动:
```bash
docker-compose up -d
```

## 3. 生产环境部署

### 使用 Systemd (Linux)

创建服务文件 `/etc/systemd/system/privacy-rag.service`:

```ini
[Unit]
Description=Privacy-Preserving RAG System
After=network.target

[Service]
Type=simple
User=rag-user
WorkingDirectory=/opt/privacy-rag
Environment="PATH=/opt/privacy-rag/venv/bin"
ExecStart=/opt/privacy-rag/venv/bin/streamlit run src/web/app.py --server.port 8501
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务:
```bash
sudo systemctl daemon-reload
sudo systemctl enable privacy-rag
sudo systemctl start privacy-rag
```

### 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### HTTPS 配置

```bash
# 安装 certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com
```

## 4. Kubernetes 部署

### 创建部署文件

**deployment.yaml**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: privacy-rag
spec:
  replicas: 2
  selector:
    matchLabels:
      app: privacy-rag
  template:
    metadata:
      labels:
        app: privacy-rag
    spec:
      containers:
      - name: rag-app
        image: privacy-rag:latest
        ports:
        - containerPort: 8501
        env:
        - name: QDRANT_HOST
          value: "qdrant-service"
        volumeMounts:
        - name: data
          mountPath: /app/data
        - name: config
          mountPath: /app/config
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: rag-data-pvc
      - name: config
        configMap:
          name: rag-config
```

**service.yaml**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: privacy-rag-service
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8501
  selector:
    app: privacy-rag
```

部署:
```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

## 5. 安全加固

### 密钥管理

```bash
# 设置严格权限
chmod 600 config/encryption.key
chown rag-user:rag-user config/encryption.key

# 使用环境变量（推荐）
export RAG_ENCRYPTION_KEY=$(cat config/encryption.key | base64)
```

### 防火墙配置

```bash
# 仅允许本地访问（最安全）
sudo ufw allow from 127.0.0.1 to any port 8501

# 或限制特定IP
sudo ufw allow from 192.168.1.0/24 to any port 8501
```

### 日志轮转

创建 `/etc/logrotate.d/privacy-rag`:
```
/opt/privacy-rag/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 rag-user rag-user
    sharedscripts
}
```

## 6. 性能优化

### GPU 加速

如果有 NVIDIA GPU:

```bash
# 安装 CUDA 支持
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 修改配置
# config/config.yaml
embedding:
  device: "cuda"
```

### 模型缓存

```bash
# 设置模型缓存目录
export TRANSFORMERS_CACHE=/path/to/cache
export HF_HOME=/path/to/cache
```

### 资源限制 (Docker)

```bash
docker run --cpus="4" --memory="8g" \
    -p 8501:8501 privacy-rag:latest
```

## 7. 监控和维护

### 健康检查

```bash
# Qdrant
curl http://localhost:6333/health

# Ollama
ollama list

# 应用
curl http://localhost:8501/healthz
```

### 日志查看

```bash
# 应用日志
tail -f logs/audit.log

# Docker 日志
docker logs -f privacy-rag

# Systemd 日志
journalctl -u privacy-rag -f
```

### 备份

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/privacy-rag/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# 备份向量数据库
docker exec qdrant tar czf - /qdrant/storage > $BACKUP_DIR/qdrant.tar.gz

# 备份配置和密钥（加密！）
tar czf - config/ | gpg --encrypt --recipient your@email.com > $BACKUP_DIR/config.tar.gz.gpg

# 备份数据
tar czf $BACKUP_DIR/data.tar.gz data/
```

### 自动化备份 (Cron)

```bash
# 每天凌晨2点备份
0 2 * * * /opt/privacy-rag/backup.sh
```

## 8. 故障排除

### Qdrant 连接失败

```bash
# 检查服务状态
docker ps | grep qdrant

# 查看日志
docker logs qdrant

# 重启服务
docker restart qdrant
```

### Ollama 模型未找到

```bash
# 检查已安装模型
ollama list

# 重新拉取
ollama pull llama3.2:3b

# 检查磁盘空间
df -h
```

### 内存不足

```bash
# 检查内存使用
free -h

# 使用更小的模型
# 或启用量化
# 或增加交换空间
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 9. 升级指南

```bash
# 1. 备份数据
./backup.sh

# 2. 拉取最新代码
git pull

# 3. 更新依赖
pip install -r requirements.txt --upgrade

# 4. 重启服务
sudo systemctl restart privacy-rag
```

## 10. 卸载

```bash
# 停止服务
sudo systemctl stop privacy-rag
sudo systemctl disable privacy-rag

# 删除服务文件
sudo rm /etc/systemd/system/privacy-rag.service

# 删除 Docker 容器
docker-compose down -v

# 删除应用目录
rm -rf /opt/privacy-rag

# 清理 Qdrant 数据（谨慎！）
rm -rf qdrant_storage/
```

## 总结

本指南提供了多种部署方式，从简单的本地开发到完整的生产环境部署。根据您的具体需求选择合适的部署方式。

关键要点：
- ✓ 始终保护好加密密钥
- ✓ 定期备份数据和配置
- ✓ 监控系统运行状态
- ✓ 及时更新依赖库
