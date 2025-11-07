PART,MANUFACTURER,DESCRIPTION are the only correct fields from David's csv
- must match from matching_context.md

copy paste cleaned version of matching_context.md into gemini memory

strict input and output for gemini
- use planning mode to iterate on the plan and rigorously critique plan
- plan before execution!
    - think about if execution is even correct / necessary


ReAct: reason -> Act:
- allows debugging of llm reasoning




copilot studio:
- copilot studio mcp github
- background of how to use mcp in copilot studio



break down written summary and matching into tasks for sprint planning:
1. clean md file
2. etc 
3. etc

do after meeting ^^
- point is to have agile methodology
- helps deliver what client actually wants over time




review db design
- necessary for multiple data sources beyond the manual
- stay focused on what properties/data is guaranteed to be true
- 

different relationships examples
- this vendor only sells these system parts
    - vendor A manufactures only syste codes 1,2, and 3
- this assembly codes only related to these some system etc
    - assembly code xyz is under system code abc
    - same for component
- above are only examples, must generate relationships from manual