SHEET_NAME_1 = "Assessment + Target Level"
SHEET_NAME_2 = "Overview"

RESPONSE_TO_NUMBER = {
    "Not implemented yet | 尚未实施 ": 1,
    "Partially implemented | 部分实施": 2,
    "Broadly implemented | 广泛实施": 3,
    "Fully implemented | 全面实施": 4,
    "Don't know | 不知道": 0,
    "Not relevant | 不相关": 99,
    None: -1,
    "nan": -1
}
NUMBER_TO_GRAY = {1: 0.1, 2: 0.3, 3: 0.7, 4: 1.0}

LEVEL_MAP_FRAC = {
    "25% - Readiness |准备就绪": 0.25, "50% - Initial Maturity | 初步成熟": 0.50,
    "75% - Intermediate Maturity | 中级成熟 ": 0.75, "100% - Advanced Maturity | 高级成熟": 1.00,
}
LEVEL_MAP_ORD = {
    "25% - Readiness |准备就绪": 1, "50% - Initial Maturity | 初步成熟": 2,
    "75% - Intermediate Maturity | 中级成熟 ": 3, "100% - Advanced Maturity | 高级成熟": 4,
}

DIM_COLORS = {
    "Management & Organisation | 管理与组织": "#edf8f6",
    "People & Culture | 人员与文化":          "#edf8f6",
    "Information Technology | 信息技术":    "#7fcac0",
    "Process Management | 流程管理":        "#7fcac0",
    "Quality Management | 质量管理":        "#7fcac0",
    "Logistics | 物流":                 "#7fcac0",
    "External Integration | 外部整合":    "#7fcac0",
    "Engineering | 工程":               "#7fcac0",
}
