<a id="流程图-flowchart"></a>
# Flowchart

Applicable to: various business flow diagrams, decision trees, approval flows, timing control logic, conditional paths, system architecture topologies, etc.

For general field semantics, see `elements/schema.md`; for general layout principles, see `elements/layout.md`. This document only describes the selection boundaries and patterns for the flowchart scenario.

> [!IMPORTANT]
> **Flowcharts must use the DSL path; Mermaid is no longer used!**
> For complex branches, decisions, loops, and skip-level relationships, prefer `layout: "dagre"` to compute the topology; if it is just a regular single-line pipeline and card strong alignment is more important than automatic topology, you can also use Flex + top-level `connector` composition.

<a id="美学规范"></a>
## Aesthetic Specifications

- **Abandon crude nodes; favor full card-based design**: Core business nodes should not use only a plain-text `rect`. **Prefer Flex composite cards** (e.g., vertically combining an [Emoji title item] and a [supplementary description item] within a `vertical` frame), so that node information is structured and clearly hierarchical.
- **Semantic color orchestration**: Node background colors must never be assigned randomly. They must be mapped by state semantics: use light blue/light purple for regular paths, warning yellow for core risk control/checks, life green for successful passes, and danger red for failure circuit-breaking. Border colors can be a darker shade of the same color family to highlight card edges.
- **Unified decision logic**: Conditional branches must use `diamond` diamond nodes, and **must not omit** the third label parameter in the `layoutOptions.edges` edge definition (must clearly state "yes/no", "pass/reject").
- **Diverse shapes**: Reasonably combine different shapes to express semantics — `ellipse` for external entities/start-end points, `diamond` for decision routing, `rect` for business processing nodes, `cylinder` for persistent storage.

<a id="layout-选型"></a>
## Layout Selection

| Mode             | Applicable Conditions                                       | Core Configuration                                                                                                 |
| ---------------- | ---------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| **Main body uses Dagre** | Standard flowcharts with decisions, branches, loops, rollbacks, and skip-level relationships | Main frame sets `layout: "dagre"`, configure `rankdir: "TB"` or `rankdir: "LR"` as needed.                          |
| **Local composite nodes** | A certain step in the flow is itself a small UI composite         | The outer layer still uses `dagre`, while the composite step internally uses `layout: "vertical"` / `"horizontal"`. Such nodes are **opaque nodes**, and outer connections can only connect to the shell. |
| **Transparent subgraph**     | Needs to be grouped by business area, and connections cross area boundaries           | The sub-container declares `layout: "dagre"` + `layoutOptions: { isCluster: true }`, becoming a transparent subgraph. Internal nodes directly participate in the outer topology computation. |
| **Regular pipeline**   | Basically a single line A → B → C → D, and card alignment requirements are extremely high   | The main body can use Flex layout, and connections switch to top-level `connector`; do not force Dagre just for the sake of "automatic".                                  |

<a id="核心属性"></a>
## Core Attributes

- **`rankdir`**: `TB` (top-bottom) or `LR` (left-right). **Strongly recommend prioritizing `LR`**, to make full use of widescreen horizontal space.
- **`edges`**: Declared by `[fromId, toId, "标签"]` in the root Dagre's `layoutOptions.edges`. **Supports reverse connections** to achieve closed loops. All edges are uniformly written in the **outermost root Dagre**, not inside a cluster.
- **`ranksep` and edge text**: If explanatory text is annotated on an edge, **the spacing must be increased according to the number of characters**: `ranksep = max(60, 字数 × 16)`.
- **Adaptive sizing**: The dagre container **must** set `width: "fit-content"` and `height: "fit-content"`.
- **`clusterTitle`**: A transparent subgraph can declare a floating title via `clusterTitle` (automatically snapped to the top-left corner, bold 14px), paired with `clusterTitleColor` to specify the title color.

<a id="两种嵌套模式"></a>
## Two Nesting Modes

<a id="不透明节点opaque-node"></a>
### Opaque Node
A sub-container within Dagre, as long as it does not declare `isCluster: true`, is an atomic node with a definite width and height to the outer Dagre. Outer connections cannot address its internal child nodes. Suitable for encapsulating complex composite cards (such as business modules with icons, version numbers, and multi-line descriptions).

<a id="透明子图compound-cluster"></a>
### Transparent Subgraph (Compound Cluster)
When a sub-container declares both `layout: "dagre"` and `layoutOptions: { isCluster: true }`, it becomes a compound subgraph of the outer Dagre. Its internal child nodes directly participate in the outer topology computation, and connections can cross subgraph boundaries. Suitable for boundary containers such as network zones, functional layers, and namespaces. Recommended to pair with `borderDash: "dashed"` dashed border + light background.

<a id="骨架示例推荐范本"></a>
## Skeleton Example (Recommended Template)

The following is a complete example of a hybrid architecture topology. It simultaneously demonstrates the standard way to write a **transparent subgraph** (Kubernetes Zone, connections can pass through) and **opaque composite nodes** (DB cluster, AI engine, connections can only connect to the shell), as well as multiple shapes (ellipse / diamond / rect / cylinder) and semantic color specifications.

```json
{
  "version": 2,
  "nodes": [
    {
      "type": "frame",
      "id": "root",
      "x": 20, "y": 20,
      "layout": "dagre",
      "width": "fit-content", "height": "fit-content",
      "padding": 60,
      "fillColor": "#F8FAFC",
      "borderColor": "#CBD5E1",
      "borderWidth": 1,
      "borderRadius": 16,
      "layoutOptions": {
        "rankdir": "LR",
        "nodesep": 60,
        "ranksep": 120,
        "edges": [
          ["user", "k8s_ingress", "HTTPS request"],
          ["k8s_ingress", "web_pod", "Route UI"],
          ["k8s_ingress", "api_pod", "Route API"],
          ["web_pod", "api_pod", "Internal REST"],
          ["api_pod", "db_cluster", "SQL Query"],
          ["api_pod", "ai_service", "gRPC Stream"]
        ]
      },
      "children": [
        {
          "type": "ellipse", "id": "user", "text": "Global Users",
          "width": 110, "height": 60,
          "fillColor": "#E2E8F0", "borderColor": "#64748B", "borderWidth": 1,
          "fontSize": 14, "textColor": "#334155"
        },
        {
          "type": "frame", "id": "zone_k8s",
          "layout": "dagre",
          "layoutOptions": {
            "isCluster": true,
            "clusterTitle": "☸️ Kubernetes Zone (isCluster)",
            "clusterTitleColor": "#2563EB"
          },
          "fillColor": "#EFF6FF", "borderColor": "#60A5FA",
          "borderWidth": 2, "borderDash": "dashed", "borderRadius": 24,
          "children": [
            {
              "type": "diamond", "id": "k8s_ingress", "text": "Nginx Ingress",
              "width": 130, "height": 70,
              "fillColor": "#DBEAFE", "borderColor": "#3B82F6", "borderWidth": 2,
              "textColor": "#1E40AF"
            },
            {
              "type": "rect", "id": "web_pod", "text": "Next.js SSR Pod",
              "width": 140, "height": 48,
              "fillColor": "#BFDBFE", "borderColor": "#2563EB", "borderWidth": 2,
              "borderRadius": 8, "textColor": "#1E3A8A"
            },
            {
              "type": "rect", "id": "api_pod", "text": "Go Lang API Pod",
              "width": 140, "height": 48,
              "fillColor": "#BFDBFE", "borderColor": "#2563EB", "borderWidth": 2,
              "borderRadius": 8, "textColor": "#1E3A8A"
            }
          ]
        },
        {
          "type": "frame", "id": "db_cluster",
          "layout": "vertical", "gap": 16, "padding": [20, 24],
          "alignItems": "center",
          "fillColor": "#F0FDF4", "borderColor": "#22C55E",
          "borderWidth": 2, "borderRadius": 16,
          "children": [
            {
              "type": "text", "id": "db_title",
              "text": "🗄️ Highly Available DB (不透明)", "fontSize": 14, "textColor": "#14532D"
            },
            {
              "type": "frame", "id": "db_row", "layout": "horizontal", "gap": 20,
              "children": [
                {
                  "type": "cylinder", "id": "db_master", "text": "Master",
                  "width": 80, "height": 50,
                  "fillColor": "#DCFCE7", "borderColor": "#16A34A", "borderWidth": 1,
                  "textColor": "#166534"
                },
                {
                  "type": "cylinder", "id": "db_replica", "text": "Replica",
                  "width": 80, "height": 50,
                  "fillColor": "#DCFCE7", "borderColor": "#16A34A", "borderWidth": 1,
                  "textColor": "#166534"
                }
              ]
            }
          ]
        },
        {
          "type": "frame", "id": "ai_service",
          "layout": "vertical", "gap": 10, "padding": [16, 20],
          "alignItems": "center",
          "fillColor": "#FAF5FF", "borderColor": "#A855F7",
          "borderWidth": 2, "borderRadius": 12,
          "children": [
            {
              "type": "text", "id": "ai_title",
              "text": "🧠 Multi-Modal Engine (不透明)", "fontSize": 14, "textColor": "#6B21A8"
            },
            {
              "type": "rect", "id": "ai_version",
              "text": "v4.2.1-beta", "width": 90, "height": 22,
              "fillColor": "#E9D5FF", "borderColor": "#C084FC", "borderWidth": 1,
              "borderRadius": 4, "fontSize": 11, "textColor": "#581C87"
            },
            {
              "type": "text", "id": "ai_desc",
              "text": "Includes Vector Store\n& Transformer Blocks",
              "fontSize": 12, "textColor": "#7E22CE", "textAlign": "center"
            }
          ]
        }
      ]
    }
  ]
}
```

**Template Key Points**:
- `zone_k8s` is a **transparent subgraph** (`isCluster: true` + `clusterTitle`), and external connections cross the dashed boundary directly to `k8s_ingress`, `web_pod`, `api_pod`.
- `db_cluster` and `ai_service` are **opaque nodes** (`layout: "vertical"`), internally combining multiple lines of structured information with Flex, and are atoms with fixed width and height to the outer Dagre. Connections can only connect to the shell ID.
- All `edges` are uniformly written in the outermost root Dagre's `layoutOptions`.
- This template uses four shapes: `ellipse` (external entity), `diamond` (routing decision), `rect` (business node), `cylinder` (database storage).

<a id="陷阱与常见报错防范"></a>
## Pitfalls and Common Error Prevention

- **Misusing Mermaid**: As long as the user has not provided `mermaid` specific syntax code, even if the description clearly says "flowchart", **force the use of Dagre mode under the DSL framework**.
- **Duplicate drawing of lines**: All child node relationships in `dagre` are defined through `edges`, and the engine automatically generates connections. **Absolutely do not go to the outer layer and use `connector` nodes to connect them again**.
- **Penetrating black boxes**: Ordinary sub-containers are opaque nodes, and external connections cannot directly address their internal child nodes (the engine automatically redirects to the shell). If penetration is needed, `layout: "dagre"` and `layoutOptions: { isCluster: true }` must be declared.
- **Missing `id`**: As long as an identifier appears in `edges`, a node with the same name and `id` can definitely be found in `children`, and the spelling must be exactly consistent.
- **Width disaster**: Sub-frames inside a Dagre container must not use `fill-container`, because the dagre parent container itself is expanded by its content.
