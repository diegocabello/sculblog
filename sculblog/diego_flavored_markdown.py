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
        self.section_stack = []  # Stack to track open sections and their levels

    def test(self, parent, block):
        return bool(self.RE_START.match(block.split('\n')[0]) or 
                   self.RE_END.match(block.split('\n')[0]))

    def run(self, parent, blocks):
        if not blocks:
            return False

        block = blocks.pop(0)
        pipe_count = len(block.strip())

        if self.RE_START.match(block):
            # Create new section
            div = etree.SubElement(parent, 'div')
            div.set('class', f'subsection level-{pipe_count-1}')
            
            # Store section info
            section_info = {'level': pipe_count, 'element': div}
            self.section_stack.append(section_info)
            
            # Process content until matching end
            while blocks:
                if (self.RE_END.match(blocks[0]) and 
                    len(blocks[0].strip()) == pipe_count):
                    blocks.pop(0)  # Remove the closing pipes
                    self.section_stack.pop()  # Remove section from stack
                    break
                
                # If we encounter a new section start
                if self.RE_START.match(blocks[0]):
                    new_count = len(blocks[0].strip())
                    if new_count > pipe_count:
                        # Nested section - process recursively
                        self.run(div, blocks)
                    else:
                        # Same level or higher - close current section
                        break
                else:
                    # Regular content - parse and add to current section
                    self.parser.parseChunk(div, blocks.pop(0))
            
            return True

        return False

# class DiegoNewWindowLinkExtension(markdown.extensions.Extension):
#     def extendMarkdown(self, md):
#         md.inlinePatterns.register(
#             NewWindowLinkProcessor(LINK_PATTERN, md), 
#             'newwindowlink', 
#             175
#         )

# class DiegoSubsectionExtension(markdown.extensions.Extension):
#     def extendMarkdown(self, md):
#         md.parser.blockprocessors.register(
#             SubsectionProcessor(md.parser), 
#             'subsection', 
#             175
#         )

# class DiegoFlavoredMarkdown(markdown.extensions.Extension):
#     def extendMarkdown(self, md):
#         DiegoNewWindowLinkExtension().extendMarkdown(md)
#         DiegoSubsectionExtension().extendMarkdown(md)

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

def count_markdown_words(markdown_text: str) -> int:
    # Remove code blocks
    code_block_pattern = r'```[\s\S]*?```'
    text = re.sub(code_block_pattern, '', markdown_text)
    
    # Remove inline code
    inline_code_pattern = r'`[^`]+`'
    text = re.sub(inline_code_pattern, '', text)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove headers (#, ##, etc)
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
    
    # Remove list markers (*, -, +) and numbers with dots
    text = re.sub(r'^\s*[-*+]\s+|^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    
    # Remove definition list colons at start of lines
    text = re.sub(r'^\s*:', '', text, flags=re.MULTILINE)
    
    # Remove blockquotes
    text = re.sub(r'^\s*>', '', text, flags=re.MULTILINE)
    
    # Remove table formatting
    text = re.sub(r'\|', ' ', text)
    
    # Remove URLs from links but keep link text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    
    # Remove image syntax completely
    text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', text)

    # Remove footnotes
    text = re.sub(r'\[\^[^\]]*\]', '', text)
    
    # Split by whitespace and filter empty strings
    words = [word for word in text.split() if word.strip()]
    
    return len(words)

"""
import markdown
from markdown.inlinepatterns import InlineProcessor
import xml.etree.ElementTree as etree

# Custom pattern for matching links with curly braces
LINK_PATTERN = r'\[(.*?)\]\{(https?://[^\}]+)\}'

class NewWindowLinkProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        text, href = m.group(1), m.group(2)
        el = etree.Element('a', href=href, target="_blank")
        el.text = text
        return el, m.start(0), m.end(0)

class NewWindowLinkExtension(markdown.extensions.Extension):
    def extendMarkdown(self, md):
        md.inlinePatterns.register(NewWindowLinkProcessor(LINK_PATTERN, md), 'newwindowlink', 175)
"""
# Using the extension
#md = markdown.Markdown(extensions=[NewWindowLinkExtension()])
#text = 'Check out [Diego\'s site]{https://diegocabello.com}'
#html = md.convert(text)
#print(html)
