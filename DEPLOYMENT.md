# Docker 部署指南

## 概述

本项目提供了完整的 Docker 部署方案，支持本地开发和生产环境部署。

## 文件说明

- `Dockerfile` - 生产环境镜像构建文件
- `docker-compose.yml` - 本地开发环境配置
- `docker-compose.prod.yml` - 生产环境配置
- `.dockerignore` - Docker 构建忽略文件
- `nginx/nginx.conf` - Nginx 反向代理配置
- `.env.prod.example` - 生产环境变量示例
- `release.sh` - 版本管理和发布脚本

## 本地开发

### 1. 启动开发环境

```bash
docker-compose up -d
```

这将启动：
- PostgreSQL 数据库（端口 5432）
- FastAPI 应用（端口 8000）

### 2. 查看日志

```bash
docker-compose logs -f app
```

### 3. 停止服务

```bash
docker-compose down
```

### 4. 停止服务并删除数据卷

```bash
docker-compose down -v
```

## 生产环境部署

### 1. 准备环境变量

复制环境变量模板：

```bash
cp .env.prod.example .env.prod
```

编辑 `.env.prod` 文件，设置以下关键参数：

```env
POSTGRES_USER=your_production_db_user
POSTGRES_PASSWORD=your_strong_password_here
POSTGRES_DB=digital_home
SECRET_KEY=your_very_long_random_secret_key_for_production
IMAGE_NAME=digital-home-backend
IMAGE_TAG=v1.0.0
```

### 2. 构建 Docker 镜像

#### 方式一：使用 release.sh 脚本（推荐）

```bash
./release.sh build v1.0.0
```

#### 方式二：直接使用 docker build

```bash
docker build -t digital-home-backend:v1.0.0 .
docker tag digital-home-backend:v1.0.0 digital-home-backend:latest
```

### 3. 配置 Nginx（可选）

如果需要使用 Nginx 作为反向代理：

```bash
mkdir -p nginx/ssl
```

将 SSL 证书放入 `nginx/ssl/` 目录：
- `cert.pem` - 证书文件
- `key.pem` - 私钥文件

编辑 `nginx/nginx.conf`，取消 HTTPS 配置的注释。

### 4. 启动生产环境

```bash
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

### 5. 查看服务状态

```bash
docker-compose -f docker-compose.prod.yml ps
```

### 6. 查看日志

```bash
docker-compose -f docker-compose.prod.yml logs -f
```

### 7. 停止服务

```bash
docker-compose -f docker-compose.prod.yml down
```

## 版本管理

### 查看当前版本

```bash
./release.sh get-version
```

### 增加版本号

```bash
./release.sh bump patch    # 1.0.0 -> 1.0.1
./release.sh bump minor    # 1.0.0 -> 1.1.0
./release.sh bump major    # 1.0.0 -> 2.0.0
```

### 设置特定版本

```bash
./release.sh set v1.2.3
```

## 发布流程

### 完整发布流程（构建 + 推送到镜像仓库）

```bash
./release.sh release minor docker.io/your-username
```

这将：
1. 更新 pyproject.toml
2. 构建 Docker 镜像
3. 推送到指定的镜像仓库

### 分步发布

```bash
# 1. 构建镜像
./release.sh build

# 2. 推送到镜像仓库
./release.sh push docker.io/your-username
```

## 数据库迁移

### 运行数据库迁移

```bash
docker-compose exec app alembic upgrade head
```

### 生产环境迁移

```bash
docker-compose -f docker-compose.prod.yml exec app alembic upgrade head
```

### 回滚迁移

```bash
docker-compose exec app alembic downgrade -1
```

## 健康检查

### 检查应用健康状态

```bash
curl http://localhost:8000/
```

### 检查容器健康状态

```bash
docker-compose ps
```

## 备份和恢复

### 备份数据库

```bash
docker-compose exec db pg_dump -U postgres digital_home > backup.sql
```

### 恢复数据库

```bash
docker-compose exec -T db psql -U postgres digital_home < backup.sql
```

## 性能优化建议

1. **使用多阶段构建**：已实现，减小镜像体积
2. **启用缓存**：Docker 会自动缓存层，充分利用
3. **资源限制**：在 docker-compose.yml 中添加资源限制

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

4. **使用 CDN**：静态资源可以通过 CDN 加速

## 安全建议

1. **使用强密码**：生产环境必须使用强密码
2. **启用 HTTPS**：配置 SSL 证书
3. **限制访问**：配置防火墙规则
4. **定期更新**：及时更新依赖和镜像
5. **日志监控**：配置日志收集和监控

## 故障排查

### 查看容器日志

```bash
docker-compose logs app
docker-compose logs db
```

### 进入容器调试

```bash
docker-compose exec app bash
docker-compose exec db psql -U postgres -d digital_home
```

### 重启服务

```bash
docker-compose restart app
```

## 监控和日志

### 使用 Docker 自带监控

```bash
docker stats
```

### 集成 Prometheus + Grafana

可以添加以下服务到 docker-compose.prod.yml：

```yaml
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
```

## 常见问题

### Q: 如何查看数据库连接？

A: 
```bash
docker-compose exec db psql -U postgres -d digital_home
```
