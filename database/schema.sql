CREATE TABLE IF NOT EXISTS cases (
    case_id TEXT PRIMARY KEY,
    embedding TEXT, -- JSON serialized list of floats
    text TEXT,
    decision TEXT,
    decision_reason TEXT,
    case_source TEXT
);
