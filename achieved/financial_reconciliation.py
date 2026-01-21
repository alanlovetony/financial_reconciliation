"""
财务对账工具 - Financial Reconciliation Tool
用于对比业务系统数据与银行实际到账流水

更新说明：
- 只需上传两个文件：有益云数据 和 银行流水
- 自动根据捐赠说明中是否包含【GFYH】来区分T+1和T+N数据
  - 带【GFYH】的为 T+N
  - 不带【GFYH】的为 T+1
"""

import streamlit as st
import pandas as pd
import numpy as np
import re
from datetime import datetime, timedelta
from io import BytesIO

# 页面配置
st.set_page_config(
    page_title="财务对账工具",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 自定义CSS样式
st.markdown("""
<style>
    /* 主容器样式 */
    .main > div {
        padding-top: 1rem;
    }
    
    /* 标题样式 */
    .main-title {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.3rem;
    }
    
    .sub-title {
        text-align: center;
        color: #6c757d;
        font-size: 0.95rem;
        margin-bottom: 1rem;
    }
    
    /* 卡片样式 */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 1.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    
    .metric-card-success {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        box-shadow: 0 10px 40px rgba(17, 153, 142, 0.3);
    }
    
    .metric-card-danger {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        box-shadow: 0 10px 40px rgba(235, 51, 73, 0.3);
    }
    
    .metric-card-info {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        box-shadow: 0 10px 40px rgba(79, 172, 254, 0.3);
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 1rem;
        font-weight: 600;
        opacity: 1;
    }
    
    /* 上传区域样式 */
    .upload-section {
        background: #f8f9fa;
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        border: 2px dashed #dee2e6;
        transition: all 0.3s ease;
    }
    
    .upload-section:hover {
        border-color: #667eea;
        background: #f0f4ff;
    }
    
    /* 步骤标题 */
    .step-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin: 2rem 0 1rem 0;
    }
    
    .step-number {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1.1rem;
    }
    
    .step-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2d3748;
    }
    
    /* 表格样式 */
    .dataframe {
        border-radius: 12px !important;
        overflow: hidden;
    }
    
    /* 成功/失败标签 */
    .status-matched {
        background: #d4edda;
        color: #155724;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
    }
    
    .status-unmatched {
        background: #f8d7da;
        color: #721c24;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
    }
    
    /* 按钮样式 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
    }
    
    /* 下载按钮 */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(17, 153, 142, 0.4);
    }
    
    /* 信息框 */
    .info-box {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
        border-left: 4px solid #667eea;
        border-radius: 8px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
    }
    
    /* 隐藏Streamlit默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 透视表样式 */
    .pivot-table {
        font-size: 0.85rem;
    }
    
    .pivot-table th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 10px;
        text-align: center;
    }
    
    .pivot-table td {
        padding: 8px;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# 标题
st.markdown('<h1 class="main-title">💰 财务对账工具</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">业务系统数据 vs 银行实际到账流水 · 智能对比分析</p>', unsafe_allow_html=True)

# 侧边栏
with st.sidebar:
    st.markdown("### 📋 使用说明")
    st.markdown("""
    **文件要求：**
    - 有益云数据: 直接从有益云导出的xls文件
    - 银行流水: 包含发生时间、收入、用途、附言
    
    **自动识别规则：**
    - 捐赠说明带【GFYH】→ T+N
    - 捐赠说明不带【GFYH】→ T+1
    
    **对账逻辑：**
    - T+1: 到账日期 - 1天 = 业务日期
    - T+N: 从银行备注提取业务日期
    - 差异<1元视为匹配
    """)
    
    st.markdown("---")
    st.markdown("### 🎨 主题")
    theme = st.selectbox("选择配色", ["默认紫色", "商务蓝", "清新绿"])


def load_yiyun_file(file):
    """加载有益云文件，自动跳过第一行"""
    if file is None:
        return None
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file, skiprows=1)
        else:
            df = pd.read_excel(file, skiprows=1)
        return df
    except Exception as e:
        st.error(f"有益云文件读取失败: {str(e)}")
        return None


def load_bank_file(file):
    """加载银行流水文件"""
    if file is None:
        return None
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        return df
    except Exception as e:
        st.error(f"银行流水文件读取失败: {str(e)}")
        return None


def split_yiyun_data(df):
    """
    根据捐赠说明中是否包含【GFYH】来区分T+1和T+N数据
    - 带【GFYH】的是 T+N
    - 不带【GFYH】的是 T+1
    """
    df = df.copy()
    
    # 确保捐赠说明列存在
    if '捐赠说明' not in df.columns:
        st.error("有益云数据中缺少'捐赠说明'列")
        return None, None
    
    # 根据捐赠说明区分
    is_tn = df['捐赠说明'].astype(str).str.contains('GFYH', na=False)
    
    df_t1 = df[~is_tn].copy()
    df_tn = df[is_tn].copy()
    
    return df_t1, df_tn


def process_system_data(df_t1, df_tn):
    """处理业务系统数据 - 分别处理T+1和T+N，并单独统计月捐"""
    # 处理 T+1 数据
    df_t1 = df_t1.copy()
    df_t1['捐赠时间'] = pd.to_datetime(df_t1['捐赠时间'], errors='coerce')
    df_t1['业务日期'] = df_t1['捐赠时间'].dt.date
    
    # 识别月捐数据（捐赠说明中包含"月捐"）
    df_t1['是否月捐'] = df_t1['捐赠说明'].astype(str).str.contains('月捐', na=False)
    
    # 分离月捐和非月捐数据
    df_t1_monthly = df_t1[df_t1['是否月捐']].copy()
    df_t1_regular = df_t1[~df_t1['是否月捐']].copy()
    
    # T+1 月捐按日期汇总
    df_t1_monthly_daily = df_t1_monthly.groupby('业务日期').agg({
        '捐赠金额': 'sum',
        '捐赠项目': 'count'
    }).reset_index()
    df_t1_monthly_daily.columns = ['业务日期', '金额', '笔数']
    df_t1_monthly_daily['来源'] = 'T+1_月捐'
    
    # T+1 常规按日期汇总
    df_t1_regular_daily = df_t1_regular.groupby('业务日期').agg({
        '捐赠金额': 'sum',
        '捐赠项目': 'count'
    }).reset_index()
    df_t1_regular_daily.columns = ['业务日期', '金额', '笔数']
    df_t1_regular_daily['来源'] = 'T+1'
    
    # T+1 总汇总（用于向后兼容）
    df_t1_daily = df_t1.groupby('业务日期').agg({
        '捐赠金额': 'sum',
        '捐赠项目': 'count'
    }).reset_index()
    df_t1_daily.columns = ['业务日期', '金额', '笔数']
    df_t1_daily['来源'] = 'T+1'
    
    # 处理 T+N 数据
    df_tn = df_tn.copy()
    df_tn['捐赠时间'] = pd.to_datetime(df_tn['捐赠时间'], errors='coerce')
    df_tn['业务日期'] = df_tn['捐赠时间'].dt.date
    
    # T+N 按日期汇总
    df_tn_daily = df_tn.groupby('业务日期').agg({
        '捐赠金额': 'sum',
        '捐赠项目': 'count'
    }).reset_index()
    df_tn_daily.columns = ['业务日期', '金额', '笔数']
    df_tn_daily['来源'] = 'T+N'
    
    # 合并用于透视表
    df_combined = pd.concat([df_t1, df_tn], ignore_index=True)
    df_by_project = df_combined.groupby(['捐赠项目', '业务日期']).agg({
        '捐赠金额': 'sum'
    }).reset_index()
    df_by_project.columns = ['项目名称', '业务日期', '金额']
    
    return df_t1_daily, df_tn_daily, df_by_project, df_combined, df_t1_monthly_daily, df_t1_regular_daily


def extract_business_date(row):
    """从银行备注中提取业务日期"""
    remark = str(row.get('附言', '')) + ' ' + str(row.get('用途', ''))
    
    # 格式1: YYYYMMDD至YYYYMMDD (广发银行收单入账)
    pattern1 = r'(\d{4})(\d{2})(\d{2})至'
    match1 = re.search(pattern1, remark)
    if match1:
        try:
            return pd.to_datetime(f"{match1.group(1)}-{match1.group(2)}-{match1.group(3)}").date()
        except:
            pass
    
    # 格式2: MMDD_xxx (财付通入账)
    pattern2 = r'^(\d{2})(\d{2})_'
    match2 = re.search(pattern2, remark.strip())
    if match2:
        month, day = match2.group(1), match2.group(2)
        bank_date = pd.to_datetime(row['发生时间'])
        year = bank_date.year
        if int(month) == 12 and bank_date.month == 1:
            year -= 1
        elif int(month) == 1 and bank_date.month == 12:
            year += 1
        try:
            return pd.to_datetime(f"{year}-{month}-{day}").date()
        except:
            pass
    return None


def process_bank_data(df_bank):
    """处理银行流水数据 - 保留每一笔用于匹配"""
    df_bank = df_bank.copy()
    
    # 处理收入列（可能包含非数字值如 '-'）
    df_bank['收入'] = pd.to_numeric(df_bank['收入'], errors='coerce').fillna(0)
    
    # 只保留有收入的记录
    df_bank = df_bank[df_bank['收入'] > 0].copy()
    
    df_bank['发生时间'] = pd.to_datetime(df_bank['发生时间'], errors='coerce')
    df_bank['到账日期'] = df_bank['发生时间'].dt.date
    df_bank['银行摘要'] = df_bank.apply(
        lambda row: f"{row.get('用途', '')} | {row.get('附言', '')}", axis=1
    )
    
    return df_bank


def reconcile_data(df_t1_daily, df_tn_daily, df_bank, df_t1_monthly_daily, df_t1_regular_daily):
    """
    核心对账逻辑 - 每日一行结果，分别显示T+1和T+N的匹配状态
    
    特殊处理：
    1. 识别968结尾的银行流水（月捐T+1汇总）
    2. 单独匹配前一天的月捐数据
    3. 从T+1汇总中扣除月捐后，再匹配剩余流水
    """
    
    # 创建月捐和常规T+1的字典
    t1_monthly_dict = {row['业务日期']: {'金额': row['金额'], '笔数': row['笔数']} 
                       for _, row in df_t1_monthly_daily.iterrows()}
    t1_regular_dict = {row['业务日期']: {'金额': row['金额'], '笔数': row['笔数']} 
                       for _, row in df_t1_regular_daily.iterrows()}
    t1_dict = {row['业务日期']: {'金额': row['金额'], '笔数': row['笔数']} 
               for _, row in df_t1_daily.iterrows()}
    tn_dict = {row['业务日期']: {'金额': row['金额'], '笔数': row['笔数']} 
               for _, row in df_tn_daily.iterrows()}
    
    # 将银行流水按到账日期分组，同时保留附言信息用于识别968
    bank_detail_by_date = {}
    for _, row in df_bank.iterrows():
        bank_date = row['到账日期']
        if bank_date not in bank_detail_by_date:
            bank_detail_by_date[bank_date] = []
        bank_detail_by_date[bank_date].append({
            '金额': row['收入'],
            '附言': str(row.get('附言', '')),
            '用途': str(row.get('用途', ''))
        })
    
    # 收集所有业务日期
    all_biz_dates = set(t1_dict.keys()) | set(tn_dict.keys())
    
    # 记录匹配结果
    results = []
    matched_bank_records = {}  # 记录已匹配的银行流水 {到账日期: [已匹配的记录索引]}
    
    for biz_date in sorted(all_biz_dates):
        row_data = {
            '业务日期': biz_date,
            'T+1_系统应收': 0,
            'T+1_笔数': 0,
            'T+1_银行实收': 0,
            'T+1_到账日期': None,
            'T+1_状态': '-',
            'T+N_系统应收': 0,
            'T+N_笔数': 0,
            'T+N_银行实收': 0,
            'T+N_到账日期': None,
            'T+N_到账天数': None,
            'T+N_状态': '-',
        }
        
        # 检查 T+1 匹配
        if biz_date in t1_dict:
            t1_info = t1_dict[biz_date]
            row_data['T+1_系统应收'] = t1_info['金额']
            row_data['T+1_笔数'] = int(t1_info['笔数'])
            
            # T+1: 到账日期 = 业务日期 + 1天
            expected_bank_date = (pd.to_datetime(biz_date) + timedelta(days=1)).date()
            
            if expected_bank_date in bank_detail_by_date:
                bank_records = bank_detail_by_date[expected_bank_date]
                matched_indices = matched_bank_records.get(expected_bank_date, [])
                
                # 第一步：检查968结尾的月捐汇总
                monthly_amount = t1_monthly_dict.get(biz_date, {}).get('金额', 0)
                monthly_matched_idx = None
                
                if monthly_amount &gt; 0:
                    monthly_amount_rounded = round(monthly_amount, 2)
                    for idx, record in enumerate(bank_records):
                        if idx in matched_indices:
                            continue
                        # 检查是否968结尾
                        remark = record['附言']
                        if re.search(r'968\s*$', remark.strip()):
                            amt_rounded = round(record['金额'], 2)
                            if amt_rounded == monthly_amount_rounded:
                                # 匹配到月捐汇总
                                monthly_matched_idx = idx
                                if expected_bank_date not in matched_bank_records:
                                    matched_bank_records[expected_bank_date] = []
                                matched_bank_records[expected_bank_date].append(idx)
                                break
                
                # 第二步：匹配常规T+1（扣除月捐后的金额）
                regular_amount = t1_regular_dict.get(biz_date, {}).get('金额', 0)
                regular_matched = False
                
                if regular_amount &gt; 0:
                    regular_amount_rounded = round(regular_amount, 2)
                    for idx, record in enumerate(bank_records):
                        if idx in matched_indices:
                            continue
                        # 非968结尾
                        remark = record['附言']
                        if not re.search(r'968\s*$', remark.strip()):
                            amt_rounded = round(record['金额'], 2)
                            if amt_rounded == regular_amount_rounded:
                                # 匹配到常规T+1
                                row_data['T+1_银行实收'] = record['金额']
                                row_data['T+1_到账日期'] = expected_bank_date
                                row_data['T+1_状态'] = '✅ 匹配'
                                regular_matched = True
                                if expected_bank_date not in matched_bank_records:
                                    matched_bank_records[expected_bank_date] = []
                                matched_bank_records[expected_bank_date].append(idx)
                                break
                
                # 如果只有月捐，没有常规T+1
                if monthly_amount &gt; 0 and regular_amount == 0 and monthly_matched_idx is not None:
                    row_data['T+1_银行实收'] = bank_records[monthly_matched_idx]['金额']
                    row_data['T+1_到账日期'] = expected_bank_date
                    row_data['T+1_状态'] = '✅ 匹配(月捐)'
                    regular_matched = True
                
                # 如果都没匹配上，尝试用总金额匹配（向后兼容）
                if not regular_matched:
                    t1_amount = round(t1_info['金额'], 2)
                    for idx, record in enumerate(bank_records):
                        if idx in matched_indices:
                            continue
                        amt_rounded = round(record['金额'], 2)
                        if amt_rounded == t1_amount:
                            row_data['T+1_银行实收'] = record['金额']
                            row_data['T+1_到账日期'] = expected_bank_date
                            row_data['T+1_状态'] = '✅ 匹配'
                            if expected_bank_date not in matched_bank_records:
                                matched_bank_records[expected_bank_date] = []
                            matched_bank_records[expected_bank_date].append(idx)
                            break
                    else:
                        row_data['T+1_状态'] = '❌ 未匹配'
            else:
                row_data['T+1_状态'] = '❌ 未到账'
        
        # 检查 T+N 匹配
        if biz_date in tn_dict:
            tn_info = tn_dict[biz_date]
            row_data['T+N_系统应收'] = tn_info['金额']
            row_data['T+N_笔数'] = int(tn_info['笔数'])
            
            tn_amount = round(tn_info['金额'], 2)
            matched = False
            
            # T+N: 在后续N天内查找匹配（最多查30天）
            for days_after in range(1, 31):
                expected_bank_date = (pd.to_datetime(biz_date) + timedelta(days=days_after)).date()
                
                if expected_bank_date in bank_detail_by_date:
                    bank_records = bank_detail_by_date[expected_bank_date]
                    matched_indices = matched_bank_records.get(expected_bank_date, [])
                    
                    for idx, record in enumerate(bank_records):
                        if idx in matched_indices:
                            continue
                        amt_rounded = round(record['金额'], 2)
                        if amt_rounded == tn_amount:
                            # 完全匹配
                            row_data['T+N_银行实收'] = record['金额']
                            row_data['T+N_到账日期'] = expected_bank_date
                            row_data['T+N_到账天数'] = days_after
                            row_data['T+N_状态'] = f'✅ T+{days_after}'
                            # 记录已匹配
                            if expected_bank_date not in matched_bank_records:
                                matched_bank_records[expected_bank_date] = []
                            matched_bank_records[expected_bank_date].append(idx)
                            matched = True
                            break
                
                if matched:
                    break
            
            if not matched:
                row_data['T+N_状态'] = '❌ 未到账'
        
        results.append(row_data)
    
    # 查找未匹配的银行流水
    unmatched_bank = []
    for bank_date, records in bank_detail_by_date.items():
        matched_indices = matched_bank_records.get(bank_date, [])
        for idx, record in enumerate(records):
            if idx not in matched_indices:
                unmatched_bank.append({
                    '业务日期': None,
                    'T+1_系统应收': 0,
                    'T+1_笔数': 0,
                    'T+1_银行实收': record['金额'],
                    'T+1_到账日期': bank_date,
                    'T+1_状态': '⚠️ 无业务',
                    'T+N_系统应收': 0,
                    'T+N_笔数': 0,
                    'T+N_银行实收': 0,
                    'T+N_到账日期': None,
                    'T+N_到账天数': None,
                    'T+N_状态': '-',
                })
    
    # 合并结果
    results.extend(unmatched_bank)
    
    df_report = pd.DataFrame(results)
    
    # 格式化日期
    df_report['业务日期'] = pd.to_datetime(df_report['业务日期'])
    df_report = df_report.sort_values('业务日期').reset_index(drop=True)
    df_report['业务日期_显示'] = df_report['业务日期'].dt.strftime('%Y-%m-%d')
    df_report['业务日期_显示'] = df_report['业务日期_显示'].fillna('-')
    df_report['T+1_到账日期_显示'] = pd.to_datetime(df_report['T+1_到账日期']).dt.strftime('%Y-%m-%d')
    df_report['T+1_到账日期_显示'] = df_report['T+1_到账日期_显示'].fillna('-')
    df_report['T+N_到账日期_显示'] = pd.to_datetime(df_report['T+N_到账日期']).dt.strftime('%Y-%m-%d')
    df_report['T+N_到账日期_显示'] = df_report['T+N_到账日期_显示'].fillna('-')
    
    return df_report, df_bank


def create_pivot_table(df_by_project, df_report):
    """创建项目-日期透视表，并关联对账结果"""
    df_by_project = df_by_project.copy()
    df_by_project['业务日期'] = pd.to_datetime(df_by_project['业务日期'])
    df_by_project['日期显示'] = df_by_project['业务日期'].dt.strftime('%m/%d')
    
    pivot = df_by_project.pivot_table(
        index='项目名称',
        columns='日期显示',
        values='金额',
        aggfunc='sum',
        fill_value=0
    )
    
    # 添加合计列
    pivot['合计'] = pivot.sum(axis=1)
    
    # 按合计金额降序排列
    pivot = pivot.sort_values('合计', ascending=False)
    
    # 获取每个日期的对账状态（用于颜色标识）- 适配新格式
    date_status = {}
    for _, row in df_report.iterrows():
        if pd.notna(row['业务日期']):
            date_key = pd.to_datetime(row['业务日期']).strftime('%m/%d')
            t1_status = str(row.get('T+1_状态', '-'))
            tn_status = str(row.get('T+N_状态', '-'))
            
            # 确定综合状态
            if '✅' in t1_status and '✅' in tn_status:
                status = '✅ 全部匹配'
            elif '✅' in t1_status or '✅' in tn_status:
                if '❌' in t1_status or '❌' in tn_status:
                    status = '⚠️ 部分匹配'
                else:
                    status = '✅ 匹配'
            elif '❌' in t1_status or '❌' in tn_status:
                status = '❌ 未匹配'
            else:
                status = '-'
            
            # 计算差异
            t1_diff = row.get('T+1_银行实收', 0) - row.get('T+1_系统应收', 0)
            tn_diff = row.get('T+N_银行实收', 0) - row.get('T+N_系统应收', 0)
            
            date_status[date_key] = {
                'status': status,
                'diff': t1_diff + tn_diff,
                'source': f"T+1:{t1_status} T+N:{tn_status}"
            }
    
    return pivot, date_status


def style_pivot_table(pivot_df, date_status):
    """美化透视表 - 根据对账结果标识颜色"""
    
    def color_cell(val, col_name):
        """根据列（日期）的对账状态返回颜色"""
        if col_name == '合计' or col_name == '项目名称':
            return ''
        
        if val == 0:
            return 'color: #ccc;'
        
        status_info = date_status.get(col_name, {})
        status = status_info.get('status', '')
        
        if '✅' in status:
            # 匹配 - 亮绿色
            return 'color: #28a745; font-weight: bold;'
        elif '⚠️' in status:
            # 银行多收 - 橙色
            return 'color: #e67e00; font-weight: bold;'
        elif '❌' in status:
            # 银行少收 - 红色
            return 'color: #dc3545; font-weight: bold;'
        else:
            return ''
    
    # 应用样式
    styled = pivot_df.style.apply(
        lambda col: [color_cell(v, col.name) for v in col], 
        axis=0
    ).format('{:,.2f}')
    
    return styled


def style_report(df):
    """美化对账报告 - 每日一行，分别显示T+1和T+N状态"""
    display_df = df[['业务日期_显示', 
                     'T+1_系统应收', 'T+1_笔数', 'T+1_银行实收', 'T+1_状态',
                     'T+N_系统应收', 'T+N_笔数', 'T+N_银行实收', 'T+N_状态']].copy()
    display_df.columns = ['业务日期', 
                          'T+1应收', 'T+1笔数', 'T+1实收', 'T+1状态',
                          'T+N应收', 'T+N笔数', 'T+N实收', 'T+N状态']
    
    def highlight_row(row):
        t1_status = str(row['T+1状态'])
        tn_status = str(row['T+N状态'])
        
        # 判断整行状态
        if '⚠️' in t1_status:
            return ['background-color: #fff3cd'] * len(row)  # 黄色 - 银行有流水无业务
        elif '❌' in t1_status or '❌' in tn_status:
            return ['background-color: #f8d7da'] * len(row)  # 红色 - 有未匹配
        elif '✅' in t1_status or '✅' in tn_status:
            return ['background-color: #d4edda'] * len(row)  # 绿色 - 匹配成功
        else:
            return [''] * len(row)
    
    return display_df.style.apply(highlight_row, axis=1).format({
        'T+1应收': '¥{:,.2f}',
        'T+1实收': '¥{:,.2f}',
        'T+N应收': '¥{:,.2f}',
        'T+N实收': '¥{:,.2f}'
    })


def to_excel(df_report, pivot_df, df_bank_detail, df_t1, df_tn):
    """导出Excel - 每日一行，分别显示T+1和T+N状态"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # 对账汇总 - 新格式
        export_df = df_report[['业务日期_显示', 
                               'T+1_系统应收', 'T+1_笔数', 'T+1_银行实收', 'T+1_到账日期_显示', 'T+1_状态',
                               'T+N_系统应收', 'T+N_笔数', 'T+N_银行实收', 'T+N_到账日期_显示', 'T+N_状态']].copy()
        export_df.columns = ['业务日期', 
                             'T+1应收', 'T+1笔数', 'T+1实收', 'T+1到账日期', 'T+1状态',
                             'T+N应收', 'T+N笔数', 'T+N实收', 'T+N到账日期', 'T+N状态']
        export_df.to_excel(writer, index=False, sheet_name='对账汇总')
        
        # 项目明细透视表
        pivot_df.to_excel(writer, sheet_name='项目明细(透视)')
        
        # 银行流水
        bank_cols = ['发生时间', '收入', '到账日期', '银行摘要']
        available_cols = [c for c in bank_cols if c in df_bank_detail.columns]
        df_bank_detail[available_cols].to_excel(writer, index=False, sheet_name='银行流水')
        
        # T+1 明细
        if len(df_t1) > 0:
            df_t1.to_excel(writer, index=False, sheet_name='T+1明细')
        
        # T+N 明细
        if len(df_tn) > 0:
            df_tn.to_excel(writer, index=False, sheet_name='T+N明细')
    
    return output.getvalue()


# ==================== 主界面 ====================

# 步骤1: 上传文件
st.markdown("""
<div class="step-header">
    <div class="step-number">1</div>
    <span class="step-title">上传数据文件</span>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("##### 📄 有益云数据")
    st.markdown("""
    <div style="font-size: 0.85rem; color: #666; margin-bottom: 0.5rem;">
    直接上传有益云导出的文件，系统会自动识别：<br>
    • 带【GFYH】→ T+N &nbsp;&nbsp;• 不带【GFYH】→ T+1
    </div>
    """, unsafe_allow_html=True)
    file_yiyun = st.file_uploader("yiyun", type=['csv', 'xlsx', 'xls'], key='yiyun', label_visibility="collapsed")
    if file_yiyun:
        df_preview = load_yiyun_file(file_yiyun)
        file_yiyun.seek(0)
        if df_preview is not None:
            # 统计T+1和T+N数量
            is_tn = df_preview['捐赠说明'].astype(str).str.contains('GFYH', na=False)
            t1_count = (~is_tn).sum()
            tn_count = is_tn.sum()
            # 统计T+1中的月捐数量
            is_monthly = df_preview[~is_tn]['捐赠说明'].astype(str).str.contains('月捐', na=False)
            monthly_count = is_monthly.sum()
            st.success(f"✓ {file_yiyun.name} ({len(df_preview)}行: T+1 {t1_count}条 (月捐: {monthly_count}条), T+N {tn_count}条)")

with col2:
    st.markdown("##### 🏦 银行流水")
    st.markdown("""
    <div style="font-size: 0.85rem; color: #666; margin-bottom: 0.5rem;">
    上传银行导出的流水文件，需包含：<br>
    发生时间、收入、用途、附言
    </div>
    """, unsafe_allow_html=True)
    file_bank = st.file_uploader("bank", type=['csv', 'xlsx', 'xls'], key='bank', label_visibility="collapsed")
    if file_bank:
        df_preview = load_bank_file(file_bank)
        file_bank.seek(0)
        if df_preview is not None:
            st.success(f"✓ {file_bank.name} ({len(df_preview)}行)")

# 步骤2: 执行对账
if file_yiyun and file_bank:
    st.markdown("""
    <div class="step-header">
        <div class="step-number">2</div>
        <span class="step-title">执行对账</span>
    </div>
    """, unsafe_allow_html=True)
    
    col_btn = st.columns([1, 2, 1])
    with col_btn[1]:
        run_btn = st.button("🚀 开始智能对账", use_container_width=True, type="primary")
    
    if run_btn:
        with st.spinner("⏳ 正在分析数据..."):
            try:
                # 加载有益云数据
                df_yiyun = load_yiyun_file(file_yiyun)
                
                # 自动区分T+1和T+N
                df_t1, df_tn = split_yiyun_data(df_yiyun)
                
                if df_t1 is None or df_tn is None:
                    st.error("数据分类失败，请检查有益云数据格式")
                    st.stop()
                
                st.info(f"📊 数据识别结果: T+1 共 {len(df_t1)} 条, T+N 共 {len(df_tn)} 条")
                
                # 加载银行流水
                df_bank_raw = load_bank_file(file_bank)
                
                # 处理业务数据 - 返回 T+1日汇总、T+N日汇总、项目明细、合并数据、月捐汇总、常规T+1汇总
                df_t1_daily, df_tn_daily, df_by_project, df_combined, df_t1_monthly_daily, df_t1_regular_daily = process_system_data(df_t1, df_tn)
                
                # 处理银行流水
                df_bank = process_bank_data(df_bank_raw)
                
                # 执行对账 - 从银行流水出发匹配业务，支持月捐单独匹配
                df_report, df_bank_detail = reconcile_data(df_t1_daily, df_tn_daily, df_bank, df_t1_monthly_daily, df_t1_regular_daily)
                
                # 创建透视表
                pivot_df, date_status = create_pivot_table(df_by_project, df_report)
                
                # 统计数据 - 新格式
                t1_matched = len(df_report[df_report['T+1_状态'].str.contains('✅', na=False)])
                t1_unmatched = len(df_report[df_report['T+1_状态'].str.contains('❌', na=False)])
                tn_matched = len(df_report[df_report['T+N_状态'].str.contains('✅', na=False)])
                tn_unmatched = len(df_report[df_report['T+N_状态'].str.contains('❌', na=False)])
                bank_no_biz = len(df_report[df_report['T+1_状态'].str.contains('⚠️', na=False)])
                
                total_t1_system = df_report['T+1_系统应收'].sum()
                total_t1_bank = df_report['T+1_银行实收'].sum()
                total_tn_system = df_report['T+N_系统应收'].sum()
                total_tn_bank = df_report['T+N_银行实收'].sum()
                
                total_system = total_t1_system + total_tn_system
                total_bank = total_t1_bank + total_tn_bank
                total_diff = total_bank - total_system
                
                # 步骤3: 结果展示
                st.markdown("""
                <div class="step-header">
                    <div class="step-number">3</div>
                    <span class="step-title">对账结果</span>
                </div>
                """, unsafe_allow_html=True)
                
                # 统计卡片
                st.markdown("<br>", unsafe_allow_html=True)
                cols = st.columns(6)
                
                with cols[0]:
                    st.markdown(f"""
                    <div class="metric-card metric-card-success">
                        <div class="metric-label">✅ T+1匹配</div>
                        <div class="metric-value">{t1_matched}</div>
                        <div class="metric-label">天</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with cols[1]:
                    st.markdown(f"""
                    <div class="metric-card metric-card-success">
                        <div class="metric-label">✅ T+N匹配</div>
                        <div class="metric-value">{tn_matched}</div>
                        <div class="metric-label">天</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with cols[2]:
                    st.markdown(f"""
                    <div class="metric-card metric-card-danger">
                        <div class="metric-label">❌ 未匹配</div>
                        <div class="metric-value">{t1_unmatched + tn_unmatched}</div>
                        <div class="metric-label">T+1:{t1_unmatched} T+N:{tn_unmatched}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with cols[3]:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">📊 系统应收</div>
                        <div class="metric-value">¥{total_system:,.0f}</div>
                        <div class="metric-label">元</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with cols[4]:
                    st.markdown(f"""
                    <div class="metric-card metric-card-info">
                        <div class="metric-label">🏦 银行实收</div>
                        <div class="metric-value">¥{total_bank:,.0f}</div>
                        <div class="metric-label">元</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with cols[5]:
                    diff_class = "metric-card-success" if abs(total_diff) < 1 else "metric-card-danger"
                    st.markdown(f"""
                    <div class="metric-card {diff_class}">
                        <div class="metric-label">📈 总差异</div>
                        <div class="metric-value">¥{total_diff:,.2f}</div>
                        <div class="metric-label">元</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Tab切换展示
                tab1, tab2, tab3, tab4 = st.tabs(["📋 对账汇总", "📊 项目明细（透视表）", "🏦 银行流水明细", "📑 数据分类明细"])
                
                with tab1:
                    st.markdown("##### 按日期对账结果")
                    styled_report = style_report(df_report)
                    st.dataframe(styled_report, use_container_width=True, height=400)
                
                with tab2:
                    st.markdown("##### 项目 × 日期 金额透视表")
                    st.markdown("*行：项目名称 | 列：业务日期 | 值：捐赠金额*")
                    
                    # 颜色图例说明 - 与汇总页对账结果一致
                    st.markdown("""
                    <div style="display: flex; gap: 20px; margin: 10px 0 15px 0; flex-wrap: wrap;">
                        <span style="display: flex; align-items: center; gap: 6px;">
                            <span style="width: 16px; height: 16px; background: #d4edda; border-radius: 3px; border: 1px solid #c3e6cb;"></span>
                            <span style="font-size: 0.85rem; color: #155724; font-weight: bold;">✅ 匹配</span>
                            <span style="font-size: 0.8rem; color: #666;">该日期银行到账与系统一致</span>
                        </span>
                        <span style="display: flex; align-items: center; gap: 6px;">
                            <span style="width: 16px; height: 16px; background: #fff3cd; border-radius: 3px; border: 1px solid #ffeeba;"></span>
                            <span style="font-size: 0.85rem; color: #e67e00; font-weight: bold;">⚠️ 银行多收</span>
                            <span style="font-size: 0.8rem; color: #666;">该日期银行到账 > 系统应收</span>
                        </span>
                        <span style="display: flex; align-items: center; gap: 6px;">
                            <span style="width: 16px; height: 16px; background: #f8d7da; border-radius: 3px; border: 1px solid #f5c6cb;"></span>
                            <span style="font-size: 0.85rem; color: #dc3545; font-weight: bold;">❌ 银行少收</span>
                            <span style="font-size: 0.8rem; color: #666;">该日期银行到账 < 系统应收</span>
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 显示透视表
                    styled_pivot = style_pivot_table(pivot_df, date_status)
                    st.dataframe(styled_pivot, use_container_width=True, height=500)
                    
                    # 显示每日对账差异汇总
                    st.markdown("##### 📊 每日对账差异")
                    diff_info = []
                    for date_key, info in sorted(date_status.items()):
                        diff_info.append({
                            '日期': date_key,
                            '状态': info['status'],
                            '差异金额': f"¥{info['diff']:,.2f}"
                        })
                    if diff_info:
                        st.dataframe(pd.DataFrame(diff_info), use_container_width=True, hide_index=True)
                    
                    # 项目数量统计
                    st.markdown(f"""
                    <div class="info-box">
                        📌 共 <b>{len(pivot_df)}</b> 个项目，
                        覆盖 <b>{len(pivot_df.columns)-1}</b> 个业务日期，
                        总金额 <b>¥{pivot_df['合计'].sum():,.2f}</b>
                    </div>
                    """, unsafe_allow_html=True)
                
                with tab3:
                    st.markdown("##### 银行入账明细")
                    bank_display = df_bank_detail[['发生时间', '收入', '到账日期', '银行摘要']].copy()
                    bank_display.columns = ['入账时间', '金额', '到账日期', '摘要']
                    st.dataframe(bank_display, use_container_width=True, height=400)
                
                with tab4:
                    st.markdown("##### 数据分类明细")
                    
                    col_t1, col_tn = st.columns(2)
                    
                    with col_t1:
                        st.markdown(f"**T+1 数据** (共 {len(df_t1)} 条，不带【GFYH】)")
                        if len(df_t1) > 0:
                            t1_display = df_t1[['捐赠项目', '捐赠时间', '捐赠金额', '捐赠说明']].head(100)
                            st.dataframe(t1_display, use_container_width=True, height=300)
                    
                    with col_tn:
                        st.markdown(f"**T+N 数据** (共 {len(df_tn)} 条，带【GFYH】)")
                        if len(df_tn) > 0:
                            tn_display = df_tn[['捐赠项目', '捐赠时间', '捐赠金额', '捐赠说明']].head(100)
                            st.dataframe(tn_display, use_container_width=True, height=300)
                
                # 下载按钮
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("""
                <div class="step-header">
                    <div class="step-number">4</div>
                    <span class="step-title">导出报告</span>
                </div>
                """, unsafe_allow_html=True)
                
                col_dl = st.columns([1, 2, 1])
                with col_dl[1]:
                    excel_data = to_excel(df_report, pivot_df, df_bank_detail, df_t1, df_tn)
                    st.download_button(
                        label="📥 下载完整Excel报告",
                        data=excel_data,
                        file_name=f"对账报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                
            except Exception as e:
                st.error(f"❌ 处理出错: {str(e)}")
                st.exception(e)

else:
    # 未上传完整文件时的提示
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("👆 请上传有益云数据和银行流水文件后开始对账")
    
    # 示例数据格式
    with st.expander("📖 查看数据格式要求"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**有益云数据**")
            st.markdown("""
            直接从有益云系统导出的 Excel/CSV 文件
            
            系统会自动根据**捐赠说明**字段区分：
            - 带 `【GFYH】` → **T+N** (广发银行收款)
            - 不带 `【GFYH】` → **T+1** (财付通收款)
            """)
        with col2:
            st.markdown("**银行流水**")
            st.markdown("""
            银行导出的流水文件，需包含以下列：
            - `发生时间` - 银行入账时间
            - `收入` - 入账金额
            - `用途` - 交易用途
            - `附言` - 附言信息（用于提取业务日期）
            """)

# 页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #999; padding: 1rem;'>
    💡 财务对账工具 v3.0 | 支持自动识别T+1/T+N | 差异<1元视为匹配
</div>
""", unsafe_allow_html=True)
