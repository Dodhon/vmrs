# Architecture Diagram Prompt Tips

General guidance for writing prompts that generate clean, effective architecture diagrams.

## Structure

- **Define columns/sections upfront** - State the number and order of sections (e.g., "5 columns left to right: A, B, C, D, E")
- **Use consistent hierarchy** - ALL CAPS for section headers, bullet points for details
- **Keep descriptions brief** - One line per element when possible

## Visual Clarity

- **Avoid icons unless necessary** - Simple labeled boxes are cleaner and more consistent
- **Use color to show flow types** - Assign distinct colors to different data flows (e.g., blue for one source, green for another)
- **Separate batch vs real-time** - Processing pipelines (batch) should be visually distinct from query-time operations (ad hoc)
- **Use dashed lines for feedback loops** - Helps distinguish reverse flows from primary data flows

## Common Pitfalls

- **Too much detail in one section** - If a section has more than 4-5 elements, consider simplifying or splitting
- **Redundant labels** - Don't repeat information that's already clear from context
- **Overly specific schemas** - Abbreviate relationship names (→ instead of ←[RELATIONSHIP_NAME]—)
- **Explanatory text in boxes** - Keep box labels to 2-3 words; put explanations in the prompt, not the diagram

## Flow Representation

- **Use arrows consistently** - → for primary flow, dashed for secondary/feedback
- **Show merge points explicitly** - When multiple flows combine, call it out
- **Separate concerns** - If something happens at build time vs query time, show them in different parts of the diagram

## Style Section Essentials

```
Style:
- Background color and box style
- Color assignments for different flows
- What to minimize (text, icons, labels)
- What to emphasize
```
