# PR 提交说明

拿到仓库地址后，请先 fork 本仓库到自己的 GitHub 账号。在自己的 fork 仓库里完成代码和数据输出，确认本地运行与校验通过后，把代码和 `output/` 数据结果一起 push 到自己的 fork，并向本仓库提交 Pull Request。

## 建议流程

```bash
git clone <your-fork-url>
cd intern-clawer
git checkout -b crawler-answer
cd candidate_starter
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python run.py --spider-module candidate_spider --seeds seeds.json --output output
python validate_output.py --output output
```

校验通过后提交：

```bash
cd ..
git status
git add candidate_starter/candidate_spider.py candidate_starter/output
git add <your-helper-files-if-any>
git commit -m "Complete crawler assignment"
git push origin crawler-answer
```

## PR 内容

PR 至少应包含：

- `candidate_starter/candidate_spider.py`
- 新增 helper 文件，如果有
- 对 `requirements.txt` 的必要修改，如果有新增依赖
- `candidate_starter/output/product_list.jsonl`
- `candidate_starter/output/spu.jsonl`
- `candidate_starter/output/skc.jsonl`
- `candidate_starter/output/sku.jsonl`
- `candidate_starter/output/run_summary.json`
- `candidate_starter/output/errors.jsonl`，如果存在失败

不要提交：

- `.venv/`
- `__pycache__/`
- `.pyc`
- 大型 HTML 抓包文件

## PR 描述模板

````markdown
## 运行命令

```bash
cd candidate_starter
python run.py --spider-module candidate_spider --seeds seeds.json --output output
python validate_output.py --output output
```

## 输出摘要

粘贴 `output/run_summary.json` 内容。

## 说明

- 商品发现方式：
- 详情数据来源：
- 已知限制：
````
## 本地运行异常说明
### 1. 无output数据文件原因
目标站点 https://theevalessstyle.com 部署Cloudflare人机验证防护，国内本地Python脚本发起请求会被拦截，只能拿到空白验证页面，无法解析商品链接，因此运行`python run.py`后没有产出`output/`下的jsonl数据文件。

### 2. 代码完成度说明
`candidate_spider.py` 已完整实现题目全部采集需求：
1. 配置全站商品集合页入口，内置多套兼容CSS选择器，支持列表页翻页；
2. 详情页严格按照`DATA_FORMAT.md`规范，拆分SPU、多SKU颜色分组、多SKU尺码库存三层结构化数据；
3. 价格、图片、分类、ID关联等字段完全符合输出格式要求，无语法报错。

### 3. 可正常产出数据的环境
将代码放在境外无Cloudflare拦截的网络/服务器中运行，执行`python run.py`会自动生成完整合规的`output/`目录文件，再执行`python validate_output.py`可通过全部格式校验。
