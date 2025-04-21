# 安装指南

## 环境要求

- Python 3.6+
- HTTrack（网站下载工具，仅当需要下载网站时必须）
- pip（Python包管理器）

## 安装步骤

### 1. 克隆或下载项目

```bash
git clone https://github.com/your-username/website-mirror-toolkit.git
cd website-mirror-toolkit
```

### 2. 安装Python依赖

```bash
# 使用pip安装依赖
pip install -r requirements.txt

# 或者开发模式安装
pip install -e .
```

### 3. 安装HTTrack (可选，但用于下载网站时必须)

#### Linux (Debian/Ubuntu)

```bash
sudo apt-get update
sudo apt-get install httrack
```

#### Linux (CentOS/Fedora)

```bash
sudo yum install httrack
```

#### macOS

```bash
brew install httrack
```

#### Windows

从官方网站下载安装包：<http://www.httrack.com/page/2/>

### 4. 验证安装

```bash
# 验证Python部分
python -c "import website_converter; print(website_converter.__version__)"

# 验证HTTrack
httrack --version
```

## 开发环境配置

如果您想为项目做贡献或自定义功能，建议设置虚拟环境：

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# 安装开发依赖
pip install -e .
```

## 可能的问题及解决方案

### 依赖安装问题

如果安装依赖时遇到权限问题，可以尝试：

```bash
pip install --user -r requirements.txt
```

### HTTrack安装问题

如果HTTrack安装失败，可以：

1. 检查您的系统是否支持包管理器安装
2. 尝试从源代码编译安装
3. 仅使用工具的转换功能，跳过下载步骤
