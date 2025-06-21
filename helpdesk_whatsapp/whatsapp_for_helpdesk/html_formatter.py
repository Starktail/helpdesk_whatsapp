import re
from typing import Optional

from bs4 import BeautifulSoup, NavigableString

# --- Configuration ---
# Map HTML tags to WhatsApp formatting characters.
# You can extend this map if needed.
TAG_TO_WHATSAPP = {
	"b": "*",
	"strong": "*",
	"i": "_",
	"em": "_",
	"s": "~",
	"strike": "~",
	"code": "```",
	"pre": "```",
}

# Block-level tags that should be followed by a newline for readability.
BLOCK_TAGS = ["p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "ul", "ol", "li"]


def html_to_whatsapp(html_string: str, selector: str | None) -> str:
	"""
	Converts an HTML string into a WhatsApp-formatted text string.

	This function parses the HTML, traverses the document tree, and replaces
	formatting tags (<b>, <i>, etc.) with WhatsApp's markdown-like syntax
	(*, _, etc.).

	Args:
	    html_string: The input HTML string to convert.
	    selector: (Optional) A CSS selector to target a specific part of the
	              HTML document, like '.ql-editor'. If None, the entire
	              document is processed.

	Returns:
	    A string with WhatsApp formatting.
	"""
	if not html_string:
		return ""

	# 1. Use BeautifulSoup to parse the HTML.
	#    lxml is a fast and robust parser.
	soup = BeautifulSoup(html_string, "lxml")

	# 2. (Optional) Select a specific part of the document if a selector is given.
	#    This is useful for Frappe editor fields which are often wrapped in a
	#    specific class, like '.ql-editor'.
	root_node = soup.select_one(selector) if selector else soup

	if not root_node:
		# Fallback to the full soup if the selector doesn't find anything.
		root_node = soup

	# 3. Define a recursive function to process each node in the HTML tree.
	def process_node(node) -> str:
		# --- Case 1: It's a plain text node (NavigableString) ---
		if isinstance(node, NavigableString):
			# WhatsApp doesn't render non-breaking spaces correctly, convert them.
			# Also, strip whitespace from text nodes that are just newlines.
			return str(node).replace("\xa0", " ").strip("\n")

		# --- Case 2: It's a <br> tag ---
		if node.name == "br":
			return "\n"

		# --- Case 3: It's a formatting or block tag ---

		# Recursively process all child nodes and join their results.
		processed_children = "".join(process_node(child) for child in node.children)

		# Apply WhatsApp formatting if the tag is in our map
		if node.name in TAG_TO_WHATSAPP:
			char = TAG_TO_WHATSAPP[node.name]

			# This logic is key: it places the formatting characters *around*
			# the text, but *inside* any surrounding whitespace.
			# e.g., " <b> text </b> " -> " *text* " instead of "*  text  *"
			content = processed_children.strip()
			if not content:
				return processed_children  # Don't format empty/whitespace-only tags

			leading_ws = processed_children[: len(processed_children) - len(processed_children.lstrip())]
			trailing_ws = processed_children[len(processed_children.rstrip()) :]

			return f"{leading_ws}{char}{content}{char}{trailing_ws}"

		# Add a newline after block-level elements for separation
		if node.name in BLOCK_TAGS:
			# Add newline only if the content doesn't already end with one
			# to avoid excessive blank lines.
			stripped_children = processed_children.rstrip()
			if stripped_children:
				return stripped_children + "\n"

		# For any other tag (like <span>, <a>, etc.), just return the content
		return processed_children

	# 4. Start the conversion process from the root node.
	whatsapp_text = process_node(root_node)

	# 5. Final cleanup
	#    - Collapse more than two consecutive newlines into just two.
	#    - Collapse multiple spaces into a single space (except in code blocks).
	#    - Strip leading/trailing whitespace from the final output.
	whatsapp_text = re.sub(r"(\s*\n){3,}", "\n\n", whatsapp_text)
	whatsapp_text = re.sub(r" +", " ", whatsapp_text)

	return whatsapp_text.strip()
