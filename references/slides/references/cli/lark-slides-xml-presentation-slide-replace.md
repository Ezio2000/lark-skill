<a id="slides-replace-slide块级替换--插入"></a>
# slides +replace-slide (block-level replace / insert)

Replace or insert known blocks on a specified page. First use `+xml-get --slide-id` to get the latest `block_id`, then use `+replace-slide` to write; this operation does not change the page order.

```bash
lark-cli slides +replace-slide --as user \
  --presentation "$PRES_ID" --slide-id "$SID" \
  --parts '[{"action":"block_replace","block_id":"bUn","replacement":"<shape type=\"text\" topLeftX=\"80\" topLeftY=\"80\" width=\"800\" height=\"120\"><content textType=\"title\" fontSize=\"32\"><p>新标题</p></content></shape>"}]'
```

`block_replace` uses `block_id` and `replacement`; appending elements uses `block_insert` and `insertion`. For the complete parts structure, validation, and limits, see [lark-slides-replace-slide.md](lark-slides-replace-slide.md).
