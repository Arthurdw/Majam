message_types = {
    None: ("", "{emb_content}", "", None),
    "error": ("", "{emb_content}", "", 0xFF0000),
    "perm_error": ("Insufficient Permission", "{emb_content}", "", 0xc64935),
    "unex_error": ("Error...", "**Error Code:**\n```{emb_content}```", "", 0xc64935)
}
