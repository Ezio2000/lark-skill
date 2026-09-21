<a id="okr-contentblock-富文本格式"></a>
# OKR ContentBlock Rich Text Format

The content/notes fields in OKR's Objective and KeyResult use the `ContentBlock` rich text format. This document describes its structure and usage.

<a id="两种输入输出风格"></a>
## Two Input/Output Styles

OKR shortcuts support the `--style` flag to control the input/output format of the content/notes fields:

| `--style` Value  | Description                                                                 | Applicable Scenarios                     |
|--------------|--------------------------------------------------------------------|--------------------------|
| `simple` (default) | Semi-plain text format `SemiPlainContent`, a simplified JSON structure containing only text, mention, docs, and images | Most scenarios, simple and easy to use               |
| `richtext`   | Raw `ContentBlock` rich text format, with complete block structure and style information                                | When precise control over @mention user positions or inclusion of image/document links is needed |

**Important**: On input, the format is strictly validated based on the `--style` value and is not auto-detected. On output, read operations (such as `+cycle-detail`, `+progress-get`) return the corresponding format based on `--style`.

<a id="contentblock-结构概览"></a>
## ContentBlock Structure Overview

```json
{
  "blocks": [
    {
      "block_element_type": "paragraph",
      "paragraph": {
        "style": {
          "list": {
            "list_type": "bullet",
            "indent_level": 0,
            "number": 1
          }
        },
        "elements": [
          {
            "paragraph_element_type": "textRun",
            "text_run": {
              "text": "Hello World",
              "style": {
                "bold": true,
                "strike_through": false,
                "back_color": {
                  "red": 255,
                  "green": 0,
                  "blue": 0,
                  "alpha": 1
                },
                "text_color": {
                  "red": 0,
                  "green": 255,
                  "blue": 0,
                  "alpha": 1
                },
                "link": {
                  "url": "https://example.com"
                }
              }
            }
          },
          {
            "paragraph_element_type": "docsLink",
            "docs_link": {
              "url": "https://larkoffice.com/docx/xxx",
              "title": "Lark Document"
            }
          },
          {
            "paragraph_element_type": "mention",
            "mention": {
              "user_id": "ou_xxx"
            }
          }
        ]
      }
    },
    {
      "block_element_type": "gallery",
      "gallery": {
        "images": [
          {
            "file_token": "file_xxx",
            "src": "https://...",
            "width": 800,
            "height": 600
          }
        ]
      }
    }
  ]
}
```

<a id="类型定义"></a>
## Type Definitions

### ContentBlock

Root-level content block.

| Field       | Type                      | Description      |
|----------|-------------------------|---------|
| `blocks` | `ContentBlockElement[]` | Array of content block elements |

### ContentBlockElement

Content block element, supporting paragraphs or galleries.

| Field                   | Type                 | Description                                         |
|----------------------|--------------------|--------------------------------------------|
| `block_element_type` | `BlockElementType` | Block type: `paragraph` \| `gallery`               |
| `paragraph`          | `ContentParagraph` | Paragraph content (when `block_element_type="paragraph"`) |
| `gallery`            | `ContentGallery`   | Gallery content (when `block_element_type="gallery"`)   |

### ContentParagraph

Paragraph content.

| Field         | Type                          | Description          |
|------------|-----------------------------|-------------|
| `style`    | `ContentParagraphStyle`     | Paragraph style (list type, etc.) |
| `elements` | `ContentParagraphElement[]` | Array of elements within the paragraph     |

### ContentParagraphElement

Element within a paragraph, supporting text, document links, and mentions.

| Field                       | Type                     | Description                                        |
|--------------------------|------------------------|-------------------------------------------|
| `paragraph_element_type` | `ParagraphElementType` | Element type: `textRun` \| `docsLink` \| `mention` |
| `text_run`               | `ContentTextRun`       | Text content                                      |
| `docs_link`              | `ContentDocsLink`      | Feishu document link                                    |
| `mention`                | `ContentMention`       | User mention                                      |

### ContentTextRun

Text block.

| Field      | Type                 | Description   |
|---------|--------------------|------|
| `text`  | `string`           | Text content |
| `style` | `ContentTextStyle` | Text style |

### ContentTextStyle

Text style.

| Field               | Type             | Description    |
|------------------|----------------|-------|
| `bold`           | `boolean`      | Whether bold  |
| `strike_through` | `boolean`      | Whether strikethrough |
| `back_color`     | `ContentColor` | Background color  |
| `text_color`     | `ContentColor` | Text color  |
| `link`           | `ContentLink`  | Link    |

### ContentColor

Color.

| Field      | Type        | Description           |
|---------|-----------|--------------|
| `red`   | `int32`   | Red channel (0-255) |
| `green` | `int32`   | Green channel (0-255) |
| `blue`  | `int32`   | Blue channel (0-255) |
| `alpha` | `float64` | Alpha (0-1)    |

### ContentParagraphStyle

Paragraph style.

| Field     | Type            | Description   |
|--------|---------------|------|
| `list` | `ContentList` | List style |

### ContentList

List style.

| Field             | Type         | Description                                                                  |
|----------------|------------|---------------------------------------------------------------------|
| `list_type`    | `ListType` | List type: `bullet` \| `number` \| `checkBox` \| `checkedBox` \| `indent` |
| `indent_level` | `int32`    | Indent level                                                                |
| `number`       | `int32`    | Sequence number (when `list_type="number"`)                                        |

### ContentGallery

Image block. Currently, only rich text in progress records supports displaying images.

Due to layout constraints on the progress page in the OKR application, a ContentGallery element **can contain only one image element**. To insert multiple images, multiple ContentGallery elements must be used.
(Adding multiple images to the same ContentGallery causes these images to crowd each other in the narrow horizontal layout space, resulting in a poor effect.)

| Field       | Type                   | Description    |
|----------|----------------------|-------|
| `images` | `ContentImageItem[]` | Array of image items |

### ContentImageItem

Image item.

| Field           | Type        | Description       |
|--------------|-----------|----------|
| `file_token` | `string`  | File token |
| `src`        | `string`  | Image URL   |
| `width`      | `float64` | Width       |
| `height`     | `float64` | Height       |

> **How to obtain `file_token`?** Use the [`+upload-image`](lark-okr-image-upload.md) command to upload a local image. The returned `file_token` can be used to construct a `ContentGallery` image block.

### ContentDocsLink

Feishu document link.

| Field      | Type       | Description     |
|---------|----------|--------|
| `url`   | `string` | Link URL |
| `title` | `string` | Link title   |

### ContentMention

Mention.

| Field        | Type       | Description    |
|-----------|----------|-------|
| `user_id` | `string` | User ID |

### ContentLink

Link.

| Field    | Type       | Description     |
|-------|----------|--------|
| `url` | `string` | Link URL |

<a id="semiplaincontent-半纯文本格式"></a>
## SemiPlainContent Semi-Plain Text Format

`SemiPlainContent` is a simplified, lossy representation of `ContentBlock`, suitable for most scenarios that do not require complex formatting.

<a id="结构"></a>
### Structure

```json
{
  "text": "任务一 @{ou_zhangsan} ，任务二 @{ou_lisi} ",
  "mention": ["ou_zhangsan", "ou_lisi"],
  "docs": [
    {
      "title": "产品需求文档",
      "url": "https://larkoffice.com/docx/xxx"
    }
  ],
  "images": [
    "https://example.com/image.png"
  ]
}
```

<a id="类型定义-1"></a>
### Type Definitions

| Field        | Type               | Description                                                                                                        |
|-----------|------------------|-----------------------------------------------------------------------------------------------------------|
| `text`    | `string`         | Plain text content (required, cannot be empty). **On output**, it contains ` @{userID} ` placeholders to preserve the positional context of mentions; **on input**, `@{...}` placeholders are automatically stripped, and only the content of the `mention` field is recognized |
| `mention` | `string[]`       | List of user IDs (optional), corresponding one-to-one with the `@{userID}` placeholders in text. On input, they are converted in order into mention elements **placed at the end of the text**                                 |
| `docs`    | `SemiPlainDoc[]` | List of documents (included only on output; not supported by the simple style on input)                                                                             |
| `images`  | `string[]`       | List of image URLs (included only on output; not supported by the simple style on input)                                                                        |

### SemiPlainDoc

| Field      | Type       | Description     |
|---------|----------|--------|
| `title` | `string` | Document title   |
| `url`   | `string` | Document URL |

<a id="双向转换说明"></a>
### Bidirectional Conversion Notes

- **ContentBlock → SemiPlainContent** (on output): Extracts plain text, mentioned users, document links, and image URLs, discarding formatting information (bold, lists, colors, etc.). **The positional information of mentions is preserved in text via ` @{userID} ` placeholders**, and userID is also collected into the mention array
- **SemiPlainContent → ContentBlock** (on input): Automatically strips `@{...}` placeholders from text, then merges text and mention into a single paragraph, with mentions appended in order at the end of the text. docs and images are ignored on input (not supported by the simple style)

<a id="使用示例"></a>
## Usage Examples

<a id="示例-0--style-simple-半纯文本格式"></a>
### Example 0: --style simple Semi-Plain Text Format

```json
{
  "text": "提升用户满意度",
  "mention": ["ou_123"]
}
```

Usage:
```bash
lark-cli okr +patch --level objective --style simple --target-id 123 --content '{"text":"提升用户满意度","mention":["ou_123"]}'
```

<a id="示例-1简单文本段落richtext-风格"></a>
### Example 1: Simple Text Paragraph (richtext style)

```json
{
  "blocks": [
    {
      "block_element_type": "paragraph",
      "paragraph": {
        "elements": [
          {
            "paragraph_element_type": "textRun",
            "text_run": {
              "text": "提升用户满意度"
            }
          }
        ]
      }
    }
  ]
}
```

<a id="示例-2带格式的文本段落"></a>
### Example 2: Formatted Text Paragraph

```json
{
  "blocks": [
    {
      "block_element_type": "paragraph",
      "paragraph": {
        "elements": [
          {
            "paragraph_element_type": "textRun",
            "text_run": {
              "text": "Q2 目标",
              "style": {
                "bold": true
              }
            }
          },
          {
            "paragraph_element_type": "textRun",
            "text_run": {
              "text": " - 提升产品质量"
            }
          }
        ]
      }
    }
  ]
}
```

<a id="示例-3带列表的段落"></a>
### Example 3: Paragraph with a List

```json
{
  "blocks": [
    {
      "block_element_type": "paragraph",
      "paragraph": {
        "style": {
          "list": {
            "list_type": "bullet",
            "indent_level": 0
          }
        },
        "elements": [
          {
            "paragraph_element_type": "textRun",
            "text_run": {
              "text": "完成功能开发"
            }
          }
        ]
      }
    },
    {
      "block_element_type": "paragraph",
      "paragraph": {
        "style": {
          "list": {
            "list_type": "bullet",
            "indent_level": 0
          }
        },
        "elements": [
          {
            "paragraph_element_type": "textRun",
            "text_run": {
              "text": "进行用户测试"
            }
          }
        ]
      }
    }
  ]
}
```

<a id="示例-4带用户提及和图片仅进展记录支持的段落"></a>
### Example 4: Paragraph with User Mentions and Images (supported only in progress records)

```json
{
  "blocks": [
    {
      "block_element_type": "paragraph",
      "paragraph": {
        "elements": [
          {
            "paragraph_element_type": "mention",
            "mention": {
              "user_id": "ou_example_user"
            }
          },
          {
            "paragraph_element_type": "textRun",
            "text_run": {
              "text": " 请关注此进度并查看以下图片"
            }
          }
        ]
      }
    },
    {
      "block_element_type": "gallery",
      "gallery": {
        "images": [
          {
            "file_token": "img_example_token",
            "src": "https://example.com/image.png",
            "width": 800,
            "height": 600
          }
        ]
      }
    }
  ]
}
```
