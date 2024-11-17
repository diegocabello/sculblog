use rusqlite::{params, Connection};         // For `params!` macro and `Connection` type
use std::path::Path;                        // For `Path` type
use std::fs;                                // For file operations like `fs::write` and `fs::read_to_string`
use crate::Config;                          // For `Config` type (assuming it is defined in your crate)
use std::env;                               // For accessing environment variables with `env::var`
use chrono::{Local, Datelike};                          // For getting the local date and time
use pulldown_cmark::{Options, Parser, html}; // For markdown parsing (Options, Parser, html module)
use regex::Regex;                           // For `Regex` type (for regex operations)
//use crate::manage_post::{create_post, process_markdown_file}; // For `create_post` and `process_markdown_file` functions

fn custom_date_format() -> String {
    let now = Local::now();
    
    // Get day, month, and year
    let day = now.day();
    let month = now.month();
    let year = now.year();
    
    // Get month name with special rules for June and July
    let month_name = match month {
        6 => "June".to_string(),   // Full month name for June
        7 => "July".to_string(),   // Full month name for July
        _ => now.format("%b").to_string(),  // Short month name (3 letters) for other months
    };

    // Format the date as "DD MMM YYYY"
    format!("{:02} {} {}", day, month_name, year)
}

pub fn create_post_php(category_path: &Path, file_name: &str) -> Result<(), Box<dyn std::error::Error>> {
    let post_content = format!("<?php $file_name = \"{}\"; include 'chain.php'; ?>", file_name);
    let post_php_path = category_path.join(format!("{}.php", file_name));
    
    if !post_php_path.exists() {
        fs::write(post_php_path, post_content)?;
        println!("Created {}.php", file_name);
    }
    Ok(())
}

pub fn create_post(config: &Config, category: &str, file_name: &str, header: &str) -> Result<(), Box<dyn std::error::Error>> {
    // Check if category exists
    let category_path = Path::new(&config.base_dir).join(category);
    if !category_path.exists() {
        return Err(format!("Category '{}' does not exist", category).into());
    }

    // Create the PHP file for the post
    create_post_php(&category_path, file_name)?;

    // Check or create the database entry
    let conn = Connection::open(&config.db_path)?;
    let exists: bool = conn.query_row(
        &format!("SELECT 1 FROM {} WHERE file_name = ?", category),
        params![file_name],
        |_| Ok(true)
    ).unwrap_or(false);

    if !exists {
        // Insert new entry with default values
        conn.execute(
            &format!(
                "INSERT INTO {} (file_name, date_splash, header, show, tags) VALUES (?, ?, ?, ?, ?)",
                category
            ),
            params![file_name, custom_date_format(), header, "", " "],
        )?;
        println!("Created database entry for '{}'", file_name);
    }

    Ok(())
}

pub fn markdown_to_html(content: &str) -> String {
    let mut options = Options::empty();
    options.insert(Options::ENABLE_STRIKETHROUGH);
    options.insert(Options::ENABLE_TABLES);
    options.insert(Options::ENABLE_FOOTNOTES);
    
    let parser = Parser::new_ext(content, options);
    let mut html_output = String::new();
    html::push_html(&mut html_output, parser);
    
    html_output
}

pub fn create_preview_html(html_content: &str) -> String {
    let re = Regex::new(r"<[^>]+>").unwrap();
    let text = re.replace_all(html_content, "").into_owned();
    if text.len() > 1500 {
        format!("{}...", &text[..1500])
    } else {
        text
    }
}


pub fn process_markdown_file(
    config: &Config,
    category: &str,
    file_name: &str,
) -> Result<(), Box<dyn std::error::Error>> {
    // Always use diego's home directory when running with sudo
    let home = "/home/diego".to_string();

    // Replace any instances of "~" or "$HOME" in the content_dir with the actual home path
    let content_dir = config.content_dir.replace("~", &home);
    let content_dir = content_dir.replace("$HOME", &home);

    // Construct the category path and file path
    let category_path = Path::new(&content_dir).join(category);
    println!("Category path: {}", category_path.display());
    let file_path = category_path.join(format!("{}.md", file_name));
    println!("File path: {}", file_path.display());

    // Verify the markdown file exists
    if !file_path.exists() {
        return Err(format!(
            "Markdown file '{}' does not exist",
            file_path.display()
        )
        .into());
    }

    // Connect to database and verify entry exists
    let conn = Connection::open(&config.db_path)?;
    let exists: bool = conn
        .query_row(
            &format!("SELECT 1 FROM {} WHERE file_name = ?", category),
            params![file_name],
            |_| Ok(true),
        )
        .unwrap_or(false);

    if !exists {
        return Err(format!("No database entry found for '{}'", file_name).into());
    }

    // Process markdown and update database
    let markdown_content = fs::read_to_string(file_path)?;
    let html_content = markdown_to_html(&markdown_content);
    let preview_html = create_preview_html(&html_content);
    let timestamp = Local::now().to_rfc3339();

    conn.execute(
        &format!(
            "UPDATE {} SET text = ?, preview_html = ? WHERE file_name = ?",
            category
        ),
        params![html_content, preview_html, file_name],
    )?;

    // Ensure PHP file exists
    let php_path = Path::new(&config.base_dir)
        .join(category)
        .join(format!("{}.php", file_name));

    if !php_path.exists() {
        create_post_php(&Path::new(&config.base_dir).join(category), file_name)?;
    }

    println!("Successfully processed '{}'", file_name);
    Ok(())
}