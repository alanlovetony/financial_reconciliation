# 财务对账工具 💰

一个基于 Streamlit 和 Pandas 开发的财务对账系统，用于逐笔核对银行流水与有益云系统数据。

## 📖 目录

- [功能特点](#功能特点)
- [技术架构](#技术架构)
- [核心功能实现](#核心功能实现)
- [安装与使用](#安装与使用)
- [数据格式](#数据格式)
- [开发笔记](#开发笔记)
- [常见问题](#常见问题)

## ✨ 功能特点

- 📋 **逐笔核对**: 每笔银行流水单独一行，清晰对比匹配结果
- 🔄 **智能识别**: 自动根据捐赠说明区分 T+1 和 T+N 数据
- 🎯 **精确匹配**: 金额必须完全相等才算匹配成功
- 📊 **现代化UI**: 渐变色卡片、悬浮动画、响应式设计、自定义标签页
- 💾 **导出功能**: 表格右上角一键导出 CSV/Excel 格式
- 📈 **交易统计**: 显示每笔匹配的交易笔数
- 📅 **每日汇总**: 按日期范围查看各项目捐赠统计

## 🏗 技术架构

### 技术栈

```
Frontend: Streamlit (Python Web Framework)
Data Processing: Pandas + NumPy
File I/O: OpenPyXL (Excel), CSV
State Management: st.session_state
UI Routing: st.query_params (URL参数)
```

### 项目结构

```
data_analyze/
├── financial_reconciliation_simple.py  # 主程序
├── financial_reconciliation.py         # 旧版程序（保留作参考）
├── requirements.txt                     # Python依赖
├── README.md                           # 技术文档（本文件）
├── QUICKSTART.md                       # 用户快速开始指南
├── sample_data_format.md               # 数据格式示例
├── 月捐处理说明.md                      # 月捐业务逻辑说明
├── input/                              # 输入文件目录
└── output/                             # 输出文件目录
```

## 🔧 核心功能实现

### 1. 对账核心算法 (`reconcile_each_bank_row`)

**设计思路：**
- 以银行流水为主线，逐笔查找匹配的业务记录
- 使用字典存储业务数据，提高查找效率（O(1)时间复杂度）
- 采用"已匹配"标记避免重复匹配

**实现步骤：**

```python
# 1. 数据预处理
- 将有益云数据按业务日期分组汇总
- 区分 T+1（不含GFYH）和 T+N（含GFYH）
- 特殊处理：识别月捐（含"月捐"且附言含"968"）

# 2. 构建查找字典
t1_dict = {业务日期: {金额, 笔数, 已匹配标记}}
tn_dict = {业务日期: {金额, 笔数, 已匹配标记}}
t1_monthly_dict = {业务日期: {金额, 笔数, 已匹配标记}}  # 月捐专用

# 3. 逐笔匹配银行流水
for 每笔银行流水:
    # 3.1 尝试 T+1 匹配
    业务日期 = 到账日期 - 1天
    if 附言包含"968":
        匹配月捐字典
    else:
        匹配常规T+1字典
    
    # 3.2 如果未匹配，尝试 T+N
    if not matched:
        # 从附言提取日期（如"1201_xxx" -> 12/01）
        # 或倒查过去30天
        匹配T+N字典
    
    # 3.3 金额必须完全相等
    if 银行金额 == 系统金额:
        标记为已匹配
```

**踩过的坑：**

1. **浮点数精度问题**
   - 问题：直接比较浮点数可能因精度导致匹配失败
   - 解决：使用 `round(amount, 2)` 统一保留两位小数
   
2. **日期跨年问题**
   - 问题：12月的流水可能匹配1月的业务（跨年）
   - 解决：检测月份差异，自动调整年份
   ```python
   if month == 12 and bank_dt.month == 1:
       year -= 1
   elif month == 1 and bank_dt.month == 12:
       year += 1
   ```

3. **重复匹配问题**
   - 问题：同一业务日期可能被多笔银行流水匹配
   - 解决：使用"已匹配"标记，匹配后立即标记

4. **月捐特殊处理**
   - 问题：月捐和常规捐赠在同一天，金额可能相同导致误匹配
   - 解决：分别维护月捐和常规字典，根据附言"968"区分

### 2. 页签状态保持 (Tab State Management)

**问题背景：**
Streamlit 的 `st.tabs()` 组件不支持记住选中状态，每次页面刷新都会回到第一个 tab。

**解决方案：**
使用 URL 参数 (`st.query_params`) + 自定义按钮实现

```python
# 1. 从 URL 获取当前 tab
query_params = st.query_params
current_tab = int(query_params.get("tab", 0))

# 2. 创建自定义 tab 按钮
for idx, name in enumerate(tab_names):
    if st.button(name, type="primary" if idx == current_tab else "secondary"):
        st.query_params["tab"] = str(idx)
        st.rerun()

# 3. 根据 current_tab 显示对应内容
if current_tab == 0:
    # 显示第一个 tab 内容
elif current_tab == 1:
    # 显示第二个 tab 内容
```

**优点：**
- URL 参数在页面刷新后保持
- 用户可以通过 URL 直接访问特定 tab
- 支持浏览器前进/后退

**踩过的坑：**
1. 最初尝试用 `st.session_state` 保存 tab 状态，但 Streamlit 的 tabs 组件不支持程序化切换
2. 尝试用 JavaScript 注入，但 Streamlit 的安全策略限制了 DOM 操作
3. 最终采用完全自定义的按钮方案，放弃原生 tabs 组件

### 3. 数据状态管理 (Session State)

**设计思路：**
对账是耗时操作，需要保存结果避免重复计算

```python
# 对账完成后保存到 session_state
st.session_state.reconcile_done = True
st.session_state.df_result = df_result
st.session_state.df_unmatched = df_unmatched
# ... 其他数据

# 后续页面刷新时直接读取
if st.session_state.get('reconcile_done', False):
    df_result = st.session_state.df_result
    # 使用缓存的数据
```

**关键点：**
- 对账结果、原始数据都存入 session_state
- 日期选择器的值也存入 session_state，避免重置
- 使用 `get()` 方法提供默认值，避免 KeyError

**踩过的坑：**
1. **大数据量内存问题**
   - 问题：DataFrame 存入 session_state 占用大量内存
   - 解决：目前数据量不大，暂未优化。如需优化可考虑：
     - 只存储必要字段
     - 使用 pickle 序列化压缩
     - 考虑使用数据库或文件缓存

2. **session_state 生命周期**
   - 问题：用户关闭浏览器后 session_state 丢失
   - 解决：这是预期行为，每次使用需重新上传文件

### 4. 每日汇总功能 (Daily Summary)

**设计思路：**
提供灵活的日期范围筛选，支持项目统计和明细查看

**实现要点：**

```python
# 1. 使用 st.form 避免日期选择器频繁触发刷新
with st.form(key='date_filter_form'):
    start_date = st.date_input("开始日期", ...)
    end_date = st.date_input("结束日期", ...)
    submit = st.form_submit_button("查询统计")
    
    if submit:
        # 保存到 session_state
        st.session_state.daily_start_date = start_date
        st.session_state.daily_end_date = end_date
        # 保持在当前 tab
        st.query_params["tab"] = "4"
        st.rerun()

# 2. 数据筛选和汇总
df_filtered = df[(df['日期'] >= start_date) & (df['日期'] <= end_date)]
project_summary = df_filtered.groupby('捐赠项目').agg({
    '捐赠金额': 'sum',
    '捐赠时间': 'count'
})

# 3. 显示两个表格
# 3.1 项目汇总表（按项目分组）
# 3.2 捐赠明细表（所有原始记录）
```

**踩过的坑：**

1. **日期选择器触发刷新问题**
   - 问题：每次改变日期都会触发页面刷新，跳回第一个 tab
   - 解决：使用 `st.form` 包裹，只有点击"查询"按钮才刷新
   - 配合 `st.query_params["tab"] = "4"` 保持在当前 tab

2. **表格对齐问题**
   - 问题：Streamlit 默认数字列右对齐，文本列左对齐
   - 解决：使用 `set_properties` 和 `set_table_styles` 统一左对齐
   ```python
   styled_table = df.style.set_properties(**{
       'text-align': 'left'
   }).set_table_styles([
       {'selector': 'th', 'props': [('text-align', 'left')]},
       {'selector': 'td', 'props': [('text-align', 'left')]}
   ])
   ```

3. **明细表字段保持一致**
   - 问题：需要显示与有益云原始数据完全一致的字段
   - 解决：直接使用筛选后的 DataFrame，不做字段转换
   - 只格式化显示（时间、金额），不改变列名

### 5. UI 样式优化

**自定义 CSS 注入：**

```python
st.markdown("""
<style>
    /* 自定义样式 */
</style>
""", unsafe_allow_html=True)
```

**关键样式：**

1. **表格工具栏始终显示**
   ```css
   div[data-testid="stDataFrameResizable"] div[data-testid="stElementToolbar"] {
       opacity: 1 !important;
       visibility: visible !important;
       display: flex !important;
   }
   ```
   - 问题：默认只在鼠标悬停时显示
   - 解决：强制设置 opacity 和 visibility

2. **自定义 Tab 按钮样式**
   ```css
   div[data-testid="column"] button[kind="primary"] {
       background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
       box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
   }
   ```

**踩过的坑：**

1. **CSS 选择器失效**
   - 问题：Streamlit 的 DOM 结构经常变化，选择器可能失效
   - 解决：使用 `data-testid` 属性选择器，相对稳定
   - 使用 `!important` 提高优先级

2. **样式缓存问题**
   - 问题：修改 CSS 后浏览器可能使用缓存
   - 解决：强制刷新（Ctrl+Shift+R）或清除缓存

### 6. 文件导出功能

**实现方式：**

```python
# CSV 导出
csv_data = df.to_csv(index=False, encoding='utf-8-sig')
st.download_button(
    label="导出 CSV",
    data=csv_data,
    file_name="data.csv",
    mime="text/csv"
)

# Excel 导出
output = BytesIO()
with pd.ExcelWriter(output, engine='openpyxl') as writer:
    df.to_excel(writer, index=False, sheet_name='Sheet1')
st.download_button(
    label="导出 Excel",
    data=output.getvalue(),
    file_name="data.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
```

**注意事项：**
- CSV 使用 `utf-8-sig` 编码，确保 Excel 正确显示中文
- Excel 使用 `BytesIO` 内存缓冲，避免创建临时文件
- 文件名包含日期范围，方便用户识别

## 🚀 安装与使用

### 环境要求

- Python 3.8+
- pip 或 conda

### 安装步骤

1. 克隆或下载项目
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 启动应用：
   ```bash
   streamlit run financial_reconciliation_simple.py
   ```

4. 浏览器访问：http://localhost:8501

### 使用流程

详见 [QUICKSTART.md](QUICKSTART.md)

## 📋 数据格式

### 有益云数据

必须包含以下列：

| 列名 | 类型 | 说明 | 示例 |
|-----|------|------|------|
| 捐赠项目 | 文本 | 项目名称 | "项目A" |
| 捐赠时间 | 日期时间 | 捐赠发生时间 | "2024-01-01 10:30:00" |
| 捐赠金额 | 数字 | 捐赠金额（元） | 1000.00 |
| 捐赠说明 | 文本 | 捐赠渠道说明 | "【GFYH】微信捐款" |

**注意：**
- 第一行是汇总行，会被自动跳过
- `捐赠说明` 字段用于识别 T+1/T+N/月捐

### 银行流水数据

必须包含以下列：

| 列名 | 类型 | 说明 | 示例 |
|-----|------|------|------|
| 发生时间 | 日期时间 | 银行入账时间 | "2024-01-03 14:20:00" |
| 收入 | 数字 | 入账金额（元） | 3000.00 |
| 用途 | 文本 | 交易用途 | "银联入账" |
| 附言 | 文本 | 附言信息 | "0101_1573..." |

**注意：**
- 只处理 `收入 > 0` 的记录
- `附言` 字段用于提取 T+N 的业务日期

## 📝 开发笔记

### 版本演进

- **v1.0**: 初始版本，基础对账功能
- **v2.0**: 需要分别上传 T+1、T+N、银行流水 3 个文件
- **v3.0**: 简化为只需上传 2 个文件，自动识别 T+1/T+N
- **v4.0**: 银行流水逐笔核对版，现代化 UI，增加交易笔数
- **v5.0**: 新增每日汇总功能，优化 UI，使用自定义标签页

### 技术选型考虑

**为什么选择 Streamlit？**
- ✅ 纯 Python 开发，无需前端知识
- ✅ 快速原型开发，适合内部工具
- ✅ 内置组件丰富（表格、图表、文件上传等）
- ❌ 性能有限，不适合大规模用户
- ❌ UI 定制能力有限

**为什么使用 Pandas？**
- ✅ 强大的数据处理能力
- ✅ 支持多种文件格式（CSV、Excel）
- ✅ 丰富的聚合和分组功能
- ❌ 内存占用较大

### 性能优化建议

当前实现适用于中小规模数据（< 10万条记录）。如需处理更大数据量：

1. **使用数据库**
   - 将数据导入 SQLite/PostgreSQL
   - 使用 SQL 进行聚合和查询
   - 减少内存占用

2. **分批处理**
   - 使用 `pd.read_csv(chunksize=1000)` 分批读取
   - 逐批处理和匹配
   - 避免一次性加载全部数据

3. **缓存优化**
   - 使用 `@st.cache_data` 缓存数据处理结果
   - 避免重复计算

4. **并行处理**
   - 使用 `multiprocessing` 并行处理多个日期范围
   - 注意 Streamlit 的线程安全问题

### 已知限制

1. **Streamlit 限制**
   - 每次交互都会重新运行整个脚本
   - 无法实现真正的单页应用（SPA）
   - 大文件上传可能超时

2. **对账逻辑限制**
   - 只支持金额完全相等的匹配
   - 不支持部分匹配或模糊匹配
   - 同一业务日期只能匹配一次

3. **UI 限制**
   - 表格工具栏按钮可能因 Streamlit 版本更新而失效
   - 自定义 tab 按钮无法完全模拟原生 tabs 的交互

### 未来改进方向

1. **功能增强**
   - [ ] 支持模糊匹配（金额差异在一定范围内）
   - [ ] 支持手动调整匹配结果
   - [ ] 增加对账历史记录
   - [ ] 支持多银行账户

2. **性能优化**
   - [ ] 使用数据库存储
   - [ ] 实现增量对账
   - [ ] 添加进度条显示

3. **用户体验**
   - [ ] 添加数据验证和错误提示
   - [ ] 支持拖拽上传文件
   - [ ] 增加数据可视化图表
   - [ ] 支持深色模式

## ❓ 常见问题

### 开发相关

**Q: 如何调试 Streamlit 应用？**
A: 
```python
# 方法1: 使用 st.write() 打印调试信息
st.write("Debug:", variable)

# 方法2: 使用 Python 调试器
import pdb; pdb.set_trace()

# 方法3: 查看 Streamlit 日志
streamlit run app.py --logger.level=debug
```

**Q: 如何处理 Streamlit 的重新运行问题？**
A: 使用 `st.session_state` 保存状态，避免重复计算

**Q: 如何测试对账逻辑？**
A: 
1. 准备小规模测试数据
2. 使用 pytest 编写单元测试
3. 将核心逻辑提取为独立函数，便于测试

### 使用相关

**Q: 为什么有些银行流水没有匹配上？**
A: 可能原因：
- 有益云系统中没有对应的业务记录
- 金额不完全一致（必须完全相等）
- 这笔款项来自其他渠道

**Q: 如何处理跨年数据？**
A: 系统会自动处理跨年情况，无需特殊操作

**Q: 支持哪些文件格式？**
A: CSV、XLS、XLSX

## 📄 许可证

MIT License

## 📧 联系方式

如有问题或建议，请提交 Issue。

---

**维护者注意事项：**
1. 修改对账逻辑前，务必备份测试数据
2. 修改 UI 样式时，注意 Streamlit 版本兼容性
3. 添加新功能时，更新本文档的"核心功能实现"部分
4. 遇到新的坑，记录在对应功能的"踩过的坑"部分
