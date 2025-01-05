#[derive(Debug, sqlx::FromRow)]
struct User {
    id: i32,
    username: String,
    email: String,
}

let pool = sqlx::sqlite::SqlitePool::connect("sqlite:messages.db").await?;

