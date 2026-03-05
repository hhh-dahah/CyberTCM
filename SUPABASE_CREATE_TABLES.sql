-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    nickname TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建管理员密码表
CREATE TABLE IF NOT EXISTS admin_password (
    id SERIAL PRIMARY KEY,
    password TEXT NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建完整问卷表
CREATE TABLE IF NOT EXISTS complete_questionnaires (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    -- 八纲辨证结果
    bagang_type_code TEXT,
    bagang_type_name TEXT,
    bagang_radar_data TEXT,
    bagang_energy_data TEXT,
    bagang_answers TEXT,
    -- 卫健委结果
    wjw_main_constitution TEXT,
    wjw_main_score INTEGER,
    wjw_main_result TEXT,
    wjw_all_results TEXT,
    wjw_scores TEXT,
    wjw_answers TEXT,
    -- 原始答案
    raw_answers TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_users_nickname ON users(nickname);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
CREATE INDEX IF NOT EXISTS idx_complete_user_id ON complete_questionnaires(user_id);
CREATE INDEX IF NOT EXISTS idx_complete_bagang_type ON complete_questionnaires(bagang_type_code);
CREATE INDEX IF NOT EXISTS idx_complete_wjw_main ON complete_questionnaires(wjw_main_constitution);
CREATE INDEX IF NOT EXISTS idx_complete_created_at ON complete_questionnaires(created_at);

-- 插入默认管理员密码
INSERT INTO admin_password (password) VALUES ('8888')
ON CONFLICT DO NOTHING;
