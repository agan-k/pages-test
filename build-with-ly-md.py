import os
import shutil
import subprocess
import sys
import re
import markdown
import frontmatter

def compile_lilypond_snippet(ly_code_or_path, base_name, is_file_path=False, path_prefix=""):
    """Compiles a LilyPond file or raw string block into SVG assets in docs/"""
    target_source_path = os.path.join("docs", f"{base_name}.ly")
    
    if is_file_path:
        if os.path.exists(ly_code_or_path):
            shutil.copy2(ly_code_or_path, target_source_path)
        else:
            print(f"⚠️ Warning: Reference path missing: {ly_code_or_path}")
            return ""
    else:
        with open(target_source_path, "w") as f:
            f.write(ly_code_or_path)

    cmd = [
        "lilypond", "-dbackend=svg", "-dno-point-and-click",
        f"--output=docs/{base_name}", target_source_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Core compilation crash on code block: {base_name}")
        print(result.stderr)
        sys.exit(1)
        
    log_file = f"docs/{base_name}.log"
    if os.path.exists(log_file):
        os.remove(log_file)

    page_images = []
    for item in os.listdir("docs"):
        if item.startswith(f"{base_name}-") and item.endswith(".svg"):
            page_images.append(item)
            
    page_images.sort(key=lambda x: [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', x)])
    
    if not page_images:
        single_svg_name = f"{base_name}.svg"
        if os.path.exists(os.path.join("docs", single_svg_name)):
            page_images.append(single_svg_name)
            
    img_block_markup = []
    for svg_page in page_images:
        tag = f'<img src="{path_prefix}{svg_page}" class="lilypond-score" style="display: block; max-width: 100%; margin-bottom: 20px;" alt="Page from score {base_name}">'
        img_block_markup.append(tag)
        
    return "\n".join(img_block_markup)

def process_lilypond_tags(html_content, unique_page_id, path_prefix=""):
    """Finds both <lilypond file="..." /> and <lilypond>...</lilypond> tags and converts them to SVG images"""
    snippet_counter = 1
    
    file_tags = re.findall(r'<lilypond\s+file=["\']([^"\']+\.ly)["\']\s*/>', html_content)
    for ly_filename in file_tags:
        source_ly_path = os.path.join("content", "lilypond", ly_filename)
        base_name = ly_filename.replace(".ly", "")
        img_markup = compile_lilypond_snippet(source_ly_path, base_name, is_file_path=True, path_prefix=path_prefix)
        html_content = html_content.replace(f'<lilypond file="{ly_filename}" />', img_markup)
        html_content = html_content.replace(f'<lilypond file=\'{ly_filename}\' />', img_markup)

    block_tags = re.findall(r'<lilypond>(.*?)</lilypond>', html_content, re.DOTALL)
    for raw_code in block_tags:
        clean_code = raw_code.strip()
        base_name = f"snippet-{unique_page_id}-{snippet_counter}"
        img_markup = compile_lilypond_snippet(clean_code, base_name, is_file_path=False, path_prefix=path_prefix)
        html_content = html_content.replace(f'<lilypond>{raw_code}</lilypond>', img_markup)
        snippet_counter += 1
        
    return html_content

def generate_dynamic_navbar_markup(pages_dir):
    """Scans the pages folder, strips dashes/underscores from multi-word filenames, and capitalizes them for links."""
    nav_items = []
    if os.path.exists(pages_dir):
        for filename in sorted(os.listdir(pages_dir)):
            # Strictly validate standard .html extensions, while excluding index.html
            if filename.endswith(".html") and filename != "index.html":
                file_path = os.path.join(pages_dir, filename)
                with open(file_path, "r") as f:
                    content = f.read()
                
                # Check for explicit custom override title comment: <!-- title: Custom Name -->
                title_match = re.search(r'<!--\s*title:\s*(.*?)\s*-->', content)
                if title_match:
                    display_title = title_match.group(1)
                else:
                    # Strip extension, convert dashes/underscores to spaces, and apply Title Case
                    base_name = filename.replace(".html", "")
                    display_title = base_name.replace("-", " ").replace("_", " ").title()
                
                nav_items.append({"filename": filename, "title": display_title})
                
    nav_items.append({"filename": "articles.html", "title": "Articles"})
    return nav_items

def build_navbar_for_depth(nav_items, path_prefix):
    """Constructs the HTML <li> markup list based on current folder relative paths"""
    list_items = []
    for item in nav_items:
        markup = f'<li><a href="{path_prefix}{item["filename"]}">{item["title"]}</a></li>'
        list_items.append(markup)
    return "\n".join(list_items)

def build_site():
    if os.path.exists("docs"):
        print("Cleaning up old build files in docs/...")
        shutil.rmtree("docs")
    
    os.makedirs("docs/articles", exist_ok=True)
    os.makedirs("docs/assets", exist_ok=True)
    print("Created fresh docs/ directory architecture.")
    
    try:
        with open("templates/layout.html", "r") as f: layout = f.read()
        with open("templates/article-layout.html", "r") as f: article_layout = f.read()
        with open("templates/navbar.html", "r") as f: navbar_template = f.read()
    except FileNotFoundError as e:
        print(f"Error loading assets or layout files: {e}")
        sys.exit(1)
        
    if os.path.exists("assets/style.css"): shutil.copy("assets/style.css", "docs/assets/style.css")
    if os.path.exists("assets/main.js"): shutil.copy("assets/main.js", "docs/assets/main.js")
    if os.path.exists("assets/images"): shutil.copytree("assets/images", "docs/assets/images", dirs_exist_ok=True)

    nav_items_map = generate_dynamic_navbar_markup("pages")

    # PROCESS STANDARD HTML PAGES
    if os.path.exists("pages"):
        for filename in os.listdir("pages"):
            if filename.endswith(".html"):
                with open(f"pages/{filename}", "r") as f:
                    page_content = f.read()
                
                links_html = build_navbar_for_depth(nav_items_map, path_prefix="")
                current_navbar = navbar_template.replace("{{ path_prefix }}", "").replace("{{ navbar_links }}", links_html)
                final_html = layout.replace("{{ navbar }}", current_navbar).replace("{{ content }}", page_content)
                page_id = filename.replace(".html", "")
                final_html = process_lilypond_tags(final_html, page_id, path_prefix="")
                
                with open(f"docs/{filename}", "w") as f:
                    f.write(final_html)
                print(f"Compiled page: docs/{filename}")

    # PROCESS MARKDOWN ARTICLES
    articles_metadata = []
    source_articles_dir = os.path.join("content", "articles")
    
    if os.path.exists(source_articles_dir):
        for filename in os.listdir(source_articles_dir):
            if filename.endswith(".md"):
                post_path = os.path.join(source_articles_dir, filename)
                post = frontmatter.load(post_path)
                post_html_content = markdown.markdown(post.content)
                
                built_article = article_layout
                built_article = built_article.replace("{{ title }}", str(post.get("title", "Untitled")))
                built_article = built_article.replace("{{ date }}", str(post.get("date", "Unknown Date")))
                built_article = built_article.replace("{{ author }}", str(post.get("author", "Anonymous")))
                
                summary_text = post.get("summary", "")
                if summary_text:
                    built_article = built_article.replace("{{ summary }}", str(summary_text))
                    built_article = built_article.replace("{% if summary %}", "").replace("{% endif %}", "")
                else:
                    built_article = re.sub(r'{% if summary %}.*?{% endif %}', '', built_article, flags=re.DOTALL)

                built_article = built_article.replace("{{ content }}", post_html_content)
                links_html = build_navbar_for_depth(nav_items_map, path_prefix="../")
                current_navbar = navbar_template.replace("{{ path_prefix }}", "../").replace("{{ navbar_links }}", links_html)
                final_post_html = layout.replace("{{ navbar }}", current_navbar).replace("{{ content }}", built_article)
                
                article_id = filename.replace(".md", "")
                final_post_html = process_lilypond_tags(final_post_html, article_id, path_prefix="../")
                
                output_name = f"articles/{article_id}.html"
                with open(os.path.join("docs", output_name), "w") as f:
                    f.write(final_post_html)
                
                articles_metadata.append({
                    "title": str(post.get("title", "Untitled")),
                    "date": str(post.get("date", "0000-00-00")),
                    "summary": str(summary_text),
                    "url": output_name
                })
                print(f"Compiled blog post article: docs/{output_name}")

    # GENERATE ARTICLES FEED LANDING PAGE
    articles_metadata.sort(key=lambda x: x["date"], reverse=True)
    
    feed_html_list = ["<h1>Latest Articles</h1>", '<ul class="article-feed-list" style="list-style:none; padding:0;">']
    for meta in articles_metadata:
        item = f'''
        <li style="margin-bottom: 25px;">
            <h2><a href="{meta['url']}">{meta['title']}</a></h2>
            <small style="color:#666;">Published: {meta['date']}</small>
            <p>{meta['summary']}</p>
        </li>
        '''
        feed_html_list.append(item)
    feed_html_list.append("</ul>")
    
    feed_content = "\n".join(feed_html_list)
    links_html = build_navbar_for_depth(nav_items_map, path_prefix="")
    current_navbar = navbar_template.replace("{{ path_prefix }}", "").replace("{{ navbar_links }}", links_html)
    final_feed_html = layout.replace("{{ navbar }}", current_navbar).replace("{{ content }}", feed_content)
    
    with open("docs/articles.html", "w") as f:
        f.write(final_feed_html)
    print("Compiled feed center page directory: docs/articles.html")

    for file in os.listdir("docs"):
        if file.endswith(".ly"):
            os.remove(os.path.join("docs", file))
            
    print("Build complete! All files generated in docs/.")

if __name__ == "__main__":
    build_site()
