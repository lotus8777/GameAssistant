# 游戏按键辅助

可自定义按键与触发间隔的 Windows 游戏辅助工具。支持多按键并行、按各自间隔自动触发，并通过全局热键一键启停。

## 功能

- 自定义多个按键及各自触发间隔（毫秒）
- 支持技能施法时间（按键按住时长，默认 100ms）
- 每个按键可单独启用/禁用
- 支持设置重复次数（0 为无限循环）
- 全局热键（默认 F6）随时启停
- 配置自动保存到 `config.json`

## 安装

```bash
pip install -r requirements.txt
```

## 运行

```bash
python main.py
```

**建议以管理员身份运行**，部分游戏对普通权限下的模拟按键有限制。

## 打包为 exe

### 一键打包（推荐）

双击运行 `build.bat`，完成后在 `dist\游戏按键辅助.exe` 获取可执行文件。

### 手动打包

```bash
pip install -r requirements.txt
pip install -r requirements-build.txt

pyinstaller --onefile --windowed --name "游戏按键辅助" ^
    --hidden-import=keyboard ^
    --collect-all keyboard ^
    main.py
```

打包参数说明：

| 参数 | 作用 |
|------|------|
| `--onefile` | 打成单个 exe 文件 |
| `--windowed` | 不显示黑色命令行窗口 |
| `--name` | 指定输出文件名 |

### 使用打包后的 exe

1. 将 `dist\游戏按键辅助.exe` 复制到任意目录即可运行
2. 首次运行会在 **exe 同目录** 自动生成 `config.json`
3. 建议右键 exe → **以管理员身份运行**（全局热键与游戏内按键更稳定）
4. 若杀毒软件误报，可添加信任（PyInstaller 打包的程序偶发误报）

## 使用说明

1. 在列表中添加/选择按键
2. 在下方编辑区设置：按键名、触发间隔（ms）、重复次数
3. 点击「保存修改」或「保存全部配置」
4. 切换到游戏窗口，按 F6（或你设置的热键）开始/停止

## 常用按键名

数字 `1`-`0`，字母 `a`-`z`，功能键 `f1`-`f12`，`space`、`tab`、`enter`，鼠标 `mouse left` / `mouse right` / `mouse middle`。

## 注意事项

- 请遵守游戏服务条款，勿用于违规场景
- 间隔最小为 10ms，避免过高频率影响系统稳定性
- 关闭程序时会自动保存当前配置
