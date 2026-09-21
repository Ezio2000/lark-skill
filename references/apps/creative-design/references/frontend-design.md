# Frontend Design

The goal is for this brief to have a visual identity that can never be mistaken for anything else: make deliberate, opinionated choices in color, typography, and layout, and take one genuine aesthetic risk you can justify—a solution that feels templated is a failed delivery.

<a id="让设计扎根于主题"></a>
## Ground the design in the subject

If the brief doesn't pin down what the product or subject is, pin it down yourself before you start designing: name a specific subject, its audience, the single task this page must accomplish, and state your choices explicitly. But if the subject, audience, and materials can't yield a direction you're confident won't need rework (a project from scratch, zero clues), follow the [`../creative-design.md`](../creative-design.md) "default aesthetic directive" to first ask the user about their preferences, and once they answer, pin down the direction per this section—if you can derive it, pin it down directly and don't interrupt the user just to collect preferences. If your memory holds information about the user's preferences, context about what they're building, or designs you've made before—use them as clues. The subject's own world—its materials, tools and instruments, characteristic artifacts, jargon and vernacular—is exactly where distinctive choices come from. Build everything using the brief's real content and subject matter.

<a id="视觉方向"></a>
## Visual direction

Before choosing colors or components, settle the direction in your thinking. Fill in four slots—each one must come from *this* subject:

- **World**—which world does this page belong to? Look in the subject's own world: its materials, tools and instruments, characteristic artifacts, jargon and vernacular.
- **Materials**—which real, existing material surfaces and marks belong to that world? List the subject's own first, one by one; don't reach for generic ones right away.
- **Palette**—which colors carry semantic or brand duties, which are neutral supporting colors, and which single accent color earns attention?
- **Signature**—the one device the whole page is remembered by. It must be possible only for this subject; a signature element that could be reused on the next brief is a default, not a choice.

Style is not decoration painted on after the layout is done. This direction determines typography, spacing, chart treatment, section rhythm, borders, icon style, and which components deserve emphasis.

<a id="设计原则"></a>
## Design principles

For web design, the hero section is the page's thesis. Open by showing the most characteristic thing in the subject's world, in a form determined by the subject: a big headline, an image, an animation, a live demo, an interactive moment. Make the choice deliberately: "big number + small label + supporting statistic + gradient accent" is the template answer; use it only when it truly is the best option.

Typography carries the page's character. The pairing of display and body typefaces must be deliberate, not whatever font families any project would reach for; and establish a clear type scale, with intent behind weight, width, and letter-spacing. Make the typographic treatment itself a memorable part of the design, not a neutral vehicle for carrying content.

Structure is information. Structural elements—numbering, eyebrows, dividers, labels—should encode information that genuinely exists in the content, not decorate it. Many cookie-cutter designs use numbered markers (01 / 02 / 03), but numbering only holds up when the content really is a sequence—a real process, or a typed timeline where the order itself carries information the reader needs. Before adopting choices like numbered markers, question whether they actually make sense.

Use motion deliberately. Think through whether and where animation serves the subject: page load sequences, scroll-triggered reveals, hover micro-interactions, ambient atmosphere. One choreographed moment is usually more powerful than scattered one-off effects; choose according to the needs of the visual direction. But sometimes less is more—superfluous animation reinforces the impression that "this design was AI-generated."

Match complexity to the vision. A maximalist direction demands finely crafted execution; a minimalist direction demands precision in spacing, type, and detail. Elegance is executing the chosen vision well.

Take the text content seriously. Design briefs often contain no real content, so the copy is yours to write. Copy brings as much of a templated feel as the design itself. See the section on writing below for more guidance.

<a id="流程头脑风暴探索规划评审构建再评审"></a>
## Process: brainstorm, explore, plan, review, build, review again

First calibrate the current landscape: today's AI-generated design clusters around three looks: (1) warm cream background (close to #F4F1EA) + high-contrast serif display type + terracotta accent; (2) near-black background + a single bright accent—acid green or vermilion; (3) broadsheet-style layout—hairline rules, zero border-radius, newspaper-like dense columns. All three hold up for some briefs, but they are defaults rather than choices, and they show up without regard to the subject. Wherever the brief pins down the visual direction, follow it strictly—the brief's own words always take priority, including when it names one of these three looks. Wherever the brief leaves a dimension free, don't spend that freedom on these three defaults. Like a hired human designer, you often have to weigh carefully between "doing what you're good at" and "treating each project as a chance to experiment and learn."

Do it in two passes. First, based on the user's design brief, brainstorm a short design plan: expand the visual direction above into a compact token system—color, type, layout, signature element. Color: describe the palette with 4–6 named hex values. Type: at least two typeface roles (a display face with character, used sparingly; a complementary body face; plus a functional face for captions or data if needed). Layout: a layout concept, developed and compared using a one-sentence text description plus ASCII wireframes. Signature element: the single unique element this page will be remembered by, embodying the brief in an appropriate way.

Then, before you start building, review this plan against the brief: if any part of it reads like a generic default you'd produce for any page of this kind (mentally run through similar prompts and see whether you'd land in roughly the same place), rather than a choice made specifically for this brief—revise that part, and state what you changed and why. Only once you've confirmed the design plan is relatively distinctive should you start writing code, following the revised plan strictly, deriving every color and type decision from the plan.

While writing code, pay attention to organizing CSS selector specificity. It's easy to write CSS classes that cancel each other out (especially between section-level selectors like `.section` and element-level selectors like `.cta`). This problem often shows up in padding/margin between blocks.

Try to do this planning and iteration in your thinking, and only show ideas to the user when you're fairly confident they'll impress.

<a id="克制与自我评审"></a>
## Restraint and self-review

Spend boldness in one place. Let the signature element be the only thing remembered; keep everything around it quiet and restrained, and cut any decoration that doesn't serve the brief. Not taking a risk can itself be a risk! Quietly hold the quality baseline without making a fuss: responsive down to mobile, visible keyboard focus, respect for reduced motion. Review your own work as you build, and take screenshots if the environment supports it—a picture is worth a thousand tokens. Think of Chanel's advice: before going out, look in the mirror and remove one accessory. Human creators have memory and are always trying new things; if you have somewhere to quickly note down what you've tried, it will help with later iterations.

<a id="再谈设计中的写作"></a>
## More on writing in design

Text appears in a design for only one reason: to make the design easier to understand, and therefore easier to use. Text is design material, not decoration. Put as much thought into copy as you put into spacing and color. Before you write, ask what this design needs to say and how best to say it to help people find their way through this experience.

Write from the perspective of the end user on the other side of the screen. Name things by what people can control and recognize, never by how the system is implemented. Users manage "notifications," not "webhook configuration." Describe what something does in plain language, rather than selling it. Specific always beats clever.

Default to the active voice. A control should state exactly what will happen when it's used: say "Save changes," not "Submit." Keep the same name for the same action throughout a flow: a button labeled "Publish" produces a toast that says "Published." The interface's vocabulary is the signage users follow as they move through the product. Coherence and consistency are how people find their way.

Treat failures and empty states as moments for guidance, not for rendering emotion. Explain what went wrong and how to fix it, in the interface's voice rather than some person's voice. Error messages don't apologize, and never be vague about what happened. An empty screen is an invitation to act.

Keep the register conversational and tuned: plain verbs, sentence case, no filler, with a tone that matches the brand and audience. Let each element do only one thing: a label labels, an example demonstrates, and no element quietly does double duty.
