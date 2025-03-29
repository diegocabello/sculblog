import markdown
from markdown.inlinepatterns import InlineProcessor
from markdown.blockprocessors import BlockProcessor
import xml.etree.ElementTree as etree
import re

LINK_PATTERN = r'\[(.*?)\]\{(https?://[^\}]+)\}'

class NewWindowLinkProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        text, href = m.group(1), m.group(2)
        el = etree.Element('a', href=href, target="_blank")
        el.text = text
        return el, m.start(0), m.end(0)

class SubsectionProcessor(BlockProcessor):
    def __init__(self, parser):
        super().__init__(parser)
        self.RE_START = re.compile(r'^\|{2,}$')
        self.RE_END = re.compile(r'^\|{2,}$')
        self.section_stack = []

    def test(self, parent, block):
        return bool(self.RE_START.match(block.split('\n')[0]) or 
                   self.RE_END.match(block.split('\n')[0]))

    def run(self, parent, blocks):
        if not blocks:
            return False

        block = blocks.pop(0)
        pipe_count = len(block.strip())

        if self.RE_START.match(block):
            div = etree.SubElement(parent, 'div')
            div.set('class', f'subsection level-{pipe_count-1}')
            
            section_info = {'level': pipe_count, 'element': div}
            self.section_stack.append(section_info)
            
            while blocks:
                if (self.RE_END.match(blocks[0]) and 
                    len(blocks[0].strip()) == pipe_count):
                    blocks.pop(0)
                    self.section_stack.pop()
                    break
                
                if self.RE_START.match(blocks[0]):
                    new_count = len(blocks[0].strip())
                    if new_count > pipe_count:
                        self.run(div, blocks)
                    else:
                        break
                else:
                    self.parser.parseChunk(div, blocks.pop(0))
            
            return True

        return False

class DiegoFlavoredMarkdown(markdown.extensions.Extension):
    def extendMarkdown(self, md):
        md.inlinePatterns.register(
            NewWindowLinkProcessor(LINK_PATTERN, md), 
            'newwindowlink', 
            175
        )
        md.parser.blockprocessors.register(
            SubsectionProcessor(md.parser), 
            'subsection', 
            175
        )

def convert(text: str) -> str:
    """Convert markdown text to HTML using all custom extensions."""
    return markdown.markdown(
        text, 
        extensions=['footnotes', DiegoFlavoredMarkdown()],
        output_format='html'
    )

def count_markdown_words(markdown_text: str) -> int:
    """
    Count words in markdown text, excluding code blocks, HTML, and other markup.
    """
    # Remove code blocks
    text = re.sub(r'```[\s\S]*?```', '', markdown_text)
    
    # Remove inline code
    text = re.sub(r'`[^`]+`', '', text)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove headers (#, ##, etc)
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
    
    # Remove list markers and numbers
    text = re.sub(r'^\s*[-*+]\s+|^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    
    # Remove definition list colons
    text = re.sub(r'^\s*:', '', text, flags=re.MULTILINE)
    
    # Remove blockquotes
    text = re.sub(r'^\s*>', '', text, flags=re.MULTILINE)
    
    # Remove table formatting
    text = re.sub(r'\|', ' ', text)
    
    # Remove URLs but keep link text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\{[^}]+\}', r'\1', text)
    
    # Remove footnotes
    text = re.sub(r'\[\^[^\]]*\]', '', text)
    
    # Remove image syntax
    text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', text)
    
    # Split by whitespace and filter empty strings
    words = [word for word in text.split() if word.strip()]
    
    return len(words)

if __name__ == "__main__":
    test_text = """
# Test Document

Here's a link that opens in a new window: [Example]{https://example.com}

Here's a footnote[^1] in the text.

|| 

This is a subsection

||

===

[^1]: This is the footnote text.
    """
    
    print("HTML Output:")
    print(convert(test_text))
    print("\nWord count:", count_markdown_words(test_text))