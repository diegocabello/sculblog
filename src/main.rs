use std::fs;
use std::path::Path;
//use pulldown_cmark::{Parser, Options}; //html
use rusqlite::{Connection}; // params
use serde::{Deserialize, Serialize};
use std::io::Read;
use toml;
//use chrono::Local;
//use regex::Regex;
use std::env;

mod manage_post;
use manage_post::{create_post, process_markdown_file};

//const home = env::var("HOME").unwrap_or_else(|_| ".".to_string());

fn get_config_path() -> String {
    let home = env::var("HOME").unwrap_or_else(|_| ".".to_string());
    format!("{}/.config/sculblog/config.toml", home)
}

const DEFAULT_BASE_DIR: &str = "/srv/http";
const DEFAULT_DB_PATH: &str = "/srv/http/database/db.db";
const DEFAULT_CONTENT_DIR: &str = "/home/diego/My Stuff/Writings/website";

#[derive(Serialize, Deserialize)]
struct Config {
    base_dir: String,
    db_path: String,
    content_dir: String,
}

impl Default for Config {
    fn default() -> Self {
        Config {
            base_dir: DEFAULT_BASE_DIR.to_string(),
            db_path: DEFAULT_DB_PATH.to_string(),
            content_dir: DEFAULT_CONTENT_DIR.to_string(),
        }
    }
}

fn load_or_create_config() -> Result<Config, Box<dyn std::error::Error>> {
    let config_path = get_config_path();
    let config_dir = Path::new(&config_path).parent().unwrap();
    
    // Create config directory if it doesn't exist
    fs::create_dir_all(config_dir)?;

    if !Path::new(&config_path).exists() {
        let config = Config::default();
        let toml = toml::to_string(&config)?;
        fs::write(&config_path, toml)?;
        
        // Also create the base directory and database directory
        fs::create_dir_all(DEFAULT_BASE_DIR)?;
        fs::create_dir_all(Path::new(DEFAULT_DB_PATH).parent().unwrap())?;
        
        return Ok(config);
    }    

    let mut file = std::fs::File::open(&config_path)?;
    let mut contents = String::new();
    file.read_to_string(&mut contents)?;
    let config: Config = toml::from_str(&contents)?;
    Ok(config)
}    

fn create_chain_php(category_path: &Path, category_name: &str) -> Result<(), Box<dyn std::error::Error>> {
    let chain_content = format!(
        "<?php\n$page = '{}';\n$attributes = 'post-attrs.php';\ninclude '../resources/post-template.php';\n?>",
        category_name
    );
    
    let chain_path = category_path.join("chain.php");
    fs::write(chain_path, chain_content)?;
    println!("Created chain.php for category '{}'", category_name);
    Ok(())
}

fn create_category(config: &Config, name: &str) -> Result<(), Box<dyn std::error::Error>> {
    // Create folder
    let folder_path = Path::new(&config.base_dir).join(name);
    fs::create_dir_all(&folder_path)?;
    println!("Folder '{}' created successfully", name);

    // Create chain.php file
    create_chain_php(&folder_path, name)?;

    // Create table in SQLite database
    let conn = Connection::open(&config.db_path)?;
    conn.execute(
        &format!(
            "CREATE TABLE IF NOT EXISTS {} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                header TEXT,
                text TEXT,
                date_splash TEXT,
                date_order INTEGER,
                file_name TEXT,
                preview_html TEXT,
                show TEXT,
                tags TEXT
            )",
            name
        ),
        [],
    )?;
    println!("Table '{}' created successfully in the database", name);
    Ok(())
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let config = load_or_create_config()?;
    let args: Vec<String> = std::env::args().collect();

    if args.len() < 2 {
        println!("Usage:");
        println!("  {} create category <category_name>", args[0]);
        println!("  {} create post <category_name> <file_name>", args[0]);
        println!("  {} process <category_name> <file_name>", args[0]);
        return Ok(());
    }

    match args[1].as_str() {
        "create" => {
            if args.len() < 4 {
                println!("Usage:");
                println!("  {} create category <category_name>", args[0]);
                println!("  {} create post <category_name> <file_name> <header>", args[0]);
                return Ok(());
            }
            match args[2].as_str() {
                "category" => {
                    create_category(&config, &args[3])?;
                }
                "post" => {
                    if args.len() < 5 {
                        println!("Usage: {} create post <category_name> <file_name> <header>", args[0]);
                        return Ok(());
                    }
                    create_post(&config, &args[3], &args[4], &args[5])?;
                }
                _ => println!("Invalid create command. Use 'category' or 'post'"),
            }
        }
        "process" => {
            if args.len() < 4 {
                println!("Usage: {} process <category_name> <file_name>", args[0]);
                return Ok(());
            }
            process_markdown_file(&config, &args[2], &args[3])?;
        }
        _ => println!("Invalid command. Use 'create' or 'process'"),
    }

    Ok(())
}