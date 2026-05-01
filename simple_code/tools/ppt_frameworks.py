"""PPT 框架知识库：21 套设计框架 + 转场动画"""

FRAMEWORKS = {
    "mckinsey": {
        "name": "麦肯锡商务",
        "desc": "战略咨询、高管汇报、投资分析、商业提案",
        "colors": {
            "primary": "#005587", "secondary": "#0076A8", "accent": "#F5A623",
            "title_text": "#2C3E50", "body_text": "#5D6D7E", "subtle": "#7F8C8D",
            "light_bg": "#ECF0F1", "line": "#E5E7EB",
            "success": "#27AE60", "warning": "#E74C3C",
        },
        "cover": {"align": "left", "bg": "white",
                  "deco": ["左侧蓝色窄强调条(8px)", "左上短水平线", "右侧低透明度几何方块轮廓", "信息卡片(项目编号/日期)", "保密标签"]},
        "section": {"bg": "solid_primary",
                    "deco": ["蓝色全屏背景", "居中白色大标题", "极简"]},
        "content": {"header": "top_blue_bar_4px",
                    "deco": ["左对齐页面标题", "页脚页码+来源"]},
        "toc": {"deco": ["蓝色顶条", "章节编号列表"]},
        "ending": {"deco": ["居中感谢语", "联系信息", "保密标签"]},
    },
    "google": {
        "name": "谷歌科技",
        "desc": "科技年报、技术分享、数据展示",
        "colors": {
            "primary": "#4285F4", "secondary": "#1A237E", "accent": "#FBBC04",
            "red": "#EA4335", "green": "#34A853",
            "title_text": "#1A237E", "body_text": "#5F6368", "subtle": "#9AA0A6",
            "light_bg": "#F8F9FA", "line": "#E8EAED",
        },
        "cover": {"align": "center", "bg": "light_gradient",
                  "deco": ["左侧四色竖条(10px宽,蓝→红→黄→绿)", "居中圆角白色卡片", "四色分割线(蓝150+红70+黄70+绿170,4px)", "底部四色圆点"]},
        "section": {"bg": "dark_gradient",
                    "deco": ["大号渐变章节编号", "四色装饰"]},
        "content": {"header": "four_color_gradient_bar_6px",
                    "deco": ["四色标题下划线", "KPI数据卡片(280x140,16px圆角,3px品牌色边框)", "底部四色圆点"]},
        "toc": {"deco": ["四色顶条", "品牌色圆点编号列表"]},
        "ending": {"deco": ["居中白色卡片", "渐变Thank You", "四色分割线", "四色圆点"]},
    },
    "academic": {
        "name": "学术答辩",
        "desc": "论文答辩、科研报告、课题申报",
        "colors": {
            "primary": "#003366", "secondary": "#0066CC", "accent": "#CC0000",
            "title_text": "#333333", "body_text": "#666666", "subtle": "#999999",
            "light_bg": "#F5F7FA", "line": "#D0D7E0",
            "success": "#28A745", "warning": "#FFA500", "info": "#17A2B8",
        },
        "cover": {"align": "center", "bg": "white",
                  "deco": ["深蓝顶部横条+红色左竖条(6px)", "Logo占位区", "蓝色圆点分割线", "底部灰色日期区"]},
        "section": {"bg": "solid_dark_003366",
                    "deco": ["右侧几何装饰", "左侧红条", "大号半透明背景数字", "红色水平线"]},
        "content": {"header": "dark_blue_bar_70px+red_left_bar_6px",
                    "deco": ["关键信息条(浅蓝灰#E8F4FC+蓝色左竖条)", "页脚(来源/章节/页码)"]},
        "toc": {"deco": ["2列卡片目录", "浅蓝灰卡片+左侧彩色竖条"]},
        "ending": {"deco": ["深蓝顶条", "联系信息卡片(灰底)"]},
    },
    "government_blue": {
        "name": "政务蓝",
        "desc": "重点项目汇报、五年规划、招商引资、政策解读",
        "colors": {
            "primary": "#0050B3", "secondary": "#00B4D8", "accent": "#003366",
            "title_text": "#1A1A1A", "body_text": "#4A5568", "subtle": "#718096",
            "light_bg": "#E6F4FF", "line": "#B0C4DE",
            "success": "#38A169", "warning": "#E53E3E",
        },
        "cover": {"align": "center", "bg": "deep_blue_gradient+tech_grid",
                  "deco": ["亮蓝强调条", "几何圆圈", "底部日期"]},
        "section": {"bg": "dark_gradient",
                    "deco": ["径向发光", "大号半透明章节号(描边)", "亮蓝强调条"]},
        "content": {"header": "blue_gradient_bar_6px+section_number_50x50",
                    "deco": ["渐变编号方块", "虚线分割", "底部蓝色装饰线(4px)"]},
        "toc": {"deco": ["浅蓝渐变底", "圆形编号+连接线", "浮动卡片"]},
        "ending": {"deco": ["深蓝渐变底", "波浪曲线", "亮蓝分割线"]},
    },
    "government_red": {
        "name": "政务红",
        "desc": "各级政府汇报、政策演示、工作总结",
        "colors": {
            "primary": "#8B0000", "secondary": "#003366", "accent": "#DAA520",
            "title_text": "#1A1A1A", "body_text": "#4A5568", "subtle": "#718096",
            "light_bg": "#F5F7FA", "line": "#E4E7EB",
            "success": "#38A169", "warning": "#E53E3E",
        },
        "cover": {"align": "center", "bg": "dark_blue_gradient",
                  "deco": ["顶部金色装饰线", "底部日期"]},
        "section": {"bg": "dark_blue_gradient",
                    "deco": ["大号半透明章节号", "几何装饰"]},
        "content": {"header": "red_blue_gradient_bar_6px+red_number_50x50",
                    "deco": ["底部红色装饰线(4px)", "页脚页码+机构名"]},
        "toc": {"deco": ["左侧红色竖条", "红色方块编号"]},
        "ending": {"deco": ["深蓝背景", "居中感谢语", "机构信息"]},
    },
    "pixel_retro": {
        "name": "像素复古",
        "desc": "技术分享、编程教程、游戏介绍、极客风格",
        "colors": {
            "primary": "#39FF14", "secondary": "#FF2E97", "accent": "#00D4FF",
            "yellow": "#FFD700",
            "title_text": "#E6EDF3", "body_text": "#8B949E", "subtle": "#484F58",
            "light_bg": "#161B22", "line": "#30363D",
        },
        "cover": {"align": "center", "bg": "deep_black_0D1117",
                  "deco": ["顶部/底部霓虹双线(主4px+辅2px,绿)", "像素控制台图形", "霓虹绿发光标题(filter)", "PRESS START提示"]},
        "section": {"bg": "deep_black",
                    "deco": ["全屏霓虹效果", "发光章节号", "像素装饰框"]},
        "content": {"header": "neon_green_dual_line",
                    "deco": ["像素角落方块(递减透明度100→60→30)", "扫描线网格(可选)", "底部霓虹双线", "开放内容区"]},
        "toc": {"deco": ["像素风列表", "重要性标签(红=必学/绿=可选/黄=推荐)"]},
        "ending": {"deco": ["霓虹发光标题", "GAME SAVED效果", "进度按钮组"]},
    },
    "ai_enterprise": {
        "name": "企业数智化",
        "desc": "运营商AI运维、数智化转型、高信息密度模块化报告",
        "colors": {
            "primary": "#C00000", "secondary": "#2E75B6", "accent": "#5B9BD5",
            "title_text": "#000000", "body_text": "#333333", "subtle": "#999999",
            "light_bg": "#F2F2F2", "line": "#D9D9D9",
            "warm_bg": "#FDF3EB", "warm_border": "#F8CBAD",
        },
        "cover": {"align": "center", "bg": "white",
                  "deco": ["左侧红蓝双色竖条(60px,红上蓝下)", "编号徽章1-5", "蓝色场景标签", "暖灰底部条+蓝色全宽底条"]},
        "section": {"bg": "white",
                    "deco": ["左红条+右蓝条", "红色大号编号徽章(80x80)", "水印数字(160px浅灰)", "红蓝双线"]},
        "content": {"header": "red_top_4px+red_vertical_8x40+title_32px",
                    "deco": ["数字徽章(30x30红+白字)", "蓝色场景标签", "虚线区域框(dasharray=5,5)", "暖灰面板(#FDF3EB+#F8CBAD边框)", "指标卡片(红色高亮)", "页脚(红竖条+红方块页码)"]},
        "toc": {"deco": ["红蓝双色条", "编号列表"]},
        "ending": {"deco": ["红蓝装饰", "居中感谢语"]},
    },
    "anthropic": {
        "name": "AI科技(Anthropic)",
        "desc": "AI技术演讲、开发者大会、技术培训、产品发布",
        "colors": {
            "primary": "#D97757", "secondary": "#1A1A2E", "accent": "#4A90D9",
            "mint": "#10B981", "coral": "#EF4444",
            "title_text": "#1A1A2E", "body_text": "#64748B", "subtle": "#94A3B8",
            "light_bg": "#F8FAFC", "line": "#E2E8F0",
        },
        "cover": {"align": "center", "bg": "dark_gradient_1A1A2E→0F0F1A",
                  "deco": ["网格线(白色3%透明度)", "橙蓝光晕", "神经网络节点连线", "橙色装饰短线"]},
        "section": {"bg": "dark_gradient",
                    "deco": ["网格装饰", "居中大标题", "橙色装饰线"]},
        "content": {"header": "orange_top_bar_6px",
                    "deco": ["页面类型标签(橙色大写)", "三列卡片(彩色顶边框)", "左侧橙色渐变条(#D97757→#E8956F)", "页脚居中页码"]},
        "toc": {"deco": ["左侧橙色渐变条(8px)", "橙色圆形数字", "复杂度递进图"]},
        "ending": {"deco": ["深色底+神经网络", "居中感谢", "联系信息"]},
    },
    "smart_red": {
        "name": "活力红橙",
        "desc": "公司介绍、产品发布、教育行业方案、智慧校园",
        "colors": {
            "primary": "#DE3545", "secondary": "#F0964D", "accent": "#333333",
            "title_text": "#333333", "body_text": "#666666", "subtle": "#999999",
            "light_bg": "#F5F5F7", "line": "#E0E0E0",
        },
        "cover": {"align": "center", "bg": "light_gray_F5F5F7",
                  "deco": ["左上红色大三角(0,0→350,0→0,350)", "左下深灰三角(0,720→300,720→0,420)", "右下红色大三角(1280,720→1280,320→880,720)", "多层半透明小三角叠加"]},
        "section": {"bg": "light_gray",
                    "deco": ["红色三角呼应封面(左上/右下)", "居中大号章节编号+标题", "半透明几何叠加"]},
        "content": {"header": "white_nav_bar+red_cutout_top_right",
                    "deco": ["标题双三角装饰(红+橙)", "浅灰背景#F5F5F7", "白色圆角卡片(+边框#E0E0E0)", "页脚版权+页码"]},
        "toc": {"deco": ["左侧全高红色多边形面板+大号Contents", "圆形数字索引(红描边)"]},
        "ending": {"deco": ["三角布局呼应封面", "居中感谢语"]},
    },
    "tech_blue": {
        "name": "科技蓝商务",
        "desc": "企业汇报、产品发布、方案提案、流程规范",
        "colors": {
            "primary": "#0078D7", "secondary": "#002E5D", "accent": "#4CA1E7",
            "alert": "#E60012",
            "title_text": "#333333", "body_text": "#555555", "subtle": "#666666",
            "light_bg": "#F5F5F7", "line": "#A0C4E3",
        },
        "cover": {"align": "left", "bg": "blue_gradient_left+image_right",
                  "deco": ["底部双层波浪曲线", "六边形科技图案", "副标题背景强调", "右侧全出血图片"]},
        "section": {"bg": "dark_blue_gradient_0078D7→002E5D",
                    "deco": ["居中章节号+粗体标题", "极简几何环/线条"]},
        "content": {"header": "blue_rect_accent_10x40+triangle_prefix",
                    "deco": ["纯白背景", "圆角虚线容器(dasharray=8,8,rx=10)", "页脚小灰色页码"]},
        "toc": {"deco": ["左侧深蓝侧边栏+Contents", "右侧列表+引导线"]},
        "ending": {"deco": ["深蓝渐变", "Thank You+Q&A", "底部波浪曲线首尾呼应"]},
    },
    "exhibit": {
        "name": "Exhibit暗色咨询",
        "desc": "战略规划、高管报告、投资分析、董事会演示",
        "colors": {
            "primary": "#0D1117", "secondary": "#1E40AF", "accent": "#D4AF37",
            "purple": "#7C3AED",
            "title_text": "#FFFFFF", "body_text": "#111827", "subtle": "#6B7280",
            "light_bg": "#1F2937", "line": "#374151",
        },
        "cover": {"align": "left", "bg": "dark_0D1117",
                  "deco": ["顶部蓝紫渐变条(#1E40AF→#7C3AED)", "左侧金色竖线(4px)", "右侧网格装饰", "底部日期/保密/作者"]},
        "section": {"bg": "dark",
                    "deco": ["顶部渐变条", "左侧金线", "大号半透明编号", "右侧网格"]},
        "content": {"header": "gradient_thin_bar+dark_insight_bar(gold_left)",
                    "deco": ["白色背景", "Exhibit Takeaway Bar", "页脚(来源/保密/页码)", "所有页底部CONFIDENTIAL金色文字"]},
        "toc": {"deco": ["深色底", "双竖线||分隔(金色)", "紫蓝色章节编号", "保密标签"]},
        "ending": {"deco": ["深色底+网格", "金色分割线", "联系卡片", "保密标签+版权"]},
    },
    "china_telecom": {
        "name": "中国电信",
        "desc": "电信解决方案提案、数字化转型汇报、政企报告",
        "colors": {
            "primary": "#C00000", "secondary": "#D9D9D9", "accent": "#2B2F33",
            "title_text": "#111827", "body_text": "#6B7280", "subtle": "#9CA3AF",
            "light_bg": "#FFFFFF", "line": "#CFCFCF",
            "skyline_blue": "#DCEAF8",
        },
        "cover": {"align": "left", "bg": "white",
                  "deco": ["左上角固定Logo", "左对齐标题+红色强调线", "右侧视觉卡片(标语+天际线图像)", "底部全宽横幅"]},
        "section": {"bg": "white",
                    "deco": ["右上角紧凑Logo", "左侧大号章节号+标题", "右侧视觉卡片", "页脚横幅"]},
        "content": {"header": "red_chapter_label+gray_channel+logo",
                    "deco": ["开放画布(灵活图表/表格)", "轻量级角落品牌控制", "页脚来源+页码"]},
        "toc": {"deco": ["红色圆角标题胶囊+灰色通道", "左侧视觉卡片", "右侧文本列表(≤4大节)", "点线引导线"]},
        "ending": {"deco": ["左侧结束语", "右侧结束视觉卡片", "全宽页脚横幅"]},
    },
    "medical": {
        "name": "医院/医科大学",
        "desc": "医院学术报告、病例展示、科研成果、临床研究",
        "colors": {
            "primary": "#0066B3", "secondary": "#004080", "accent": "#FF6B35",
            "green": "#00A86B",
            "title_text": "#333333", "body_text": "#666666", "subtle": "#999999",
            "light_bg": "#E6F3FA", "line": "#D0D7E0",
            "success": "#28A745", "warning": "#FFC107", "danger": "#DC3545",
        },
        "cover": {"align": "center", "bg": "white",
                  "deco": ["医学蓝顶部横条+橙色左竖条", "Logo/校徽占位(160x50)", "蓝绿圆点分割线", "底部灰色日期区"]},
        "section": {"bg": "solid_dark_004080",
                    "deco": ["右侧医学主题几何装饰", "左侧橙色竖条", "大号半透明章节号"]},
        "content": {"header": "medical_blue_bar_70px+orange_left_6px",
                    "deco": ["关键信息条(浅蓝#E6F3FA+蓝色左竖条)", "十字/心电图装饰", "页脚(来源/机构/页码)"]},
        "toc": {"deco": ["2列卡片(浅蓝/浅绿)", "彩色左竖条"]},
        "ending": {"deco": ["医学蓝顶条", "科室联系信息", "Logo区"]},
    },
    "psychology": {
        "name": "心理学治愈",
        "desc": "心理学讲座、心理治疗培训、咨询案例分享",
        "colors": {
            "primary": "#2E5C8E", "secondary": "#3D8B7A", "accent": "#E07843",
            "cool_gray": "#64748B", "trauma_red": "#B54545",
            "title_text": "#1E293B", "body_text": "#374151", "subtle": "#6B7280",
            "light_bg": "#F8FAFC", "line": "#E5E7EB",
        },
        "cover": {"align": "center", "bg": "blue_green_gradient_1E3A5F→2E5C8E→3D8B7A",
                  "deco": ["可选背景图(25%透明度)", "暖橙色细线(200px)", "底部引用卡片(半透明+治愈绿左边框)", "关键词胶囊标签"]},
        "section": {"bg": "blue_green_gradient",
                    "deco": ["低透明度同心圆", "对角线装饰", "120px半透明白色数字", "胶囊CHAPTER标签", "暖橙细线", "底部标签组"]},
        "content": {"header": "left_accent_bar_8px+title_28px+english_subtitle",
                    "deco": ["白色卡片(浅灰边框,12-16px圆角,彩色顶条/左边框)", "底部提示条(可选)", "分割线(#E5E7EB)"]},
        "toc": {"deco": ["左侧主色8px竖条", "五色编号方块(蓝/绿/橙/灰蓝/红)", "右侧学习目标卡片"]},
        "ending": {"deco": ["蓝绿渐变底", "网络连接图(点+线)", "暖橙细线", "半透明信息卡片"]},
    },
    "powerchina": {
        "name": "中国电建常规",
        "desc": "工程项目汇报、技术方案、商务洽谈、年度总结",
        "colors": {
            "primary": "#00418D", "secondary": "#002B5C", "accent": "#0066CC",
            "sky_blue": "#4A90D9", "china_red": "#C41E3A", "gold": "#C9A227",
            "title_text": "#1A1A1A", "body_text": "#4A5568", "subtle": "#718096",
            "light_bg": "#F4F6F8", "line": "#D0D7E0",
        },
        "cover": {"align": "center", "bg": "deep_blue_gradient+engineering_texture",
                  "deco": ["左侧品牌蓝装饰条", "POWERCHINA英文名", "底部红色装饰条"]},
        "section": {"bg": "dark_gradient",
                    "deco": ["大号章节编号", "英文副标题", "几何网格"]},
        "content": {"header": "blue_gradient_6px+section_number+logo",
                    "deco": ["页脚(页码/公司名/底部装饰线)"]},
        "toc": {"deco": ["左侧蓝色装饰区", "编号+竖线分隔"]},
        "ending": {"deco": ["深蓝渐变底", "Logo", "中英文感谢语"]},
    },
    "powerchina_modern": {
        "name": "中国电建现代",
        "desc": "重大项目汇报、国际业务展示、高端峰会路演、技术创新发布",
        "colors": {
            "primary": "#00418D", "secondary": "#072C61", "accent": "#0066CC",
            "china_red": "#C41E3A", "gold": "#FFD700",
            "title_text": "#FFFFFF", "body_text": "#E2E8F0", "subtle": "#94A3B8",
            "light_bg": "#001F45", "line": "#374151",
        },
        "cover": {"align": "center", "bg": "deep_blue_tech_gradient+geo_grid",
                  "deco": ["中心对称布局(央企稳重)", "基座(Foundation)厚重深蓝托底"]},
        "section": {"bg": "dark_gradient",
                    "deco": ["巨型描边数字(Stroke Only)", "建筑结构感"]},
        "content": {"header": "blue_bar_8px+label_style_title+logo_white_plate",
                    "deco": ["四角角标(Corner Marks)工程精密感", "控制台(Console)风格布局"]},
        "toc": {"deco": ["里程碑(Milestones)风格", "水平时间线/连接卡片", "电路管网节点"]},
        "ending": {"deco": ["呼应封面基座结构", "二维码/联系分区"]},
    },
    "catarc_business": {
        "name": "中汽研商务",
        "desc": "产品认证展示、评价认证、技术推广、高端商务汇报",
        "colors": {
            "primary": "#003366", "secondary": "#0050B3", "accent": "#D32F2F",
            "title_text": "#1F2937", "body_text": "#6B7280", "subtle": "#9CA3AF",
            "light_bg": "#F0F2F5", "line": "#E5E7EB",
        },
        "cover": {"align": "left", "bg": "left_whitespace+right_dark_tech_cut",
                  "deco": ["动态几何线条(Tech Lines)模拟光束", "标题左对齐或居中浮动卡片"]},
        "section": {"bg": "deep_blue_radial_gradient",
                    "deco": ["中心聚焦排版", "放射线/环形装饰"]},
        "content": {"header": "gradient_blue_6px+section_number+title+gray_line",
                    "deco": ["干净白底最大化内容区", "右下角极淡Logo水印"]},
        "toc": {"deco": ["水平卡片+微妙阴影", "超大半透明编号背景"]},
        "ending": {"deco": ["呼应封面深色调", "精致联系信息"]},
    },
    "catarc_standard": {
        "name": "中汽研常规",
        "desc": "产品认证、评价认证、技术推广、商务来访",
        "colors": {
            "primary": "#004098", "secondary": "#002B6E", "accent": "#CC0000",
            "title_text": "#333333", "body_text": "#666666", "subtle": "#999999",
            "light_bg": "#F5F5F5", "line": "#E0E0E0",
            "success": "#4CAF50",
        },
        "cover": {"align": "center", "bg": "background_image+semi_transparent_overlay",
                  "deco": ["大号居中Logo", "中英文机构名称"]},
        "section": {"bg": "dark_gradient",
                    "deco": ["大号章节编号", "英文副标题"]},
        "content": {"header": "blue_top_4px+blue_number_50x50+title_28px+logo",
                    "deco": ["底部蓝色装饰线(4px)", "右对齐页码"]},
        "toc": {"deco": ["双竖线||分隔", "左侧装饰竖线", "右侧统计数据区"]},
        "ending": {"deco": ["深蓝纯色底", "居中Logo+感谢语"]},
    },
    "catarc_modern": {
        "name": "中汽研现代科技",
        "desc": "高端发布会、前瞻技术展示、国际交流",
        "colors": {
            "primary": "#001529", "secondary": "#1890FF", "accent": "#00E5FF",
            "title_text": "#FFFFFF", "body_text": "#374151", "subtle": "#6B7280",
            "light_bg": "#F7F9FC", "line": "#E5E7EB",
        },
        "cover": {"align": "left", "bg": "deep_blue_radial_gradient",
                  "deco": ["右侧抽象光流(Luminous Flow)", "标题左下对齐+霓虹色下划线"]},
        "section": {"bg": "dark",
                    "deco": ["背景大号描边数字(Stroke)", "倾斜装饰线模拟速度感"]},
        "content": {"header": "asymmetric_title+left_geo_bar+logo_glow+right_accent_line",
                    "deco": ["极浅灰背景#F7F9FC", "浮动标题栏", "右下角科技风几何水印"]},
        "toc": {"deco": ["分屏(左暗右亮)", "霓虹青(#00E5FF)编号高亮"]},
        "ending": {"deco": ["呼应封面深色底", "极简Thank You+光晕环"]},
    },
    "cmb": {
        "name": "招商银行交易银行",
        "desc": "交易银行产品介绍、销售收款方案、客户案例、分行培训",
        "colors": {
            "primary": "#C8152D", "secondary": "#8F0F1B", "accent": "#E26A74",
            "finance_blue": "#2175D9",
            "title_text": "#1F1F1F", "body_text": "#666666", "subtle": "#999999",
            "light_bg": "#FFFFFF", "line": "#E9E9E9",
            "positive": "#27AE60", "negative": "#E74C3C",
        },
        "cover": {"align": "center", "bg": "brand_cover_bg_image",
                  "deco": ["居中白色排版", "克制分割线(Signal Red #E26A74)"]},
        "section": {"bg": "solid_deep_red_8F0F1B",
                    "deco": ["背景大号半透明章节号(220px)", "左对齐标题+章节描述"]},
        "content": {"header": "narrow_red_top_strip+right_logo",
                    "deco": ["页面标题+章节标签+关键信息行", "开放正文区", "页脚(章节/来源/页码)", "浅灰分割线(#E9E9E9)"]},
        "toc": {"deco": ["红色顶条+Logo", "两列索引(≤4项)", "红色编号+深色文字"]},
        "ending": {"deco": ["复用封面背景", "居中结束语", "紧凑联系卡片"]},
    },
    "cqu": {
        "name": "重庆大学",
        "desc": "学术答辩、科研报告、教学展示，融合山城层叠意象",
        "colors": {
            "primary": "#006BB7", "secondary": "#004A82", "accent": "#D4A84B",
            "sky_blue": "#3A9BD9", "cloud_blue": "#E3F2FD",
            "title_text": "#1A2E44", "body_text": "#333D4A", "subtle": "#6B7B8C",
            "light_bg": "#FAFCFF", "line": "#E5E7EB",
        },
        "cover": {"align": "left", "bg": "white_FAFCFF+left_bottom_diagonal_deep_blue(40%面积)",
                  "deco": ["右上角Logo", "波浪纹样(长江/嘉陵江,蓝色8%透明度)", "金色光点(山城夜景,#D4A84B 60%透明度,r=3)", "底部演讲者+日期"]},
        "section": {"bg": "solid_dark_004A82",
                    "deco": ["右上角对角浅色区域(天蓝渐变)", "左侧大号半透明章节号", "底部金色线+白色Logo"]},
        "content": {"header": "diagonal_blue_accent_bar(80px,8-12度倾斜)+title+logo",
                    "deco": ["左侧细金色装饰线", "底部波浪纹样", "白色内容区(灵活布局)"]},
        "toc": {"deco": ["对角强调条+标题", "左侧大号金色数字索引", "底部波浪"]},
        "ending": {"deco": ["居中大号Logo(320-400px)", "感谢语", "底部对角蓝色区+联系信息", "波浪+金色光点"]},
    },
}


# === 转场动画知识库（7 种页面切换效果）===

TRANSITIONS = {
    "fade":    {"name": "淡入淡出", "desc": "柔和过渡，适合封面、结尾、正式场合",          "duration_ms": 700, "element": "fade",    "attrs": {}},
    "push":    {"name": "推入",     "desc": "从右侧推入，适合章节切换、内容递进",          "duration_ms": 500, "element": "push",    "attrs": {"dir": "r"}},
    "wipe":    {"name": "擦除",     "desc": "从右侧擦入，适合内容页、数据展示",            "duration_ms": 400, "element": "wipe",    "attrs": {"dir": "r"}},
    "split":   {"name": "拆分",     "desc": "从中间向两侧展开，适合章节、对比内容",        "duration_ms": 500, "element": "split",   "attrs": {"orient": "horz", "dir": "out"}},
    "strips":  {"name": "条纹",     "desc": "对角线条纹擦入，适合科技风格",                "duration_ms": 500, "element": "strips",  "attrs": {"dir": "rd"}},
    "cover":   {"name": "覆盖",     "desc": "新页覆盖旧页，适合快节奏展示",                "duration_ms": 500, "element": "cover",   "attrs": {"dir": "r"}},
    "random":  {"name": "随机",     "desc": "随机选择效果，适合轻松场合",                  "duration_ms": 500, "element": "random",  "attrs": {}},
    "none":    {"name": "无转场",   "desc": "立即切换，适合打印、快速翻阅",                "duration_ms": 0,   "element": None,      "attrs": {}},
}

TRANSITION_DEFAULTS = {"title": "fade", "section": "push", "content": "wipe"}


# === 入场动画知识库（23 种元素入场效果）===
# filter: PowerPoint animEffect filter 字符串（ECMA-376 §19.5.10）
# presetID/presetSubtype: PowerPoint 内部动画编号

ENTRANCE_ANIMATIONS = {
    "appear":       {"name": "出现",     "desc": "立即显示，无动画效果",       "filter": None,                    "presetID": 1,  "presetSub": 0},
    "fade":         {"name": "淡入",     "desc": "渐渐浮现，最常用的入场效果", "filter": "fade",                  "presetID": 10, "presetSub": 0},
    "fly":          {"name": "飞入",     "desc": "从底部飞入，适合要点逐条出现", "filter": "slide(fromBottom)",    "presetID": 2,  "presetSub": 4},
    "cut":          {"name": "切入",     "desc": "从左侧切入",                 "filter": "slide(fromLeft)",       "presetID": 42, "presetSub": 8},
    "zoom":         {"name": "缩放",     "desc": "从小到大放大出现",            "filter": "image",                 "presetID": 23, "presetSub": 0},
    "wipe":         {"name": "擦除",     "desc": "从左到右擦除显示",            "filter": "wipe(left)",            "presetID": 22, "presetSub": 1},
    "split":        {"name": "拆分",     "desc": "从中间向两边展开",            "filter": "barn(inVertical)",      "presetID": 16, "presetSub": 21},
    "blinds":       {"name": "百叶窗",   "desc": "水平百叶窗效果",              "filter": "blinds(horizontal)",    "presetID": 3,  "presetSub": 10},
    "checkerboard": {"name": "棋盘格",   "desc": "棋盘格渐显效果",              "filter": "checkerboard(across)",  "presetID": 5,  "presetSub": 6},
    "dissolve":     {"name": "溶解",     "desc": "像素点溶解显示",              "filter": "dissolve",              "presetID": 9,  "presetSub": 0},
    "random_bars":  {"name": "随机线条", "desc": "水平随机线条擦入",            "filter": "randombar(horizontal)", "presetID": 14, "presetSub": 10},
    "peek":         {"name": "窥视",     "desc": "从下方探出",                  "filter": "wipe(down)",            "presetID": 12, "presetSub": 4},
    "wheel":        {"name": "轮子",     "desc": "四分轮旋转显示",              "filter": "wheel(4)",              "presetID": 21, "presetSub": 0},
    "box":          {"name": "盒状",     "desc": "从中心向外扩展方框",          "filter": "box(in)",               "presetID": 4,  "presetSub": 0},
    "circle":       {"name": "圆形",     "desc": "从中心向外扩展圆形",          "filter": "circle(in)",            "presetID": 6,  "presetSub": 0},
    "diamond":      {"name": "菱形",     "desc": "从中心向外扩展菱形",          "filter": "diamond(in)",           "presetID": 8,  "presetSub": 0},
    "plus":         {"name": "十字",     "desc": "从中心向外扩展十字",          "filter": "plus(in)",              "presetID": 13, "presetSub": 0},
    "strips":       {"name": "条纹",     "desc": "从右下角对角条纹",            "filter": "strips(downRight)",     "presetID": 18, "presetSub": 12},
    "wedge":        {"name": "楔形",     "desc": "楔形展开",                    "filter": "wedge",                 "presetID": 20, "presetSub": 0},
    "stretch":      {"name": "伸展",     "desc": "横向拉伸显示",                "filter": "stretch(across)",       "presetID": 17, "presetSub": 0},
    "expand":       {"name": "展开",     "desc": "从中心展开放大",              "filter": "stretch(across)",       "presetID": 50, "presetSub": 0},
    "swivel":       {"name": "旋转",     "desc": "旋转出现",                    "filter": "wheel(1)",              "presetID": 19, "presetSub": 0},
}

# mixed/random 模式使用的动画池
ENTRANCE_MIXED_POOL = [
    "blinds", "checkerboard", "dissolve", "fly", "cut",
    "random_bars", "box", "split", "strips", "wedge", "wheel",
    "wipe", "expand", "fade", "swivel", "zoom",
]

# 触发模式
ENTRANCE_TRIGGERS = {
    "after-previous": "前一个结束后自动播放（默认，无需点击）",
    "on-click":       "点击后播放（演讲者控制节奏）",
    "with-previous":  "与前一个同时播放（同时出现）",
}

ENTRANCE_DEFAULTS = {"title": "fade", "section": "fade", "content": "fade"}


# === 工具定义 ===

definition = {
    "type": "function",
    "function": {
        "name": "ppt_frameworks",
        "description": """查询可用的 PPT 设计框架、转场动画和入场动画。在创建 PPT 之前调用此工具。
共 21 套框架、8 种转场、23 种入场动画、3 种触发模式。""",
        "parameters": {"type": "object", "properties": {}},
    },
}


def label(args):
    return "正在查询 PPT 框架"


def execute(args, **kwargs):
    lines = ["=== 设计框架（{} 套）===\n".format(len(FRAMEWORKS))]
    for key, fw in FRAMEWORKS.items():
        colors = fw['colors']
        acc = colors.get('accent', colors.get('secondary', ''))
        lines.append(f"【{key}】{fw['name']}")
        lines.append(f"  {fw['desc']}")
        lines.append(f"  主色:{colors['primary']} 强调:{acc}")
        lines.append("")

    lines.append("=== 转场动画（页面切换）===\n")
    for key, tr in TRANSITIONS.items():
        if key != "none":
            lines.append(f"  {key}: {tr['name']} — {tr['desc']}")
    lines.append("  none: 无转场")
    lines.append("  默认: 封面=fade 章节=push 内容=wipe\n")

    lines.append("=== 入场动画（元素出现方式）===\n")
    for key, an in ENTRANCE_ANIMATIONS.items():
        lines.append(f"  {key}: {an['name']} — {an['desc']}")
    lines.append("")
    lines.append("  触发模式:")
    for key, desc in ENTRANCE_TRIGGERS.items():
        lines.append(f"    {key}: {desc}")
    lines.append("  特殊模式: mixed(首元素淡入,其余循环变化) / random(随机选择)")

    lines.append("\n用法: create_ppt(framework=\"框架名\", slides=[{transition:\"转场\", entrance:\"入场动画\"}, ...])")
    return "\n".join(lines)
